# 🚀 How to Run the Student Insights Pipeline

## Quick Start (5 minutes)

### Prerequisites
1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Python 3.9+** installed

### Option 1: One-Click Deploy (Recommended)

**Windows:**
```cmd
run.bat
```

**Mac/Linux:**
```bash
./run.sh
```

**Manual Python:**
```bash
python deploy.py
```

### Option 2: Step-by-Step Deploy

1. **Setup Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure AWS**
```bash
aws configure
# Enter your AWS Access Key ID, Secret, Region (af-south-1), and output format (json)
```

3. **Deploy Infrastructure**
```bash
python deploy.py --environment dev
```

4. **Test Deployment**
```bash
python test_deployment.py
```

## What Gets Deployed

### AWS Resources Created:
- **S3 Buckets**: Raw and processed data storage
- **Lambda Function**: Data ingestion API
- **API Gateway**: REST endpoint for data submission
- **Glue Job**: Data transformation pipeline
- **Athena Database**: Analytics queries
- **IAM Roles**: Secure access permissions

### Estimated Costs:
- **Development**: $2-5/month
- **Production**: $10-20/month
- **Free Tier**: First 10GB of Athena queries free

## Using the Pipeline

### 1. Submit Student Data

**Via API:**
```bash
curl -X POST https://your-api-url/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "12345",
    "name": "John Doe",
    "math_score": 85,
    "reading_score": 90,
    "writing_score": 88,
    "grade_level": "9",
    "subject": "Mathematics",
    "attendance_rate": 0.95,
    "assignment_completion_rate": 0.92
  }'
```

**Via CSV Upload:**
```bash
aws s3 cp your_data.csv s3://your-raw-bucket/raw/date=2024/01/26/hour=10/
```

### 2. Run Analytics Queries

**In AWS Athena Console:**
```sql
-- View all students
SELECT * FROM student_insights_pipeline_database_dev.latest_student_data
WHERE year = '2024'
LIMIT 10;

-- High-risk students
SELECT student_id, name, risk_level, average_score
FROM student_insights_pipeline_database_dev.high_risk_students;

-- Performance summary
SELECT performance_category, COUNT(*) as student_count
FROM student_insights_pipeline_database_dev.latest_student_data
WHERE year = '2024'
GROUP BY performance_category;
```

### 3. Monitor and Optimize

**Check Costs:**
```bash
python scripts/athena-performance-optimizer.py \
  --database student_insights_pipeline_database_dev \
  --action report
```

**Monitor S3 Health:**
```bash
python scripts/monitor-s3-organization.py \
  --bucket your-processed-bucket \
  --output health_report.json
```

## Sample Queries to Try

### Student Performance Analysis
```sql
-- Top 10 performing students
SELECT student_id, name, average_score, performance_category
FROM student_insights_pipeline_database_dev.latest_student_data
WHERE year = '2024'
ORDER BY average_score DESC
LIMIT 10;
```

### Risk Assessment
```sql
-- Students needing immediate intervention
SELECT student_id, name, risk_level, 
       average_score, attendance_rate
FROM student_insights_pipeline_database_dev.high_risk_students
WHERE risk_level = 'High Risk';
```

### Trend Analysis
```sql
-- Monthly performance trends
SELECT year, month, 
       AVG(average_score) as monthly_avg,
       COUNT(*) as student_count
FROM student_insights_pipeline_database_dev.processed_student_data
WHERE year = '2024'
GROUP BY year, month
ORDER BY year, month;
```

### Subject Comparison
```sql
-- Performance by subject
SELECT subject, 
       COUNT(*) as student_count,
       AVG(average_score) as avg_score,
       COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk_count
FROM student_insights_pipeline_database_dev.latest_student_data
WHERE year = '2024'
GROUP BY subject
ORDER BY avg_score DESC;
```

## Troubleshooting

### Common Issues:

**1. AWS Permissions Error**
```bash
# Check your AWS permissions
aws sts get-caller-identity
aws iam get-user
```

**2. CloudFormation Stack Exists**
```bash
# Delete existing stack
aws cloudformation delete-stack --stack-name student-insights-pipeline-dev
```

**3. Lambda Function Timeout**
```bash
# Check Lambda logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/student-insights-ingestion-dev
```

**4. Athena Query Fails**
```bash
# Check query execution
aws athena get-query-execution --query-execution-id YOUR_QUERY_ID
```

### Getting Help:

1. **Check CloudWatch Logs** for detailed error messages
2. **Review AWS Console** for resource status
3. **Run health checks** using provided scripts
4. **Check DEPLOYMENT_GUIDE.md** for detailed troubleshooting

## Next Steps

After successful deployment:

1. **Integrate with your SIS** (Student Information System)
2. **Create custom dashboards** using the analytics queries
3. **Set up automated reporting** schedules
4. **Train educators** on using the insights
5. **Monitor costs** and optimize queries

## File Structure

```
student_insights_pipeline/
├── run.bat / run.sh          # Quick deploy scripts
├── deploy.py                 # Main deployment script
├── test_deployment.py        # Validation tests
├── requirements.txt          # Python dependencies
├── infrastructure/           # CloudFormation templates
├── ingestion/               # Lambda function code
├── transformation/          # Glue job scripts
├── analytics/               # Athena queries
├── scripts/                 # Utility scripts
├── tests/                   # Test suites
└── docs/                    # Documentation
```

## Success Indicators

Your deployment is working when:
- ✅ API endpoint accepts and processes data
- ✅ S3 buckets contain processed Parquet files
- ✅ Athena queries return student data
- ✅ Cost monitoring shows reasonable usage
- ✅ All health checks pass

## Support

For issues or questions:
- Check the troubleshooting section above
- Review CloudWatch logs for detailed errors
- Ensure AWS permissions are correctly configured
- Verify all prerequisites are met

**Happy analyzing! 📊🎓**
