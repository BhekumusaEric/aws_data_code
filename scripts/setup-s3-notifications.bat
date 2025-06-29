@echo off
REM Setup S3 Bucket Notifications for Student Insights Pipeline
REM Run this script AFTER CloudFormation stack deployment

echo 🔧 Setting up S3 bucket notifications for Student Insights Pipeline
echo ==================================================

REM Configuration
set STACK_NAME=student-insights-pipeline-dev
set REGION=af-south-1
set CONFIG_FILE=infrastructure\s3-notification-config.json

REM Check if AWS CLI is configured
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI not configured. Please run 'aws configure' first.
    pause
    exit /b 1
)

echo ✅ AWS CLI configured

REM Get stack outputs
echo 📋 Getting CloudFormation stack outputs...

for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %REGION% --query "Stacks[0].Outputs[?OutputKey==`RawDataBucketName`].OutputValue" --output text') do set RAW_BUCKET=%%i

for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %REGION% --query "Stacks[0].Outputs[?OutputKey==`DataProcessingLambdaArn`].OutputValue" --output text') do set LAMBDA_ARN=%%i

if "%RAW_BUCKET%"=="" (
    echo ❌ Could not retrieve raw bucket name from stack outputs.
    echo    Stack name: %STACK_NAME%
    echo    Region: %REGION%
    pause
    exit /b 1
)

if "%LAMBDA_ARN%"=="" (
    echo ❌ Could not retrieve Lambda ARN from stack outputs.
    echo    Stack name: %STACK_NAME%
    echo    Region: %REGION%
    pause
    exit /b 1
)

echo ✅ Retrieved stack outputs:
echo    Raw Bucket: %RAW_BUCKET%
echo    Lambda ARN: %LAMBDA_ARN%

REM Create temporary notification config with actual values
set TEMP_CONFIG=%TEMP%\s3-notification-config-temp.json

REM Use PowerShell to replace the placeholder
powershell -Command "(Get-Content '%CONFIG_FILE%') -replace 'arn:aws:lambda:af-south-1:986831602518:function:student-insights-pipeline-data-processing-dev', '%LAMBDA_ARN%' | Set-Content '%TEMP_CONFIG%'"

echo 📝 Created notification configuration

REM Apply the notification configuration
echo 🚀 Applying S3 bucket notification configuration...

aws s3api put-bucket-notification-configuration --bucket %RAW_BUCKET% --notification-configuration file://%TEMP_CONFIG% --region %REGION%

if errorlevel 1 (
    echo ❌ Failed to configure S3 bucket notifications
    pause
    exit /b 1
)

echo ✅ S3 bucket notifications configured successfully!
echo.
echo 📊 Configuration Summary:
echo    • Bucket: %RAW_BUCKET%
echo    • Trigger: s3:ObjectCreated:* events
echo    • Filter: Files in 'raw/' prefix with '.csv' suffix
echo    • Action: Invoke Lambda function for data processing
echo.
echo 🧪 Test the setup by uploading a CSV file to s3://%RAW_BUCKET%/raw/

REM Cleanup
del "%TEMP_CONFIG%" 2>nul

echo 🎉 Setup complete! Your data pipeline is ready to process files.
pause
