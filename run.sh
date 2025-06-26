#!/bin/bash

# Student Insights Pipeline - Quick Run Script
# This script sets up and deploys the complete pipeline

set -e  # Exit on any error

echo "🚀 Student Insights Pipeline - Quick Deploy"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first:"
    echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9 or later."
    exit 1
fi

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region || echo "us-east-1")
print_success "AWS credentials configured for account: $ACCOUNT_ID in region: $REGION"

# Set environment (default to dev)
ENVIRONMENT=${1:-dev}
print_status "Deploying to environment: $ENVIRONMENT"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if stack already exists
STACK_NAME="student-insights-pipeline-$ENVIRONMENT"
if aws cloudformation describe-stacks --stack-name $STACK_NAME &> /dev/null; then
    print_warning "Stack $STACK_NAME already exists!"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Skipping deployment. Testing existing stack..."
        python3 test_deployment.py $STACK_NAME
        exit 0
    fi
    
    print_status "Updating existing stack..."
    UPDATE_MODE=true
else
    print_status "Creating new stack..."
    UPDATE_MODE=false
fi

# Run the deployment
print_status "Starting deployment process..."
echo "This may take 10-15 minutes..."

if python3 deploy.py --environment $ENVIRONMENT --region $REGION; then
    print_success "Deployment completed successfully!"
    
    # Run tests
    print_status "Running deployment tests..."
    if python3 test_deployment.py $STACK_NAME; then
        print_success "All tests passed!"
    else
        print_warning "Some tests failed, but deployment may still be functional."
    fi
    
    # Get stack outputs for user
    print_status "Getting deployment information..."
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
    
    echo ""
    print_success "🎉 Student Insights Pipeline is ready!"
    echo ""
    echo "📖 What you can do now:"
    echo "1. 📊 Run analytics queries in AWS Athena console"
    echo "2. 🔗 Test the API endpoint (URL shown above)"
    echo "3. 📁 Check S3 buckets for processed data"
    echo "4. 📈 Monitor costs in AWS Billing console"
    echo ""
    echo "📚 For detailed usage instructions, see:"
    echo "   - DEPLOYMENT_GUIDE.md"
    echo "   - analytics/athena_queries.sql (sample queries)"
    echo ""
    echo "🔍 Sample API test:"
    API_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' --output text)
    if [ ! -z "$API_URL" ]; then
        echo "curl -X POST $API_URL/ingest \\"
        echo "  -H 'Content-Type: application/json' \\"
        echo "  -d '{\"student_id\":\"test123\",\"name\":\"Test Student\",\"math_score\":85}'"
    fi
    echo ""
    
else
    print_error "Deployment failed! Check the error messages above."
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "1. Check AWS permissions (CloudFormation, S3, Lambda, IAM)"
    echo "2. Verify AWS CLI is configured correctly"
    echo "3. Check if you have sufficient AWS service limits"
    echo "4. Review CloudFormation events in AWS console"
    echo ""
    echo "📞 For help, check the troubleshooting section in DEPLOYMENT_GUIDE.md"
    exit 1
fi

# Cleanup function
cleanup() {
    if [ "$1" = "cleanup" ]; then
        print_status "Cleaning up deployment..."
        read -p "Are you sure you want to delete the stack $STACK_NAME? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Deleting CloudFormation stack..."
            aws cloudformation delete-stack --stack-name $STACK_NAME
            print_status "Stack deletion initiated. Check AWS console for progress."
        fi
    fi
}

# Handle cleanup if requested
if [ "$1" = "cleanup" ]; then
    cleanup cleanup
fi
