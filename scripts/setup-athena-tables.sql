/*
Athena Table Setup Script
Student Insights Pipeline

This script sets up all necessary tables, views, and optimizations
for the Student Insights Pipeline analytics engine.

Prerequisites:
1. S3 buckets created by CloudFormation
2. Glue database created
3. Processed data available in S3

Usage:
1. Replace {database_name} with your actual database name
2. Replace {processed_bucket_name} with your S3 bucket name
3. Execute sections in order
*/

-- =============================================================================
-- 1. DATABASE SETUP
-- =============================================================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS {database_name}
COMMENT 'Student Insights Pipeline - Analytics Database'
LOCATION 's3://{processed_bucket_name}/database/';

-- Use the database
USE {database_name};

-- =============================================================================
-- 2. MAIN DATA TABLE
-- =============================================================================

-- Drop table if exists (for clean setup)
DROP TABLE IF EXISTS processed_student_data;

-- Create main processed student data table
CREATE EXTERNAL TABLE processed_student_data (
    -- Student Identification
    student_id string COMMENT 'Unique student identifier',
    name string COMMENT 'Student full name',
    
    -- Academic Performance
    math_score double COMMENT 'Mathematics score (0-100)',
    reading_score double COMMENT 'Reading comprehension score (0-100)',
    writing_score double COMMENT 'Writing skills score (0-100)',
    average_score double COMMENT 'Calculated average of all scores',
    
    -- Performance Classification
    performance_category string COMMENT 'Performance level: Excellent, Good, Satisfactory, Needs Improvement, At Risk',
    risk_level string COMMENT 'Risk assessment: No Risk, Low Risk, Medium Risk, High Risk',
    
    -- Student Demographics
    grade_level string COMMENT 'Student grade level (K, 1-12)',
    subject string COMMENT 'Subject area for this record',
    
    -- Engagement Metrics
    attendance_rate double COMMENT 'Attendance rate (0.0-1.0)',
    assignment_completion_rate double COMMENT 'Assignment completion rate (0.0-1.0)',
    
    -- Academic Calendar
    academic_year string COMMENT 'Academic year (e.g., 2023-2024)',
    semester string COMMENT 'Semester: Fall, Spring, Summer',
    
    -- Data Quality
    data_completeness_score double COMMENT 'Data quality score (0.0-1.0)',
    
    -- Processing Metadata
    ingestion_timestamp timestamp COMMENT 'When data was first ingested',
    transformation_timestamp timestamp COMMENT 'When data was processed/transformed',
    transformation_date date COMMENT 'Date of transformation (for partitioning)',
    environment string COMMENT 'Environment: dev, staging, prod',
    data_source string COMMENT 'Source of data: api_ingestion, csv_upload, etc.',
    
    -- Calculated Fields (from Glue job)
    risk_score int COMMENT 'Calculated risk score (0-7)',
    csv_row_number int COMMENT 'Original CSV row number (if applicable)'
)
PARTITIONED BY (
    year string COMMENT 'Year partition (YYYY)',
    month string COMMENT 'Month partition (MM)', 
    day string COMMENT 'Day partition (DD)',
    subject_partition string COMMENT 'Subject partition for query optimization'
)
STORED AS PARQUET
LOCATION 's3://{processed_bucket_name}/processed/'
TBLPROPERTIES (
    'classification' = 'parquet',
    'compressionType' = 'snappy',
    'typeOfData' = 'file',
    'projection.enabled' = 'true',
    
    -- Partition projection for automatic partition discovery
    'projection.year.type' = 'integer',
    'projection.year.range' = '2020,2030',
    'projection.year.interval' = '1',
    'projection.year.interval.unit' = 'YEARS',
    
    'projection.month.type' = 'integer', 
    'projection.month.range' = '1,12',
    'projection.month.digits' = '2',
    'projection.month.interval' = '1',
    'projection.month.interval.unit' = 'MONTHS',
    
    'projection.day.type' = 'integer',
    'projection.day.range' = '1,31', 
    'projection.day.digits' = '2',
    'projection.day.interval' = '1',
    'projection.day.interval.unit' = 'DAYS',
    
    'projection.subject_partition.type' = 'enum',
    'projection.subject_partition.values' = 'Mathematics,English,Science,History,Art,Physical Education,Other',
    
    -- Storage location template
    'storage.location.template' = 's3://{processed_bucket_name}/processed/year=${year}/month=${month}/day=${day}/subject=${subject_partition}/',
    
    -- Performance optimizations
    'has_encrypted_data' = 'false',
    'parquet.compress' = 'SNAPPY'
);

-- =============================================================================
-- 3. RAW DATA TABLE (for debugging and data lineage)
-- =============================================================================

CREATE EXTERNAL TABLE IF NOT EXISTS raw_student_data (
    student_id string,
    name string,
    math_score double,
    reading_score double,
    writing_score double,
    grade_level string,
    subject string,
    attendance_rate double,
    assignment_completion_rate double,
    timestamp timestamp,
    ingestion_timestamp timestamp,
    processing_date string,
    processing_hour string,
    environment string,
    data_source string
)
PARTITIONED BY (
    date_partition string,
    hour_partition string
)
STORED AS TEXTFILE
LOCATION 's3://{raw_bucket_name}/raw/'
TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.date_partition.type' = 'date',
    'projection.date_partition.range' = '2020/01/01,2030/12/31',
    'projection.date_partition.format' = 'yyyy/MM/dd',
    'projection.date_partition.interval' = '1',
    'projection.date_partition.interval.unit' = 'DAYS',
    
    'projection.hour_partition.type' = 'integer',
    'projection.hour_partition.range' = '0,23',
    'projection.hour_partition.digits' = '2',
    
    'storage.location.template' = 's3://{raw_bucket_name}/raw/date=${date_partition}/hour=${hour_partition}/'
);

