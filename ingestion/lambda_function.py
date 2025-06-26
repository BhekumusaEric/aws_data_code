"""
Student Insights Pipeline - Data Ingestion Lambda Function

This function handles incoming student data from multiple sources:
- JSON data from API Gateway (single student records)
- CSV data from file uploads (batch processing)

Features:
- Data validation using JSON Schema
- Multi-format support (JSON/CSV)
- Structured logging for debugging
- Error classification and handling
- Data enrichment with metadata
- S3 partitioning by date and data type
"""

import json
import boto3
import os
import csv
import io
import base64
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')

# Environment variables from CloudFormation
RAW_BUCKET = os.environ.get('RAW_BUCKET_NAME')
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET_NAME')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

# Data validation schema
STUDENT_DATA_SCHEMA = {
    "type": "object",
    "required": ["student_id", "name"],
    "properties": {
        "student_id": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "math_score": {"type": "number", "minimum": 0, "maximum": 100},
        "reading_score": {"type": "number", "minimum": 0, "maximum": 100},
        "writing_score": {"type": "number", "minimum": 0, "maximum": 100},
        "grade_level": {"type": "string"},
        "subject": {"type": "string"},
        "attendance_rate": {"type": "number", "minimum": 0, "maximum": 1},
        "assignment_completion_rate": {"type": "number", "minimum": 0, "maximum": 1}
    }
}


