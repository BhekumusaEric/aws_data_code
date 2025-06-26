/*
Student Insights Pipeline - Comprehensive Athena Analytics Queries
==================================================================

This file contains a complete library of SQL queries for educational analytics,
designed to provide actionable insights for educators and administrators.

Query Categories:
1. Table Setup & Schema Definitions
2. Student Performance Analysis
3. Risk Assessment & Early Warning
4. Subject-Specific Analytics
5. Trend Analysis & Time Series
6. Class & Grade Level Comparisons
7. Attendance & Engagement Analysis
8. Data Quality & Monitoring
9. Administrative Reports
10. Advanced Analytics & Predictions

Usage:
- Replace {database_name} with your Glue database name
- Replace date parameters with actual values
- Optimize partition filters for cost efficiency
*/

-- =============================================================================
-- 1. TABLE SETUP & SCHEMA DEFINITIONS
-- =============================================================================

-- Create external table for processed student data
-- This should match the Glue table created by CloudFormation
CREATE EXTERNAL TABLE IF NOT EXISTS {database_name}.processed_student_data (
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
LOCATION 's3://{processed_bucket_name}/processed/'
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
    'storage.location.template' = 's3://{processed_bucket_name}/processed/year=${year}/month=${month}/day=${day}/subject=${subject_partition}/'
);

-- Create view for current academic year data (performance optimization)
CREATE OR REPLACE VIEW {database_name}.current_academic_year AS
SELECT *
FROM {database_name}.processed_student_data
WHERE academic_year = (
    SELECT MAX(academic_year)
    FROM {database_name}.processed_student_data
);

-- Create view for latest student records (most recent data per student)
CREATE OR REPLACE VIEW {database_name}.latest_student_data AS
WITH ranked_data AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY student_id, subject
               ORDER BY transformation_timestamp DESC
           ) as rn
    FROM {database_name}.processed_student_data
    WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
      AND month >= CAST(MONTH(CURRENT_DATE) - 1 AS VARCHAR)
)
SELECT * FROM ranked_data WHERE rn = 1;

-- =============================================================================
-- 2. STUDENT PERFORMANCE ANALYSIS
-- =============================================================================

-- Query 2.1: Overall Performance Summary
-- Purpose: Get high-level performance metrics for all students
SELECT
    COUNT(DISTINCT student_id) as total_students,
    ROUND(AVG(average_score), 2) as overall_average,
    ROUND(AVG(math_score), 2) as avg_math_score,
    ROUND(AVG(reading_score), 2) as avg_reading_score,
    ROUND(AVG(writing_score), 2) as avg_writing_score,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance_percent,
    ROUND(AVG(assignment_completion_rate) * 100, 1) as avg_completion_percent
FROM {database_name}.latest_student_data
WHERE year = '2024';

-- Query 2.2: Performance Distribution by Category
-- Purpose: Understand the distribution of student performance levels
SELECT
    performance_category,
    COUNT(*) as student_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(MIN(average_score), 2) as min_score,
    ROUND(MAX(average_score), 2) as max_score
FROM {database_name}.latest_student_data
WHERE year = '2024'
GROUP BY performance_category
ORDER BY
    CASE performance_category
        WHEN 'Excellent' THEN 1
        WHEN 'Good' THEN 2
        WHEN 'Satisfactory' THEN 3
        WHEN 'Needs Improvement' THEN 4
        WHEN 'At Risk' THEN 5
        ELSE 6
    END;

-- Query 2.3: Top Performing Students
-- Purpose: Identify highest achieving students for recognition
SELECT
    student_id,
    name,
    grade_level,
    ROUND(average_score, 2) as average_score,
    performance_category,
    ROUND(attendance_rate * 100, 1) as attendance_percent,
    ROUND(assignment_completion_rate * 100, 1) as completion_percent,
    academic_year,
    semester
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND average_score IS NOT NULL
ORDER BY average_score DESC
LIMIT 20;

