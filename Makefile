# Student Insights Pipeline - Development Makefile

.PHONY: help install install-dev test test-coverage lint format clean deploy package

# Default target
help:
	@echo "Student Insights Pipeline - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean build artifacts"
	@echo ""
	@echo "Deployment:"
	@echo "  validate-cf  - Validate CloudFormation template"
	@echo "  deploy-dev   - Deploy to development environment"
	@echo "  deploy-prod  - Deploy to production environment"
	@echo "  package      - Package Lambda functions"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e .[dev]

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Code Quality
lint:
	flake8 src/ tests/
	black --check src/ tests/

format:
	black src/ tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# CloudFormation
validate-cf:
	aws cloudformation validate-template --template-body file://infrastructure/cloudformation.yaml

# Deployment
deploy-dev:
	aws cloudformation deploy \
		--template-file infrastructure/cloudformation.yaml \
		--stack-name student-insights-pipeline-dev \
		--parameter-overrides Environment=dev \
		--capabilities CAPABILITY_NAMED_IAM \
		--region af-south-1

deploy-prod:
	aws cloudformation deploy \
		--template-file infrastructure/cloudformation.yaml \
		--stack-name student-insights-pipeline-prod \
		--parameter-overrides Environment=prod \
		--capabilities CAPABILITY_NAMED_IAM \
		--region af-south-1

# Package Lambda functions
package:
	mkdir -p build/
	cd ingestion && zip -r ../build/ingestion-lambda.zip . -x "*.pyc" "__pycache__/*"
	cd transformation && zip -r ../build/transformation-lambda.zip . -x "*.pyc" "__pycache__/*"

# Local development with LocalStack
localstack-start:
	docker run --rm -it -p 4566:4566 -p 4571:4571 localstack/localstack

# Data operations
upload-sample-data:
	aws s3 cp data/sample_student_data.csv s3://$(RAW_BUCKET_NAME)/raw/sample_data.csv

# Environment setup
setup-env:
	@echo "Setting up environment variables..."
	@echo "Please set the following environment variables:"
	@echo "export RAW_BUCKET_NAME=your-raw-bucket-name"
	@echo "export PROCESSED_BUCKET_NAME=your-processed-bucket-name"
	@echo "export ATHENA_DATABASE=your-athena-database"
	@echo "export ATHENA_WORKGROUP=your-athena-workgroup"
