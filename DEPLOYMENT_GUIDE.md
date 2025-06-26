# Student Insights Pipeline - Deployment Guide

## 🚀 Quick Start Deployment

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.9+ installed
- Git (for cloning the repository)

### Step 1: Environment Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd student_insights_pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: AWS Configuration

```bash
# Configure AWS CLI (if not already done)
aws configure

# Verify AWS access
aws sts get-caller-identity
```

### Step 3: Deploy Infrastructure

```bash
# Deploy CloudFormation stack
aws cloudformation deploy \
    --template-file infrastructure/cloudformation.yaml \
    --stack-name student-insights-pipeline-dev \
    --parameter-overrides Environment=dev \
    --capabilities CAPABILITY_NAMED_IAM \
    --region us-east-1

# Wait for deployment to complete (5-10 minutes)
aws cloudformation wait stack-create-complete \
    --stack-name student-insights-pipeline-dev
```

### Step 4: Get Stack Outputs

```bash
# Get important outputs from CloudFormation
aws cloudformation describe-stacks \
    --stack-name student-insights-pipeline-dev \
    --query 'Stacks[0].Outputs' \
    --output table
```

### Step 5: Setup Environment Variables

```bash
# Create .env file from template
cp .env.example .env

# Edit .env with your actual values from CloudFormation outputs
# RAW_BUCKET_NAME=student-insights-pipeline-raw-data-dev-123456789012
# PROCESSED_BUCKET_NAME=student-insights-pipeline-processed-data-dev-123456789012
# ATHENA_DATABASE=student_insights_pipeline_database_dev
```

### Step 6: Setup Athena Tables

```bash
# Run Athena table setup
python scripts/athena-table-manager.py \
    --database student_insights_pipeline_database_dev \
    --action setup
```

### Step 7: Upload Sample Data

```bash
# Upload sample data to trigger the pipeline
aws s3 cp data/sample_student_data.csv \
    s3://your-raw-bucket-name/raw/date=2024/01/26/hour=10/sample_data.csv
```

### Step 8: Verify Deployment

```bash
# Check table health
python scripts/athena-table-manager.py \
    --database student_insights_pipeline_database_dev \
    --action health-check
```

## 🔧 Manual Testing

### Test Data Ingestion API

```bash
# Test the Lambda ingestion endpoint
curl -X POST https://your-api-gateway-url/dev/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test123",
    "name": "Test Student",
    "math_score": 85,
    "reading_score": 90,
    "writing_score": 88,
    "grade_level": "9",
    "subject": "Mathematics",
    "attendance_rate": 0.95,
    "assignment_completion_rate": 0.92
  }'
```

### Test Athena Queries

```sql
-- Test basic query in Athena console
SELECT COUNT(*) as total_records
FROM student_insights_pipeline_database_dev.processed_student_data
WHERE year = '2024';
```

## 📊 Running Analytics

### Execute Sample Queries

```bash
# Run performance analysis
aws athena start-query-execution \
    --query-string "SELECT performance_category, COUNT(*) as student_count FROM student_insights_pipeline_database_dev.latest_student_data WHERE year = '2024' GROUP BY performance_category" \
    --result-configuration OutputLocation=s3://your-processed-bucket/athena-results/ \
    --query-execution-context Database=student_insights_pipeline_database_dev
```

### Generate Reports

```bash
# Generate performance report
python scripts/athena-performance-optimizer.py \
    --database student_insights_pipeline_database_dev \
    --action report \
    --output performance_report.json
```

## 🔍 Monitoring and Troubleshooting

### Check CloudWatch Logs

```bash
# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/student-insights

# View recent log events
aws logs filter-log-events \
    --log-group-name /aws/lambda/student-insights-ingestion-dev \
    --start-time $(date -d '1 hour ago' +%s)000
```

### Monitor Costs

```bash
# Check S3 storage costs
aws s3api list-objects-v2 \
    --bucket your-raw-bucket-name \
    --query 'sum(Contents[].Size)' \
    --output text

# Monitor Athena query costs
python scripts/athena-performance-optimizer.py \
    --database student_insights_pipeline_database_dev \
    --action analyze
```

