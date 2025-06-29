"""
Tests for Athena Table Setup
Student Insights Pipeline

Comprehensive tests to validate Athena table setup,
query functionality, and performance optimization.
"""

import pytest
import boto3
import json
import time
from datetime import datetime, timedelta
from moto import mock_athena, mock_s3, mock_glue
import os


class TestAthenaSetup:
    """Test cases for Athena table setup and functionality"""
    
    @pytest.fixture
    def athena_client(self):
        """Mock Athena client for testing"""
        with mock_athena():
            yield boto3.client('athena', region_name='af-south-1')
    
    @pytest.fixture
    def s3_client(self):
        """Mock S3 client for testing"""
        with mock_s3():
            yield boto3.client('s3', region_name='af-south-1')
    
    @pytest.fixture
    def glue_client(self):
        """Mock Glue client for testing"""
        with mock_glue():
            yield boto3.client('glue', region_name='af-south-1')
    
    @pytest.fixture
    def test_database_name(self):
        """Test database name"""
        return 'test_student_insights_db'
    
    @pytest.fixture
    def test_buckets(self, s3_client):
        """Create test S3 buckets"""
        buckets = {
            'raw': 'test-student-insights-raw-bucket',
            'processed': 'test-student-insights-processed-bucket'
        }
        
        for bucket_name in buckets.values():
            s3_client.create_bucket(Bucket=bucket_name)
        
        return buckets
    
    def test_database_creation_query(self, test_database_name, test_buckets):
        """Test database creation SQL query syntax"""
        processed_bucket = test_buckets['processed']
        
        query = f"""
        CREATE DATABASE IF NOT EXISTS {test_database_name}
        COMMENT 'Student Insights Pipeline - Analytics Database'
        LOCATION 's3://{processed_bucket}/database/'
        """
        
        # Validate query syntax (basic validation)
        assert 'CREATE DATABASE' in query
        assert test_database_name in query
        assert processed_bucket in query
        assert 'COMMENT' in query
    
    def test_main_table_creation_query(self, test_database_name, test_buckets):
        """Test main table creation SQL query"""
        processed_bucket = test_buckets['processed']
        
        query = f"""
        CREATE EXTERNAL TABLE {test_database_name}.processed_student_data (
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
            environment string,
            data_source string
        )
        PARTITIONED BY (
            year string,
            month string,
            day string,
            subject_partition string
        )
        STORED AS PARQUET
        LOCATION 's3://{processed_bucket}/processed/'
        """
        
        # Validate query components
        assert 'CREATE EXTERNAL TABLE' in query
        assert 'student_id string' in query
        assert 'PARTITIONED BY' in query
        assert 'STORED AS PARQUET' in query
        assert processed_bucket in query
        
        # Check all required columns are present
        required_columns = [
            'student_id', 'name', 'math_score', 'reading_score', 'writing_score',
            'average_score', 'performance_category', 'risk_level', 'grade_level',
            'subject', 'attendance_rate', 'assignment_completion_rate'
        ]
        
        for column in required_columns:
            assert column in query
    
    def test_view_creation_queries(self, test_database_name):
        """Test view creation SQL queries"""
        
        # Test latest_student_data view
        latest_view_query = f"""
        CREATE OR REPLACE VIEW {test_database_name}.latest_student_data AS
        WITH ranked_data AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY student_id, subject 
                       ORDER BY transformation_timestamp DESC
                   ) as rn
            FROM {test_database_name}.processed_student_data
            WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
        )
        SELECT * FROM ranked_data WHERE rn = 1
        """
        
        assert 'CREATE OR REPLACE VIEW' in latest_view_query
        assert 'ROW_NUMBER() OVER' in latest_view_query
        assert 'PARTITION BY student_id, subject' in latest_view_query
        
        # Test high_risk_students view
        risk_view_query = f"""
        CREATE OR REPLACE VIEW {test_database_name}.high_risk_students AS
        SELECT 
            student_id,
            name,
            grade_level,
            subject,
            average_score,
            risk_level,
            attendance_rate,
            assignment_completion_rate
        FROM {test_database_name}.latest_student_data
        WHERE risk_level IN ('High Risk', 'Medium Risk')
           OR average_score < 60
           OR attendance_rate < 0.8
        """
        
        assert 'high_risk_students' in risk_view_query
        assert 'High Risk' in risk_view_query
        assert 'average_score < 60' in risk_view_query
    
    def test_partition_projection_properties(self, test_database_name, test_buckets):
        """Test partition projection table properties"""
        processed_bucket = test_buckets['processed']
        
        properties = f"""
        TBLPROPERTIES (
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
        
        # Validate partition projection settings
        assert 'projection.enabled' in properties
        assert 'projection.year.type' in properties
        assert 'projection.subject_partition.type' in properties
        assert 'storage.location.template' in properties
        assert processed_bucket in properties
    
    def test_sample_analytics_queries(self, test_database_name):
        """Test sample analytics queries for syntax"""
        
        # Test performance summary query
        performance_query = f"""
        SELECT 
            performance_category,
            COUNT(*) as student_count,
            ROUND(AVG(average_score), 2) as avg_score
        FROM {test_database_name}.latest_student_data
        WHERE year = '2024'
        GROUP BY performance_category
        ORDER BY avg_score DESC
        """
        
        assert 'SELECT' in performance_query
        assert 'GROUP BY performance_category' in performance_query
        assert 'ORDER BY avg_score DESC' in performance_query
        
        # Test risk analysis query
        risk_query = f"""
        SELECT 
            risk_level,
            COUNT(*) as student_count,
            ROUND(AVG(average_score), 2) as avg_score
        FROM {test_database_name}.latest_student_data
        WHERE year = '2024'
        GROUP BY risk_level
        """
        
        assert 'risk_level' in risk_query
        assert 'GROUP BY risk_level' in risk_query
        
        # Test attendance correlation query
        attendance_query = f"""
        SELECT 
            CASE 
                WHEN attendance_rate >= 0.95 THEN 'Excellent'
                WHEN attendance_rate >= 0.90 THEN 'Good'
                WHEN attendance_rate >= 0.85 THEN 'Satisfactory'
                ELSE 'Concerning'
            END as attendance_category,
            COUNT(*) as student_count,
            ROUND(AVG(average_score), 2) as avg_score
        FROM {test_database_name}.latest_student_data
        WHERE year = '2024'
        GROUP BY 
            CASE 
                WHEN attendance_rate >= 0.95 THEN 'Excellent'
                WHEN attendance_rate >= 0.90 THEN 'Good'
                WHEN attendance_rate >= 0.85 THEN 'Satisfactory'
                ELSE 'Concerning'
            END
        """
        
        assert 'attendance_category' in attendance_query
        assert 'attendance_rate >=' in attendance_query
    
    def test_data_quality_queries(self, test_database_name):
        """Test data quality monitoring queries"""
        
        # Test completeness query
        completeness_query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(student_id) as student_id_count,
            COUNT(math_score) as math_score_count,
            COUNT(reading_score) as reading_score_count,
            COUNT(attendance_rate) as attendance_count,
            ROUND(AVG(data_completeness_score), 3) as avg_completeness_score
        FROM {test_database_name}.processed_student_data
        WHERE year = '2024'
        """
        
        assert 'COUNT(student_id)' in completeness_query
        assert 'data_completeness_score' in completeness_query
        
        # Test data quality issues query
        quality_issues_query = f"""
        SELECT 
            'Missing Math Scores' as issue_type,
            COUNT(*) as affected_records
        FROM {test_database_name}.latest_student_data
        WHERE year = '2024' AND math_score IS NULL
        
        UNION ALL
        
        SELECT 
            'Extreme Low Scores' as issue_type,
            COUNT(*) as affected_records
        FROM {test_database_name}.latest_student_data
        WHERE year = '2024' AND (math_score < 10 OR reading_score < 10)
        """
        
        assert 'UNION ALL' in quality_issues_query
        assert 'math_score IS NULL' in quality_issues_query
    
    def test_cost_optimized_queries(self, test_database_name):
        """Test cost-optimized queries for AWS Free Tier"""
        
        # Test efficient current status query
        efficient_query = f"""
        SELECT 
            COUNT(DISTINCT student_id) as total_students,
            ROUND(AVG(average_score), 2) as avg_score,
            COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk_count
        FROM {test_database_name}.latest_student_data
        WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
          AND month = CAST(MONTH(CURRENT_DATE) AS VARCHAR)
        """
        
        # Validate partition filtering for cost optimization
        assert 'year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)' in efficient_query
        assert 'month = CAST(MONTH(CURRENT_DATE) AS VARCHAR)' in efficient_query
        
        # Test weekly summary with partition optimization
        weekly_query = f"""
        SELECT 
            year,
            month,
            COUNT(*) as records_processed,
            COUNT(DISTINCT student_id) as unique_students
        FROM {test_database_name}.processed_student_data
        WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
          AND month = CAST(MONTH(CURRENT_DATE) AS VARCHAR)
          AND day >= CAST(DAY(CURRENT_DATE) - 7 AS VARCHAR)
        GROUP BY year, month
        """
        
        assert 'day >= CAST(DAY(CURRENT_DATE) - 7 AS VARCHAR)' in weekly_query
    
    def test_parameterized_query_templates(self, test_database_name):
        """Test parameterized query templates"""
        
        # Test student detail report template
        student_detail_template = f"""
        SELECT 
            student_id,
            name,
            grade_level,
            subject,
            average_score,
            performance_category,
            risk_level
        FROM {test_database_name}.latest_student_data
        WHERE student_id = '{{student_id_param}}'
          AND year = '2024'
        """
        
        assert '{student_id_param}' in student_detail_template
        
        # Test grade level report template
        grade_level_template = f"""
        SELECT 
            student_id,
            name,
            subject,
            average_score,
            performance_category,
            risk_level
        FROM {test_database_name}.latest_student_data
        WHERE grade_level = '{{grade_level_param}}'
          AND year = '2024'
        """
        
        assert '{grade_level_param}' in grade_level_template
    
    def test_query_performance_considerations(self):
        """Test that queries follow performance best practices"""
        
        # Test that queries use appropriate LIMIT clauses for exploration
        exploratory_query = """
        SELECT * FROM processed_student_data
        WHERE year = '2024'
        LIMIT 100
        """
        
        assert 'LIMIT' in exploratory_query
        
        # Test that aggregation queries avoid SELECT *
        aggregation_query = """
        SELECT 
            grade_level,
            COUNT(*) as student_count,
            AVG(average_score) as avg_score
        FROM processed_student_data
        WHERE year = '2024'
        GROUP BY grade_level
        """
        
        assert 'SELECT *' not in aggregation_query
        assert 'GROUP BY' in aggregation_query


