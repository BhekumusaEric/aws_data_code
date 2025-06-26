#!/usr/bin/env python3
"""
Student Insights Pipeline - Quick Start
One-click setup and deployment
"""

import subprocess
import sys
import os


def print_header():
    """Print welcome header"""
    print("🚀 Student Insights Pipeline - Quick Start")
    print("=" * 50)
    print()
    print("This script will:")
    print("1. ✅ Check Python dependencies")
    print("2. 🔧 Configure AWS credentials")
    print("3. 🚀 Deploy the complete pipeline")
    print("4. 🧪 Test the deployment")
    print()


def check_dependencies():
    """Check and install required dependencies"""
    print("📦 Checking Python dependencies...")
    
    required_packages = ['boto3', 'requests', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--user'
            ] + missing_packages, check=True)
            print("✅ All dependencies installed!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True


def configure_aws():
    """Configure AWS credentials"""
    print("\n🔧 Configuring AWS credentials...")
    
    # Check if already configured
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials already configured for account: {identity['Account']}")
        return True
    except Exception:
        print("❌ AWS credentials not configured")
        
        # Run the AWS configuration script
        try:
            result = subprocess.run([sys.executable, 'configure_aws.py'], 
                                  capture_output=False, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running AWS configuration: {e}")
            return False


def deploy_pipeline():
    """Deploy the pipeline"""
    print("\n🚀 Deploying Student Insights Pipeline...")
    print("This may take 10-15 minutes...")
    print()
    
    try:
        result = subprocess.run([sys.executable, 'deploy.py', '--environment', 'dev'], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False


def test_deployment():
    """Test the deployment"""
    print("\n🧪 Testing deployment...")
    
    try:
        result = subprocess.run([sys.executable, 'test_deployment.py'], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


def main():
    """Main quick start function"""
    print_header()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Step 2: Configure AWS
    if not configure_aws():
        print("❌ Failed to configure AWS credentials")
        return False
    
    # Step 3: Deploy pipeline
    if not deploy_pipeline():
        print("❌ Failed to deploy pipeline")
        return False
    
    # Step 4: Test deployment
    if not test_deployment():
        print("⚠️ Deployment completed but some tests failed")
        print("The pipeline may still be functional")
    
    # Success!
    print("\n🎉 Student Insights Pipeline is ready!")
    print()
    print("📋 What you can do now:")
    print("1. 📊 Run analytics queries in AWS Athena console")
    print("2. 🔗 Test the API endpoint")
    print("3. 📁 Check S3 buckets for processed data")
    print("4. 📈 Monitor costs in AWS Billing console")
    print()
    print("📚 For detailed usage instructions, see:")
    print("   - RUN_INSTRUCTIONS.md")
    print("   - analytics/athena_queries.sql (sample queries)")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("✅ Quick start completed successfully!")
        else:
            print("❌ Quick start failed. Check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Quick start cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
