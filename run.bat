@echo off
REM Student Insights Pipeline - Windows Run Script

echo 🚀 Student Insights Pipeline - Quick Deploy
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9 or later.
    pause
    exit /b 1
)

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI is not installed. Please install it first:
    echo https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    pause
    exit /b 1
)

REM Check AWS credentials
echo 🔍 Checking AWS credentials...
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS credentials not configured. Please run 'aws configure' first.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo ✅ AWS credentials configured for account: %ACCOUNT_ID%

REM Set environment (default to dev)
set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=dev
echo 📋 Deploying to environment: %ENVIRONMENT%

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔧 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Check if stack already exists
set STACK_NAME=student-insights-pipeline-%ENVIRONMENT%
aws cloudformation describe-stacks --stack-name %STACK_NAME% >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Stack %STACK_NAME% already exists!
    set /p REPLY="Do you want to update it? (y/N): "
    if /i not "%REPLY%"=="y" (
        echo 🧪 Skipping deployment. Testing existing stack...
        python test_deployment.py %STACK_NAME%
        pause
        exit /b 0
    )
    echo 🔄 Updating existing stack...
) else (
    echo 🆕 Creating new stack...
)

REM Run the deployment
echo 🚀 Starting deployment process...
echo This may take 10-15 minutes...

python deploy.py --environment %ENVIRONMENT% --region af-south-1
if errorlevel 1 (
    echo ❌ Deployment failed! Check the error messages above.
    echo.
    echo 🔧 Troubleshooting tips:
    echo 1. Check AWS permissions (CloudFormation, S3, Lambda, IAM)
    echo 2. Verify AWS CLI is configured correctly
    echo 3. Check if you have sufficient AWS service limits
    echo 4. Review CloudFormation events in AWS console
    echo.
    echo 📞 For help, check the troubleshooting section in DEPLOYMENT_GUIDE.md
    pause
    exit /b 1
)

echo ✅ Deployment completed successfully!

REM Run tests
echo 🧪 Running deployment tests...
python test_deployment.py %STACK_NAME%

REM Get stack outputs for user
echo 📋 Getting deployment information...
aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[*].[OutputKey,OutputValue]" --output table

echo.
echo 🎉 Student Insights Pipeline is ready!
echo.
echo 📖 What you can do now:
echo 1. 📊 Run analytics queries in AWS Athena console
echo 2. 🔗 Test the API endpoint (URL shown above)
echo 3. 📁 Check S3 buckets for processed data
echo 4. 📈 Monitor costs in AWS Billing console
echo.
echo 📚 For detailed usage instructions, see:
echo    - DEPLOYMENT_GUIDE.md
echo    - analytics/athena_queries.sql (sample queries)
echo.

REM Get API URL for sample test
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue" --output text') do set API_URL=%%i
if not "%API_URL%"=="" (
    echo 🔍 Sample API test:
    echo curl -X POST %API_URL%/ingest ^
    echo   -H "Content-Type: application/json" ^
    echo   -d "{\"student_id\":\"test123\",\"name\":\"Test Student\",\"math_score\":85}"
)

echo.
echo Press any key to exit...
pause >nul