## 🧪 Running Tests

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_data_quality.py -v
pytest tests/test_athena_setup.py -v
pytest tests/test_athena_performance.py -v
```

### Integration Tests

```bash
# Test complete pipeline
python tests/integration_test.py
```

## 📈 Performance Optimization

### Setup S3 Lifecycle Policies

```bash
# Setup lifecycle management
python scripts/setup-s3-lifecycle.py \
    --environment dev \
    --account-id $(aws sts get-caller-identity --query Account --output text)
```

### Monitor S3 Organization

```bash
# Check S3 data organization health
python scripts/monitor-s3-organization.py \
    --environment dev \
    --bucket your-processed-bucket-name \
    --output s3_health_report.json
```

## 🔄 Data Pipeline Operations

### Manual Glue Job Execution

```bash
# Trigger Glue transformation job manually
aws glue start-job-run \
    --job-name student-insights-transformation-dev
```

### Check Pipeline Status

```bash
# Check recent Glue job runs
aws glue get-job-runs \
    --job-name student-insights-transformation-dev \
    --max-items 5
```

## 🚨 Troubleshooting Common Issues

### Issue 1: CloudFormation Deployment Fails

```bash
# Check stack events for errors
aws cloudformation describe-stack-events \
    --stack-name student-insights-pipeline-dev \
    --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

### Issue 2: Lambda Function Errors

```bash
# Check Lambda function configuration
aws lambda get-function \
    --function-name student-insights-ingestion-dev

# Test Lambda function directly
aws lambda invoke \
    --function-name student-insights-ingestion-dev \
    --payload '{"body": "{\"student_id\":\"test\",\"name\":\"Test\"}"}' \
    response.json
```

### Issue 3: Athena Query Failures

```bash
# Check query execution details
aws athena get-query-execution \
    --query-execution-id your-query-execution-id
```

### Issue 4: S3 Access Issues

```bash
# Check bucket permissions
aws s3api get-bucket-policy \
    --bucket your-bucket-name

# Test S3 access
aws s3 ls s3://your-bucket-name/
```

## 🔧 Maintenance Operations

### Update Lambda Code

```bash
# Package and update Lambda function
cd ingestion
zip -r ../ingestion-lambda.zip .
aws lambda update-function-code \
    --function-name student-insights-ingestion-dev \
    --zip-file fileb://../ingestion-lambda.zip
```

### Update Glue Job

```bash
# Update Glue job script
aws s3 cp transformation/glue_job_script.py \
    s3://your-processed-bucket/scripts/

aws glue update-job \
    --job-name student-insights-transformation-dev \
    --job-update ScriptLocation=s3://your-processed-bucket/scripts/glue_job_script.py
```

## 📊 Sample Queries to Try

### Student Performance Analysis

```sql
-- Top performing students
SELECT student_id, name, average_score, performance_category
FROM student_insights_pipeline_database_dev.latest_student_data
WHERE year = '2024'
ORDER BY average_score DESC
LIMIT 10;
```

### Risk Assessment

```sql
-- High-risk students needing intervention
SELECT student_id, name, risk_level, average_score, attendance_rate
FROM student_insights_pipeline_database_dev.high_risk_students
WHERE grade_level = '9';
```

### Performance Trends

```sql
-- Monthly performance trends
SELECT year, month, AVG(average_score) as monthly_avg
FROM student_insights_pipeline_database_dev.processed_student_data
WHERE year = '2024'
GROUP BY year, month
ORDER BY year, month;
```

## 🎯 Success Criteria

Your deployment is successful when:

- [ ] CloudFormation stack deploys without errors
- [ ] Lambda function processes sample data successfully
- [ ] Glue job transforms data to Parquet format
- [ ] Athena queries return expected results
- [ ] S3 buckets contain processed data
- [ ] Cost monitoring shows reasonable usage
- [ ] All tests pass successfully

## 📞 Support

If you encounter issues:

1. Check CloudWatch logs for detailed error messages
2. Verify IAM permissions are correctly configured
3. Ensure all environment variables are set correctly
4. Review the troubleshooting section above
5. Run the health check scripts to identify issues

## 🔄 Next Steps

After successful deployment:

1. Set up automated data ingestion from your student information system
2. Create custom dashboards using the analytics queries
3. Implement automated reporting schedules
4. Set up monitoring and alerting for production use
5. Train educators on using the analytics insights