-- Query 2.4: Students Needing Support
-- Purpose: Identify students who need immediate academic intervention
SELECT
    student_id,
    name,
    grade_level,
    subject,
    ROUND(average_score, 2) as average_score,
    performance_category,
    risk_level,
    ROUND(attendance_rate * 100, 1) as attendance_percent,
    ROUND(assignment_completion_rate * 100, 1) as completion_percent,
    CASE
        WHEN average_score < 60 AND attendance_rate < 0.8 THEN 'Critical - Academic & Attendance'
        WHEN average_score < 60 THEN 'Critical - Academic'
        WHEN attendance_rate < 0.8 THEN 'Critical - Attendance'
        WHEN assignment_completion_rate < 0.7 THEN 'Moderate - Completion'
        ELSE 'Monitor'
    END as intervention_priority
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND (
      average_score < 70
      OR attendance_rate < 0.85
      OR assignment_completion_rate < 0.8
      OR risk_level IN ('High Risk', 'Medium Risk')
  )
ORDER BY
    CASE
        WHEN average_score < 60 AND attendance_rate < 0.8 THEN 1
        WHEN average_score < 60 THEN 2
        WHEN attendance_rate < 0.8 THEN 3
        ELSE 4
    END,
    average_score ASC;

-- =============================================================================
-- 3. RISK ASSESSMENT & EARLY WARNING
-- =============================================================================

-- Query 3.1: Risk Level Distribution
-- Purpose: Understand the distribution of students across risk levels
SELECT
    risk_level,
    COUNT(*) as student_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance_percent
FROM {database_name}.latest_student_data
WHERE year = '2024'
GROUP BY risk_level
ORDER BY
    CASE risk_level
        WHEN 'High Risk' THEN 1
        WHEN 'Medium Risk' THEN 2
        WHEN 'Low Risk' THEN 3
        WHEN 'No Risk' THEN 4
        ELSE 5
    END;

-- Query 3.2: High Risk Students Detail
-- Purpose: Detailed analysis of high-risk students for intervention planning
SELECT
    student_id,
    name,
    grade_level,
    subject,
    risk_level,
    ROUND(average_score, 2) as average_score,
    ROUND(math_score, 2) as math_score,
    ROUND(reading_score, 2) as reading_score,
    ROUND(writing_score, 2) as writing_score,
    ROUND(attendance_rate * 100, 1) as attendance_percent,
    ROUND(assignment_completion_rate * 100, 1) as completion_percent,
    CASE
        WHEN average_score < 50 THEN 'Severe Academic Difficulty'
        WHEN average_score < 60 THEN 'Moderate Academic Difficulty'
        WHEN attendance_rate < 0.7 THEN 'Chronic Absenteeism'
        WHEN assignment_completion_rate < 0.6 THEN 'Assignment Completion Issues'
        ELSE 'Multiple Factors'
    END as primary_concern,
    academic_year,
    semester
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND risk_level = 'High Risk'
ORDER BY average_score ASC, attendance_rate ASC;

-- Query 3.3: Early Warning Indicators
-- Purpose: Identify students showing early warning signs
WITH warning_indicators AS (
    SELECT
        student_id,
        name,
        grade_level,
        subject,
        average_score,
        attendance_rate,
        assignment_completion_rate,
        CASE WHEN average_score < 70 THEN 1 ELSE 0 END as low_academic_flag,
        CASE WHEN attendance_rate < 0.85 THEN 1 ELSE 0 END as attendance_flag,
        CASE WHEN assignment_completion_rate < 0.8 THEN 1 ELSE 0 END as completion_flag
    FROM {database_name}.latest_student_data
    WHERE year = '2024'
)
SELECT
    student_id,
    name,
    grade_level,
    subject,
    ROUND(average_score, 2) as average_score,
    ROUND(attendance_rate * 100, 1) as attendance_percent,
    ROUND(assignment_completion_rate * 100, 1) as completion_percent,
    (low_academic_flag + attendance_flag + completion_flag) as warning_score,
    CASE
        WHEN (low_academic_flag + attendance_flag + completion_flag) >= 3 THEN 'Immediate Intervention'
        WHEN (low_academic_flag + attendance_flag + completion_flag) = 2 THEN 'Close Monitoring'
        WHEN (low_academic_flag + attendance_flag + completion_flag) = 1 THEN 'Watch List'
        ELSE 'No Concerns'
    END as recommendation
FROM warning_indicators
WHERE (low_academic_flag + attendance_flag + completion_flag) > 0
ORDER BY warning_score DESC, average_score ASC;

-- =============================================================================
-- 4. SUBJECT-SPECIFIC ANALYTICS
-- =============================================================================

