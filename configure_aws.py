#!/usr/bin/env python3
"""
AWS Configuration Helper
Student Insights Pipeline

This script helps configure AWS credentials for the pipeline.
"""

import os
import boto3
from pathlib import Path


def check_existing_credentials():
    """Check if AWS credentials are already configured"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials already configured!")
        print(f"   Account: {identity['Account']}")
        print(f"   Region: {boto3.Session().region_name or 'af-south-1'}")
        return True
    except Exception:
        return False


def configure_credentials_interactive():
    """Interactive AWS credentials configuration"""
    print("🔧 AWS Credentials Configuration")
    print("=" * 40)
    print()
    print("You'll need your AWS Access Key ID and Secret Access Key.")
    print("You can find these in your AWS Console under IAM > Users > Security credentials")
    print()
    
    # Get credentials from user
    access_key = input("Enter your AWS Access Key ID: ").strip()
    if not access_key:
        print("❌ Access Key ID is required")
        return False
    
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    if not secret_key:
        print("❌ Secret Access Key is required")
        return False
    
    region = input("Enter your preferred AWS region (default: af-south-1): ").strip()
    if not region:
        region = "af-south-1"
    
    # Create AWS credentials directory
    aws_dir = Path.home() / ".aws"
    aws_dir.mkdir(exist_ok=True)
    
    # Write credentials file
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    
    try:
        # Write credentials
        with open(credentials_file, 'w') as f:
            f.write("[default]\n")
            f.write(f"aws_access_key_id = {access_key}\n")
            f.write(f"aws_secret_access_key = {secret_key}\n")
        
        # Write config
        with open(config_file, 'w') as f:
            f.write("[default]\n")
            f.write(f"region = {region}\n")
            f.write("output = json\n")
        
        print(f"✅ AWS credentials saved to {credentials_file}")
        print(f"✅ AWS config saved to {config_file}")
        
        # Test the credentials
        print("\n🧪 Testing credentials...")
        if check_existing_credentials():
            print("✅ Credentials are working!")
            return True
        else:
            print("❌ Credentials test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False


def configure_environment_variables():
    """Configure AWS credentials using environment variables"""
    print("🔧 Environment Variables Configuration")
    print("=" * 40)
    print()
    print("You can set AWS credentials as environment variables.")
    print("This is useful for temporary configuration or CI/CD.")
    print()
    
    access_key = input("Enter your AWS Access Key ID: ").strip()
    if not access_key:
        print("❌ Access Key ID is required")
        return False
    
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    if not secret_key:
        print("❌ Secret Access Key is required")
        return False
    
    region = input("Enter your preferred AWS region (default: af-south-1): ").strip()
    if not region:
        region = "af-south-1"
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
    os.environ['AWS_DEFAULT_REGION'] = region
    
    print("\n✅ Environment variables set for this session")
    print("\n📋 To make these permanent, add to your system environment:")
    print(f"   set AWS_ACCESS_KEY_ID={access_key}")
    print(f"   set AWS_SECRET_ACCESS_KEY={secret_key}")
    print(f"   set AWS_DEFAULT_REGION={region}")
    
    # Test the credentials
    print("\n🧪 Testing credentials...")
    if check_existing_credentials():
        print("✅ Credentials are working!")
        return True
    else:
        print("❌ Credentials test failed")
        return False


def main():
    """Main configuration function"""
    print("🚀 Student Insights Pipeline - AWS Configuration")
    print("=" * 50)
    print()
    
    # Check if already configured
    if check_existing_credentials():
        print("\n🎉 AWS is already configured and working!")
        print("\n📋 You can now run:")
        print("   python deploy.py")
        return True
    
    print("❌ AWS credentials not found or not working")
    print()
    print("Choose configuration method:")
    print("1. Credentials file (recommended)")
    print("2. Environment variables (temporary)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if configure_credentials_interactive():
                print("\n🎉 AWS configuration completed!")
                print("\n📋 You can now run:")
                print("   python deploy.py")
                return True
            else:
                print("\n❌ Configuration failed. Please try again.")
                return False
        
        elif choice == "2":
            if configure_environment_variables():
                print("\n🎉 AWS configuration completed!")
                print("\n📋 You can now run:")
                print("   python deploy.py")
                return True
            else:
                print("\n❌ Configuration failed. Please try again.")
                return False
        
        elif choice == "3":
            print("👋 Exiting configuration")
            return False
        
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n📞 Need help?")
        print("1. Check your AWS credentials in the AWS Console")
        print("2. Make sure you have programmatic access enabled")
        print("3. Verify your IAM permissions include CloudFormation, S3, Lambda")
        exit(1)