class DataIngestionError(Exception):
    """Custom exception for data ingestion errors"""
    def __init__(self, message: str, error_type: str = "GENERAL"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


def validate_student_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate student data against schema

    Args:
        data: Student data dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    for field in STUDENT_DATA_SCHEMA["required"]:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")

    # Validate data types and ranges
    for field, rules in STUDENT_DATA_SCHEMA["properties"].items():
        if field in data and data[field] is not None:
            value = data[field]

            if rules["type"] == "string" and not isinstance(value, str):
                errors.append(f"Field {field} must be a string")
            elif rules["type"] == "number" and not isinstance(value, (int, float)):
                errors.append(f"Field {field} must be a number")
            elif rules["type"] == "number":
                if "minimum" in rules and value < rules["minimum"]:
                    errors.append(f"Field {field} must be >= {rules['minimum']}")
                if "maximum" in rules and value > rules["maximum"]:
                    errors.append(f"Field {field} must be <= {rules['maximum']}")

    return len(errors) == 0, errors


def enrich_student_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich student data with metadata

    Args:
        data: Original student data

    Returns:
        Enriched data with metadata
    """
    enriched = data.copy()

    # Add processing metadata
    now = datetime.now(timezone.utc)
    enriched.update({
        'ingestion_timestamp': now.isoformat(),
        'processing_date': now.strftime('%Y-%m-%d'),
        'processing_hour': now.strftime('%H'),
        'environment': ENVIRONMENT,
        'data_source': 'api_ingestion'
    })

    # Calculate average score if individual scores are present
    scores = []
    for score_field in ['math_score', 'reading_score', 'writing_score']:
        if score_field in enriched and enriched[score_field] is not None:
            scores.append(enriched[score_field])

    if scores:
        enriched['average_score'] = round(sum(scores) / len(scores), 2)

        # Determine performance category
        avg_score = enriched['average_score']
        if avg_score >= 90:
            enriched['performance_category'] = 'Excellent'
        elif avg_score >= 80:
            enriched['performance_category'] = 'Good'
        elif avg_score >= 70:
            enriched['performance_category'] = 'Satisfactory'
        elif avg_score >= 60:
            enriched['performance_category'] = 'Needs Improvement'
        else:
            enriched['performance_category'] = 'At Risk'

    return enriched


def generate_s3_key(data: Dict[str, Any], file_format: str = 'json') -> str:
    """
    Generate S3 key with proper partitioning

    Args:
        data: Student data
        file_format: File format (json/csv)

    Returns:
        S3 key path
    """
    now = datetime.now(timezone.utc)
    date_partition = now.strftime('%Y/%m/%d')
    hour_partition = now.strftime('%H')

    student_id = data.get('student_id', 'unknown')
    timestamp = now.strftime('%Y%m%d_%H%M%S')

    return f"raw/date={date_partition}/hour={hour_partition}/student_{student_id}_{timestamp}.{file_format}"


def store_to_s3(data: Dict[str, Any], bucket: str, key: str) -> bool:
    """
    Store data to S3 with error handling

    Args:
        data: Data to store
        bucket: S3 bucket name
        key: S3 key

    Returns:
        Success status
    """
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType='application/json',
            Metadata={
                'ingestion-timestamp': data.get('ingestion_timestamp', ''),
                'environment': ENVIRONMENT,
                'student-id': str(data.get('student_id', ''))
            }
        )

        logger.info(f"Successfully stored data to s3://{bucket}/{key}")
        return True

    except Exception as e:
        logger.error(f"Failed to store data to S3: {str(e)}")
        raise DataIngestionError(f"S3 storage failed: {str(e)}", "S3_ERROR")


def process_json_data(event_body: str) -> Dict[str, Any]:
    """
    Process JSON data from API Gateway

    Args:
        event_body: JSON string from API Gateway

    Returns:
        Processing result
    """
    try:
        # Parse JSON
        data = json.loads(event_body)
        logger.info(f"Processing JSON data for student: {data.get('student_id', 'unknown')}")

        # Handle both single record and array of records
        if isinstance(data, list):
            results = []
            for record in data:
                is_valid, errors = validate_student_data(record)
                if not is_valid:
                    raise DataIngestionError(f"Validation failed: {', '.join(errors)}", "VALIDATION_ERROR")

                enriched_data = enrich_student_data(record)
                s3_key = generate_s3_key(enriched_data)
                store_to_s3(enriched_data, RAW_BUCKET, s3_key)

                results.append({
                    'student_id': record.get('student_id'),
                    's3_key': s3_key,
                    'status': 'success'
                })

            return {
                'processed_count': len(results),
                'results': results,
                'status': 'success'
            }

        else:
            # Single record
            is_valid, errors = validate_student_data(data)
            if not is_valid:
                raise DataIngestionError(f"Validation failed: {', '.join(errors)}", "VALIDATION_ERROR")

            enriched_data = enrich_student_data(data)
            s3_key = generate_s3_key(enriched_data)
            store_to_s3(enriched_data, RAW_BUCKET, s3_key)

            return {
                'student_id': data.get('student_id'),
                's3_key': s3_key,
                'status': 'success'
            }

    except json.JSONDecodeError as e:
        raise DataIngestionError(f"Invalid JSON format: {str(e)}", "JSON_ERROR")
    except DataIngestionError:
        raise
    except Exception as e:
        raise DataIngestionError(f"JSON processing failed: {str(e)}", "PROCESSING_ERROR")


def process_csv_data(csv_content: str) -> Dict[str, Any]:
    """
    Process CSV data from file upload

    Args:
        csv_content: CSV content as string

    Returns:
        Processing result
    """
    try:
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        results = []
        errors = []

        for row_num, row in enumerate(csv_reader, start=1):
            try:
                # Clean and convert data types
                cleaned_row = {}
                for key, value in row.items():
                    if value.strip():  # Skip empty values
                        # Try to convert numeric fields
                        if key in ['math_score', 'reading_score', 'writing_score']:
                            try:
                                cleaned_row[key] = float(value)
                            except ValueError:
                                cleaned_row[key] = value
                        elif key in ['attendance_rate', 'assignment_completion_rate']:
                            try:
                                cleaned_row[key] = float(value)
                            except ValueError:
                                cleaned_row[key] = value
                        else:
                            cleaned_row[key] = value.strip()

                # Validate row
                is_valid, validation_errors = validate_student_data(cleaned_row)
                if not is_valid:
                    errors.append(f"Row {row_num}: {', '.join(validation_errors)}")
                    continue

                # Enrich and store
                enriched_data = enrich_student_data(cleaned_row)
                enriched_data['data_source'] = 'csv_upload'
                enriched_data['csv_row_number'] = row_num

                s3_key = generate_s3_key(enriched_data)
                store_to_s3(enriched_data, RAW_BUCKET, s3_key)

                results.append({
                    'row_number': row_num,
                    'student_id': cleaned_row.get('student_id'),
                    's3_key': s3_key,
                    'status': 'success'
                })

            except Exception as e:
                errors.append(f"Row {row_num}: Processing error - {str(e)}")

        return {
            'processed_count': len(results),
            'error_count': len(errors),
            'results': results,
            'errors': errors,
            'status': 'completed' if not errors else 'completed_with_errors'
        }

    except Exception as e:
        raise DataIngestionError(f"CSV processing failed: {str(e)}", "CSV_ERROR")


def lambda_handler(event, context):
    """
    Main Lambda handler for student data ingestion

    Supports:
    - JSON data from API Gateway
    - CSV data from file uploads
    - Batch processing
    - Comprehensive error handling
    """

    # Log the incoming event (excluding sensitive data)
    logger.info(f"Processing request - Method: {event.get('httpMethod', 'Unknown')}")

    try:
        # Validate environment configuration
        if not RAW_BUCKET:
            raise DataIngestionError("RAW_BUCKET_NAME environment variable not set", "CONFIG_ERROR")

        # Determine content type and process accordingly
        headers = event.get('headers', {})
        content_type = headers.get('content-type', headers.get('Content-Type', ''))

        if 'application/json' in content_type or not content_type:
            # Process JSON data
            body = event.get('body', '{}')
            if event.get('isBase64Encoded', False):
                body = base64.b64decode(body).decode('utf-8')

            result = process_json_data(body)

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'message': 'Data ingestion completed successfully',
                    'result': result,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            }

        elif 'text/csv' in content_type or 'application/csv' in content_type:
            # Process CSV data
            body = event.get('body', '')
            if event.get('isBase64Encoded', False):
                body = base64.b64decode(body).decode('utf-8')

            result = process_csv_data(body)

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'CSV data ingestion completed',
                    'result': result,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            }

        else:
            raise DataIngestionError(f"Unsupported content type: {content_type}", "CONTENT_TYPE_ERROR")

    except DataIngestionError as e:
        logger.error(f"Data ingestion error: {e.message} (Type: {e.error_type})")

        status_code = 400
        if e.error_type in ['S3_ERROR', 'CONFIG_ERROR']:
            status_code = 500

        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': e.message,
                'error_type': e.error_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        }
