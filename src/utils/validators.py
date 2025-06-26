"""
Data validation utilities for Student Insights Pipeline
"""

import jsonschema
from typing import Dict, List, Any, Tuple
from datetime import datetime


class StudentDataSchema:
    """JSON Schema for student data validation"""
    
    SCHEMA = {
        "type": "object",
        "required": ["student_id", "name"],
        "properties": {
            "student_id": {
                "type": "string",
                "minLength": 1,
                "maxLength": 50,
                "pattern": "^[a-zA-Z0-9_-]+$"
            },
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100
            },
            "math_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 100
            },
            "reading_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 100
            },
            "writing_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 100
            },
            "grade_level": {
                "type": "string",
                "enum": ["9", "10", "11", "12", "K", "1", "2", "3", "4", "5", "6", "7", "8"]
            },
            "subject": {
                "type": "string",
                "enum": ["Mathematics", "English", "Science", "History", "Art", "Physical Education"]
            },
            "attendance_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "assignment_completion_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "timestamp": {
                "type": "string",
                "format": "date-time"
            }
        },
        "additionalProperties": True
    }


def validate_student_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate student data against schema
    
    Args:
        data: Student data dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    try:
        jsonschema.validate(data, StudentDataSchema.SCHEMA)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]
    except Exception as e:
        return False, [f"Validation error: {str(e)}"]


def validate_batch_data(data_list: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Validate a batch of student data records
    
    Args:
        data_list: List of student data dictionaries
        
    Returns:
        Tuple of (valid_records, error_messages)
    """
    valid_records = []
    errors = []
    
    for i, record in enumerate(data_list):
        is_valid, validation_errors = validate_student_data(record)
        if is_valid:
            valid_records.append(record)
        else:
            errors.extend([f"Record {i+1}: {error}" for error in validation_errors])
    
    return valid_records, errors


def sanitize_student_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and clean student data
    
    Args:
        data: Raw student data
        
    Returns:
        Sanitized data
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Strip whitespace and handle empty strings
            cleaned_value = value.strip()
            if cleaned_value:
                sanitized[key] = cleaned_value
        elif value is not None:
            sanitized[key] = value
    
    # Convert numeric strings to numbers where appropriate
    numeric_fields = ['math_score', 'reading_score', 'writing_score', 'attendance_rate', 'assignment_completion_rate']
    for field in numeric_fields:
        if field in sanitized and isinstance(sanitized[field], str):
            try:
                sanitized[field] = float(sanitized[field])
            except ValueError:
                pass  # Keep as string if conversion fails
    
    return sanitized
