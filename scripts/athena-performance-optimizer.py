#!/usr/bin/env python3
"""
Athena Performance Optimizer & Cost Manager
Student Insights Pipeline

This script provides comprehensive performance monitoring and cost optimization
for Athena queries in the Student Insights Pipeline.

Features:
- Query performance analysis
- Cost monitoring and alerts
- Automatic optimization recommendations
- Query pattern analysis
- Resource usage tracking
"""

import boto3
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_execution_id: str
    query: str
    execution_time_ms: int
    data_scanned_bytes: int
    data_scanned_mb: float
    cost_estimate_usd: float
    result_count: int
    status: str
    error_message: Optional[str] = None


@dataclass
class OptimizationRecommendation:
    """Query optimization recommendation"""
    query_id: str
    recommendation_type: str
    description: str
    potential_savings_percent: float
    priority: str  # high, medium, low


class AthenaPerformanceOptimizer:
    """Athena performance optimizer and cost manager"""
    
    def __init__(self, database_name: str, region: str = 'us-east-1'):
        self.database_name = database_name
        self.region = region
        self.athena_client = boto3.client('athena', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        
        # Cost calculation constants (approximate AWS pricing)
        self.cost_per_tb_scanned = 5.00  # USD per TB scanned
        self.bytes_per_tb = 1024 ** 4
        
    def analyze_query_performance(self, query_execution_id: str) -> QueryMetrics:
        """
        Analyze performance metrics for a specific query
        
        Args:
            query_execution_id: Athena query execution ID
            
        Returns:
            QueryMetrics object with performance data
        """
        try:
            response = self.athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            execution = response['QueryExecution']
            
            # Extract basic metrics
            query = execution['Query']
            status = execution['Status']['State']
            
            # Calculate execution time
            start_time = execution['Status']['SubmissionDateTime']
            completion_time = execution['Status'].get('CompletionDateTime', datetime.now())
            execution_time_ms = int((completion_time - start_time).total_seconds() * 1000)
            
            # Extract data scanned
            statistics = execution.get('Statistics', {})
            data_scanned_bytes = statistics.get('DataScannedInBytes', 0)
            data_scanned_mb = data_scanned_bytes / (1024 * 1024)
            
            # Calculate cost estimate
            cost_estimate_usd = (data_scanned_bytes / self.bytes_per_tb) * self.cost_per_tb_scanned
            
            # Get result count if available
            result_count = 0
            try:
                results = self.athena_client.get_query_results(QueryExecutionId=query_execution_id)
                result_count = len(results['ResultSet']['Rows']) - 1  # Subtract header
            except Exception:
                pass  # Results might not be available
            
            # Extract error message if failed
            error_message = None
            if status == 'FAILED':
                error_message = execution['Status'].get('StateChangeReason', 'Unknown error')
            
            return QueryMetrics(
                query_execution_id=query_execution_id,
                query=query,
                execution_time_ms=execution_time_ms,
                data_scanned_bytes=data_scanned_bytes,
                data_scanned_mb=data_scanned_mb,
                cost_estimate_usd=cost_estimate_usd,
                result_count=result_count,
                status=status,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Error analyzing query {query_execution_id}: {str(e)}")
            raise
    
    def get_recent_queries(self, hours_back: int = 24) -> List[str]:
        """
        Get recent query execution IDs
        
        Args:
            hours_back: Number of hours to look back
            
        Returns:
            List of query execution IDs
        """
        try:
            # Note: This is a simplified implementation
            # In practice, you might want to use CloudTrail or store query IDs
            
            # For now, return empty list as we can't easily get historical queries
            # without additional setup
            logger.warning("Recent queries retrieval requires CloudTrail integration")
            return []
            
        except Exception as e:
            logger.error(f"Error getting recent queries: {str(e)}")
            return []
    
    def analyze_query_patterns(self, query_metrics: List[QueryMetrics]) -> Dict[str, Any]:
        """
        Analyze query patterns for optimization opportunities
        
        Args:
            query_metrics: List of query metrics to analyze
            
        Returns:
            Analysis report with patterns and recommendations
        """
        if not query_metrics:
            return {'error': 'No query metrics provided'}
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_queries': len(query_metrics),
            'performance_summary': {},
            'cost_summary': {},
            'patterns': {},
            'recommendations': []
        }
        
        # Performance summary
        execution_times = [q.execution_time_ms for q in query_metrics if q.status == 'SUCCEEDED']
        data_scanned = [q.data_scanned_mb for q in query_metrics if q.status == 'SUCCEEDED']
        costs = [q.cost_estimate_usd for q in query_metrics if q.status == 'SUCCEEDED']
        
        if execution_times:
            analysis['performance_summary'] = {
                'avg_execution_time_ms': sum(execution_times) / len(execution_times),
                'max_execution_time_ms': max(execution_times),
                'min_execution_time_ms': min(execution_times),
                'avg_data_scanned_mb': sum(data_scanned) / len(data_scanned),
                'total_data_scanned_mb': sum(data_scanned),
                'avg_cost_usd': sum(costs) / len(costs),
                'total_cost_usd': sum(costs)
            }
        
        # Identify patterns
        slow_queries = [q for q in query_metrics if q.execution_time_ms > 30000]  # > 30 seconds
        expensive_queries = [q for q in query_metrics if q.cost_estimate_usd > 0.01]  # > 1 cent
        failed_queries = [q for q in query_metrics if q.status == 'FAILED']
        
        analysis['patterns'] = {
            'slow_queries_count': len(slow_queries),
            'expensive_queries_count': len(expensive_queries),
            'failed_queries_count': len(failed_queries),
            'success_rate': len([q for q in query_metrics if q.status == 'SUCCEEDED']) / len(query_metrics)
        }
        
        # Generate recommendations
        recommendations = []
        
        if len(slow_queries) > len(query_metrics) * 0.2:  # > 20% slow queries
            recommendations.append(OptimizationRecommendation(
                query_id='pattern_analysis',
                recommendation_type='performance',
                description='High number of slow queries detected. Consider adding partition filters and optimizing WHERE clauses.',
                potential_savings_percent=30.0,
                priority='high'
            ))
        
        if len(expensive_queries) > len(query_metrics) * 0.3:  # > 30% expensive queries
            recommendations.append(OptimizationRecommendation(
                query_id='pattern_analysis',
                recommendation_type='cost',
                description='High data scanning costs detected. Implement partition pruning and column selection.',
                potential_savings_percent=50.0,
                priority='high'
            ))
        
        if analysis['patterns']['success_rate'] < 0.9:  # < 90% success rate
            recommendations.append(OptimizationRecommendation(
                query_id='pattern_analysis',
                recommendation_type='reliability',
                description='Low query success rate. Review query syntax and data availability.',
                potential_savings_percent=0.0,
                priority='medium'
            ))
        
        analysis['recommendations'] = [
            {
                'type': r.recommendation_type,
                'description': r.description,
                'potential_savings_percent': r.potential_savings_percent,
                'priority': r.priority
            }
            for r in recommendations
        ]
        
        return analysis
    
    def optimize_query(self, original_query: str) -> Tuple[str, List[str]]:
        """
        Suggest optimizations for a query
        
        Args:
            original_query: Original SQL query
            
        Returns:
            Tuple of (optimized_query, list_of_optimizations_applied)
        """
        optimized_query = original_query
        optimizations = []
        
        # Optimization 1: Add LIMIT if not present and no aggregation
        if 'LIMIT' not in optimized_query.upper() and 'GROUP BY' not in optimized_query.upper():
            if 'SELECT *' in optimized_query.upper():
                optimized_query += '\nLIMIT 1000'
                optimizations.append('Added LIMIT 1000 to prevent large result sets')
        
        # Optimization 2: Suggest partition filters
        if 'WHERE' in optimized_query.upper():
            if 'year =' not in optimized_query.lower():
                optimizations.append('Consider adding year partition filter: WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)')
            if 'month =' not in optimized_query.lower():
                optimizations.append('Consider adding month partition filter for recent data')
        else:
            optimizations.append('Add WHERE clause with partition filters to reduce data scanning')
        
        # Optimization 3: Column selection
        if 'SELECT *' in optimized_query.upper():
            optimizations.append('Replace SELECT * with specific columns to reduce data transfer')
        
        # Optimization 4: Use views for common patterns
        if 'latest_student_data' not in optimized_query.lower():
            if 'ROW_NUMBER() OVER' in optimized_query.upper():
                optimizations.append('Consider using latest_student_data view instead of manual ROW_NUMBER()')
        
        return optimized_query, optimizations
    
    def create_cost_alert(self, threshold_usd: float = 1.0) -> Dict[str, Any]:
        """
        Create CloudWatch alarm for Athena costs
        
        Args:
            threshold_usd: Cost threshold in USD
            
        Returns:
            Alarm creation result
        """
        try:
            alarm_name = f'athena-cost-alert-{self.database_name}'
            
            response = self.cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='DataScannedInBytes',
                Namespace='AWS/Athena',
                Period=3600,  # 1 hour
                Statistic='Sum',
                Threshold=threshold_usd * self.bytes_per_tb / self.cost_per_tb_scanned,
                ActionsEnabled=True,
                AlarmDescription=f'Athena cost alert for {self.database_name}',
                Dimensions=[
                    {
                        'Name': 'WorkGroup',
                        'Value': 'primary'
                    }
                ],
                Unit='Bytes'
            )
            
            logger.info(f"Created cost alert: {alarm_name}")
            return {'status': 'success', 'alarm_name': alarm_name}
            
        except Exception as e:
            logger.error(f"Error creating cost alert: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def generate_performance_report(self, query_metrics: List[QueryMetrics]) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            query_metrics: List of query metrics
            
        Returns:
            Comprehensive performance report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'database': self.database_name,
            'analysis_period': '24 hours',
            'summary': {},
            'top_expensive_queries': [],
            'top_slow_queries': [],
            'failed_queries': [],
            'optimization_opportunities': [],
            'cost_breakdown': {},
            'recommendations': []
        }
        
        if not query_metrics:
            report['error'] = 'No query metrics available'
            return report
        
        # Summary statistics
        successful_queries = [q for q in query_metrics if q.status == 'SUCCEEDED']
        failed_queries = [q for q in query_metrics if q.status == 'FAILED']
        
        report['summary'] = {
            'total_queries': len(query_metrics),
            'successful_queries': len(successful_queries),
            'failed_queries': len(failed_queries),
            'success_rate_percent': len(successful_queries) / len(query_metrics) * 100,
            'total_cost_usd': sum(q.cost_estimate_usd for q in successful_queries),
            'total_data_scanned_gb': sum(q.data_scanned_mb for q in successful_queries) / 1024,
            'avg_execution_time_ms': sum(q.execution_time_ms for q in successful_queries) / len(successful_queries) if successful_queries else 0
        }
        
        # Top expensive queries
        expensive_queries = sorted(successful_queries, key=lambda x: x.cost_estimate_usd, reverse=True)[:5]
        report['top_expensive_queries'] = [
            {
                'query_id': q.query_execution_id,
                'cost_usd': round(q.cost_estimate_usd, 4),
                'data_scanned_mb': round(q.data_scanned_mb, 2),
                'query_preview': q.query[:100] + '...' if len(q.query) > 100 else q.query
            }
            for q in expensive_queries
        ]
        
        # Top slow queries
        slow_queries = sorted(successful_queries, key=lambda x: x.execution_time_ms, reverse=True)[:5]
        report['top_slow_queries'] = [
            {
                'query_id': q.query_execution_id,
                'execution_time_ms': q.execution_time_ms,
                'execution_time_seconds': round(q.execution_time_ms / 1000, 2),
                'query_preview': q.query[:100] + '...' if len(q.query) > 100 else q.query
            }
            for q in slow_queries
        ]
        
        # Failed queries
        report['failed_queries'] = [
            {
                'query_id': q.query_execution_id,
                'error_message': q.error_message,
                'query_preview': q.query[:100] + '...' if len(q.query) > 100 else q.query
            }
            for q in failed_queries[:5]  # Top 5 failed queries
        ]
        
        # Generate recommendations
        recommendations = []
        
        if report['summary']['total_cost_usd'] > 0.50:  # > 50 cents
            recommendations.append('High query costs detected. Implement partition pruning and column selection.')
        
        if report['summary']['avg_execution_time_ms'] > 10000:  # > 10 seconds
            recommendations.append('Slow query performance detected. Consider query optimization and indexing.')
        
        if report['summary']['success_rate_percent'] < 95:
            recommendations.append('Low success rate detected. Review query syntax and data availability.')
        
        report['recommendations'] = recommendations
        
        return report


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Optimize Athena performance and manage costs')
    parser.add_argument('--database', required=True, help='Athena database name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--action', choices=['analyze', 'optimize-query', 'create-alert', 'report'], 
                       default='report', help='Action to perform')
    parser.add_argument('--query-id', help='Query execution ID to analyze')
    parser.add_argument('--query-file', help='File containing SQL query to optimize')
    parser.add_argument('--cost-threshold', type=float, default=1.0, help='Cost alert threshold in USD')
    parser.add_argument('--output', help='Output file for reports (JSON)')
    
    args = parser.parse_args()
    
    optimizer = AthenaPerformanceOptimizer(args.database, args.region)
    
    if args.action == 'analyze' and args.query_id:
        metrics = optimizer.analyze_query_performance(args.query_id)
        print(f"📊 Query Analysis Results:")
        print(f"   Execution Time: {metrics.execution_time_ms}ms")
        print(f"   Data Scanned: {metrics.data_scanned_mb:.2f}MB")
        print(f"   Cost Estimate: ${metrics.cost_estimate_usd:.4f}")
        print(f"   Status: {metrics.status}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(metrics.__dict__, f, indent=2, default=str)
    
    elif args.action == 'optimize-query' and args.query_file:
        with open(args.query_file, 'r') as f:
            query = f.read()
        
        optimized_query, optimizations = optimizer.optimize_query(query)
        print("🔧 Query Optimization Suggestions:")
        for opt in optimizations:
            print(f"   • {opt}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump({
                    'original_query': query,
                    'optimized_query': optimized_query,
                    'optimizations': optimizations
                }, f, indent=2)
    
    elif args.action == 'create-alert':
        result = optimizer.create_cost_alert(args.cost_threshold)
        if result['status'] == 'success':
            print(f"✅ Cost alert created: {result['alarm_name']}")
        else:
            print(f"❌ Failed to create alert: {result['error']}")
    
    elif args.action == 'report':
        # For demo purposes, create a sample report
        sample_metrics = []  # Would be populated with real data
        report = optimizer.generate_performance_report(sample_metrics)
        
        print("📈 Performance Report Generated")
        print(f"   Database: {report['database']}")
        print(f"   Analysis Period: {report['analysis_period']}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
