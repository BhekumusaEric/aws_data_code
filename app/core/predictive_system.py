#!/usr/bin/env python3
"""
Core Predictive Intervention System
Main business logic and data processing
"""

import pandas as pd
import numpy as np
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


class PredictiveInterventionSystem:
    """AI-powered predictive intervention system for student success"""
    
    def __init__(self):
        self.aws_configured = self.check_aws_connection()
        self.sample_data = self.generate_enhanced_sample_data()
        self.intervention_strategies = self.load_intervention_strategies()
    
    def check_aws_connection(self) -> bool:
        """Check if AWS is configured"""
        try:
            sts = boto3.client('sts')
            sts.get_caller_identity()
            return True
        except Exception:
            return False
    
    def generate_enhanced_sample_data(self) -> pd.DataFrame:
        """Generate enhanced sample data with predictive features"""
        np.random.seed(42)
        
        students = []
        subjects = ['Mathematics', 'English', 'Science', 'History', 'Art']
        grades = ['9', '10', '11', '12']
        
        for i in range(100):  # Smaller dataset for detailed analysis
            # Generate realistic student progression
            base_ability = np.random.normal(75, 15)
            motivation_factor = np.random.uniform(0.6, 1.0)
            support_factor = np.random.uniform(0.7, 1.0)
            
            # Generate historical performance (last 6 months)
            historical_scores = []
            current_performance = base_ability
            
            for month in range(6):
                # Add trend and noise
                trend = np.random.normal(0, 2)  # Small monthly changes
                noise = np.random.normal(0, 5)
                current_performance = max(0, min(100, current_performance + trend + noise))
                historical_scores.append(current_performance)
            
            # Calculate predictive features
            performance_trend = np.polyfit(range(6), historical_scores, 1)[0]  # Slope
            performance_volatility = np.std(historical_scores)
            recent_performance = np.mean(historical_scores[-2:])  # Last 2 months
            
            student = {
                'student_id': f'STU{i+1:04d}',
                'name': f'Student {i+1}',
                'grade_level': np.random.choice(grades),
                'subject': np.random.choice(subjects),
                
                # Current performance
                'current_score': recent_performance,
                'attendance_rate': max(0.5, min(1.0, motivation_factor + np.random.normal(0, 0.1))),
                'assignment_completion_rate': max(0.4, min(1.0, motivation_factor + np.random.normal(0, 0.15))),
                
                # Predictive features
                'performance_trend': performance_trend,  # Positive = improving, Negative = declining
                'performance_volatility': performance_volatility,
                'historical_scores': historical_scores,
                
                # Risk factors
                'engagement_level': motivation_factor,
                'support_level': support_factor,
                'last_updated': datetime.now() - timedelta(days=np.random.randint(1, 30))
            }
            
            # Calculate composite risk score
            student['risk_score'] = self.calculate_risk_score(student)
            student['risk_level'] = self.categorize_risk(student['risk_score'])
            
            students.append(student)
        
        return pd.DataFrame(students)
    
    def calculate_risk_score(self, student: Dict) -> float:
        """Calculate comprehensive risk score (0-100, higher = more risk)"""
        # Performance factors (40% weight)
        performance_risk = max(0, (80 - student['current_score']) / 80 * 40)
        
        # Trend factors (25% weight)
        trend_risk = max(0, -student['performance_trend'] * 5) * 25 / 10
        
        # Engagement factors (20% weight)
        attendance_risk = max(0, (0.9 - student['attendance_rate']) / 0.9 * 20)
        
        # Completion factors (15% weight)
        completion_risk = max(0, (0.9 - student['assignment_completion_rate']) / 0.9 * 15)
        
        total_risk = performance_risk + trend_risk + attendance_risk + completion_risk
        return min(100, max(0, total_risk))
    
    def categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level based on score"""
        if risk_score < 30:
            return "Low"
        elif risk_score < 60:
            return "Medium"
        else:
            return "High"
    
    def load_intervention_strategies(self) -> Dict:
        """Load intervention strategies database"""
        return {
            "academic_support": {
                "tutoring": {
                    "description": "One-on-one or small group tutoring sessions",
                    "effectiveness": 0.85,
                    "time_commitment": "2-3 hours/week",
                    "cost": "Medium",
                    "suitable_for": ["Low performance", "Specific subject struggles"]
                },
                "study_skills": {
                    "description": "Teaching effective study techniques and time management",
                    "effectiveness": 0.75,
                    "time_commitment": "1 hour/week",
                    "cost": "Low",
                    "suitable_for": ["Poor study habits", "Time management issues"]
                }
            },
            "engagement_support": {
                "mentoring": {
                    "description": "Pairing with older student or adult mentor",
                    "effectiveness": 0.80,
                    "time_commitment": "1 hour/week",
                    "cost": "Low",
                    "suitable_for": ["Low motivation", "Social isolation"]
                },
                "extracurricular": {
                    "description": "Involvement in clubs, sports, or activities",
                    "effectiveness": 0.70,
                    "time_commitment": "2-4 hours/week",
                    "cost": "Variable",
                    "suitable_for": ["Low engagement", "Social connection needs"]
                }
            },
            "family_support": {
                "parent_communication": {
                    "description": "Regular communication with parents about progress",
                    "effectiveness": 0.75,
                    "time_commitment": "30 minutes/week",
                    "cost": "Low",
                    "suitable_for": ["All students", "Communication gaps"]
                },
                "home_strategies": {
                    "description": "Providing parents with specific home support strategies",
                    "effectiveness": 0.70,
                    "time_commitment": "Ongoing",
                    "cost": "Low",
                    "suitable_for": ["Home environment issues", "Parent engagement"]
                }
            }
        }
    
    def get_student_data(self, filters: Dict = None) -> pd.DataFrame:
        """Get filtered student data"""
        data = self.sample_data.copy()
        
        if filters:
            if 'grade_levels' in filters and filters['grade_levels']:
                data = data[data['grade_level'].isin(filters['grade_levels'])]
            
            if 'subjects' in filters and filters['subjects']:
                data = data[data['subject'].isin(filters['subjects'])]
            
            if 'risk_levels' in filters and filters['risk_levels']:
                data = data[data['risk_level'].isin(filters['risk_levels'])]
        
        return data
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """Get individual student data"""
        student_data = self.sample_data[self.sample_data['student_id'] == student_id]
        if not student_data.empty:
            return student_data.iloc[0].to_dict()
        return None
    
    def predict_future_performance(self, student_data: Dict, months_ahead: int = 3) -> Dict:
        """Predict future performance based on current trends"""
        current_score = student_data['current_score']
        trend = student_data['performance_trend']
        volatility = student_data['performance_volatility']
        
        # Simple linear projection with uncertainty
        predicted_scores = []
        for month in range(1, months_ahead + 1):
            predicted_score = current_score + (trend * month)
            # Add uncertainty bounds
            uncertainty = volatility * np.sqrt(month)  # Uncertainty grows with time
            
            predicted_scores.append({
                'month': month,
                'predicted_score': max(0, min(100, predicted_score)),
                'lower_bound': max(0, min(100, predicted_score - uncertainty)),
                'upper_bound': max(0, min(100, predicted_score + uncertainty)),
                'confidence': max(0.5, 1.0 - (month * 0.1))  # Confidence decreases over time
            })
        
        return {
            'predictions': predicted_scores,
            'trend_direction': 'improving' if trend > 0 else 'declining' if trend < 0 else 'stable',
            'confidence_level': 'high' if volatility < 5 else 'medium' if volatility < 10 else 'low'
        }
    
    def generate_intervention_recommendations(self, student_data: Dict) -> List[Dict]:
        """Generate personalized intervention recommendations"""
        recommendations = []
        risk_score = student_data['risk_score']
        
        # Academic performance interventions
        if student_data['current_score'] < 70:
            recommendations.append({
                'category': 'Academic Support',
                'intervention': 'tutoring',
                'priority': 'High' if student_data['current_score'] < 60 else 'Medium',
                'description': 'One-on-one tutoring in ' + student_data['subject'],
                'expected_improvement': '15-25 points',
                'timeline': '4-6 weeks',
                'resources_needed': ['Qualified tutor', '2-3 hours/week'],
                'success_indicators': ['Improved test scores', 'Better assignment completion']
            })
        
        # Attendance interventions
        if student_data['attendance_rate'] < 0.85:
            recommendations.append({
                'category': 'Engagement Support',
                'intervention': 'attendance_monitoring',
                'priority': 'High',
                'description': 'Daily check-ins and attendance tracking',
                'expected_improvement': 'Improved attendance rate',
                'timeline': '2-4 weeks',
                'resources_needed': ['Daily monitoring system', 'Parent communication'],
                'success_indicators': ['Consistent attendance', 'Reduced absences']
            })
        
        # Assignment completion interventions
        if student_data['assignment_completion_rate'] < 0.80:
            recommendations.append({
                'category': 'Academic Support',
                'intervention': 'study_skills',
                'priority': 'Medium',
                'description': 'Study skills and time management training',
                'expected_improvement': 'Better organization and completion rates',
                'timeline': '3-4 weeks',
                'resources_needed': ['Study skills curriculum', '1 hour/week'],
                'success_indicators': ['Improved completion rate', 'Better organization']
            })
        
        # Trend-based interventions
        if student_data['performance_trend'] < -1:  # Declining performance
            recommendations.append({
                'category': 'Early Intervention',
                'intervention': 'immediate_support',
                'priority': 'High',
                'description': 'Immediate intervention to address declining performance',
                'expected_improvement': 'Stabilize and reverse decline',
                'timeline': '1-2 weeks',
                'resources_needed': ['Teacher meeting', 'Parent conference', 'Support plan'],
                'success_indicators': ['Stabilized performance', 'Improved engagement']
            })
        
        return sorted(recommendations, key=lambda x: {'High': 3, 'Medium': 2, 'Low': 1}[x['priority']], reverse=True)
    
    def get_dashboard_metrics(self, filters: Dict = None) -> Dict:
        """Calculate dashboard metrics"""
        data = self.get_student_data(filters)
        
        total_students = len(data)
        high_risk_students = len(data[data['risk_level'] == 'High'])
        medium_risk_students = len(data[data['risk_level'] == 'Medium'])
        low_risk_students = len(data[data['risk_level'] == 'Low'])
        
        avg_score = data['current_score'].mean()
        avg_attendance = data['attendance_rate'].mean()
        avg_completion = data['assignment_completion_rate'].mean()
        
        # Calculate trends
        improving_students = len(data[data['performance_trend'] > 0.5])
        declining_students = len(data[data['performance_trend'] < -0.5])
        
        return {
            'total_students': total_students,
            'risk_distribution': {
                'high': high_risk_students,
                'medium': medium_risk_students,
                'low': low_risk_students
            },
            'performance_metrics': {
                'average_score': avg_score,
                'average_attendance': avg_attendance * 100,
                'average_completion': avg_completion * 100
            },
            'trends': {
                'improving': improving_students,
                'declining': declining_students,
                'stable': total_students - improving_students - declining_students
            }
        }
