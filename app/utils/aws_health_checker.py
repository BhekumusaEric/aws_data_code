#!/usr/bin/env python3
"""
AWS Health Checker
Comprehensive health monitoring for all AWS services used in the Student Insights Pipeline
"""

import boto3
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import time


class AWSHealthChecker:
    """Comprehensive AWS service health checker for the Student Insights Pipeline"""
    
    def __init__(self, region: str = 'af-south-1'):
        self.region = region
        self.services_status = {}
        
        # Initialize AWS clients with error handling
        try:
            self.s3 = boto3.client('s3', region_name=region)
            self.lambda_client = boto3.client('lambda', region_name=region)
            self.athena = boto3.client('athena', region_name=region)
            self.glue = boto3.client('glue', region_name=region)
            self.apigateway = boto3.client('apigateway', region_name=region)
            self.cloudwatch = boto3.client('cloudwatch', region_name=region)
            self.sts = boto3.client('sts')
            self.aws_configured = True
        except Exception as e:
            self.aws_configured = False
            self.aws_error = str(e)
    
    def check_aws_credentials(self) -> Dict[str, Any]:
        """Check if AWS credentials are properly configured"""
        try:
            identity = self.sts.get_caller_identity()
            return {
                'status': 'healthy',
                'account_id': identity.get('Account'),
                'user_arn': identity.get('Arn'),
                'region': self.region,
                'message': 'AWS credentials configured successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'AWS credentials not configured: {str(e)}',
                'suggestion': 'Run: aws configure'
            }
    
    def check_s3_buckets(self, bucket_names: List[str] = None) -> Dict[str, Any]:
        """Check S3 bucket accessibility and configuration"""
        if not bucket_names:
            bucket_names = [
                'student-insights-pipeline-raw-data-dev',
                'student-insights-pipeline-processed-data-dev'
            ]
        
        bucket_status = {}
        overall_status = 'healthy'
        
        for bucket_name in bucket_names:
            try:
                # Check if bucket exists and is accessible
                self.s3.head_bucket(Bucket=bucket_name)
                
                # Check bucket location
                location = self.s3.get_bucket_location(Bucket=bucket_name)
                
                # Check bucket versioning
                versioning = self.s3.get_bucket_versioning(Bucket=bucket_name)
                
                # Check bucket notification configuration
                try:
                    notifications = self.s3.get_bucket_notification_configuration(Bucket=bucket_name)
                    has_notifications = len(notifications.get('LambdaConfigurations', [])) > 0
                except:
                    has_notifications = False
                
                bucket_status[bucket_name] = {
                    'status': 'healthy',
                    'location': location.get('LocationConstraint', 'us-east-1'),
                    'versioning': versioning.get('Status', 'Disabled'),
                    'notifications_configured': has_notifications
                }
                
            except Exception as e:
                bucket_status[bucket_name] = {
                    'status': 'error',
                    'message': str(e)
                }
                overall_status = 'error'
        
        return {
            'status': overall_status,
            'buckets': bucket_status,
            'total_buckets': len(bucket_names),
            'healthy_buckets': len([b for b in bucket_status.values() if b['status'] == 'healthy'])
        }
    
    def check_lambda_functions(self, function_names: List[str] = None) -> Dict[str, Any]:
        """Check Lambda function status and recent executions"""
        if not function_names:
            function_names = [
                'student-insights-pipeline-data-ingestion-dev',
                'student-insights-pipeline-data-processing-dev'
            ]
        
        function_status = {}
        overall_status = 'healthy'
        
        for function_name in function_names:
            try:
                # Get function configuration
                func_config = self.lambda_client.get_function(FunctionName=function_name)
                
                # Get recent invocations from CloudWatch
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(hours=24)
                
                try:
                    metrics = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/Lambda',
                        MetricName='Invocations',
                        Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=3600,
                        Statistics=['Sum']
                    )
                    
                    invocations_24h = sum([point['Sum'] for point in metrics['Datapoints']])
                    
                    # Get error metrics
                    error_metrics = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/Lambda',
                        MetricName='Errors',
                        Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=3600,
                        Statistics=['Sum']
                    )
                    
                    errors_24h = sum([point['Sum'] for point in error_metrics['Datapoints']])
                    
                except Exception:
                    invocations_24h = 0
                    errors_24h = 0
                
                function_status[function_name] = {
                    'status': 'healthy',
                    'runtime': func_config['Configuration']['Runtime'],
                    'last_modified': func_config['Configuration']['LastModified'],
                    'memory_size': func_config['Configuration']['MemorySize'],
                    'timeout': func_config['Configuration']['Timeout'],
                    'invocations_24h': int(invocations_24h),
                    'errors_24h': int(errors_24h)
                }
                
            except Exception as e:
                function_status[function_name] = {
                    'status': 'error',
                    'message': str(e)
                }
                overall_status = 'error'
        
        return {
            'status': overall_status,
            'functions': function_status,
            'total_functions': len(function_names),
            'healthy_functions': len([f for f in function_status.values() if f['status'] == 'healthy'])
        }
    
    def check_api_gateway(self, api_name: str = 'student-insights-pipeline-api-dev') -> Dict[str, Any]:
        """Check API Gateway status and recent activity"""
        try:
            # Get all REST APIs
            apis = self.apigateway.get_rest_apis()
            
            target_api = None
            for api in apis['items']:
                if api_name in api['name']:
                    target_api = api
                    break
            
            if not target_api:
                return {
                    'status': 'error',
                    'message': f'API Gateway {api_name} not found'
                }
            
            # Get API stages
            stages = self.apigateway.get_stages(restApiId=target_api['id'])
            
            # Get recent metrics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            try:
                metrics = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/ApiGateway',
                    MetricName='Count',
                    Dimensions=[{'Name': 'ApiName', 'Value': target_api['name']}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,
                    Statistics=['Sum']
                )
                
                requests_24h = sum([point['Sum'] for point in metrics['Datapoints']])
                
            except Exception:
                requests_24h = 0
            
            return {
                'status': 'healthy',
                'api_id': target_api['id'],
                'api_name': target_api['name'],
                'created_date': target_api['createdDate'].isoformat(),
                'stages': [stage['stageName'] for stage in stages['item']],
                'requests_24h': int(requests_24h),
                'endpoint_url': f"https://{target_api['id']}.execute-api.{self.region}.amazonaws.com/"
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def check_athena_workgroup(self, workgroup_name: str = 'student-insights-pipeline-workgroup-dev') -> Dict[str, Any]:
        """Check Athena workgroup status and recent queries"""
        try:
            # Get workgroup details
            workgroup = self.athena.get_work_group(WorkGroup=workgroup_name)
            
            # Get recent query executions
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            try:
                executions = self.athena.list_query_executions(
                    WorkGroup=workgroup_name,
                    MaxResults=50
                )
                
                recent_queries = 0
                successful_queries = 0
                failed_queries = 0
                
                for execution_id in executions['QueryExecutionIds'][:10]:  # Check last 10
                    try:
                        execution = self.athena.get_query_execution(QueryExecutionId=execution_id)
                        exec_time = execution['QueryExecution']['Status']['SubmissionDateTime']
                        
                        if exec_time >= start_time:
                            recent_queries += 1
                            status = execution['QueryExecution']['Status']['State']
                            if status == 'SUCCEEDED':
                                successful_queries += 1
                            elif status in ['FAILED', 'CANCELLED']:
                                failed_queries += 1
                    except:
                        continue
                        
            except Exception:
                recent_queries = 0
                successful_queries = 0
                failed_queries = 0
            
            return {
                'status': 'healthy',
                'workgroup_name': workgroup_name,
                'state': workgroup['WorkGroup']['State'],
                'creation_time': workgroup['WorkGroup']['CreationTime'].isoformat(),
                'queries_24h': recent_queries,
                'successful_queries_24h': successful_queries,
                'failed_queries_24h': failed_queries,
                'result_location': workgroup['WorkGroup']['Configuration']['ResultConfiguration'].get('OutputLocation', 'Not configured')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def check_glue_catalog(self, database_name: str = 'student_insights_pipeline_database_dev') -> Dict[str, Any]:
        """Check Glue Data Catalog status"""
        try:
            # Get database details
            database = self.glue.get_database(Name=database_name)
            
            # Get tables in database
            tables = self.glue.get_tables(DatabaseName=database_name)
            
            table_info = {}
            for table in tables['TableList']:
                table_info[table['Name']] = {
                    'location': table['StorageDescriptor'].get('Location', 'Not specified'),
                    'input_format': table['StorageDescriptor'].get('InputFormat', 'Unknown'),
                    'columns': len(table['StorageDescriptor'].get('Columns', [])),
                    'partitions': len(table.get('PartitionKeys', []))
                }
            
            return {
                'status': 'healthy',
                'database_name': database_name,
                'creation_time': database['Database']['CreateTime'].isoformat(),
                'description': database['Database'].get('Description', 'No description'),
                'tables': table_info,
                'table_count': len(tables['TableList'])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run health check on all AWS services"""
        if not self.aws_configured:
            return {
                'overall_status': 'error',
                'message': 'AWS not configured',
                'error': getattr(self, 'aws_error', 'Unknown error'),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        health_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'region': self.region,
            'services': {}
        }
        
        # Check each service
        health_results['services']['credentials'] = self.check_aws_credentials()
        health_results['services']['s3'] = self.check_s3_buckets()
        health_results['services']['lambda'] = self.check_lambda_functions()
        health_results['services']['api_gateway'] = self.check_api_gateway()
        health_results['services']['athena'] = self.check_athena_workgroup()
        health_results['services']['glue'] = self.check_glue_catalog()
        
        # Determine overall status
        service_statuses = [service['status'] for service in health_results['services'].values()]
        if all(status == 'healthy' for status in service_statuses):
            health_results['overall_status'] = 'healthy'
        elif any(status == 'healthy' for status in service_statuses):
            health_results['overall_status'] = 'partial'
        else:
            health_results['overall_status'] = 'error'
        
        # Count healthy services
        health_results['healthy_services'] = len([s for s in service_statuses if s == 'healthy'])
        health_results['total_services'] = len(service_statuses)
        
        return health_results