-- Query 4.1: Subject Performance Comparison
-- Purpose: Compare average performance across different subjects
SELECT
    subject,
    COUNT(DISTINCT student_id) as student_count,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(STDDEV(average_score), 2) as score_stddev,
    ROUND(MIN(average_score), 2) as min_score,
    ROUND(MAX(average_score), 2) as max_score,
    COUNT(CASE WHEN average_score >= 90 THEN 1 END) as excellent_count,
    COUNT(CASE WHEN average_score < 60 THEN 1 END) as at_risk_count,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance_percent
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND subject IS NOT NULL
GROUP BY subject
ORDER BY avg_score DESC;

-- Query 4.2: Mathematics Performance Deep Dive
-- Purpose: Detailed analysis of mathematics performance
SELECT
    grade_level,
    COUNT(*) as student_count,
    ROUND(AVG(math_score), 2) as avg_math_score,
    ROUND(STDDEV(math_score), 2) as math_score_stddev,
    COUNT(CASE WHEN math_score >= 90 THEN 1 END) as excellent_math,
    COUNT(CASE WHEN math_score BETWEEN 80 AND 89 THEN 1 END) as good_math,
    COUNT(CASE WHEN math_score BETWEEN 70 AND 79 THEN 1 END) as satisfactory_math,
    COUNT(CASE WHEN math_score BETWEEN 60 AND 69 THEN 1 END) as needs_improvement_math,
    COUNT(CASE WHEN math_score < 60 THEN 1 END) as at_risk_math,
    ROUND(COUNT(CASE WHEN math_score < 60 THEN 1 END) * 100.0 / COUNT(*), 1) as at_risk_percentage
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND subject = 'Mathematics'
  AND math_score IS NOT NULL
GROUP BY grade_level
ORDER BY grade_level;

-- Query 4.3: Reading vs Writing Performance Correlation
-- Purpose: Analyze correlation between reading and writing scores
SELECT
    grade_level,
    COUNT(*) as student_count,
    ROUND(AVG(reading_score), 2) as avg_reading,
    ROUND(AVG(writing_score), 2) as avg_writing,
    ROUND(AVG(reading_score - writing_score), 2) as reading_writing_gap,
    COUNT(CASE WHEN reading_score > writing_score + 10 THEN 1 END) as reading_stronger,
    COUNT(CASE WHEN writing_score > reading_score + 10 THEN 1 END) as writing_stronger,
    COUNT(CASE WHEN ABS(reading_score - writing_score) <= 10 THEN 1 END) as balanced_skills
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND subject = 'English'
  AND reading_score IS NOT NULL
  AND writing_score IS NOT NULL
GROUP BY grade_level
ORDER BY grade_level;

-- =============================================================================
-- 5. TREND ANALYSIS & TIME SERIES
-- =============================================================================

-- Query 5.1: Monthly Performance Trends
-- Purpose: Track performance changes over time
SELECT
    year,
    month,
    COUNT(DISTINCT student_id) as student_count,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance_percent,
    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk_count,
    ROUND(COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) * 100.0 / COUNT(*), 1) as high_risk_percentage
FROM {database_name}.processed_student_data
WHERE year = '2024'
GROUP BY year, month
ORDER BY year, month;

-- Query 5.2: Student Progress Tracking
-- Purpose: Track individual student progress over time
WITH student_progress AS (
    SELECT
        student_id,
        name,
        subject,
        year,
        month,
        average_score,
        attendance_rate,
        ROW_NUMBER() OVER (PARTITION BY student_id, subject ORDER BY year, month) as period_rank,
        LAG(average_score) OVER (PARTITION BY student_id, subject ORDER BY year, month) as prev_score,
        LAG(attendance_rate) OVER (PARTITION BY student_id, subject ORDER BY year, month) as prev_attendance
    FROM {database_name}.processed_student_data
    WHERE year = '2024'
)
SELECT
    student_id,
    name,
    subject,
    year,
    month,
    ROUND(average_score, 2) as current_score,
    ROUND(prev_score, 2) as previous_score,
    ROUND(average_score - prev_score, 2) as score_change,
    ROUND((attendance_rate - prev_attendance) * 100, 1) as attendance_change,
    CASE
        WHEN average_score - prev_score > 10 THEN 'Significant Improvement'
        WHEN average_score - prev_score > 5 THEN 'Moderate Improvement'
        WHEN average_score - prev_score > -5 THEN 'Stable'
        WHEN average_score - prev_score > -10 THEN 'Moderate Decline'
        ELSE 'Significant Decline'
    END as progress_category
