"""
Tests for Data Quality Framework
Student Insights Pipeline
"""

import pytest
import json
from datetime import datetime, timezone
from src.data_quality.validators import (
    StudentDataValidator, 
    BatchDataValidator, 
    ValidationSeverity,
    ValidationResult
)
from src.data_quality.profiler import (
    DataProfiler,
    QualityScorer,
    AnomalyDetector
)


class TestStudentDataValidator:
    """Test cases for StudentDataValidator"""
    
    def test_valid_record(self):
        """Test validation of a valid student record"""
        validator = StudentDataValidator()
        
        valid_record = {
            "student_id": "12345",
            "name": "John Doe",
            "math_score": 85,
            "reading_score": 90,
            "writing_score": 88,
            "grade_level": "9",
            "subject": "Mathematics",
            "attendance_rate": 0.95,
            "assignment_completion_rate": 0.92,
            "timestamp": "2024-01-15T09:30:00Z"
        }
        
        is_valid, results = validator.validate_record(valid_record)
        
        assert is_valid == True
        assert len([r for r in results if r.severity == ValidationSeverity.ERROR]) == 0
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields"""
        validator = StudentDataValidator()
        
        invalid_record = {
            "math_score": 85,
            "reading_score": 90
        }
        
        is_valid, results = validator.validate_record(invalid_record)
        
        assert is_valid == False
        error_results = [r for r in results if r.severity == ValidationSeverity.ERROR]
        assert len(error_results) > 0
        
        # Should have errors for missing student_id and name
        error_fields = [r.field for r in error_results]
        assert any('student_id' in field for field in error_fields)
        assert any('name' in field for field in error_fields)
    
    def test_invalid_score_ranges(self):
        """Test validation with invalid score ranges"""
        validator = StudentDataValidator()
        
        invalid_record = {
            "student_id": "12345",
            "name": "John Doe",
            "math_score": 150,  # Invalid: > 100
            "reading_score": -10,  # Invalid: < 0
            "writing_score": 88
        }
        
        is_valid, results = validator.validate_record(invalid_record)
        
        assert is_valid == False
        error_results = [r for r in results if r.severity == ValidationSeverity.ERROR]
        assert len(error_results) >= 2  # At least 2 score errors
    
    def test_invalid_attendance_rate(self):
        """Test validation with invalid attendance rate"""
        validator = StudentDataValidator()
        
        invalid_record = {
            "student_id": "12345",
            "name": "John Doe",
            "attendance_rate": 1.5  # Invalid: > 1.0
        }
        
        is_valid, results = validator.validate_record(invalid_record)
        
        assert is_valid == False
        error_results = [r for r in results if r.severity == ValidationSeverity.ERROR]
        attendance_errors = [r for r in error_results if r.field == 'attendance_rate']
        assert len(attendance_errors) > 0
    
    def test_warning_conditions(self):
        """Test conditions that generate warnings but don't invalidate record"""
        validator = StudentDataValidator()
        
        warning_record = {
            "student_id": "12345",
            "name": "John Doe",
            "math_score": 5,  # Very low score - should generate warning
            "attendance_rate": 0.2  # Very low attendance - should generate warning
        }
        
        is_valid, results = validator.validate_record(warning_record)
        
        assert is_valid == True  # Should still be valid despite warnings
        warning_results = [r for r in results if r.severity == ValidationSeverity.WARNING]
        assert len(warning_results) >= 2  # Should have warnings for low score and attendance


class TestBatchDataValidator:
    """Test cases for BatchDataValidator"""
    
    def test_batch_validation(self):
        """Test batch validation with mixed valid/invalid records"""
        validator = BatchDataValidator()
        
        batch_data = [
            {
                "student_id": "12345",
                "name": "John Doe",
                "math_score": 85
            },
            {
                "student_id": "12346",
                "name": "Jane Smith",
                "math_score": 150  # Invalid score
            },
            {
                # Missing required fields
                "math_score": 75
            }
        ]
        
        report = validator.validate_batch(batch_data)
        
        assert report['summary']['total_records'] == 3
        assert report['summary']['valid_records'] == 1
        assert report['summary']['invalid_records'] == 2
        assert report['summary']['validation_rate'] == 1/3