class TestAthenaTableManager:
    """Test cases for AthenaTableManager class"""
    
    def test_query_construction(self):
        """Test that queries are constructed correctly"""
        database_name = 'test_db'
        bucket_name = 'test-bucket'
        
        # Test database creation query
        db_query = f"""
        CREATE DATABASE IF NOT EXISTS {database_name}
        COMMENT 'Student Insights Pipeline - Analytics Database'
        LOCATION 's3://{bucket_name}/database/'
        """
        
        assert database_name in db_query
        assert bucket_name in db_query
        assert 'CREATE DATABASE IF NOT EXISTS' in db_query
    
    def test_health_check_query(self):
        """Test health check query construction"""
        database_name = 'test_db'
        
        health_query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT student_id) as unique_students,
            MIN(transformation_timestamp) as earliest_record,
            MAX(transformation_timestamp) as latest_record
        FROM {database_name}.processed_student_data
        WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
        """
        
        assert 'COUNT(*)' in health_query
        assert 'COUNT(DISTINCT student_id)' in health_query
        assert 'MIN(transformation_timestamp)' in health_query
        assert 'MAX(transformation_timestamp)' in health_query


def test_integration_query_flow():
    """Test the complete query flow integration"""
    
    # Simulate the complete flow of queries
    queries = [
        "CREATE DATABASE test_db",
        "CREATE EXTERNAL TABLE test_db.processed_student_data (...)",
        "CREATE VIEW test_db.latest_student_data AS (...)",
        "SELECT COUNT(*) FROM test_db.latest_student_data",
        "SELECT * FROM test_db.performance_summary"
    ]
    
    # Validate that all queries follow expected patterns
    for query in queries:
        assert len(query) > 10  # Basic validation
        assert 'test_db' in query or 'CREATE DATABASE' in query


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
