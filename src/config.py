"""
Configuration management for Student Insights Pipeline
"""

import os
from typing import Optional


class Config:
    """Configuration class for the Student Insights Pipeline"""
    
    # AWS Configuration
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    
    # S3 Bucket Configuration
    RAW_BUCKET_NAME: Optional[str] = os.getenv('RAW_BUCKET_NAME')
    PROCESSED_BUCKET_NAME: Optional[str] = os.getenv('PROCESSED_BUCKET_NAME')
    
    # Lambda Configuration
    LAMBDA_TIMEOUT: int = int(os.getenv('LAMBDA_TIMEOUT', '300'))
    LAMBDA_MEMORY_SIZE: int = int(os.getenv('LAMBDA_MEMORY_SIZE', '512'))
    
    # Data Processing Configuration
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '100'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    
    # Athena Configuration
    ATHENA_DATABASE: Optional[str] = os.getenv('ATHENA_DATABASE')
    ATHENA_WORKGROUP: Optional[str] = os.getenv('ATHENA_WORKGROUP')
    ATHENA_OUTPUT_LOCATION: Optional[str] = os.getenv('ATHENA_OUTPUT_LOCATION')
    
    # Environment
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'dev')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        required_vars = [
            'RAW_BUCKET_NAME',
            'PROCESSED_BUCKET_NAME',
            'ATHENA_DATABASE',
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True


# Development/Testing Configuration
class DevConfig(Config):
    """Development configuration"""
    ENVIRONMENT = 'dev'
    LOG_LEVEL = 'DEBUG'


# Production Configuration  
class ProdConfig(Config):
    """Production configuration"""
    ENVIRONMENT = 'prod'
    LOG_LEVEL = 'INFO'


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv('ENVIRONMENT', 'dev').lower()
    
    if env == 'prod':
        return ProdConfig()
    else:
        return DevConfig()