FROM student_progress
WHERE prev_score IS NOT NULL
  AND period_rank > 1
ORDER BY student_id, subject, year, month;

-- Query 5.3: Semester Comparison
-- Purpose: Compare performance between semesters
SELECT
    academic_year,
    semester,
    grade_level,
    COUNT(DISTINCT student_id) as student_count,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(AVG(math_score), 2) as avg_math,
    ROUND(AVG(reading_score), 2) as avg_reading,
    ROUND(AVG(writing_score), 2) as avg_writing,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance_percent,
    COUNT(CASE WHEN performance_category = 'At Risk' THEN 1 END) as at_risk_count
FROM {database_name}.latest_student_data
WHERE year = '2024'
GROUP BY academic_year, semester, grade_level
ORDER BY academic_year, semester, grade_level;

-- =============================================================================
-- 6. CLASS & GRADE LEVEL COMPARISONS
-- =============================================================================

-- Query 6.1: Grade Level Performance Comparison
-- Purpose: Compare performance across different grade levels
SELECT
    grade_level,
    COUNT(DISTINCT student_id) as student_count,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(STDDEV(average_score), 2) as score_stddev,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY average_score), 2) as q1_score,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY average_score), 2) as median_score,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY average_score), 2) as q3_score,
    COUNT(CASE WHEN average_score >= 90 THEN 1 END) as excellent_count,
    COUNT(CASE WHEN average_score < 60 THEN 1 END) as at_risk_count,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance_percent
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND grade_level IS NOT NULL
GROUP BY grade_level
ORDER BY
    CASE
        WHEN grade_level = 'K' THEN 0
        ELSE CAST(grade_level AS INTEGER)
    END;

-- =============================================================================
-- 7. ATTENDANCE & ENGAGEMENT ANALYSIS
-- =============================================================================

-- Query 7.1: Attendance Impact on Performance
-- Purpose: Analyze correlation between attendance and academic performance
SELECT
    CASE
        WHEN attendance_rate >= 0.95 THEN 'Excellent (95%+)'
        WHEN attendance_rate >= 0.90 THEN 'Good (90-94%)'
        WHEN attendance_rate >= 0.85 THEN 'Satisfactory (85-89%)'
        WHEN attendance_rate >= 0.80 THEN 'Concerning (80-84%)'
        ELSE 'Critical (<80%)'
    END as attendance_category,
    COUNT(*) as student_count,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(AVG(math_score), 2) as avg_math,
    ROUND(AVG(reading_score), 2) as avg_reading,
    ROUND(AVG(writing_score), 2) as avg_writing,
    ROUND(AVG(assignment_completion_rate) * 100, 1) as avg_completion_percent,
    COUNT(CASE WHEN risk_level IN ('High Risk', 'Medium Risk') THEN 1 END) as at_risk_count
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND attendance_rate IS NOT NULL
GROUP BY
    CASE
        WHEN attendance_rate >= 0.95 THEN 'Excellent (95%+)'
        WHEN attendance_rate >= 0.90 THEN 'Good (90-94%)'
        WHEN attendance_rate >= 0.85 THEN 'Satisfactory (85-89%)'
        WHEN attendance_rate >= 0.80 THEN 'Concerning (80-84%)'
        ELSE 'Critical (<80%)'
    END
ORDER BY AVG(attendance_rate) DESC;

-- Query 7.2: Assignment Completion Analysis
-- Purpose: Analyze assignment completion patterns and impact
SELECT
    grade_level,
    CASE
        WHEN assignment_completion_rate >= 0.95 THEN 'Excellent (95%+)'
        WHEN assignment_completion_rate >= 0.85 THEN 'Good (85-94%)'
        WHEN assignment_completion_rate >= 0.75 THEN 'Satisfactory (75-84%)'
        WHEN assignment_completion_rate >= 0.65 THEN 'Concerning (65-74%)'
        ELSE 'Critical (<65%)'
    END as completion_category,
    COUNT(*) as student_count,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance_percent
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND assignment_completion_rate IS NOT NULL
GROUP BY
    grade_level,
    CASE
        WHEN assignment_completion_rate >= 0.95 THEN 'Excellent (95%+)'
        WHEN assignment_completion_rate >= 0.85 THEN 'Good (85-94%)'
        WHEN assignment_completion_rate >= 0.75 THEN 'Satisfactory (75-84%)'
        WHEN assignment_completion_rate >= 0.65 THEN 'Concerning (65-74%)'
        ELSE 'Critical (<65%)'
    END
