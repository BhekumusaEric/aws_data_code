#!/usr/bin/env python3
"""
S3 Lifecycle Management Setup Script
Student Insights Pipeline

This script sets up lifecycle policies for optimal cost management
and data organization in the Student Insights Pipeline S3 buckets.
"""

import boto3
import json
import logging
from typing import Dict, List
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3LifecycleManager:
    """Manages S3 lifecycle policies for the Student Insights Pipeline"""
    
    def __init__(self, environment: str = 'dev'):
        self.s3_client = boto3.client('s3')
        self.environment = environment
        
    def get_bucket_names(self, account_id: str) -> Dict[str, str]:
        """Get bucket names for the environment"""
        return {
            'raw': f'student-insights-pipeline-raw-data-{self.environment}-{account_id}',
            'processed': f'student-insights-pipeline-processed-data-{self.environment}-{account_id}'
        }
    
    def create_raw_data_lifecycle_policy(self) -> Dict:
        """
        Create lifecycle policy for raw data bucket
        
        Strategy:
        - Keep in Standard for 30 days (active processing)
        - Move to IA after 30 days (occasional access)
        - Move to Glacier after 90 days (archive)
        - Delete after 2 years (compliance)
        """
        return {
            'Rules': [
                {
                    'ID': 'RawDataLifecycle',
                    'Status': 'Enabled',
                    'Filter': {
                        'Prefix': 'raw/'
                    },
                    'Transitions': [
                        {
                            'Days': 30,
                            'StorageClass': 'STANDARD_IA'
                        },
                        {
                            'Days': 90,
                            'StorageClass': 'GLACIER'
                        },
                        {
                            'Days': 365,
                            'StorageClass': 'DEEP_ARCHIVE'
                        }
                    ],
                    'Expiration': {
                        'Days': 730  # 2 years
                    }
                },
                {
                    'ID': 'IncompleteMultipartUploads',
                    'Status': 'Enabled',
                    'Filter': {},
                    'AbortIncompleteMultipartUpload': {
                        'DaysAfterInitiation': 7
                    }
                }
            ]
        }
    
    def create_processed_data_lifecycle_policy(self) -> Dict:
        """
        Create lifecycle policy for processed data bucket
        
        Strategy:
        - Keep in Standard for 1 year (active analytics)
        - Move to IA after 1 year (historical analysis)
        - Move to Glacier after 3 years (long-term archive)
        - Keep indefinitely for compliance
        """
        return {
            'Rules': [
                {
                    'ID': 'ProcessedDataLifecycle',
                    'Status': 'Enabled',
                    'Filter': {
                        'Prefix': 'processed/'
                    },
                    'Transitions': [
                        {
                            'Days': 365,
                            'StorageClass': 'STANDARD_IA'
                        },
                        {
                            'Days': 1095,  # 3 years
                            'StorageClass': 'GLACIER'
                        },
                        {
                            'Days': 2555,  # 7 years
                            'StorageClass': 'DEEP_ARCHIVE'
                        }
                    ]
                },
                {
                    'ID': 'QualityReportsLifecycle',
                    'Status': 'Enabled',
                    'Filter': {
                        'Prefix': 'quality-reports/'
                    },
                    'Transitions': [
                        {
                            'Days': 90,
                            'StorageClass': 'STANDARD_IA'
                        },
                        {
                            'Days': 365,
                            'StorageClass': 'GLACIER'
                        }
                    ]
                },
                {
                    'ID': 'AthenaResultsCleanup',
                    'Status': 'Enabled',
                    'Filter': {
                        'Prefix': 'athena-results/temp/'
                    },
                    'Expiration': {
                        'Days': 30  # Clean up temporary query results
                    }
                },
                {
                    'ID': 'IncompleteMultipartUploads',
                    'Status': 'Enabled',
                    'Filter': {},
                    'AbortIncompleteMultipartUpload': {
                        'DaysAfterInitiation': 7
                    }
                }
            ]
        }
    
    def apply_lifecycle_policy(self, bucket_name: str, policy: Dict) -> bool:
        """
        Apply lifecycle policy to a bucket
        
        Args:
            bucket_name: S3 bucket name
            policy: Lifecycle policy configuration
            
        Returns:
            Success status
        """
        try:
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=policy
            )
            logger.info(f"Successfully applied lifecycle policy to {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply lifecycle policy to {bucket_name}: {str(e)}")
            return False
    
    def verify_lifecycle_policy(self, bucket_name: str) -> Dict:
        """
        Verify lifecycle policy is applied correctly
        
        Args:
            bucket_name: S3 bucket name
            
        Returns:
            Current lifecycle configuration
        """
        try:
            response = self.s3_client.get_bucket_lifecycle_configuration(
                Bucket=bucket_name
            )
            logger.info(f"Lifecycle policy verified for {bucket_name}")
            return response.get('Rules', [])
            
        except Exception as e:
            logger.error(f"Failed to verify lifecycle policy for {bucket_name}: {str(e)}")
            return {}
    
    def setup_all_policies(self, account_id: str) -> bool:
        """
        Set up lifecycle policies for all buckets
        
        Args:
            account_id: AWS account ID
            
        Returns:
            Success status
        """
        buckets = self.get_bucket_names(account_id)
        success = True
        
        # Apply raw data lifecycle policy
        raw_policy = self.create_raw_data_lifecycle_policy()
        if not self.apply_lifecycle_policy(buckets['raw'], raw_policy):
            success = False
        
        # Apply processed data lifecycle policy
        processed_policy = self.create_processed_data_lifecycle_policy()
        if not self.apply_lifecycle_policy(buckets['processed'], processed_policy):
            success = False
        
        return success
    
    def generate_cost_estimate(self, data_volume_gb_per_month: float = 10) -> Dict:
        """
        Generate cost estimate based on lifecycle policies
        
        Args:
            data_volume_gb_per_month: Expected data volume in GB per month
            
        Returns:
            Cost breakdown by storage class
        """
        # AWS S3 pricing (af-south-1, approximate)
        pricing = {
            'STANDARD': 0.023,  # per GB/month
            'STANDARD_IA': 0.0125,
            'GLACIER': 0.004,
            'DEEP_ARCHIVE': 0.00099
        }
        
        # Calculate cumulative storage over time
        monthly_costs = []
        cumulative_gb = 0
        
        for month in range(1, 25):  # 2 years
            cumulative_gb += data_volume_gb_per_month
            
            # Determine storage class distribution based on age
            standard_gb = min(cumulative_gb, data_volume_gb_per_month * 1)  # Last month
            ia_gb = min(cumulative_gb - standard_gb, data_volume_gb_per_month * 2)  # Months 2-3
            glacier_gb = min(cumulative_gb - standard_gb - ia_gb, data_volume_gb_per_month * 9)  # Months 4-12
            deep_archive_gb = max(0, cumulative_gb - standard_gb - ia_gb - glacier_gb)  # 12+ months
            
            monthly_cost = (
                standard_gb * pricing['STANDARD'] +
                ia_gb * pricing['STANDARD_IA'] +
                glacier_gb * pricing['GLACIER'] +
                deep_archive_gb * pricing['DEEP_ARCHIVE']
            )
            
            monthly_costs.append({
                'month': month,
                'total_gb': cumulative_gb,
                'standard_gb': standard_gb,
                'ia_gb': ia_gb,
                'glacier_gb': glacier_gb,
                'deep_archive_gb': deep_archive_gb,
                'monthly_cost': monthly_cost
            })
        
        return {
            'monthly_breakdown': monthly_costs,
            'year_1_total': sum(m['monthly_cost'] for m in monthly_costs[:12]),
            'year_2_total': sum(m['monthly_cost'] for m in monthly_costs[12:24]),
            'pricing_assumptions': pricing
        }


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Setup S3 lifecycle policies')
    parser.add_argument('--environment', default='dev', help='Environment (dev/staging/prod)')
    parser.add_argument('--account-id', required=True, help='AWS Account ID')
    parser.add_argument('--dry-run', action='store_true', help='Show policies without applying')
    parser.add_argument('--cost-estimate', action='store_true', help='Generate cost estimate')
    
    args = parser.parse_args()
    
    manager = S3LifecycleManager(args.environment)
    
    if args.cost_estimate:
        estimate = manager.generate_cost_estimate()
        print("\n=== Cost Estimate ===")
        print(f"Year 1 Total: ${estimate['year_1_total']:.2f}")
        print(f"Year 2 Total: ${estimate['year_2_total']:.2f}")
        return
    
    if args.dry_run:
        print("\n=== Raw Data Lifecycle Policy ===")
        print(json.dumps(manager.create_raw_data_lifecycle_policy(), indent=2))
        print("\n=== Processed Data Lifecycle Policy ===")
        print(json.dumps(manager.create_processed_data_lifecycle_policy(), indent=2))
        return
    
    # Apply policies
    success = manager.setup_all_policies(args.account_id)
    
    if success:
        logger.info("All lifecycle policies applied successfully")
    else:
        logger.error("Some lifecycle policies failed to apply")
        exit(1)


if __name__ == "__main__":
    main()
