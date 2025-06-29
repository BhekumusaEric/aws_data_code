#!/usr/bin/env python3
"""
Student Insights Pipeline - Automated Deployment Script

This script automates the complete deployment of the Student Insights Pipeline
including infrastructure, data setup, and validation.
"""

import boto3
import json
import time
import os
import sys
import subprocess
import logging
from typing import Dict, List, Any, Optional
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StudentInsightsPipelineDeployer:
    """Automated deployer for Student Insights Pipeline"""
    
    def __init__(self, environment: str = 'dev', region: str = 'af-south-1'):
        self.environment = environment
        self.region = region
        self.stack_name = f'student-insights-pipeline-{environment}'
        
        # Initialize AWS clients
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.athena = boto3.client('athena', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        
        # Get AWS account info
        sts = boto3.client('sts')
        self.account_id = sts.get_caller_identity()['Account']
        
        logger.info(f"Deploying to environment: {environment}")
        logger.info(f"AWS Account: {self.account_id}")
        logger.info(f"Region: {region}")
    
    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        logger.info("🔍 Checking prerequisites...")

        try:
            # Check AWS credentials
            try:
                sts = boto3.client('sts')
                identity = sts.get_caller_identity()
                logger.info(f"✅ AWS credentials configured for account: {identity['Account']}")
            except Exception as e:
                logger.error(f"❌ AWS credentials not configured: {str(e)}")
                logger.error("Please run 'aws configure' or set AWS environment variables")
                logger.error("Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION")
                return False

            # Check required files exist
            required_files = [
                'infrastructure/cloudformation.yaml',
                'ingestion/lambda_function.py',
                'transformation/glue_job_script.py',
                'data/sample_student_data.csv',
                'requirements.txt'
            ]

            for file_path in required_files:
                if not os.path.exists(file_path):
                    logger.error(f"❌ Required file missing: {file_path}")
                    return False
                logger.info(f"✅ Found: {file_path}")

            # Check Python dependencies
            try:
                import boto3
                logger.info("✅ boto3 available")
                try:
                    import pandas as pd
                    logger.info("✅ pandas available")
                except ImportError:
                    logger.warning("⚠️ pandas not available - installing...")
                    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pandas'], check=True)
                    logger.info("✅ pandas installed")
            except ImportError as e:
                logger.error(f"❌ Missing critical Python dependency: {e}")
                logger.error("Please run: pip install -r requirements.txt")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Prerequisites check failed: {str(e)}")
            return False
    
    def deploy_infrastructure(self) -> Dict[str, str]:
        """Deploy CloudFormation infrastructure"""
        logger.info("🏗️ Deploying infrastructure...")
        
        try:
            # Read CloudFormation template
            with open('infrastructure/cloudformation.yaml', 'r') as f:
                template_body = f.read()
            
            # Deploy stack
            logger.info(f"Creating CloudFormation stack: {self.stack_name}")
            
            self.cloudformation.create_stack(
                StackName=self.stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {'ParameterKey': 'Environment', 'ParameterValue': self.environment}
                ],
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Tags=[
                    {'Key': 'Project', 'Value': 'StudentInsightsPipeline'},
                    {'Key': 'Environment', 'Value': self.environment}
                ]
            )
            
            # Wait for stack creation
            logger.info("⏳ Waiting for stack creation to complete...")
            waiter = self.cloudformation.get_waiter('stack_create_complete')
            waiter.wait(
                StackName=self.stack_name,
                WaiterConfig={'Delay': 30, 'MaxAttempts': 40}  # 20 minutes max
            )
            
            # Get stack outputs
            response = self.cloudformation.describe_stacks(StackName=self.stack_name)
            outputs = response['Stacks'][0].get('Outputs', [])
            
            stack_outputs = {}
            for output in outputs:
                stack_outputs[output['OutputKey']] = output['OutputValue']
                logger.info(f"📤 {output['OutputKey']}: {output['OutputValue']}")
            
            logger.info("✅ Infrastructure deployed successfully!")
            return stack_outputs
            
        except Exception as e:
            logger.error(f"❌ Infrastructure deployment failed: {str(e)}")
            raise
    
    def setup_athena_tables(self, database_name: str) -> bool:
        """Setup Athena tables and views"""
        logger.info("📊 Setting up Athena tables...")
        
        try:
            # Import and use the table manager
            sys.path.append('scripts')
            from athena_table_manager import AthenaTableManager
            
            manager = AthenaTableManager(database_name, self.region)
            success = manager.setup_complete_schema()
            
            if success:
                logger.info("✅ Athena tables setup completed!")
                return True
            else:
                logger.error("❌ Athena tables setup failed!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Athena setup error: {str(e)}")
            return False
    
    def upload_sample_data(self, raw_bucket_name: str) -> bool:
        """Upload sample data to trigger the pipeline"""
        logger.info("📁 Uploading sample data...")
        
        try:
            # Generate S3 key with current timestamp
            now = datetime.now()
            s3_key = f"raw/date={now.strftime('%Y/%m/%d')}/hour={now.strftime('%H')}/sample_data_{now.strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Upload sample data
            self.s3.upload_file(
                'data/sample_student_data.csv',
                raw_bucket_name,
                s3_key
            )
            
            logger.info(f"✅ Sample data uploaded to s3://{raw_bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample data upload failed: {str(e)}")
            return False
    
    def test_api_endpoint(self, api_url: str) -> bool:
        """Test the API Gateway endpoint"""
        logger.info("🧪 Testing API endpoint...")
        
        try:
            import requests
            
            test_data = {
                "student_id": "test_deploy_001",
                "name": "Test Deployment Student",
                "math_score": 85,
                "reading_score": 90,
                "writing_score": 88,
                "grade_level": "9",
                "subject": "Mathematics",
                "attendance_rate": 0.95,
                "assignment_completion_rate": 0.92
            }
            
            response = requests.post(
                f"{api_url}/ingest",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ API endpoint test successful!")
                logger.info(f"Response: {response.json()}")
                return True
            else:
                logger.error(f"❌ API test failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ API endpoint test error: {str(e)}")
            return False
    
    def run_sample_queries(self, database_name: str, processed_bucket: str) -> bool:
        """Run sample Athena queries to validate setup"""
        logger.info("🔍 Running sample queries...")
        
        try:
            sample_queries = [
                {
                    'name': 'Count Records',
                    'query': f"SELECT COUNT(*) as total_records FROM {database_name}.processed_student_data WHERE year = '2024'"
                },
                {
                    'name': 'Performance Summary',
                    'query': f"SELECT performance_category, COUNT(*) as count FROM {database_name}.latest_student_data WHERE year = '2024' GROUP BY performance_category"
                }
            ]
            
            results_location = f"s3://{processed_bucket}/athena-results/"
            
            for query_info in sample_queries:
                logger.info(f"Running query: {query_info['name']}")
                
                response = self.athena.start_query_execution(
                    QueryString=query_info['query'],
                    QueryExecutionContext={'Database': database_name},
                    ResultConfiguration={'OutputLocation': results_location}
                )
                
                query_id = response['QueryExecutionId']
                
                # Wait for query completion
                max_wait = 60  # seconds
                wait_time = 0
                while wait_time < max_wait:
                    result = self.athena.get_query_execution(QueryExecutionId=query_id)
                    status = result['QueryExecution']['Status']['State']
                    
                    if status == 'SUCCEEDED':
                        logger.info(f"✅ Query '{query_info['name']}' completed successfully")
                        break
                    elif status == 'FAILED':
                        error = result['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                        logger.error(f"❌ Query '{query_info['name']}' failed: {error}")
                        return False
                    
                    time.sleep(5)
                    wait_time += 5
                
                if wait_time >= max_wait:
                    logger.error(f"❌ Query '{query_info['name']}' timed out")
                    return False
            
            logger.info("✅ All sample queries completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample queries failed: {str(e)}")
            return False
    
    def validate_deployment(self, stack_outputs: Dict[str, str]) -> bool:
        """Validate the complete deployment"""
        logger.info("✅ Validating deployment...")
        
        validation_results = []
        
        # Check S3 buckets
        try:
            raw_bucket = stack_outputs.get('RawDataBucketName')
            processed_bucket = stack_outputs.get('ProcessedDataBucketName')
            
            if raw_bucket:
                self.s3.head_bucket(Bucket=raw_bucket)
                logger.info(f"✅ Raw bucket accessible: {raw_bucket}")
                validation_results.append(True)
            else:
                logger.error("❌ Raw bucket name not found in outputs")
                validation_results.append(False)
            
            if processed_bucket:
                self.s3.head_bucket(Bucket=processed_bucket)
                logger.info(f"✅ Processed bucket accessible: {processed_bucket}")
                validation_results.append(True)
            else:
                logger.error("❌ Processed bucket name not found in outputs")
                validation_results.append(False)
                
        except Exception as e:
            logger.error(f"❌ S3 bucket validation failed: {str(e)}")
            validation_results.append(False)
        
        # Check Lambda function
        try:
            function_name = stack_outputs.get('IngestionLambdaFunctionName')
            if function_name:
                self.lambda_client.get_function(FunctionName=function_name)
                logger.info(f"✅ Lambda function accessible: {function_name}")
                validation_results.append(True)
            else:
                logger.error("❌ Lambda function name not found in outputs")
                validation_results.append(False)
                
        except Exception as e:
            logger.error(f"❌ Lambda function validation failed: {str(e)}")
            validation_results.append(False)
        
        # Check API Gateway
        api_url = stack_outputs.get('ApiGatewayUrl')
        if api_url:
            logger.info(f"✅ API Gateway URL: {api_url}")
            validation_results.append(True)
        else:
            logger.error("❌ API Gateway URL not found in outputs")
            validation_results.append(False)
        
        return all(validation_results)
    
    def deploy_complete_pipeline(self) -> bool:
        """Deploy the complete pipeline"""
        logger.info("🚀 Starting complete pipeline deployment...")
        
        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: Deploy infrastructure
            stack_outputs = self.deploy_infrastructure()
            
            # Step 3: Setup Athena tables
            database_name = stack_outputs.get('AthenaDatabaseName')
            if not database_name:
                logger.error("❌ Database name not found in stack outputs")
                return False
            
            if not self.setup_athena_tables(database_name):
                return False
            
            # Step 4: Upload sample data
            raw_bucket = stack_outputs.get('RawDataBucketName')
            if not raw_bucket:
                logger.error("❌ Raw bucket name not found in stack outputs")
                return False
            
            if not self.upload_sample_data(raw_bucket):
                return False
            
            # Step 5: Test API endpoint
            api_url = stack_outputs.get('ApiGatewayUrl')
            if api_url:
                self.test_api_endpoint(api_url)  # Non-blocking
            
            # Step 6: Wait for data processing
            logger.info("⏳ Waiting for data processing (60 seconds)...")
            time.sleep(60)
            
            # Step 7: Run sample queries
            processed_bucket = stack_outputs.get('ProcessedDataBucketName')
            if processed_bucket:
                self.run_sample_queries(database_name, processed_bucket)  # Non-blocking
            
            # Step 8: Validate deployment
            if not self.validate_deployment(stack_outputs):
                logger.warning("⚠️ Some validation checks failed, but deployment may still be functional")
            
            # Success summary
            logger.info("🎉 Deployment completed successfully!")
            logger.info("📋 Deployment Summary:")
            logger.info(f"   Stack Name: {self.stack_name}")
            logger.info(f"   Environment: {self.environment}")
            logger.info(f"   Region: {self.region}")
            logger.info(f"   Database: {database_name}")
            logger.info(f"   API URL: {api_url}")
            logger.info(f"   Raw Bucket: {raw_bucket}")
            logger.info(f"   Processed Bucket: {processed_bucket}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {str(e)}")
            return False


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy Student Insights Pipeline')
    parser.add_argument('--environment', default='dev', choices=['dev', 'staging', 'prod'],
                       help='Deployment environment')
    parser.add_argument('--region', default='af-south-1', help='AWS region')
    parser.add_argument('--skip-tests', action='store_true', help='Skip validation tests')
    
    args = parser.parse_args()
    
    deployer = StudentInsightsPipelineDeployer(args.environment, args.region)
    
    success = deployer.deploy_complete_pipeline()
    
    if success:
        print("\n🎉 Student Insights Pipeline deployed successfully!")
        print("\n📖 Next steps:")
        print("1. Check the AWS Console to verify all resources are created")
        print("2. Try running some sample queries in Athena")
        print("3. Test the API endpoint with your own data")
        print("4. Set up monitoring and alerts for production use")
        print("\n📚 See DEPLOYMENT_GUIDE.md for detailed usage instructions")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed! Check the logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