ORDER BY grade_level, AVG(assignment_completion_rate) DESC;

-- =============================================================================
-- 8. DATA QUALITY & MONITORING
-- =============================================================================

-- Query 8.1: Data Completeness Report
-- Purpose: Monitor data quality and completeness
SELECT
    year,
    month,
    COUNT(*) as total_records,
    COUNT(student_id) as student_id_count,
    COUNT(name) as name_count,
    COUNT(math_score) as math_score_count,
    COUNT(reading_score) as reading_score_count,
    COUNT(writing_score) as writing_score_count,
    COUNT(attendance_rate) as attendance_count,
    COUNT(assignment_completion_rate) as completion_count,
    ROUND(AVG(data_completeness_score), 3) as avg_completeness_score,
    COUNT(CASE WHEN data_completeness_score < 0.7 THEN 1 END) as low_quality_records
FROM {database_name}.processed_student_data
WHERE year = '2024'
GROUP BY year, month
ORDER BY year, month;

-- Query 8.2: Data Quality Issues
-- Purpose: Identify potential data quality issues
SELECT
    'Missing Math Scores' as issue_type,
    COUNT(*) as affected_records,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {database_name}.latest_student_data WHERE year = '2024'), 2) as percentage
FROM {database_name}.latest_student_data
WHERE year = '2024' AND math_score IS NULL

UNION ALL

SELECT
    'Missing Reading Scores' as issue_type,
    COUNT(*) as affected_records,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {database_name}.latest_student_data WHERE year = '2024'), 2) as percentage
FROM {database_name}.latest_student_data
WHERE year = '2024' AND reading_score IS NULL

UNION ALL

SELECT
    'Missing Attendance Data' as issue_type,
    COUNT(*) as affected_records,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {database_name}.latest_student_data WHERE year = '2024'), 2) as percentage
FROM {database_name}.latest_student_data
WHERE year = '2024' AND attendance_rate IS NULL

UNION ALL

SELECT
    'Extreme Low Scores (<10)' as issue_type,
    COUNT(*) as affected_records,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {database_name}.latest_student_data WHERE year = '2024'), 2) as percentage
FROM {database_name}.latest_student_data
WHERE year = '2024' AND (math_score < 10 OR reading_score < 10 OR writing_score < 10)

ORDER BY affected_records DESC;

-- =============================================================================
-- 9. ADMINISTRATIVE REPORTS
-- =============================================================================

-- Query 9.1: Executive Summary Dashboard
-- Purpose: High-level metrics for administrators
SELECT
    'Current Academic Year Summary' as report_type,
    COUNT(DISTINCT student_id) as total_students,
    COUNT(DISTINCT grade_level) as grade_levels,
    ROUND(AVG(average_score), 2) as overall_avg_score,
    ROUND(AVG(attendance_rate) * 100, 1) as overall_attendance_percent,
    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk_students,
    COUNT(CASE WHEN performance_category = 'Excellent' THEN 1 END) as excellent_students,
    ROUND(COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) * 100.0 / COUNT(*), 1) as high_risk_percentage,
    ROUND(COUNT(CASE WHEN performance_category = 'Excellent' THEN 1 END) * 100.0 / COUNT(*), 1) as excellent_percentage
FROM {database_name}.latest_student_data
WHERE year = '2024';

-- Query 9.2: Grade Level Summary Report
-- Purpose: Summary statistics by grade level for administrators
SELECT
    grade_level,
    COUNT(DISTINCT student_id) as enrollment,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance,
    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk_count,
    COUNT(CASE WHEN performance_category = 'Excellent' THEN 1 END) as excellent_count,
    ROUND(COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) * 100.0 / COUNT(*), 1) as risk_percentage,
    ROUND(COUNT(CASE WHEN performance_category = 'Excellent' THEN 1 END) * 100.0 / COUNT(*), 1) as excellence_percentage,
    ROUND(AVG(assignment_completion_rate) * 100, 1) as avg_completion_rate
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND grade_level IS NOT NULL
GROUP BY grade_level
ORDER BY
    CASE
        WHEN grade_level = 'K' THEN 0
        ELSE CAST(grade_level AS INTEGER)
    END;

