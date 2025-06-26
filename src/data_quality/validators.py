"""
Data Quality Validators for Student Insights Pipeline

Comprehensive validation framework for student data including:
- Schema validation
- Business rule validation  
- Data type validation
- Range validation
- Consistency validation
"""

import re
import json
import jsonschema
from typing import Dict, List, Any, Tuple, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np


class ValidationSeverity(Enum):
    """Validation error severity levels"""
    ERROR = "error"      # Critical errors that prevent processing
    WARNING = "warning"  # Issues that should be flagged but don't prevent processing
    INFO = "info"       # Informational messages


@dataclass
class ValidationResult:
    """Result of a validation check"""
    field: str
    rule: str
    severity: ValidationSeverity
    message: str
    value: Any = None
    expected: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'field': self.field,
            'rule': self.rule,
            'severity': self.severity.value,
            'message': self.message,
            'value': self.value,
            'expected': self.expected
        }


class SchemaValidator:
    """JSON Schema validator for student data"""
    
    STUDENT_SCHEMA = {
        "type": "object",
        "required": ["student_id", "name"],
        "properties": {
            "student_id": {
                "type": "string",
                "minLength": 1,
                "maxLength": 50,
                "pattern": "^[a-zA-Z0-9_-]+$",
                "description": "Unique student identifier"
            },
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "pattern": "^[a-zA-Z\\s\\-\\.]+$",
                "description": "Student full name"
            },
            "math_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Mathematics score (0-100)"
            },
            "reading_score": {
                "type": "number", 
                "minimum": 0,
                "maximum": 100,
                "description": "Reading score (0-100)"
            },
            "writing_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Writing score (0-100)"
            },
            "grade_level": {
                "type": "string",
                "enum": ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                "description": "Student grade level"
            },
            "subject": {
                "type": "string",
                "enum": ["Mathematics", "English", "Science", "History", "Art", "Physical Education", "Other"],
                "description": "Subject area"
            },
            "attendance_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Attendance rate (0.0-1.0)"
            },
            "assignment_completion_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Assignment completion rate (0.0-1.0)"
            },
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Record timestamp"
            }
        },
        "additionalProperties": True
    }
    
    def __init__(self, schema: Dict[str, Any] = None):
        self.schema = schema or self.STUDENT_SCHEMA
        self.validator = jsonschema.Draft7Validator(self.schema)
    
    def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            
        Returns:
            List of validation results
        """
        results = []
        
        for error in self.validator.iter_errors(data):
            field = '.'.join(str(x) for x in error.absolute_path) if error.absolute_path else 'root'
            
            results.append(ValidationResult(
                field=field,
                rule='schema_validation',
                severity=ValidationSeverity.ERROR,
                message=error.message,
                value=error.instance if hasattr(error, 'instance') else None
            ))
        
        return results


class StudentDataValidator:
    """Comprehensive validator for individual student records"""
    
    def __init__(self):
        self.schema_validator = SchemaValidator()
    
    def validate_record(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationResult]]:
        """
        Validate a single student record
        
        Args:
            data: Student data record
            
        Returns:
            Tuple of (is_valid, validation_results)
        """
        results = []
        
        # Schema validation
        schema_results = self.schema_validator.validate(data)
        results.extend(schema_results)
        
        # Business rule validation
        business_results = self._validate_business_rules(data)
        results.extend(business_results)
        
        # Data consistency validation
        consistency_results = self._validate_consistency(data)
        results.extend(consistency_results)
        
        # Determine if record is valid (no ERROR severity issues)
        has_errors = any(r.severity == ValidationSeverity.ERROR for r in results)
        
        return not has_errors, results
    
    def _validate_business_rules(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate business-specific rules"""
        results = []
        
        # Rule: Student ID format validation
        student_id = data.get('student_id', '')
        if student_id and not re.match(r'^[a-zA-Z0-9_-]+$', student_id):
            results.append(ValidationResult(
                field='student_id',
                rule='format_validation',
                severity=ValidationSeverity.ERROR,
                message='Student ID contains invalid characters',
                value=student_id
            ))
        
        # Rule: Name validation
        name = data.get('name', '')
        if name and not re.match(r'^[a-zA-Z\s\-\.]+$', name):
            results.append(ValidationResult(
                field='name',
                rule='format_validation',
                severity=ValidationSeverity.WARNING,
                message='Name contains potentially invalid characters',
                value=name
            ))
        
        # Rule: Score reasonableness
        scores = ['math_score', 'reading_score', 'writing_score']
        for score_field in scores:
            score = data.get(score_field)
            if score is not None:
                if score < 0 or score > 100:
                    results.append(ValidationResult(
                        field=score_field,
                        rule='range_validation',
                        severity=ValidationSeverity.ERROR,
                        message=f'Score must be between 0 and 100',
                        value=score,
                        expected='0-100'
                    ))
                elif score < 10:
                    results.append(ValidationResult(
                        field=score_field,
                        rule='reasonableness_check',
                        severity=ValidationSeverity.WARNING,
                        message=f'Unusually low score detected',
                        value=score
                    ))
        
        # Rule: Attendance rate validation
        attendance = data.get('attendance_rate')
        if attendance is not None:
            if attendance < 0 or attendance > 1:
                results.append(ValidationResult(
                    field='attendance_rate',
                    rule='range_validation',
                    severity=ValidationSeverity.ERROR,
                    message='Attendance rate must be between 0.0 and 1.0',
                    value=attendance,
                    expected='0.0-1.0'
                ))
            elif attendance < 0.3:
                results.append(ValidationResult(
                    field='attendance_rate',
                    rule='reasonableness_check',
                    severity=ValidationSeverity.WARNING,
                    message='Very low attendance rate detected',
                    value=attendance
                ))
        
        return results
    
    def _validate_consistency(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data consistency across fields"""
        results = []
        
        # Rule: Grade level and score consistency
        grade_level = data.get('grade_level')
        if grade_level:
            scores = [data.get(f) for f in ['math_score', 'reading_score', 'writing_score'] if data.get(f) is not None]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                
                # Expected score ranges by grade level (rough guidelines)
                grade_expectations = {
                    'K': (40, 80), '1': (45, 85), '2': (50, 85), '3': (55, 90),
                    '4': (60, 90), '5': (60, 95), '6': (65, 95), '7': (65, 95),
                    '8': (70, 95), '9': (70, 100), '10': (70, 100), '11': (75, 100), '12': (75, 100)
                }
                
                if grade_level in grade_expectations:
                    min_expected, max_expected = grade_expectations[grade_level]
                    if avg_score < min_expected - 20 or avg_score > max_expected + 10:
                        results.append(ValidationResult(
                            field='average_score',
                            rule='grade_consistency',
                            severity=ValidationSeverity.WARNING,
                            message=f'Average score unusual for grade level {grade_level}',
                            value=avg_score,
                            expected=f'{min_expected}-{max_expected}'
                        ))
        
        return results


class BatchDataValidator:
    """Validator for batch data processing"""
    
    def __init__(self):
        self.record_validator = StudentDataValidator()
    
    def validate_batch(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of student records
        
        Args:
            data_list: List of student data records
            
        Returns:
            Batch validation report
        """
        valid_records = []
        invalid_records = []
        all_validation_results = []
        
        for i, record in enumerate(data_list):
            is_valid, results = self.record_validator.validate_record(record)
            
            record_info = {
                'index': i,
                'student_id': record.get('student_id', 'unknown'),
                'record': record,
                'validation_results': [r.to_dict() for r in results]
            }
            
            if is_valid:
                valid_records.append(record_info)
            else:
                invalid_records.append(record_info)
            
            all_validation_results.extend(results)
        
        # Generate summary statistics
        total_records = len(data_list)
        valid_count = len(valid_records)
        invalid_count = len(invalid_records)
        
        error_count = sum(1 for r in all_validation_results if r.severity == ValidationSeverity.ERROR)
        warning_count = sum(1 for r in all_validation_results if r.severity == ValidationSeverity.WARNING)
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total_records': total_records,
                'valid_records': valid_count,
                'invalid_records': invalid_count,
                'validation_rate': valid_count / total_records if total_records > 0 else 0,
                'error_count': error_count,
                'warning_count': warning_count
            },
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'validation_details': [r.to_dict() for r in all_validation_results]
        }