class TestDataProfiler:
    """Test cases for DataProfiler"""
    
    def test_profile_dataset(self):
        """Test dataset profiling"""
        profiler = DataProfiler()
        
        sample_data = [
            {
                "student_id": "12345",
                "name": "John Doe",
                "math_score": 85,
                "reading_score": 90,
                "grade_level": "9",
                "attendance_rate": 0.95
            },
            {
                "student_id": "12346",
                "name": "Jane Smith",
                "math_score": 78,
                "reading_score": 85,
                "grade_level": "9",
                "attendance_rate": 0.88
            },
            {
                "student_id": "12347",
                "name": "Bob Johnson",
                "math_score": 92,
                "reading_score": None,  # Missing value
                "grade_level": "10",
                "attendance_rate": 0.92
            }
        ]
        
        profile = profiler.profile_dataset(sample_data)
        
        assert 'dataset_statistics' in profile
        assert profile['dataset_statistics']['total_records'] == 3
        
        assert 'field_profiles' in profile
        assert 'math_score' in profile['field_profiles']
        
        # Check math_score profile
        math_profile = profile['field_profiles']['math_score']
        assert math_profile['total_count'] == 3
        assert math_profile['null_count'] == 0
        assert math_profile['completeness_rate'] == 1.0
        
        # Check reading_score profile (has one null)
        reading_profile = profile['field_profiles']['reading_score']
        assert reading_profile['total_count'] == 3
        assert reading_profile['null_count'] == 1
        assert reading_profile['completeness_rate'] == 2/3
    
    def test_empty_dataset(self):
        """Test profiling empty dataset"""
        profiler = DataProfiler()
        
        profile = profiler.profile_dataset([])
        
        assert 'error' in profile


class TestQualityScorer:
    """Test cases for QualityScorer"""
    
    def test_score_complete_record(self):
        """Test scoring a complete, valid record"""
        scorer = QualityScorer()
        
        complete_record = {
            "student_id": "12345",
            "name": "John Doe",
            "math_score": 85,
            "reading_score": 90,
            "writing_score": 88,
            "grade_level": "9",
            "subject": "Mathematics",
            "attendance_rate": 0.95,
            "assignment_completion_rate": 0.92
        }
        
        scores = scorer.score_record(complete_record)
        
        assert 'completeness' in scores
        assert 'validity' in scores
        assert 'overall' in scores
        
        # Should have high scores for complete, valid record
        assert scores['completeness'] > 0.8
        assert scores['validity'] == 1.0
        assert scores['overall'] > 0.8
    
    def test_score_incomplete_record(self):
        """Test scoring an incomplete record"""
        scorer = QualityScorer()
        
        incomplete_record = {
            "student_id": "12345",
            "name": "John Doe"
            # Missing most optional fields
        }
        
        scores = scorer.score_record(incomplete_record)
        
        # Should have lower completeness score
        assert scores['completeness'] < 1.0
        assert scores['validity'] == 1.0  # No invalid data, just missing
        assert scores['overall'] < 1.0
    
    def test_score_invalid_record(self):
        """Test scoring a record with invalid data"""
        scorer = QualityScorer()
        
        invalid_record = {
            "student_id": "12345",
            "name": "John Doe",
            "math_score": 150,  # Invalid
            "attendance_rate": 1.5  # Invalid
        }
        
        scores = scorer.score_record(invalid_record)
        
        # Should have low validity score
        assert scores['validity'] < 1.0
        assert scores['overall'] < 0.8
    
    def test_score_batch(self):
        """Test batch scoring"""
        scorer = QualityScorer()
        
        batch_records = [
            {
                "student_id": "12345",
                "name": "John Doe",
                "math_score": 85
            },
            {
                "student_id": "12346",
                "name": "Jane Smith",
                "math_score": 150  # Invalid
            }
        ]
        
        batch_scores = scorer.score_batch(batch_records)
        
        assert 'batch_size' in batch_scores
        assert batch_scores['batch_size'] == 2
        assert 'average_overall' in batch_scores
        assert 'individual_scores' in batch_scores
        assert len(batch_scores['individual_scores']) == 2