-- =============================================================================
-- 10. ADVANCED ANALYTICS & PREDICTIONS
-- =============================================================================

-- Query 10.1: Student Success Prediction Model
-- Purpose: Identify factors that predict student success
WITH success_factors AS (
    SELECT
        student_id,
        name,
        grade_level,
        average_score,
        attendance_rate,
        assignment_completion_rate,
        CASE WHEN average_score >= 80 THEN 1 ELSE 0 END as is_successful,
        CASE WHEN attendance_rate >= 0.9 THEN 1 ELSE 0 END as good_attendance,
        CASE WHEN assignment_completion_rate >= 0.85 THEN 1 ELSE 0 END as good_completion,
        CASE WHEN math_score >= 80 THEN 1 ELSE 0 END as strong_math,
        CASE WHEN reading_score >= 80 THEN 1 ELSE 0 END as strong_reading
    FROM {database_name}.latest_student_data
    WHERE year = '2024'
      AND average_score IS NOT NULL
      AND attendance_rate IS NOT NULL
      AND assignment_completion_rate IS NOT NULL
)
SELECT
    'Success Factor Analysis' as analysis_type,
    COUNT(*) as total_students,
    SUM(is_successful) as successful_students,
    ROUND(AVG(is_successful) * 100, 1) as success_rate_percent,
    ROUND(AVG(CASE WHEN good_attendance = 1 THEN is_successful END) * 100, 1) as success_rate_good_attendance,
    ROUND(AVG(CASE WHEN good_completion = 1 THEN is_successful END) * 100, 1) as success_rate_good_completion,
    ROUND(AVG(CASE WHEN strong_math = 1 THEN is_successful END) * 100, 1) as success_rate_strong_math,
    ROUND(AVG(CASE WHEN strong_reading = 1 THEN is_successful END) * 100, 1) as success_rate_strong_reading
FROM success_factors;

-- Query 10.2: Cohort Analysis
-- Purpose: Analyze student cohorts and their progression
WITH cohort_data AS (
    SELECT
        student_id,
        grade_level,
        academic_year,
        semester,
        average_score,
        attendance_rate,
        risk_level,
        ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY academic_year, semester) as period_number
    FROM {database_name}.processed_student_data
    WHERE year = '2024'
)
SELECT
    grade_level as cohort,
    period_number,
    COUNT(DISTINCT student_id) as students_remaining,
    ROUND(AVG(average_score), 2) as avg_score,
    ROUND(AVG(attendance_rate) * 100, 1) as avg_attendance,
    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk_count,
    ROUND(COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) * 100.0 / COUNT(*), 1) as high_risk_percentage
FROM cohort_data
GROUP BY grade_level, period_number
ORDER BY grade_level, period_number;

-- Query 10.3: Performance Correlation Analysis
-- Purpose: Analyze correlations between different performance metrics
SELECT
    'Performance Correlations' as analysis_type,
    ROUND(CORR(math_score, reading_score), 3) as math_reading_correlation,
    ROUND(CORR(math_score, writing_score), 3) as math_writing_correlation,
    ROUND(CORR(reading_score, writing_score), 3) as reading_writing_correlation,
    ROUND(CORR(average_score, attendance_rate), 3) as score_attendance_correlation,
    ROUND(CORR(average_score, assignment_completion_rate), 3) as score_completion_correlation,
    ROUND(CORR(attendance_rate, assignment_completion_rate), 3) as attendance_completion_correlation
FROM {database_name}.latest_student_data
WHERE year = '2024'
  AND math_score IS NOT NULL
  AND reading_score IS NOT NULL
  AND writing_score IS NOT NULL
  AND attendance_rate IS NOT NULL
  AND assignment_completion_rate IS NOT NULL;

-- =============================================================================
-- 11. PARAMETERIZED QUERY TEMPLATES
-- =============================================================================

-- Query 11.1: Student Detail Report (Template)
-- Purpose: Detailed report for a specific student
-- Usage: Replace {student_id_param} with actual student ID
SELECT
    student_id,
    name,
    grade_level,
    subject,
    ROUND(average_score, 2) as average_score,
    ROUND(math_score, 2) as math_score,
    ROUND(reading_score, 2) as reading_score,
    ROUND(writing_score, 2) as writing_score,
    performance_category,
    risk_level,
    ROUND(attendance_rate * 100, 1) as attendance_percent,
    ROUND(assignment_completion_rate * 100, 1) as completion_percent,
    academic_year,
    semester,
    transformation_timestamp as last_updated
