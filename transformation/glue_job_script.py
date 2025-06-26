"""
Student Insights Pipeline - Data Transformation Script

This AWS Glue job processes raw student data from S3 and transforms it into
an optimized format for analytics. The transformation includes:

- Data cleaning and validation
- Schema standardization
- Data enrichment with calculated fields
- Quality scoring and risk assessment
- Partitioned output for efficient querying

Input: Raw JSON files from S3 (from ingestion Lambda)
Output: Parquet files partitioned by date and subject
"""

import sys
import json
import boto3
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'RAW_BUCKET_NAME',
    'PROCESSED_BUCKET_NAME',
    'ENVIRONMENT'
])

job.init(args['JOB_NAME'], args)

# Configuration
RAW_BUCKET = args['RAW_BUCKET_NAME']
PROCESSED_BUCKET = args['PROCESSED_BUCKET_NAME']
ENVIRONMENT = args['ENVIRONMENT']

logger.info(f"Starting data transformation job for environment: {ENVIRONMENT}")
logger.info(f"Raw bucket: {RAW_BUCKET}")
logger.info(f"Processed bucket: {PROCESSED_BUCKET}")


def define_student_schema():
    """
    Define the schema for student data

    Returns:
        StructType: Spark SQL schema
    """
    return StructType([
        StructField("student_id", StringType(), False),
        StructField("name", StringType(), False),
        StructField("math_score", DoubleType(), True),
        StructField("reading_score", DoubleType(), True),
        StructField("writing_score", DoubleType(), True),
        StructField("grade_level", StringType(), True),
        StructField("subject", StringType(), True),
        StructField("attendance_rate", DoubleType(), True),
        StructField("assignment_completion_rate", DoubleType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("ingestion_timestamp", TimestampType(), True),
        StructField("processing_date", StringType(), True),
        StructField("processing_hour", StringType(), True),
        StructField("environment", StringType(), True),
        StructField("data_source", StringType(), True),
        StructField("average_score", DoubleType(), True),
        StructField("performance_category", StringType(), True),
        StructField("csv_row_number", IntegerType(), True)
    ])


def read_raw_data(bucket_name: str, date_partition: str = None) -> DataFrame:
    """
    Read raw JSON data from S3

    Args:
        bucket_name: S3 bucket name
        date_partition: Optional date partition (YYYY/MM/DD)

    Returns:
        Spark DataFrame with raw data
    """
    try:
        if date_partition:
            s3_path = f"s3://{bucket_name}/raw/date={date_partition}/"
        else:
            s3_path = f"s3://{bucket_name}/raw/"

        logger.info(f"Reading data from: {s3_path}")

        # Read JSON files
        df = spark.read.option("multiline", "true").json(s3_path)

        logger.info(f"Successfully read {df.count()} records from raw data")
        return df

    except Exception as e:
        logger.error(f"Error reading raw data: {str(e)}")
        raise


def clean_and_validate_data(df: DataFrame) -> DataFrame:
    """
    Clean and validate the raw data

    Args:
        df: Raw DataFrame

    Returns:
        Cleaned DataFrame
    """
    logger.info("Starting data cleaning and validation")

    # Remove records with missing required fields
    df_clean = df.filter(
        (col("student_id").isNotNull()) &
        (col("name").isNotNull()) &
        (col("student_id") != "") &
        (col("name") != "")
    )

    # Validate score ranges (0-100)
    score_columns = ["math_score", "reading_score", "writing_score"]
    for score_col in score_columns:
        df_clean = df_clean.withColumn(
            score_col,
            when(
                (col(score_col).isNotNull()) &
                (col(score_col) >= 0) &
                (col(score_col) <= 100),
                col(score_col)
            ).otherwise(None)
        )

    # Validate rate fields (0-1)
    rate_columns = ["attendance_rate", "assignment_completion_rate"]
    for rate_col in rate_columns:
        df_clean = df_clean.withColumn(
            rate_col,
            when(
                (col(rate_col).isNotNull()) &
                (col(rate_col) >= 0) &
                (col(rate_col) <= 1),
                col(rate_col)
            ).otherwise(None)
        )

    # Standardize grade levels
    df_clean = df_clean.withColumn(
        "grade_level",
        when(col("grade_level").isin(["9", "10", "11", "12", "K", "1", "2", "3", "4", "5", "6", "7", "8"]),
             col("grade_level")).otherwise("Unknown")
    )

    # Standardize subjects
    valid_subjects = ["Mathematics", "English", "Science", "History", "Art", "Physical Education"]
    df_clean = df_clean.withColumn(
        "subject",
        when(col("subject").isin(valid_subjects), col("subject")).otherwise("Other")
    )

    records_before = df.count()
    records_after = df_clean.count()
    logger.info(f"Data cleaning completed. Records: {records_before} -> {records_after}")

    return df_clean


def enrich_data(df: DataFrame) -> DataFrame:
    """
    Enrich data with calculated fields and insights

    Args:
        df: Cleaned DataFrame

    Returns:
        Enriched DataFrame
    """
    logger.info("Starting data enrichment")

    # Calculate average score (only from non-null scores)
    df_enriched = df.withColumn(
        "average_score",
        when(
            col("math_score").isNotNull() |
            col("reading_score").isNotNull() |
            col("writing_score").isNotNull(),
            (
                coalesce(col("math_score"), lit(0)) +
                coalesce(col("reading_score"), lit(0)) +
                coalesce(col("writing_score"), lit(0))
            ) / (
                (when(col("math_score").isNotNull(), 1).otherwise(0)) +
                (when(col("reading_score").isNotNull(), 1).otherwise(0)) +
                (when(col("writing_score").isNotNull(), 1).otherwise(0))
            )
        ).otherwise(None)
    )

    # Determine performance category based on average score
    df_enriched = df_enriched.withColumn(
        "performance_category",
        when(col("average_score") >= 90, "Excellent")
        .when(col("average_score") >= 80, "Good")
        .when(col("average_score") >= 70, "Satisfactory")
        .when(col("average_score") >= 60, "Needs Improvement")
        .when(col("average_score").isNotNull(), "At Risk")
        .otherwise("No Data")
    )

    # Calculate risk level based on multiple factors
    df_enriched = df_enriched.withColumn(
        "risk_score",
        (
            # Academic risk (0-3 points)
            when(col("average_score") < 60, 3)
            .when(col("average_score") < 70, 2)
            .when(col("average_score") < 80, 1)
            .otherwise(0)
        ) + (
            # Attendance risk (0-2 points)
            when(col("attendance_rate") < 0.7, 2)
            .when(col("attendance_rate") < 0.85, 1)
            .otherwise(0)
        ) + (
            # Assignment completion risk (0-2 points)
            when(col("assignment_completion_rate") < 0.6, 2)
            .when(col("assignment_completion_rate") < 0.8, 1)
            .otherwise(0)
        )
    )

    # Determine risk level from risk score
    df_enriched = df_enriched.withColumn(
        "risk_level",
        when(col("risk_score") >= 5, "High Risk")
        .when(col("risk_score") >= 3, "Medium Risk")
        .when(col("risk_score") >= 1, "Low Risk")
        .otherwise("No Risk")
    )

    # Add academic year and semester based on timestamp
    df_enriched = df_enriched.withColumn(
        "academic_year",
        when(month(col("ingestion_timestamp")).between(8, 12),
             concat(year(col("ingestion_timestamp")), lit("-"), year(col("ingestion_timestamp")) + 1))
        .otherwise(
             concat(year(col("ingestion_timestamp")) - 1, lit("-"), year(col("ingestion_timestamp")))
        )
    )

    df_enriched = df_enriched.withColumn(
        "semester",
        when(month(col("ingestion_timestamp")).between(8, 12), "Fall")
        .when(month(col("ingestion_timestamp")).between(1, 5), "Spring")
        .otherwise("Summer")
    )

    # Add data quality indicators
    df_enriched = df_enriched.withColumn(
        "data_completeness_score",
        (
            (when(col("math_score").isNotNull(), 1).otherwise(0)) +
            (when(col("reading_score").isNotNull(), 1).otherwise(0)) +
            (when(col("writing_score").isNotNull(), 1).otherwise(0)) +
            (when(col("attendance_rate").isNotNull(), 1).otherwise(0)) +
            (when(col("assignment_completion_rate").isNotNull(), 1).otherwise(0)) +
            (when(col("grade_level") != "Unknown", 1).otherwise(0)) +
            (when(col("subject") != "Other", 1).otherwise(0))
        ) / 7.0
    )

    # Add processing metadata
    df_enriched = df_enriched.withColumn("transformation_timestamp", current_timestamp())
    df_enriched = df_enriched.withColumn("transformation_date", current_date())

    logger.info("Data enrichment completed")
    return df_enriched


def create_data_quality_report(df: DataFrame) -> Dict[str, Any]:
    """
    Create a data quality report

    Args:
        df: DataFrame to analyze

    Returns:
        Data quality report dictionary
    """
    logger.info("Generating data quality report")

    total_records = df.count()

    # Calculate completeness for key fields
    completeness_stats = {}
    key_fields = ["student_id", "name", "math_score", "reading_score", "writing_score",
                  "attendance_rate", "assignment_completion_rate", "grade_level", "subject"]

    for field in key_fields:
        non_null_count = df.filter(col(field).isNotNull()).count()
        completeness_stats[field] = {
            "total_records": total_records,
            "non_null_records": non_null_count,
            "completeness_rate": non_null_count / total_records if total_records > 0 else 0
        }

    # Calculate score statistics
    score_stats = {}
    score_fields = ["math_score", "reading_score", "writing_score", "average_score"]

    for field in score_fields:
        stats = df.select(
            avg(col(field)).alias("mean"),
            stddev(col(field)).alias("stddev"),
            min(col(field)).alias("min"),
            max(col(field)).alias("max"),
            count(when(col(field).isNotNull(), 1)).alias("count")
        ).collect()[0]

        score_stats[field] = {
            "mean": float(stats["mean"]) if stats["mean"] else None,
            "stddev": float(stats["stddev"]) if stats["stddev"] else None,
            "min": float(stats["min"]) if stats["min"] else None,
            "max": float(stats["max"]) if stats["max"] else None,
            "count": stats["count"]
        }

    # Risk level distribution
    risk_distribution = df.groupBy("risk_level").count().collect()
    risk_stats = {row["risk_level"]: row["count"] for row in risk_distribution}

    # Performance category distribution
    performance_distribution = df.groupBy("performance_category").count().collect()
    performance_stats = {row["performance_category"]: row["count"] for row in performance_distribution}

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_records": total_records,
        "completeness_stats": completeness_stats,
        "score_statistics": score_stats,
        "risk_distribution": risk_stats,
        "performance_distribution": performance_stats,
        "environment": ENVIRONMENT
    }

    logger.info(f"Data quality report generated for {total_records} records")
    return report