class TestAnomalyDetector:
    """Test cases for AnomalyDetector"""
    
    def test_detect_low_score_anomaly(self):
        """Test detection of very low scores"""
        detector = AnomalyDetector()
        
        low_score_record = {
            "student_id": "12345",
            "name": "John Doe",
            "math_score": 15  # Very low score
        }
        
        anomalies = detector.detect_record_anomalies(low_score_record)
        
        assert len(anomalies) > 0
        low_score_anomalies = [a for a in anomalies if a['type'] == 'very_low_score']
        assert len(low_score_anomalies) > 0
    
    def test_detect_attendance_anomaly(self):
        """Test detection of very low attendance"""
        detector = AnomalyDetector()
        
        low_attendance_record = {
            "student_id": "12345",
            "name": "John Doe",
            "attendance_rate": 0.2  # Very low attendance
        }
        
        anomalies = detector.detect_record_anomalies(low_attendance_record)
        
        assert len(anomalies) > 0
        attendance_anomalies = [a for a in anomalies if a['type'] == 'very_low_attendance']
        assert len(attendance_anomalies) > 0
    
    def test_no_anomalies_normal_record(self):
        """Test that normal records don't trigger anomalies"""
        detector = AnomalyDetector()
        
        normal_record = {
            "student_id": "12345",
            "name": "John Doe",
            "math_score": 85,
            "attendance_rate": 0.95
        }
        
        anomalies = detector.detect_record_anomalies(normal_record)
        
        assert len(anomalies) == 0


# Integration test
def test_full_data_quality_pipeline():
    """Test the complete data quality pipeline"""
    
    # Sample data with various quality issues
    test_data = [
        {
            "student_id": "12345",
            "name": "John Doe",
            "math_score": 85,
            "reading_score": 90,
            "writing_score": 88,
            "grade_level": "9",
            "attendance_rate": 0.95,
            "assignment_completion_rate": 0.92
        },
        {
            "student_id": "12346",
            "name": "Jane Smith",
            "math_score": 150,  # Invalid score
            "reading_score": 85,
            "grade_level": "9",
            "attendance_rate": 0.88
        },
        {
            "student_id": "12347",
            "name": "Bob Johnson",
            "math_score": 5,  # Very low score (anomaly)
            "attendance_rate": 0.2  # Very low attendance (anomaly)
        },
        {
            # Missing required fields
            "math_score": 75
        }
    ]
    
    # Run validation
    batch_validator = BatchDataValidator()
    validation_report = batch_validator.validate_batch(test_data)
    
    # Run profiling
    profiler = DataProfiler()
    profile_report = profiler.profile_dataset(test_data)
    
    # Run quality scoring
    scorer = QualityScorer()
    quality_scores = scorer.score_batch(test_data)
    
    # Run anomaly detection
    detector = AnomalyDetector()
    all_anomalies = []
    for record in test_data:
        anomalies = detector.detect_record_anomalies(record)
        all_anomalies.extend(anomalies)
    
    # Assertions
    assert validation_report['summary']['total_records'] == 4
    assert validation_report['summary']['valid_records'] < 4  # Some invalid records
    
    assert profile_report['dataset_statistics']['total_records'] == 4
    assert 'quality_metrics' in profile_report
    
    assert quality_scores['batch_size'] == 4
    assert quality_scores['average_overall'] < 1.0  # Should be less than perfect due to issues
    
    assert len(all_anomalies) > 0  # Should detect some anomalies