FROM {database_name}.latest_student_data
WHERE student_id = '{student_id_param}'
  AND year = '2024'
ORDER BY subject, transformation_timestamp DESC;

-- Query 11.2: Grade Level Report (Template)
-- Purpose: Comprehensive report for a specific grade level
-- Usage: Replace {grade_level_param} with actual grade level
SELECT
    student_id,
    name,
    subject,
    ROUND(average_score, 2) as average_score,
    performance_category,
    risk_level,
    ROUND(attendance_rate * 100, 1) as attendance_percent,
    ROUND(assignment_completion_rate * 100, 1) as completion_percent,
    CASE
        WHEN risk_level = 'High Risk' THEN 'Immediate intervention needed'
        WHEN risk_level = 'Medium Risk' THEN 'Monitor closely'
        WHEN performance_category = 'Excellent' THEN 'Consider enrichment opportunities'
        ELSE 'Continue current support'
    END as recommendation
FROM {database_name}.latest_student_data
WHERE grade_level = '{grade_level_param}'
  AND year = '2024'
ORDER BY
    CASE risk_level
        WHEN 'High Risk' THEN 1
        WHEN 'Medium Risk' THEN 2
        ELSE 3
    END,
    average_score ASC;

-- Query 11.3: Date Range Analysis (Template)
-- Purpose: Analyze data for a specific date range
-- Usage: Replace {start_date} and {end_date} with actual dates (YYYY-MM-DD format)
SELECT
    DATE(transformation_timestamp) as analysis_date,
    COUNT(DISTINCT student_id) as students_analyzed,
    ROUND(AVG(average_score), 2) as daily_avg_score,
    ROUND(AVG(attendance_rate) * 100, 1) as daily_avg_attendance,
    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as daily_high_risk_count,
    COUNT(CASE WHEN performance_category = 'Excellent' THEN 1 END) as daily_excellent_count
FROM {database_name}.processed_student_data
WHERE DATE(transformation_timestamp) BETWEEN DATE '{start_date}' AND DATE '{end_date}'
GROUP BY DATE(transformation_timestamp)
ORDER BY analysis_date;

-- =============================================================================
-- 12. COST-OPTIMIZED QUERIES FOR AWS FREE TIER
-- =============================================================================

-- Query 12.1: Efficient Current Status Query
-- Purpose: Get current status with minimal data scanning
SELECT
    COUNT(DISTINCT student_id) as total_students,
    ROUND(AVG(average_score), 2) as avg_score,
    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk_count
FROM {database_name}.latest_student_data
WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
  AND month = CAST(MONTH(CURRENT_DATE) AS VARCHAR);

-- Query 12.2: Weekly Summary (Partition-Optimized)
-- Purpose: Weekly summary with efficient partition pruning
SELECT
    year,
    month,
    COUNT(*) as records_processed,
    COUNT(DISTINCT student_id) as unique_students,
    ROUND(AVG(average_score), 2) as weekly_avg_score
FROM {database_name}.processed_student_data
WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
  AND month = CAST(MONTH(CURRENT_DATE) AS VARCHAR)
  AND day >= CAST(DAY(CURRENT_DATE) - 7 AS VARCHAR)
GROUP BY year, month
ORDER BY year, month;

/*
=============================================================================
QUERY USAGE GUIDELINES
=============================================================================

1. PERFORMANCE OPTIMIZATION:
   - Always include partition filters (year, month, day, subject) when possible
   - Use the latest_student_data view for current analysis
   - Limit result sets with appropriate WHERE clauses

2. COST OPTIMIZATION:
   - Prefer queries that scan fewer partitions
   - Use LIMIT clauses for exploratory queries
   - Monitor query costs in AWS console

3. EDUCATIONAL INSIGHTS:
   - Focus on actionable insights for educators
   - Combine multiple metrics for comprehensive analysis
   - Use risk levels and performance categories for prioritization

4. DATA QUALITY:
   - Always check for NULL values in critical fields
   - Use data_completeness_score to filter high-quality records
   - Monitor data freshness with transformation_timestamp

5. CUSTOMIZATION:
   - Replace template parameters with actual values
   - Adjust thresholds based on institutional standards
   - Add institution-specific fields as needed

=============================================================================
*/