def write_processed_data(df: DataFrame, bucket_name: str) -> None:
    """
    Write processed data to S3 in Parquet format with partitioning

    Args:
        df: Processed DataFrame
        bucket_name: S3 bucket name for output
    """
    logger.info("Writing processed data to S3")

    # Add partition columns
    df_partitioned = df.withColumn("year", year(col("transformation_date"))) \
                       .withColumn("month", month(col("transformation_date"))) \
                       .withColumn("day", dayofmonth(col("transformation_date")))

    # Output path
    output_path = f"s3://{bucket_name}/processed/"

    try:
        # Write as Parquet with partitioning
        df_partitioned.write \
            .mode("append") \
            .partitionBy("year", "month", "day", "subject") \
            .option("compression", "snappy") \
            .parquet(output_path)

        logger.info(f"Successfully wrote processed data to {output_path}")

    except Exception as e:
        logger.error(f"Error writing processed data: {str(e)}")
        raise


def write_quality_report(report: Dict[str, Any], bucket_name: str) -> None:
    """
    Write data quality report to S3

    Args:
        report: Data quality report dictionary
        bucket_name: S3 bucket name
    """
    logger.info("Writing data quality report to S3")

    try:
        # Convert to JSON
        report_json = json.dumps(report, indent=2, default=str)

        # Generate S3 key with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        s3_key = f"quality-reports/data_quality_report_{timestamp}.json"

        # Write to S3
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=report_json,
            ContentType='application/json'
        )

        logger.info(f"Data quality report written to s3://{bucket_name}/{s3_key}")

    except Exception as e:
        logger.error(f"Error writing quality report: {str(e)}")
        raise


