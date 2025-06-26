#!/usr/bin/env python3
"""
S3 Data Organization Monitoring Script
Student Insights Pipeline

This script monitors and reports on S3 data organization health,
including partition efficiency, file sizes, and query performance.
"""

import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3OrganizationMonitor:
    """Monitors S3 data organization for the Student Insights Pipeline"""
    
    def __init__(self, environment: str = 'dev'):
        self.s3_client = boto3.client('s3')
        self.cloudwatch = boto3.client('cloudwatch')
        self.environment = environment
        
    def analyze_partition_efficiency(self, bucket_name: str, prefix: str = 'processed/') -> Dict:
        """
        Analyze partition efficiency for processed data
        
        Args:
            bucket_name: S3 bucket name
            prefix: Prefix to analyze
            
        Returns:
            Partition analysis report
        """
        logger.info(f"Analyzing partition efficiency for {bucket_name}/{prefix}")
        
        partition_stats = defaultdict(lambda: {'file_count': 0, 'total_size': 0, 'files': []})
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    size = obj['Size']
                    
                    # Extract partition information
                    if '/year=' in key and '/month=' in key and '/day=' in key:
                        parts = key.split('/')
                        year = next((p.split('=')[1] for p in parts if p.startswith('year=')), 'unknown')
                        month = next((p.split('=')[1] for p in parts if p.startswith('month=')), 'unknown')
                        day = next((p.split('=')[1] for p in parts if p.startswith('day=')), 'unknown')
                        subject = next((p.split('=')[1] for p in parts if p.startswith('subject=')), 'unknown')
                        
                        partition_key = f"{year}/{month}/{day}/{subject}"
                        partition_stats[partition_key]['file_count'] += 1
                        partition_stats[partition_key]['total_size'] += size
                        partition_stats[partition_key]['files'].append({
                            'key': key,
                            'size': size,
                            'size_mb': round(size / (1024 * 1024), 2)
                        })
            
            # Analyze partition health
            analysis = {
                'total_partitions': len(partition_stats),
                'partition_details': {},
                'health_summary': {
                    'optimal_partitions': 0,
                    'small_file_partitions': 0,
                    'large_file_partitions': 0,
                    'empty_partitions': 0
                }
            }
            
            for partition, stats in partition_stats.items():
                avg_file_size_mb = (stats['total_size'] / stats['file_count']) / (1024 * 1024)
                total_size_mb = stats['total_size'] / (1024 * 1024)
                
                # Classify partition health
                if stats['file_count'] == 0:
                    health = 'empty'
                    analysis['health_summary']['empty_partitions'] += 1
                elif avg_file_size_mb < 10:  # Small files
                    health = 'small_files'
                    analysis['health_summary']['small_file_partitions'] += 1
                elif avg_file_size_mb > 1000:  # Very large files
                    health = 'large_files'
                    analysis['health_summary']['large_file_partitions'] += 1
                else:
                    health = 'optimal'
                    analysis['health_summary']['optimal_partitions'] += 1
                
                analysis['partition_details'][partition] = {
                    'file_count': stats['file_count'],
                    'total_size_mb': round(total_size_mb, 2),
                    'avg_file_size_mb': round(avg_file_size_mb, 2),
                    'health': health,
                    'files': stats['files'][:5]  # Sample of files
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing partition efficiency: {str(e)}")
            return {}
    
    def check_file_size_distribution(self, bucket_name: str, prefix: str = 'processed/') -> Dict:
        """
        Check file size distribution for optimization opportunities
        
        Args:
            bucket_name: S3 bucket name
            prefix: Prefix to analyze
            
        Returns:
            File size distribution report
        """
        logger.info(f"Checking file size distribution for {bucket_name}/{prefix}")
        
        size_buckets = {
            'tiny': {'min': 0, 'max': 1, 'count': 0, 'total_size': 0},  # < 1MB
            'small': {'min': 1, 'max': 10, 'count': 0, 'total_size': 0},  # 1-10MB
            'medium': {'min': 10, 'max': 100, 'count': 0, 'total_size': 0},  # 10-100MB
            'large': {'min': 100, 'max': 1000, 'count': 0, 'total_size': 0},  # 100MB-1GB
            'huge': {'min': 1000, 'max': float('inf'), 'count': 0, 'total_size': 0}  # > 1GB
        }
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                for obj in page.get('Contents', []):
                    size_mb = obj['Size'] / (1024 * 1024)
                    
                    for bucket_name, bucket_info in size_buckets.items():
                        if bucket_info['min'] <= size_mb < bucket_info['max']:
                            bucket_info['count'] += 1
                            bucket_info['total_size'] += size_mb
                            break
            
            # Calculate percentages and recommendations
            total_files = sum(bucket['count'] for bucket in size_buckets.values())
            total_size = sum(bucket['total_size'] for bucket in size_buckets.values())
            
            distribution = {}
            for name, bucket in size_buckets.items():
                distribution[name] = {
                    'count': bucket['count'],
                    'percentage': (bucket['count'] / total_files * 100) if total_files > 0 else 0,
                    'total_size_mb': round(bucket['total_size'], 2),
                    'size_percentage': (bucket['total_size'] / total_size * 100) if total_size > 0 else 0
                }
            
            # Generate recommendations
            recommendations = []
            if distribution['tiny']['percentage'] > 20:
                recommendations.append("Consider compacting tiny files (< 1MB) to improve query performance")
            if distribution['small']['percentage'] > 50:
                recommendations.append("High number of small files detected - consider file compaction")
            if distribution['huge']['percentage'] > 5:
                recommendations.append("Large files detected - consider splitting for better parallelism")
            
            return {
                'distribution': distribution,
                'total_files': total_files,
                'total_size_mb': round(total_size, 2),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking file size distribution: {str(e)}")
            return {}
    
    def analyze_query_patterns(self, days_back: int = 7) -> Dict:
        """
        Analyze Athena query patterns to optimize partitioning
        
        Args:
            days_back: Number of days to look back for query analysis
            
        Returns:
            Query pattern analysis
        """
        logger.info(f"Analyzing query patterns for last {days_back} days")
        
        try:
            # This would require CloudTrail integration for full analysis
            # For now, return a template structure
            return {
                'analysis_period': f"Last {days_back} days",
                'common_filters': {
                    'year': {'usage_count': 0, 'efficiency': 'high'},
                    'month': {'usage_count': 0, 'efficiency': 'high'},
                    'day': {'usage_count': 0, 'efficiency': 'medium'},
                    'subject': {'usage_count': 0, 'efficiency': 'high'}
                },
                'partition_pruning_efficiency': 'unknown',
                'recommendations': [
                    "Enable CloudTrail for detailed query pattern analysis",
                    "Monitor Athena query metrics in CloudWatch"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing query patterns: {str(e)}")
            return {}
    
    def generate_optimization_report(self, bucket_name: str) -> Dict:
        """
        Generate comprehensive optimization report
        
        Args:
            bucket_name: S3 bucket name to analyze
            
        Returns:
            Complete optimization report
        """
        logger.info(f"Generating optimization report for {bucket_name}")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'bucket': bucket_name,
            'environment': self.environment,
            'partition_analysis': self.analyze_partition_efficiency(bucket_name),
            'file_size_analysis': self.check_file_size_distribution(bucket_name),
            'query_pattern_analysis': self.analyze_query_patterns(),
            'overall_health': 'unknown',
            'priority_actions': []
        }
        
        # Determine overall health
        partition_health = report['partition_analysis'].get('health_summary', {})
        file_size_analysis = report['file_size_analysis']
        
        health_score = 0
        max_score = 100
        
        # Partition health scoring (40 points)
        if partition_health:
            optimal_ratio = partition_health.get('optimal_partitions', 0) / max(partition_health.get('total_partitions', 1), 1)
            health_score += optimal_ratio * 40
        
        # File size health scoring (40 points)
        if file_size_analysis:
            tiny_ratio = file_size_analysis['distribution'].get('tiny', {}).get('percentage', 0) / 100
            small_ratio = file_size_analysis['distribution'].get('small', {}).get('percentage', 0) / 100
            health_score += max(0, 40 - (tiny_ratio * 20 + small_ratio * 10))
        
        # Query efficiency scoring (20 points) - placeholder
        health_score += 15  # Assume reasonable efficiency
        
        # Determine health level
        if health_score >= 80:
            report['overall_health'] = 'excellent'
        elif health_score >= 60:
            report['overall_health'] = 'good'
        elif health_score >= 40:
            report['overall_health'] = 'fair'
        else:
            report['overall_health'] = 'poor'
        
        # Generate priority actions
        if file_size_analysis.get('recommendations'):
            report['priority_actions'].extend(file_size_analysis['recommendations'])
        
        if partition_health.get('small_file_partitions', 0) > 0:
            report['priority_actions'].append(f"Compact {partition_health['small_file_partitions']} partitions with small files")
        
        return report


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Monitor S3 data organization')
    parser.add_argument('--environment', default='dev', help='Environment (dev/staging/prod)')
    parser.add_argument('--bucket', required=True, help='S3 bucket name to analyze')
    parser.add_argument('--output', help='Output file for report (JSON)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    monitor = S3OrganizationMonitor(args.environment)
    report = monitor.generate_optimization_report(args.bucket)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {args.output}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
