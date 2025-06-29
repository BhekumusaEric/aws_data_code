#!/bin/bash
# Setup S3 Bucket Notifications for Student Insights Pipeline
# Run this script AFTER CloudFormation stack deployment

set -e

# Configuration
STACK_NAME="student-insights-pipeline-dev"
REGION="af-south-1"
CONFIG_FILE="infrastructure/s3-notification-config.json"

echo "🔧 Setting up S3 bucket notifications for Student Insights Pipeline"
echo "=================================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Get stack outputs
echo "📋 Getting CloudFormation stack outputs..."

RAW_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`RawDataBucketName`].OutputValue' \
    --output text)

LAMBDA_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`DataProcessingLambdaArn`].OutputValue' \
    --output text)

if [ -z "$RAW_BUCKET" ] || [ -z "$LAMBDA_ARN" ]; then
    echo "❌ Could not retrieve stack outputs. Make sure the stack is deployed successfully."
    echo "   Stack name: $STACK_NAME"
    echo "   Region: $REGION"
    exit 1
fi

echo "✅ Retrieved stack outputs:"
echo "   Raw Bucket: $RAW_BUCKET"
echo "   Lambda ARN: $LAMBDA_ARN"

# Create temporary notification config with actual values
TEMP_CONFIG="/tmp/s3-notification-config-temp.json"
sed "s|REPLACE_WITH_LAMBDA_ARN|$LAMBDA_ARN|g" $CONFIG_FILE > $TEMP_CONFIG

echo "📝 Created notification configuration:"
cat $TEMP_CONFIG

# Apply the notification configuration
echo "🚀 Applying S3 bucket notification configuration..."

aws s3api put-bucket-notification-configuration \
    --bucket $RAW_BUCKET \
    --notification-configuration file://$TEMP_CONFIG \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ S3 bucket notifications configured successfully!"
    echo ""
    echo "📊 Configuration Summary:"
    echo "   • Bucket: $RAW_BUCKET"
    echo "   • Trigger: s3:ObjectCreated:* events"
    echo "   • Filter: Files in 'raw/' prefix with '.csv' suffix"
    echo "   • Action: Invoke Lambda function for data processing"
    echo ""
    echo "🧪 Test the setup by uploading a CSV file to s3://$RAW_BUCKET/raw/"
else
    echo "❌ Failed to configure S3 bucket notifications"
    exit 1
fi

# Cleanup
rm -f $TEMP_CONFIG

echo "🎉 Setup complete! Your data pipeline is ready to process files."
