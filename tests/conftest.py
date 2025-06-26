"""
Pytest configuration and fixtures for Student Insights Pipeline tests
"""

import pytest
import boto3
from moto import mock_s3, mock_lambda, mock_apigateway
import os


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def s3_client(aws_credentials):
    """Create a mocked S3 client."""
    with mock_s3():
        yield boto3.client('s3', region_name='us-east-1')


@pytest.fixture
def lambda_client(aws_credentials):
    """Create a mocked Lambda client."""
    with mock_lambda():
        yield boto3.client('lambda', region_name='us-east-1')


@pytest.fixture
def api_gateway_client(aws_credentials):
    """Create a mocked API Gateway client."""
    with mock_apigateway():
        yield boto3.client('apigateway', region_name='us-east-1')


@pytest.fixture
def sample_student_data():
    """Sample student data for testing."""
    return {
        "student_id": "12345",
        "name": "Test Student",
        "math_score": 85,
        "reading_score": 90,
        "writing_score": 88,
        "timestamp": "2024-01-15T09:30:00Z",
        "grade_level": "9",
        "subject": "Mathematics",
        "attendance_rate": 0.95,
        "assignment_completion_rate": 0.92
    }


@pytest.fixture
def test_buckets(s3_client):
    """Create test S3 buckets."""
    raw_bucket = 'test-raw-bucket'
    processed_bucket = 'test-processed-bucket'
    
    s3_client.create_bucket(Bucket=raw_bucket)
    s3_client.create_bucket(Bucket=processed_bucket)
    
    return {
        'raw': raw_bucket,
        'processed': processed_bucket
    }
