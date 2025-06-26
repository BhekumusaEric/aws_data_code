"""
Helper utilities for Student Insights Pipeline
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import statistics


def calculate_average_score(data: Dict[str, Any], score_fields: List[str] = None) -> Optional[float]:
    """
    Calculate average score from multiple score fields
    
    Args:
        data: Student data dictionary
        score_fields: List of score field names to average
        
    Returns:
        Average score or None if no valid scores
    """
    if score_fields is None:
        score_fields = ['math_score', 'reading_score', 'writing_score']
    
    scores = []
    for field in score_fields:
        if field in data and data[field] is not None:
            try:
                score = float(data[field])
                if 0 <= score <= 100:  # Valid score range
                    scores.append(score)
            except (ValueError, TypeError):
                continue
    
    return round(statistics.mean(scores), 2) if scores else None


def determine_risk_level(data: Dict[str, Any]) -> str:
    """
    Determine student risk level based on performance metrics
    
    Args:
        data: Student data dictionary
        
    Returns:
        Risk level string
    """
    # Calculate average score
    avg_score = calculate_average_score(data)
    attendance_rate = data.get('attendance_rate', 1.0)
    completion_rate = data.get('assignment_completion_rate', 1.0)
    
    # Risk factors
    risk_factors = 0
    
    # Academic performance risk
    if avg_score is not None:
        if avg_score < 60:
            risk_factors += 3  # High academic risk
        elif avg_score < 70:
            risk_factors += 2  # Medium academic risk
        elif avg_score < 80:
            risk_factors += 1  # Low academic risk
    
    # Attendance risk
    if attendance_rate < 0.7:
        risk_factors += 2  # High attendance risk
    elif attendance_rate < 0.85:
        risk_factors += 1  # Medium attendance risk
    
    # Assignment completion risk
    if completion_rate < 0.6:
        risk_factors += 2  # High completion risk
    elif completion_rate < 0.8:
        risk_factors += 1  # Medium completion risk
    
    # Determine overall risk level
    if risk_factors >= 5:
        return "High Risk"
    elif risk_factors >= 3:
        return "Medium Risk"
    elif risk_factors >= 1:
        return "Low Risk"
    else:
        return "No Risk"


def determine_performance_category(avg_score: float) -> str:
    """
    Categorize performance based on average score
    
    Args:
        avg_score: Average score
        
    Returns:
        Performance category
    """
    if avg_score >= 90:
        return "Excellent"
    elif avg_score >= 80:
        return "Good"
    elif avg_score >= 70:
        return "Satisfactory"
    elif avg_score >= 60:
        return "Needs Improvement"
    else:
        return "At Risk"


def format_timestamp(timestamp: Any = None) -> str:
    """
    Format timestamp to ISO format
    
    Args:
        timestamp: Timestamp to format (defaults to current time)
        
    Returns:
        ISO formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    elif isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            timestamp = datetime.now(timezone.utc)
    elif not isinstance(timestamp, datetime):
        timestamp = datetime.now(timezone.utc)
    
    return timestamp.isoformat()


def generate_student_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate insights for a student record
    
    Args:
        data: Student data dictionary
        
    Returns:
        Dictionary with insights
    """
    insights = {}
    
    # Calculate metrics
    avg_score = calculate_average_score(data)
    risk_level = determine_risk_level(data)
    
    insights['average_score'] = avg_score
    insights['risk_level'] = risk_level
    
    if avg_score is not None:
        insights['performance_category'] = determine_performance_category(avg_score)
    
    # Subject-specific insights
    subject = data.get('subject')
    if subject:
        insights['subject_focus'] = subject
        
        # Subject-specific score
        subject_score_map = {
            'Mathematics': 'math_score',
            'English': 'reading_score',  # Could also use writing_score
            'Science': 'math_score'  # Science often correlates with math
        }
        
        if subject in subject_score_map:
            score_field = subject_score_map[subject]
            if score_field in data:
                insights[f'{subject.lower()}_score'] = data[score_field]
    
    # Attendance insights
    attendance_rate = data.get('attendance_rate')
    if attendance_rate is not None:
        if attendance_rate < 0.8:
            insights['attendance_concern'] = True
            insights['attendance_recommendation'] = "Monitor attendance closely"
        else:
            insights['attendance_concern'] = False
    
    # Assignment completion insights
    completion_rate = data.get('assignment_completion_rate')
    if completion_rate is not None:
        if completion_rate < 0.7:
            insights['completion_concern'] = True
            insights['completion_recommendation'] = "Provide additional assignment support"
        else:
            insights['completion_concern'] = False
    
    return insights


def create_data_quality_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a data quality report for a student record
    
    Args:
        data: Student data dictionary
        
    Returns:
        Data quality report
    """
    report = {
        'timestamp': format_timestamp(),
        'student_id': data.get('student_id'),
        'completeness': {},
        'validity': {},
        'overall_quality': 'Good'
    }
    
    # Check completeness
    required_fields = ['student_id', 'name']
    optional_fields = ['math_score', 'reading_score', 'writing_score', 'grade_level', 'subject']
    
    for field in required_fields:
        report['completeness'][field] = field in data and data[field] is not None
    
    for field in optional_fields:
        if field in data:
            report['completeness'][field] = data[field] is not None
    
    # Check validity
    score_fields = ['math_score', 'reading_score', 'writing_score']
    for field in score_fields:
        if field in data and data[field] is not None:
            try:
                score = float(data[field])
                report['validity'][field] = 0 <= score <= 100
            except (ValueError, TypeError):
                report['validity'][field] = False
    
    # Overall quality assessment
    completeness_score = sum(report['completeness'].values()) / len(report['completeness'])
    validity_issues = sum(1 for v in report['validity'].values() if not v)
    
    if completeness_score < 0.7 or validity_issues > 2:
        report['overall_quality'] = 'Poor'
    elif completeness_score < 0.9 or validity_issues > 0:
        report['overall_quality'] = 'Fair'
    
    return report
