#!/usr/bin/env python3
"""
Athena Table Manager
Student Insights Pipeline

This script automates the setup, maintenance, and optimization
of Athena tables for the Student Insights Pipeline.

Features:
- Automated table creation and updates
- Partition management and optimization
- Query performance monitoring
- Cost optimization recommendations
"""

import boto3
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AthenaTableManager:
    """Manages Athena tables for Student Insights Pipeline"""
    
    def __init__(self, database_name: str, region: str = 'af-south-1'):
        self.database_name = database_name
        self.region = region
        self.athena_client = boto3.client('athena', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.glue_client = boto3.client('glue', region_name=region)
        
        # Query execution configuration
        self.query_output_location = f's3://{self._get_bucket_name("processed")}/athena-results/'
        
    def _get_bucket_name(self, bucket_type: str) -> str:
        """Get bucket name based on type and environment"""
        # This would typically come from CloudFormation outputs or environment variables
        account_id = boto3.client('sts').get_caller_identity()['Account']
        environment = 'dev'  # Could be parameterized
        return f'student-insights-pipeline-{bucket_type}-data-{environment}-{account_id}'
    
    def execute_query(self, query: str, wait_for_completion: bool = True) -> Dict[str, Any]:
        """
        Execute an Athena query
        
        Args:
            query: SQL query to execute
            wait_for_completion: Whether to wait for query completion
            
        Returns:
            Query execution result
        """
        try:
            response = self.athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.database_name},
                ResultConfiguration={'OutputLocation': self.query_output_location}
            )
            
            query_execution_id = response['QueryExecutionId']
            logger.info(f"Started query execution: {query_execution_id}")
            
            if wait_for_completion:
                return self._wait_for_query_completion(query_execution_id)
            else:
                return {'QueryExecutionId': query_execution_id, 'Status': 'RUNNING'}
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def _wait_for_query_completion(self, query_execution_id: str, max_wait_seconds: int = 300) -> Dict[str, Any]:
        """Wait for query completion and return results"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            response = self.athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = response['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                logger.info(f"Query {query_execution_id} completed with status: {status}")
                return response
            
            time.sleep(2)
        
        raise TimeoutError(f"Query {query_execution_id} did not complete within {max_wait_seconds} seconds")
    
    def create_database(self) -> bool:
        """Create the Athena database if it doesn't exist"""
        try:
            processed_bucket = self._get_bucket_name("processed")
            query = f"""
            CREATE DATABASE IF NOT EXISTS {self.database_name}
            COMMENT 'Student Insights Pipeline - Analytics Database'
            LOCATION 's3://{processed_bucket}/database/'
            """
            
            result = self.execute_query(query)
            if result['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                logger.info(f"Database {self.database_name} created successfully")
                return True
            else:
                logger.error(f"Failed to create database: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            return False
    
    def setup_main_table(self) -> bool:
        """Set up the main processed student data table"""
        try:
            processed_bucket = self._get_bucket_name("processed")
            
            # First drop the table if it exists
            drop_query = f"DROP TABLE IF EXISTS {self.database_name}.processed_student_data"
            self.execute_query(drop_query)
            
            # Create the main table
            create_query = f"""
            CREATE EXTERNAL TABLE {self.database_name}.processed_student_data (
                student_id string,
                name string,
                math_score double,
                reading_score double,
                writing_score double,
                average_score double,
                performance_category string,
                risk_level string,
                grade_level string,
                subject string,
                attendance_rate double,
                assignment_completion_rate double,
                academic_year string,
                semester string,
                data_completeness_score double,
                ingestion_timestamp timestamp,
                transformation_timestamp timestamp,
                transformation_date date,
                environment string,
                data_source string,
                risk_score int,
                csv_row_number int
            )
            PARTITIONED BY (
                year string,
                month string,
                day string,
                subject_partition string
            )
            STORED AS PARQUET
            LOCATION 's3://{processed_bucket}/processed/'
            TBLPROPERTIES (
                'classification' = 'parquet',
                'compressionType' = 'snappy',
                'projection.enabled' = 'true',
                'projection.year.type' = 'integer',
                'projection.year.range' = '2020,2030',
                'projection.month.type' = 'integer',
                'projection.month.range' = '1,12',
                'projection.month.digits' = '2',
                'projection.day.type' = 'integer',
                'projection.day.range' = '1,31',
                'projection.day.digits' = '2',
                'projection.subject_partition.type' = 'enum',
                'projection.subject_partition.values' = 'Mathematics,English,Science,History,Art,Physical Education,Other',
                'storage.location.template' = 's3://{processed_bucket}/processed/year=${{year}}/month=${{month}}/day=${{day}}/subject=${{subject_partition}}/'
            )
            """
            
            result = self.execute_query(create_query)
            if result['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                logger.info("Main table created successfully")
                return True
            else:
                logger.error(f"Failed to create main table: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up main table: {str(e)}")
            return False
    
    def create_views(self) -> bool:
        """Create optimized views for common queries"""
        views = {
            'latest_student_data': f"""
            CREATE OR REPLACE VIEW {self.database_name}.latest_student_data AS
            WITH ranked_data AS (
                SELECT *,
                       ROW_NUMBER() OVER (
                           PARTITION BY student_id, subject 
                           ORDER BY transformation_timestamp DESC
                       ) as rn
                FROM {self.database_name}.processed_student_data
                WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
                  AND month >= CAST(MONTH(CURRENT_DATE) - 3 AS VARCHAR)
            )
            SELECT * FROM ranked_data WHERE rn = 1
            """,
            
            'high_risk_students': f"""
            CREATE OR REPLACE VIEW {self.database_name}.high_risk_students AS
            SELECT 
                student_id,
                name,
                grade_level,
                subject,
                average_score,
                risk_level,
                attendance_rate,
                assignment_completion_rate,
                transformation_timestamp,
                CASE 
                    WHEN average_score < 50 AND attendance_rate < 0.7 THEN 'Critical - Multiple Factors'
                    WHEN average_score < 50 THEN 'Critical - Academic'
                    WHEN attendance_rate < 0.7 THEN 'Critical - Attendance'
                    ELSE 'High Risk - Monitor Closely'
                END as intervention_priority
            FROM {self.database_name}.latest_student_data
            WHERE risk_level IN ('High Risk', 'Medium Risk')
               OR average_score < 60
               OR attendance_rate < 0.8
            """,
            
            'performance_summary': f"""
            CREATE OR REPLACE VIEW {self.database_name}.performance_summary AS
            SELECT 
                grade_level,
                subject,
                COUNT(DISTINCT student_id) as total_students,
                ROUND(AVG(average_score), 2) as avg_score,
                ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance_percent,
                COUNT(CASE WHEN performance_category = 'Excellent' THEN 1 END) as excellent_count,
                COUNT(CASE WHEN performance_category = 'At Risk' THEN 1 END) as at_risk_count,
                COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk_count,
                MAX(transformation_timestamp) as last_updated
            FROM {self.database_name}.latest_student_data
            GROUP BY grade_level, subject
            """
        }
        
        success_count = 0
        for view_name, view_query in views.items():
            try:
                result = self.execute_query(view_query)
                if result['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                    logger.info(f"View {view_name} created successfully")
                    success_count += 1
                else:
                    logger.error(f"Failed to create view {view_name}: {result}")
            except Exception as e:
                logger.error(f"Error creating view {view_name}: {str(e)}")
        
        return success_count == len(views)
    
    def check_table_health(self) -> Dict[str, Any]:
        """Check the health and status of tables"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'database': self.database_name,
            'tables': {},
            'views': {},
            'overall_status': 'healthy'
        }
        
        try:
            # Check main table
            table_query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT student_id) as unique_students,
                MIN(transformation_timestamp) as earliest_record,
                MAX(transformation_timestamp) as latest_record,
                COUNT(DISTINCT CONCAT(year, month, day, subject_partition)) as partition_count
            FROM {self.database_name}.processed_student_data
            WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
            """
            
            result = self.execute_query(table_query)
            if result['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                # Get query results
                results = self.athena_client.get_query_results(
                    QueryExecutionId=result['QueryExecution']['QueryExecutionId']
                )
                
                if results['ResultSet']['Rows']:
                    data_row = results['ResultSet']['Rows'][1]['Data']  # Skip header
                    health_report['tables']['processed_student_data'] = {
                        'status': 'healthy',
                        'total_records': int(data_row[0]['VarCharValue']) if data_row[0].get('VarCharValue') else 0,
                        'unique_students': int(data_row[1]['VarCharValue']) if data_row[1].get('VarCharValue') else 0,
                        'earliest_record': data_row[2].get('VarCharValue'),
                        'latest_record': data_row[3].get('VarCharValue'),
                        'partition_count': int(data_row[4]['VarCharValue']) if data_row[4].get('VarCharValue') else 0
                    }
            
            # Check views
            for view_name in ['latest_student_data', 'high_risk_students', 'performance_summary']:
                try:
                    view_query = f"SELECT COUNT(*) FROM {self.database_name}.{view_name} LIMIT 1"
                    view_result = self.execute_query(view_query)
                    
                    if view_result['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                        health_report['views'][view_name] = {'status': 'healthy'}
                    else:
                        health_report['views'][view_name] = {'status': 'error'}
                        health_report['overall_status'] = 'degraded'
                        
                except Exception as e:
                    health_report['views'][view_name] = {'status': 'error', 'error': str(e)}
                    health_report['overall_status'] = 'degraded'
            
        except Exception as e:
            logger.error(f"Error checking table health: {str(e)}")
            health_report['overall_status'] = 'error'
            health_report['error'] = str(e)
        
        return health_report
    
    def optimize_tables(self) -> Dict[str, Any]:
        """Run optimization operations on tables"""
        optimization_report = {
            'timestamp': datetime.now().isoformat(),
            'operations': [],
            'recommendations': []
        }
        
        try:
            # Update table statistics
            stats_query = f"ANALYZE TABLE {self.database_name}.processed_student_data COMPUTE STATISTICS"
            result = self.execute_query(stats_query)
            
            optimization_report['operations'].append({
                'operation': 'compute_statistics',
                'status': 'success' if result['QueryExecution']['Status']['State'] == 'SUCCEEDED' else 'failed',
                'execution_id': result['QueryExecution']['QueryExecutionId']
            })
            
            # Check for optimization opportunities
            health = self.check_table_health()
            
            if 'processed_student_data' in health['tables']:
                table_info = health['tables']['processed_student_data']
                
                if table_info['partition_count'] > 100:
                    optimization_report['recommendations'].append(
                        "Consider implementing partition pruning in queries to reduce costs"
                    )
                
                if table_info['total_records'] > 1000000:
                    optimization_report['recommendations'].append(
                        "Consider implementing data archiving for older records"
                    )
            
        except Exception as e:
            logger.error(f"Error during optimization: {str(e)}")
            optimization_report['error'] = str(e)
        
        return optimization_report
    
    def setup_complete_schema(self) -> bool:
        """Set up the complete schema including database, tables, and views"""
        logger.info("Starting complete schema setup...")
        
        steps = [
            ("Creating database", self.create_database),
            ("Setting up main table", self.setup_main_table),
            ("Creating views", self.create_views)
        ]
        
        for step_name, step_function in steps:
            logger.info(f"Executing: {step_name}")
            if not step_function():
                logger.error(f"Failed at step: {step_name}")
                return False
            logger.info(f"Completed: {step_name}")
        
        logger.info("Schema setup completed successfully!")
        return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Manage Athena tables for Student Insights Pipeline')
    parser.add_argument('--database', required=True, help='Athena database name')
    parser.add_argument('--region', default='af-south-1', help='AWS region')
    parser.add_argument('--action', choices=['setup', 'health-check', 'optimize'], 
                       default='setup', help='Action to perform')
    parser.add_argument('--output', help='Output file for reports (JSON)')
    
    args = parser.parse_args()
    
    manager = AthenaTableManager(args.database, args.region)
    
    if args.action == 'setup':
        success = manager.setup_complete_schema()
        if success:
            print("✅ Schema setup completed successfully!")
        else:
            print("❌ Schema setup failed!")
            exit(1)
    
    elif args.action == 'health-check':
        report = manager.check_table_health()
        print(f"📊 Table Health Status: {report['overall_status'].upper()}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2))
    
    elif args.action == 'optimize':
        report = manager.optimize_tables()
        print("🔧 Optimization completed!")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