-- =============================================================================
-- 4. PERFORMANCE OPTIMIZATION VIEWS
-- =============================================================================

-- Current academic year view (most commonly queried data)
CREATE OR REPLACE VIEW current_academic_year AS
SELECT *
FROM processed_student_data
WHERE academic_year = (
    SELECT MAX(academic_year) 
    FROM processed_student_data
    WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
);

-- Latest student data view (most recent record per student per subject)
CREATE OR REPLACE VIEW latest_student_data AS
WITH ranked_data AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY student_id, subject 
               ORDER BY transformation_timestamp DESC
           ) as rn
    FROM processed_student_data
    WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
      AND month >= CAST(MONTH(CURRENT_DATE) - 3 AS VARCHAR) -- Last 3 months
)
SELECT 
    student_id,
    name,
    math_score,
    reading_score,
    writing_score,
    average_score,
    performance_category,
    risk_level,
    grade_level,
    subject,
    attendance_rate,
    assignment_completion_rate,
    academic_year,
    semester,
    data_completeness_score,
    ingestion_timestamp,
    transformation_timestamp,
    environment,
    data_source,
    year,
    month,
    day,
    subject_partition
FROM ranked_data 
WHERE rn = 1;

-- High-risk students view (for quick access to at-risk students)
CREATE OR REPLACE VIEW high_risk_students AS
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
FROM latest_student_data
WHERE risk_level IN ('High Risk', 'Medium Risk')
   OR average_score < 60
   OR attendance_rate < 0.8
ORDER BY 
    CASE 
        WHEN average_score < 50 AND attendance_rate < 0.7 THEN 1
        WHEN average_score < 50 THEN 2
        WHEN attendance_rate < 0.7 THEN 3
        ELSE 4
    END,
    average_score ASC;

-- Performance summary view (for dashboards)
CREATE OR REPLACE VIEW performance_summary AS
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
FROM latest_student_data
GROUP BY grade_level, subject;

-- =============================================================================
-- 5. DATA QUALITY TABLES
-- =============================================================================

-- Data quality reports table (for storing quality metrics)
CREATE EXTERNAL TABLE IF NOT EXISTS data_quality_reports (
    report_id string,
    timestamp timestamp,
    total_records bigint,
    completeness_stats struct<
        student_id: struct<total_records: bigint, non_null_records: bigint, completeness_rate: double>,
        name: struct<total_records: bigint, non_null_records: bigint, completeness_rate: double>,
        math_score: struct<total_records: bigint, non_null_records: bigint, completeness_rate: double>,
        reading_score: struct<total_records: bigint, non_null_records: bigint, completeness_rate: double>,
        writing_score: struct<total_records: bigint, non_null_records: bigint, completeness_rate: double>
    >,
    score_statistics struct<
        math_score: struct<mean: double, stddev: double, min: double, max: double, count: bigint>,
        reading_score: struct<mean: double, stddev: double, min: double, max: double, count: bigint>,
        writing_score: struct<mean: double, stddev: double, min: double, max: double, count: bigint>,
        average_score: struct<mean: double, stddev: double, min: double, max: double, count: bigint>
    >,
    risk_distribution map<string, bigint>,
    performance_distribution map<string, bigint>,
    environment string
)
STORED AS JSON
LOCATION 's3://{processed_bucket_name}/quality-reports/'
TBLPROPERTIES (
    'classification' = 'json',
    'typeOfData' = 'file'
);

-- =============================================================================
-- 6. UTILITY FUNCTIONS AND PROCEDURES
-- =============================================================================

-- Note: Athena doesn't support stored procedures, but we can create reusable query patterns

-- Refresh partitions (run this after new data is loaded)
-- MSCK REPAIR TABLE processed_student_data;

-- Update table statistics for better query planning
-- ANALYZE TABLE processed_student_data COMPUTE STATISTICS;

-- =============================================================================
-- 7. PERFORMANCE MONITORING
-- =============================================================================

-- Query to check partition health
-- SELECT 
--     year, month, day, subject_partition,
--     COUNT(*) as record_count,
--     MIN(transformation_timestamp) as earliest_record,
--     MAX(transformation_timestamp) as latest_record
-- FROM processed_student_data
-- WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
-- GROUP BY year, month, day, subject_partition
-- ORDER BY year, month, day, subject_partition;

-- Query to check data freshness
-- SELECT 
--     MAX(transformation_timestamp) as latest_data,
--     COUNT(*) as total_records,
--     COUNT(DISTINCT student_id) as unique_students
-- FROM processed_student_data
-- WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR);

/*
=============================================================================
SETUP COMPLETION CHECKLIST
=============================================================================

After running this script:

1. [ ] Verify all tables are created successfully
2. [ ] Check partition projection is working
3. [ ] Test sample queries from athena_queries.sql
4. [ ] Verify views return expected data
5. [ ] Check data quality reports table
6. [ ] Monitor query performance and costs
7. [ ] Set up automated partition refresh if needed

=============================================================================
*/
