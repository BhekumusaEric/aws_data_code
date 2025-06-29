# S3 Bucket Notifications Setup Guide

## 📋 **Overview**

After deploying the CloudFormation stack, you need to manually configure S3 bucket notifications to trigger Lambda functions when new data files are uploaded. This is required because CloudFormation had a circular dependency issue that was resolved by removing the notification configuration from the template.

## 📁 **Files Created**

### **1. Configuration File**
- **Location**: `infrastructure/s3-notification-config.json`
- **Purpose**: JSON configuration for S3 bucket notifications
- **Content**: Defines Lambda trigger for CSV files in the `raw/` prefix

### **2. Setup Scripts**
- **Linux/Mac**: `scripts/setup-s3-notifications.sh`
- **Windows**: `scripts/setup-s3-notifications.bat`
- **Purpose**: Automated setup of S3 notifications after stack deployment

## 🚀 **Quick Setup (Recommended)**

### **Step 1: Deploy CloudFormation Stack**
```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation.yaml \
  --stack-name student-insights-pipeline-dev \
  --parameter-overrides Environment=dev \
  --capabilities CAPABILITY_NAMED_IAM \
  --region af-south-1
```

### **Step 2: Run Notification Setup Script**

**Linux/Mac:**
```bash
chmod +x scripts/setup-s3-notifications.sh
./scripts/setup-s3-notifications.sh
```

**Windows:**
```cmd
scripts\setup-s3-notifications.bat
```

## 🔧 **Manual Setup (Alternative)**

If you prefer to set up notifications manually:

### **Step 1: Get Stack Outputs**
```bash
# Get raw bucket name
RAW_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name student-insights-pipeline-dev \
  --region af-south-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`RawDataBucketName`].OutputValue' \
  --output text)

# Get Lambda ARN
LAMBDA_ARN=$(aws cloudformation describe-stacks \
  --stack-name student-insights-pipeline-dev \
  --region af-south-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`DataProcessingLambdaArn`].OutputValue' \
  --output text)

echo "Bucket: $RAW_BUCKET"
echo "Lambda: $LAMBDA_ARN"
```

### **Step 2: Update Configuration File**
Edit `infrastructure/s3-notification-config.json` and replace `REPLACE_WITH_LAMBDA_ARN` with your actual Lambda ARN.

### **Step 3: Apply Configuration**
```bash
aws s3api put-bucket-notification-configuration \
  --bucket $RAW_BUCKET \
  --notification-configuration file://infrastructure/s3-notification-config.json \
  --region af-south-1
```

## 📊 **Configuration Details**

### **Trigger Configuration**
```json
{
  "LambdaConfigurations": [
    {
      "Id": "ProcessRawDataFiles",
      "LambdaFunctionArn": "arn:aws:lambda:af-south-1:123456789012:function:student-insights-pipeline-data-processing-dev",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "raw/"
            },
            {
              "Name": "suffix", 
              "Value": ".csv"
            }
          ]
        }
      }
    }
  ]
}
```

### **What This Does**
- **Triggers**: When any file is created in the S3 bucket
- **Filter**: Only files in the `raw/` folder with `.csv` extension
- **Action**: Invokes the data processing Lambda function
- **Event Types**: All object creation events (PUT, POST, COPY, multipart upload completion)

## 🧪 **Testing the Setup**

### **Step 1: Upload Test File**
```bash
# Create a test CSV file
echo "student_id,name,math_score,reading_score,writing_score,grade_level,subject" > test-data.csv
echo "STU001,John Doe,85,78,82,10,Mathematics" >> test-data.csv

# Upload to trigger the Lambda
aws s3 cp test-data.csv s3://$RAW_BUCKET/raw/test-data.csv
```

### **Step 2: Check Lambda Logs**
```bash
# Get recent log events
aws logs describe-log-streams \
  --log-group-name "/aws/lambda/student-insights-pipeline-data-processing-dev" \
  --order-by LastEventTime \
  --descending \
  --max-items 1 \
  --region af-south-1

# View logs (replace LOG_STREAM_NAME with actual value)
aws logs get-log-events \
  --log-group-name "/aws/lambda/student-insights-pipeline-data-processing-dev" \
  --log-stream-name "LOG_STREAM_NAME" \
  --region af-south-1
```

## ❗ **Troubleshooting**

### **Common Issues**

#### **1. Permission Denied**
```
Error: Access Denied
```
**Solution**: Ensure your AWS credentials have `s3:PutBucketNotification` permission.

#### **2. Lambda Not Found**
```
Error: Unable to validate the following destination configurations
```
**Solution**: Verify the Lambda ARN is correct and the function exists.

#### **3. Stack Outputs Not Found**
```
Error: Could not retrieve stack outputs
```
**Solution**: Ensure the CloudFormation stack deployed successfully and the stack name is correct.

### **Verification Commands**
```bash
# Check if notifications are configured
aws s3api get-bucket-notification-configuration \
  --bucket $RAW_BUCKET \
  --region af-south-1

# List Lambda functions
aws lambda list-functions \
  --region af-south-1 \
  --query 'Functions[?contains(FunctionName, `student-insights`)].FunctionName'
```

## 🎯 **Next Steps**

After setting up S3 notifications:

1. **Upload Sample Data**: Test with real CSV files
2. **Monitor Lambda Execution**: Check CloudWatch logs
3. **Verify Data Processing**: Confirm processed data appears in the processed bucket
4. **Set Up Athena Queries**: Query the processed data using Athena
5. **Configure Dashboards**: Set up monitoring and alerting

## 📚 **Related Files**

- `infrastructure/cloudformation.yaml` - Main infrastructure template
- `infrastructure/s3-notification-config.json` - S3 notification configuration
- `scripts/setup-s3-notifications.sh` - Linux/Mac setup script
- `scripts/setup-s3-notifications.bat` - Windows setup script
- `CLOUDFORMATION_FIXES.md` - Details about template fixes

**Your S3 bucket notifications are now ready to trigger data processing automatically!** 🎉