def main():
    """
    Main transformation pipeline
    """
    try:
        logger.info("=== Starting Student Data Transformation Pipeline ===")

        # Step 1: Read raw data
        logger.info("Step 1: Reading raw data from S3")
        raw_df = read_raw_data(RAW_BUCKET)

        if raw_df.count() == 0:
            logger.warning("No data found in raw bucket. Exiting.")
            return

        # Step 2: Clean and validate data
        logger.info("Step 2: Cleaning and validating data")
        clean_df = clean_and_validate_data(raw_df)

        # Step 3: Enrich data
        logger.info("Step 3: Enriching data with calculated fields")
        enriched_df = enrich_data(clean_df)

        # Step 4: Generate data quality report
        logger.info("Step 4: Generating data quality report")
        quality_report = create_data_quality_report(enriched_df)

        # Step 5: Write processed data
        logger.info("Step 5: Writing processed data to S3")
        write_processed_data(enriched_df, PROCESSED_BUCKET)

        # Step 6: Write quality report
        logger.info("Step 6: Writing data quality report")
        write_quality_report(quality_report, PROCESSED_BUCKET)

        # Log summary statistics
        final_count = enriched_df.count()
        logger.info(f"=== Transformation Complete ===")
        logger.info(f"Total records processed: {final_count}")
        logger.info(f"Data quality score: {quality_report.get('completeness_stats', {}).get('student_id', {}).get('completeness_rate', 0):.2%}")

        # Show sample of processed data
        logger.info("Sample of processed data:")
        enriched_df.select(
            "student_id", "name", "average_score", "performance_category",
            "risk_level", "data_completeness_score"
        ).show(10, truncate=False)

    except Exception as e:
        logger.error(f"Transformation pipeline failed: {str(e)}")
        raise

    finally:
        # Commit the job
        job.commit()


# Execute main pipeline
if __name__ == "__main__":
    main()