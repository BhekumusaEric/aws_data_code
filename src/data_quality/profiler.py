"""
Data Quality Profiler for Student Insights Pipeline

Provides data profiling, quality scoring, and anomaly detection
capabilities for comprehensive data quality assessment.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import statistics
from collections import Counter, defaultdict


@dataclass
class DataProfile:
    """Data profile for a field or dataset"""
    field_name: str
    data_type: str
    total_count: int
    null_count: int
    unique_count: int
    completeness_rate: float
    uniqueness_rate: float
    min_value: Any = None
    max_value: Any = None
    mean_value: Any = None
    median_value: Any = None
    std_dev: Any = None
    most_common_values: List[Tuple[Any, int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'field_name': self.field_name,
            'data_type': self.data_type,
            'total_count': self.total_count,
            'null_count': self.null_count,
            'unique_count': self.unique_count,
            'completeness_rate': self.completeness_rate,
            'uniqueness_rate': self.uniqueness_rate,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'mean_value': self.mean_value,
            'median_value': self.median_value,
            'std_dev': self.std_dev,
            'most_common_values': self.most_common_values
        }


class DataProfiler:
    """Comprehensive data profiler for student data"""
    
    def __init__(self):
        self.numeric_fields = ['math_score', 'reading_score', 'writing_score', 'attendance_rate', 'assignment_completion_rate']
        self.categorical_fields = ['grade_level', 'subject', 'performance_category', 'risk_level']
        self.text_fields = ['student_id', 'name']
    
    def profile_dataset(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create comprehensive profile of a dataset
        
        Args:
            data: List of student records
            
        Returns:
            Complete dataset profile
        """
        if not data:
            return {'error': 'No data provided for profiling'}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(data)
        
        # Overall dataset statistics
        dataset_stats = {
            'total_records': len(df),
            'total_fields': len(df.columns),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Profile each field
        field_profiles = {}
        for column in df.columns:
            field_profiles[column] = self._profile_field(df[column], column)
        
        # Calculate dataset-level quality metrics
        quality_metrics = self._calculate_quality_metrics(df, field_profiles)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(df)
        
        return {
            'dataset_statistics': dataset_stats,
            'field_profiles': {k: v.to_dict() for k, v in field_profiles.items()},
            'quality_metrics': quality_metrics,
            'anomalies': anomalies
        }
    
    def _profile_field(self, series: pd.Series, field_name: str) -> DataProfile:
        """Profile a single field"""
        total_count = len(series)
        null_count = series.isnull().sum()
        non_null_series = series.dropna()
        unique_count = non_null_series.nunique()
        
        completeness_rate = (total_count - null_count) / total_count if total_count > 0 else 0
        uniqueness_rate = unique_count / total_count if total_count > 0 else 0
        
        # Determine data type
        if field_name in self.numeric_fields:
            data_type = 'numeric'
        elif field_name in self.categorical_fields:
            data_type = 'categorical'
        elif field_name in self.text_fields:
            data_type = 'text'
        else:
            data_type = 'unknown'
        
        # Calculate statistics based on data type
        min_value = max_value = mean_value = median_value = std_dev = None
        most_common_values = None
        
        if data_type == 'numeric' and len(non_null_series) > 0:
            try:
                numeric_series = pd.to_numeric(non_null_series, errors='coerce').dropna()
                if len(numeric_series) > 0:
                    min_value = float(numeric_series.min())
                    max_value = float(numeric_series.max())
                    mean_value = float(numeric_series.mean())
                    median_value = float(numeric_series.median())
                    std_dev = float(numeric_series.std()) if len(numeric_series) > 1 else 0
            except Exception:
                pass
        
        if data_type in ['categorical', 'text'] and len(non_null_series) > 0:
            value_counts = non_null_series.value_counts()
            most_common_values = [(str(val), int(count)) for val, count in value_counts.head(10).items()]
        
        return DataProfile(
            field_name=field_name,
            data_type=data_type,
            total_count=total_count,
            null_count=null_count,
            unique_count=unique_count,
            completeness_rate=completeness_rate,
            uniqueness_rate=uniqueness_rate,
            min_value=min_value,
            max_value=max_value,
            mean_value=mean_value,
            median_value=median_value,
            std_dev=std_dev,
            most_common_values=most_common_values
        )
    
    def _calculate_quality_metrics(self, df: pd.DataFrame, field_profiles: Dict[str, DataProfile]) -> Dict[str, Any]:
        """Calculate dataset-level quality metrics"""
        
        # Overall completeness
        total_cells = df.size
        null_cells = df.isnull().sum().sum()
        overall_completeness = (total_cells - null_cells) / total_cells if total_cells > 0 else 0
        
        # Field-level completeness statistics
        completeness_rates = [profile.completeness_rate for profile in field_profiles.values()]
        
        # Uniqueness statistics for key fields
        key_field_uniqueness = {}
        if 'student_id' in field_profiles:
            key_field_uniqueness['student_id'] = field_profiles['student_id'].uniqueness_rate
        
        # Score field statistics
        score_fields = ['math_score', 'reading_score', 'writing_score']
        score_completeness = []
        for field in score_fields:
            if field in field_profiles:
                score_completeness.append(field_profiles[field].completeness_rate)
        
        avg_score_completeness = statistics.mean(score_completeness) if score_completeness else 0
        
        # Data consistency metrics
        consistency_score = self._calculate_consistency_score(df)
        
        return {
            'overall_completeness': overall_completeness,
            'avg_field_completeness': statistics.mean(completeness_rates) if completeness_rates else 0,
            'min_field_completeness': min(completeness_rates) if completeness_rates else 0,
            'max_field_completeness': max(completeness_rates) if completeness_rates else 0,
            'key_field_uniqueness': key_field_uniqueness,
            'score_field_completeness': avg_score_completeness,
            'data_consistency_score': consistency_score,
            'quality_score': self._calculate_overall_quality_score(
                overall_completeness, avg_score_completeness, consistency_score
            )
        }
    
    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate data consistency score"""
        consistency_checks = []
        
        # Check 1: Score ranges (0-100)
        score_fields = ['math_score', 'reading_score', 'writing_score']
        for field in score_fields:
            if field in df.columns:
                valid_scores = df[field].dropna()
                if len(valid_scores) > 0:
                    in_range = ((valid_scores >= 0) & (valid_scores <= 100)).sum()
                    consistency_checks.append(in_range / len(valid_scores))
        
        # Check 2: Rate ranges (0-1)
        rate_fields = ['attendance_rate', 'assignment_completion_rate']
        for field in rate_fields:
            if field in df.columns:
                valid_rates = df[field].dropna()
                if len(valid_rates) > 0:
                    in_range = ((valid_rates >= 0) & (valid_rates <= 1)).sum()
                    consistency_checks.append(in_range / len(valid_rates))
        
        # Check 3: Grade level consistency
        if 'grade_level' in df.columns:
            valid_grades = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
            grade_data = df['grade_level'].dropna()
            if len(grade_data) > 0:
                valid_grade_count = grade_data.isin(valid_grades).sum()
                consistency_checks.append(valid_grade_count / len(grade_data))
        
        return statistics.mean(consistency_checks) if consistency_checks else 1.0
    
    def _calculate_overall_quality_score(self, completeness: float, score_completeness: float, consistency: float) -> float:
        """Calculate overall quality score (0-1)"""
        # Weighted average of different quality dimensions
        weights = {
            'completeness': 0.4,
            'score_completeness': 0.3,
            'consistency': 0.3
        }
        
        return (
            completeness * weights['completeness'] +
            score_completeness * weights['score_completeness'] +
            consistency * weights['consistency']
        )
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect data anomalies"""
        anomalies = []
        
        # Anomaly 1: Duplicate student IDs
        if 'student_id' in df.columns:
            duplicates = df['student_id'].duplicated()
            if duplicates.any():
                duplicate_ids = df[duplicates]['student_id'].tolist()
                anomalies.append({
                    'type': 'duplicate_student_ids',
                    'severity': 'high',
                    'description': f'Found {len(duplicate_ids)} duplicate student IDs',
                    'affected_records': duplicate_ids
                })
        
        # Anomaly 2: Outlier scores
        score_fields = ['math_score', 'reading_score', 'writing_score']
        for field in score_fields:
            if field in df.columns:
                scores = df[field].dropna()
                if len(scores) > 0:
                    Q1 = scores.quantile(0.25)
                    Q3 = scores.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = scores[(scores < lower_bound) | (scores > upper_bound)]
                    if len(outliers) > 0:
                        anomalies.append({
                            'type': 'score_outliers',
                            'field': field,
                            'severity': 'medium',
                            'description': f'Found {len(outliers)} outlier scores in {field}',
                            'outlier_values': outliers.tolist()
                        })
        
        # Anomaly 3: Inconsistent attendance vs completion rates
        if 'attendance_rate' in df.columns and 'assignment_completion_rate' in df.columns:
            both_present = df[['attendance_rate', 'assignment_completion_rate']].dropna()
            if len(both_present) > 0:
                # Flag cases where completion rate is much higher than attendance
                inconsistent = both_present[
                    both_present['assignment_completion_rate'] > both_present['attendance_rate'] + 0.3
                ]
                if len(inconsistent) > 0:
                    anomalies.append({
                        'type': 'attendance_completion_inconsistency',
                        'severity': 'medium',
                        'description': f'Found {len(inconsistent)} records with completion rate much higher than attendance',
                        'affected_count': len(inconsistent)
                    })
        
        return anomalies


class QualityScorer:
    """Calculate quality scores for student data"""
    
    def __init__(self):
        self.profiler = DataProfiler()
    
    def score_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate quality score for a single record
        
        Args:
            record: Student data record
            
        Returns:
            Quality score breakdown
        """
        scores = {}
        
        # Completeness score (0-1)
        required_fields = ['student_id', 'name']
        optional_fields = ['math_score', 'reading_score', 'writing_score', 'grade_level', 'subject']
        
        required_present = sum(1 for field in required_fields if record.get(field))
        optional_present = sum(1 for field in optional_fields if record.get(field))
        
        scores['completeness'] = (
            (required_present / len(required_fields)) * 0.7 +
            (optional_present / len(optional_fields)) * 0.3
        )
        
        # Validity score (0-1)
        validity_checks = []
        
        # Score range checks
        for field in ['math_score', 'reading_score', 'writing_score']:
            if field in record and record[field] is not None:
                score = record[field]
                validity_checks.append(1 if 0 <= score <= 100 else 0)
        
        # Rate range checks
        for field in ['attendance_rate', 'assignment_completion_rate']:
            if field in record and record[field] is not None:
                rate = record[field]
                validity_checks.append(1 if 0 <= rate <= 1 else 0)
        
        scores['validity'] = statistics.mean(validity_checks) if validity_checks else 1.0
        
        # Overall quality score
        scores['overall'] = (scores['completeness'] * 0.6 + scores['validity'] * 0.4)
        
        return scores
    
    def score_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate quality scores for a batch of records
        
        Args:
            records: List of student data records
            
        Returns:
            Batch quality score summary
        """
        individual_scores = [self.score_record(record) for record in records]
        
        if not individual_scores:
            return {'error': 'No records to score'}
        
        # Calculate aggregate scores
        completeness_scores = [s['completeness'] for s in individual_scores]
        validity_scores = [s['validity'] for s in individual_scores]
        overall_scores = [s['overall'] for s in individual_scores]
        
        return {
            'batch_size': len(records),
            'average_completeness': statistics.mean(completeness_scores),
            'average_validity': statistics.mean(validity_scores),
            'average_overall': statistics.mean(overall_scores),
            'min_overall': min(overall_scores),
            'max_overall': max(overall_scores),
            'records_above_threshold': {
                '0.8': sum(1 for s in overall_scores if s >= 0.8),
                '0.6': sum(1 for s in overall_scores if s >= 0.6),
                '0.4': sum(1 for s in overall_scores if s >= 0.4)
            },
            'individual_scores': individual_scores
        }


class AnomalyDetector:
    """Detect anomalies in student data"""
    
    def __init__(self):
        self.score_thresholds = {
            'very_low': 30,
            'very_high': 98,
            'impossible_low': 0,
            'impossible_high': 100
        }
    
    def detect_record_anomalies(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a single record
        
        Args:
            record: Student data record
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Score-based anomalies
        score_fields = ['math_score', 'reading_score', 'writing_score']
        for field in score_fields:
            if field in record and record[field] is not None:
                score = record[field]
                
                if score <= self.score_thresholds['very_low']:
                    anomalies.append({
                        'type': 'very_low_score',
                        'field': field,
                        'value': score,
                        'severity': 'medium',
                        'description': f'Very low {field}: {score}'
                    })
                elif score >= self.score_thresholds['very_high']:
                    anomalies.append({
                        'type': 'very_high_score',
                        'field': field,
                        'value': score,
                        'severity': 'low',
                        'description': f'Very high {field}: {score}'
                    })
        
        # Attendance anomalies
        if 'attendance_rate' in record and record['attendance_rate'] is not None:
            attendance = record['attendance_rate']
            if attendance < 0.3:
                anomalies.append({
                    'type': 'very_low_attendance',
                    'field': 'attendance_rate',
                    'value': attendance,
                    'severity': 'high',
                    'description': f'Very low attendance rate: {attendance:.2%}'
                })
        
        return anomalies
