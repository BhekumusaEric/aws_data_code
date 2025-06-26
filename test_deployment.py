#!/usr/bin/env python3
"""
Student Insights Pipeline - Deployment Test Script

Quick test script to validate the deployment is working correctly.
"""

import boto3
import json
import time
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_deployment(stack_name='student-insights-pipeline-dev'):
    """Test the deployed Student Insights Pipeline"""
    
    logger.info("🧪 Testing Student Insights Pipeline deployment...")
    
    # Get CloudFormation outputs
    cf = boto3.client('cloudformation')
    try:
        response = cf.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0]['Outputs']
        
        stack_outputs = {}
        for output in outputs:
            stack_outputs[output['OutputKey']] = output['OutputValue']
        
        logger.info("✅ Retrieved stack outputs")
        
    except Exception as e:
        logger.error(f"❌ Failed to get stack outputs: {e}")
        return False
    
    # Test 1: API Gateway endpoint
    api_url = stack_outputs.get('ApiGatewayUrl')
    if api_url:
        logger.info("🔗 Testing API Gateway endpoint...")
        
        test_student = {
            "student_id": f"test_{int(time.time())}",
            "name": "Test Student",
            "math_score": 85,
            "reading_score": 90,
            "writing_score": 88,
            "grade_level": "10",
            "subject": "Mathematics",
            "attendance_rate": 0.95,
            "assignment_completion_rate": 0.92
        }
        
        try:
            response = requests.post(
                f"{api_url}/ingest",
                json=test_student,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ API Gateway test successful!")
                logger.info(f"Response: {response.json()}")
            else:
                logger.error(f"❌ API test failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ API test error: {e}")
    
    # Test 2: S3 buckets
    s3 = boto3.client('s3')
    
    raw_bucket = stack_outputs.get('RawDataBucketName')
    processed_bucket = stack_outputs.get('ProcessedDataBucketName')
    
    if raw_bucket:
        try:
            s3.head_bucket(Bucket=raw_bucket)
            logger.info(f"✅ Raw bucket accessible: {raw_bucket}")
            
            # List some objects
            objects = s3.list_objects_v2(Bucket=raw_bucket, MaxKeys=5)
            if 'Contents' in objects:
                logger.info(f"📁 Found {len(objects['Contents'])} objects in raw bucket")
            else:
                logger.info("📁 Raw bucket is empty (expected for new deployment)")
                
        except Exception as e:
            logger.error(f"❌ Raw bucket test failed: {e}")
    
    if processed_bucket:
        try:
            s3.head_bucket(Bucket=processed_bucket)
            logger.info(f"✅ Processed bucket accessible: {processed_bucket}")
            
        except Exception as e:
            logger.error(f"❌ Processed bucket test failed: {e}")
    
    # Test 3: Athena database
    athena = boto3.client('athena')
    database_name = stack_outputs.get('AthenaDatabaseName')
    
    if database_name and processed_bucket:
        logger.info("📊 Testing Athena queries...")
        
        test_query = f"""
        SELECT 'deployment_test' as test_type, 
               COUNT(*) as record_count,
               CURRENT_TIMESTAMP as query_time
        FROM {database_name}.processed_student_data
        WHERE year = '2024'
        LIMIT 1
        """
        
        try:
            response = athena.start_query_execution(
                QueryString=test_query,
                QueryExecutionContext={'Database': database_name},
                ResultConfiguration={
                    'OutputLocation': f's3://{processed_bucket}/athena-results/'
                }
            )
            
            query_id = response['QueryExecutionId']
            logger.info(f"🔍 Started test query: {query_id}")
            
            # Wait for completion
            max_wait = 30
            wait_time = 0
            while wait_time < max_wait:
                result = athena.get_query_execution(QueryExecutionId=query_id)
                status = result['QueryExecution']['Status']['State']
                
                if status == 'SUCCEEDED':
                    logger.info("✅ Athena test query successful!")
                    
                    # Get results
                    results = athena.get_query_results(QueryExecutionId=query_id)
                    if len(results['ResultSet']['Rows']) > 1:
                        data_row = results['ResultSet']['Rows'][1]['Data']
                        logger.info(f"📊 Query result: {[cell.get('VarCharValue', '') for cell in data_row]}")
                    break
                    
                elif status == 'FAILED':
                    error = result['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                    logger.error(f"❌ Athena test query failed: {error}")
                    break
                
                time.sleep(2)
                wait_time += 2
            
            if wait_time >= max_wait:
                logger.warning("⏰ Athena test query timed out")
                
        except Exception as e:
            logger.error(f"❌ Athena test error: {e}")
    
    # Test 4: Lambda function
    lambda_client = boto3.client('lambda')
    function_name = stack_outputs.get('IngestionLambdaFunctionName')
    
    if function_name:
        try:
            response = lambda_client.get_function(FunctionName=function_name)
            logger.info(f"✅ Lambda function accessible: {function_name}")
            logger.info(f"📦 Runtime: {response['Configuration']['Runtime']}")
            logger.info(f"💾 Memory: {response['Configuration']['MemorySize']}MB")
            
        except Exception as e:
            logger.error(f"❌ Lambda function test failed: {e}")
    
    # Summary
    logger.info("\n📋 Test Summary:")
    logger.info(f"   Stack: {stack_name}")
    logger.info(f"   API URL: {api_url}")
    logger.info(f"   Database: {database_name}")
    logger.info(f"   Raw Bucket: {raw_bucket}")
    logger.info(f"   Processed Bucket: {processed_bucket}")
    
    logger.info("\n🎯 Next Steps:")
    logger.info("1. Upload your own student data via the API")
    logger.info("2. Run analytics queries in the Athena console")
    logger.info("3. Check the sample queries in analytics/athena_queries.sql")
    logger.info("4. Monitor costs in the AWS Billing console")
    
    return True


if __name__ == "__main__":
    import sys
    
    stack_name = sys.argv[1] if len(sys.argv) > 1 else 'student-insights-pipeline-dev'
    
    print(f"🧪 Testing deployment: {stack_name}")
    print("=" * 50)
    
    success = test_deployment(stack_name)
    
    if success:
        print("\n🎉 Deployment test completed!")
    else:
        print("\n❌ Some tests failed - check logs above")
        sys.exit(1)
