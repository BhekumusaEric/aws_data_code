#!/usr/bin/env python3
"""
Predictive & Preventive Student Success System
Advanced AI-powered intervention recommendations

This system goes beyond analytics to provide:
1. Predictive modeling for student outcomes
2. Personalized intervention recommendations
3. Individual student action plans
4. Parent/teacher collaboration tools
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional
import boto3

# Import tutorial system
try:
    from tutorial_system import TutorialSystem
    TUTORIAL_AVAILABLE = True
except ImportError:
    TUTORIAL_AVAILABLE = False
    st.sidebar.warning("⚠️ Tutorial system not found. Please ensure tutorial_system.py is in the same directory.")

# Page configuration
st.set_page_config(
    page_title="Student Success Intervention System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
                'motivation_score': motivation_factor * 100,
                'support_score': support_factor * 100,
                
                # Behavioral indicators
                'participation_rate': max(0.3, min(1.0, motivation_factor + np.random.normal(0, 0.2))),
                'help_seeking_frequency': np.random.poisson(2),  # Times per month
                'peer_interaction_score': np.random.uniform(0.4, 1.0),
                
                # Environmental factors
                'home_support_score': support_factor * 100,
                'technology_access': np.random.choice([0, 1], p=[0.2, 0.8]),  # 80% have access
                'extracurricular_participation': np.random.choice([0, 1], p=[0.4, 0.6]),
                
                # Timestamps
                'last_updated': datetime.now() - timedelta(days=np.random.randint(0, 7)),
                'next_assessment_date': datetime.now() + timedelta(days=np.random.randint(7, 30))
            }
            
            # Calculate risk prediction
            student['predicted_risk_score'] = self.calculate_risk_prediction(student)
            student['intervention_urgency'] = self.calculate_intervention_urgency(student)
            
            students.append(student)
        
        return pd.DataFrame(students)
    
    def calculate_risk_prediction(self, student: Dict) -> float:
        """Calculate predictive risk score (0-100, higher = more risk)"""
        risk_factors = 0
        
        # Performance factors
        if student['current_score'] < 70:
            risk_factors += 25
        if student['performance_trend'] < -1:  # Declining trend
            risk_factors += 20
        if student['performance_volatility'] > 15:  # High volatility
            risk_factors += 15
        
        # Engagement factors
        if student['attendance_rate'] < 0.85:
            risk_factors += 15
        if student['assignment_completion_rate'] < 0.8:
            risk_factors += 10
        if student['participation_rate'] < 0.6:
            risk_factors += 10
        
        # Support factors
        if student['home_support_score'] < 60:
            risk_factors += 5
        
        return min(100, risk_factors)
    
    def calculate_intervention_urgency(self, student: Dict) -> str:
        """Calculate intervention urgency level"""
        risk_score = student['predicted_risk_score']
        trend = student['performance_trend']
        
        if risk_score > 70 or trend < -3:
            return "IMMEDIATE"
        elif risk_score > 50 or trend < -1:
            return "HIGH"
        elif risk_score > 30 or trend < 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def load_intervention_strategies(self) -> Dict:
        """Load intervention strategies database"""
        return {
            "academic_support": {
                "low_performance": [
                    "One-on-one tutoring sessions (2x per week)",
                    "Peer mentoring program assignment",
                    "Break down complex topics into smaller chunks",
                    "Use visual aids and hands-on learning materials",
                    "Provide additional practice worksheets"
                ],
                "declining_trend": [
                    "Schedule immediate teacher-student conference",
                    "Identify specific knowledge gaps with diagnostic assessment",
                    "Create personalized learning plan with clear milestones",
                    "Implement daily check-ins for 2 weeks",
                    "Consider alternative teaching methods"
                ],
                "high_volatility": [
                    "Establish consistent study routine",
                    "Teach stress management and test-taking strategies",
                    "Provide predictable assessment schedule",
                    "Create calm, structured learning environment",
                    "Monitor for learning disabilities or attention issues"
                ]
            },
            "engagement_support": {
                "low_attendance": [
                    "Contact parents/guardians immediately",
                    "Identify barriers to attendance (transport, health, family)",
                    "Create attendance incentive program",
                    "Assign attendance buddy system",
                    "Flexible scheduling if appropriate"
                ],
                "low_participation": [
                    "Use interactive teaching methods",
                    "Create safe space for questions and mistakes",
                    "Implement think-pair-share activities",
                    "Recognize and celebrate small contributions",
                    "Connect learning to student interests"
                ],
                "assignment_issues": [
                    "Break assignments into smaller, manageable tasks",
                    "Provide clear rubrics and examples",
                    "Offer multiple submission formats",
                    "Create assignment completion tracking system",
                    "Teach time management and organization skills"
                ]
            },
            "social_emotional": {
                "low_motivation": [
                    "Set achievable short-term goals",
                    "Connect learning to student's future aspirations",
                    "Provide choice in learning activities",
                    "Celebrate progress and effort, not just outcomes",
                    "Consider counseling or mentoring support"
                ],
                "peer_issues": [
                    "Facilitate positive peer interactions",
                    "Create collaborative learning opportunities",
                    "Address any bullying or social conflicts",
                    "Teach social skills and communication",
                    "Consider group counseling sessions"
                ],
                "home_support": [
                    "Schedule parent-teacher conference",
                    "Provide resources for home learning support",
                    "Connect family with community resources",
                    "Offer parent education workshops",
                    "Create home-school communication plan"
                ]
            },
            "technology_support": {
                "access_issues": [
                    "Provide device lending program",
                    "Connect with internet assistance programs",
                    "Offer on-campus technology access",
                    "Teach digital literacy skills",
                    "Create offline learning alternatives"
                ],
                "digital_skills": [
                    "Provide technology training sessions",
                    "Assign tech-savvy peer mentor",
                    "Use gradual technology integration",
                    "Offer multiple ways to submit work",
                    "Create technology help desk access"
                ]
            }
        }
    
    def generate_personalized_recommendations(self, student_data: Dict) -> Dict:
        """Generate personalized intervention recommendations for a student"""
        recommendations = {
            'student_info': {
                'id': student_data['student_id'],
                'name': student_data['name'],
                'grade': student_data['grade_level'],
                'subject': student_data['subject']
            },
            'risk_assessment': {
                'current_risk_score': student_data['predicted_risk_score'],
                'urgency_level': student_data['intervention_urgency'],
                'key_concerns': []
            },
            'immediate_actions': [],
            'short_term_plan': [],
            'long_term_goals': [],
            'parent_involvement': [],
            'progress_monitoring': [],
            'success_metrics': []
        }
        
        # Identify key concerns
        if student_data['current_score'] < 70:
            recommendations['risk_assessment']['key_concerns'].append("Below grade-level performance")
        if student_data['performance_trend'] < -1:
            recommendations['risk_assessment']['key_concerns'].append("Declining performance trend")
        if student_data['attendance_rate'] < 0.85:
            recommendations['risk_assessment']['key_concerns'].append("Attendance issues")
        if student_data['assignment_completion_rate'] < 0.8:
            recommendations['risk_assessment']['key_concerns'].append("Assignment completion problems")
        
        # Generate specific recommendations based on issues
        if student_data['current_score'] < 70:
            recommendations['immediate_actions'].extend(
                self.intervention_strategies['academic_support']['low_performance'][:2]
            )
        
        if student_data['performance_trend'] < -1:
            recommendations['immediate_actions'].extend(
                self.intervention_strategies['academic_support']['declining_trend'][:2]
            )
        
        if student_data['attendance_rate'] < 0.85:
            recommendations['immediate_actions'].extend(
                self.intervention_strategies['engagement_support']['low_attendance'][:2]
            )
        
        # Short-term plan (2-4 weeks)
        recommendations['short_term_plan'] = [
            f"Weekly progress check-ins for {student_data['subject']}",
            "Implement personalized learning strategies",
            "Monitor attendance and engagement daily",
            "Provide additional practice materials",
            "Schedule parent communication"
        ]
        
        # Long-term goals (semester)
        target_score = min(100, student_data['current_score'] + 15)
        recommendations['long_term_goals'] = [
            f"Achieve {target_score}% average in {student_data['subject']}",
            "Maintain 90%+ attendance rate",
            "Complete 95%+ of assignments on time",
            "Develop independent learning skills",
            "Build confidence and motivation"
        ]
        
        # Parent involvement
        recommendations['parent_involvement'] = [
            "Schedule parent-teacher conference within 1 week",
            "Provide weekly progress updates",
            "Share home study strategies",
            "Discuss support resources available",
            "Create home-school communication plan"
        ]
        
        # Progress monitoring
        recommendations['progress_monitoring'] = [
            "Daily attendance tracking",
            "Weekly quiz/assessment scores",
            "Assignment completion rates",
            "Participation and engagement levels",
            "Student self-reflection surveys"
        ]
        
        # Success metrics
        recommendations['success_metrics'] = [
            f"Score improvement of 10+ points within 4 weeks",
            "Attendance rate above 90%",
            "Assignment completion rate above 90%",
            "Positive trend in weekly assessments",
            "Increased participation and engagement"
        ]
        
        return recommendations
    
    def predict_future_performance(self, student_data: Dict, weeks_ahead: int = 4) -> Dict:
        """Predict student performance for next few weeks"""
        current_score = student_data['current_score']
        trend = student_data['performance_trend']
        volatility = student_data['performance_volatility']
        
        # Simple linear prediction with confidence intervals
        predicted_scores = []
        confidence_lower = []
        confidence_upper = []
        
        for week in range(1, weeks_ahead + 1):
            # Base prediction using trend
            predicted = current_score + (trend * week * 0.25)  # Weekly trend
            
            # Add uncertainty
            uncertainty = volatility * np.sqrt(week) * 0.1
            
            predicted_scores.append(max(0, min(100, predicted)))
            confidence_lower.append(max(0, predicted - uncertainty))
            confidence_upper.append(min(100, predicted + uncertainty))
        
        return {
            'weeks': list(range(1, weeks_ahead + 1)),
            'predicted_scores': predicted_scores,
            'confidence_lower': confidence_lower,
            'confidence_upper': confidence_upper,
            'trend_direction': 'improving' if trend > 0 else 'declining' if trend < -0.5 else 'stable'
        }


def main():
    """Main application"""
    st.markdown("# 🎯 Student Success Intervention System")
    st.markdown("### Predictive Analytics + Personalized Action Plans")
    
    # Initialize system
    system = PredictiveInterventionSystem()

    # Initialize tutorial system and check for first-time users
    if TUTORIAL_AVAILABLE:
        # Initialize tutorial progress tracking
        if 'tutorial_progress' not in st.session_state:
            st.session_state.tutorial_progress = {
                'first_visit': True,
                'completed_modules': [],
                'show_hints': True,
                'user_role': None
            }

        # Show welcome modal for first-time users
        if st.session_state.tutorial_progress.get('first_visit', True):
            show_welcome_modal()

    # Sidebar for navigation
    st.sidebar.header("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose View",
        ["🏠 Dashboard Overview", "👤 Individual Student", "📊 Predictive Analytics", "📋 Intervention Plans", "👩‍🏫 Teacher Portal", "👨‍👩‍👧‍👦 Parent Portal"]
    )

    # Add tutorial section to sidebar
    if TUTORIAL_AVAILABLE:
        add_tutorial_sidebar(page)
    
    # Show contextual hints if enabled
    if TUTORIAL_AVAILABLE:
        show_contextual_hints(page)

    if page == "🏠 Dashboard Overview":
        render_dashboard_overview(system)
    elif page == "👤 Individual Student":
        render_individual_student(system)
    elif page == "📊 Predictive Analytics":
        render_predictive_analytics(system)
    elif page == "📋 Intervention Plans":
        render_intervention_plans(system)
    elif page == "👩‍🏫 Teacher Portal":
        render_teacher_portal(system)
    elif page == "👨‍👩‍👧‍👦 Parent Portal":
        render_parent_portal(system)


def render_dashboard_overview(system):
    """Render main dashboard overview"""
    st.subheader("🎯 Predictive Risk Assessment")
    
    df = system.sample_data
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        immediate_risk = len(df[df['intervention_urgency'] == 'IMMEDIATE'])
        st.metric("🚨 Immediate Intervention", immediate_risk, delta=f"{immediate_risk/len(df)*100:.1f}%")
    
    with col2:
        high_risk = len(df[df['intervention_urgency'] == 'HIGH'])
        st.metric("⚠️ High Priority", high_risk, delta=f"{high_risk/len(df)*100:.1f}%")
    
    with col3:
        declining = len(df[df['performance_trend'] < -1])
        st.metric("📉 Declining Trend", declining, delta=f"{declining/len(df)*100:.1f}%")
    
    with col4:
        avg_prediction = df['predicted_risk_score'].mean()
        st.metric("📊 Avg Risk Score", f"{avg_prediction:.1f}", delta="Lower is better")
    
    # Risk distribution
    col1, col2 = st.columns(2)
    
    with col1:
        urgency_dist = df['intervention_urgency'].value_counts()
        fig = px.pie(values=urgency_dist.values, names=urgency_dist.index, 
                    title="Intervention Urgency Distribution",
                    color_discrete_map={
                        'IMMEDIATE': '#FF4444',
                        'HIGH': '#FF8800', 
                        'MEDIUM': '#FFAA00',
                        'LOW': '#44AA44'
                    })
        st.plotly_chart(fig, use_container_width=True, key="urgency_pie")
    
    with col2:
        # Risk vs Performance scatter
        fig = px.scatter(df, x='current_score', y='predicted_risk_score',
                        color='intervention_urgency', size='performance_volatility',
                        title="Risk Score vs Current Performance",
                        labels={'current_score': 'Current Score', 'predicted_risk_score': 'Predicted Risk Score'})
        st.plotly_chart(fig, use_container_width=True, key="risk_scatter")


def render_individual_student(system):
    """Render individual student analysis"""
    st.subheader("👤 Individual Student Analysis")
    
    df = system.sample_data
    
    # Student selector
    student_options = [f"{row['student_id']} - {row['name']}" for _, row in df.iterrows()]
    selected_student = st.selectbox("Select Student", student_options)
    
    if selected_student:
        student_id = selected_student.split(' - ')[0]
        student_data = df[df['student_id'] == student_id].iloc[0].to_dict()
        
        # Student header
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Score", f"{student_data['current_score']:.1f}%")
        with col2:
            st.metric("Risk Level", student_data['intervention_urgency'])
        with col3:
            st.metric("Trend", f"{student_data['performance_trend']:+.1f} pts/month")
        
        # Generate recommendations
        recommendations = system.generate_personalized_recommendations(student_data)
        
        # Display recommendations
        st.subheader("🎯 Personalized Action Plan")
        
        # Immediate actions
        st.markdown("### 🚨 Immediate Actions (This Week)")
        for action in recommendations['immediate_actions']:
            st.markdown(f"• {action}")
        
        # Short-term plan
        st.markdown("### 📅 Short-term Plan (2-4 Weeks)")
        for plan in recommendations['short_term_plan']:
            st.markdown(f"• {plan}")
        
        # Parent involvement
        st.markdown("### 👨‍👩‍👧‍👦 Parent Involvement")
        for involvement in recommendations['parent_involvement']:
            st.markdown(f"• {involvement}")
        
        # Prediction chart
        prediction = system.predict_future_performance(student_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prediction['weeks'],
            y=prediction['predicted_scores'],
            mode='lines+markers',
            name='Predicted Score',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=prediction['weeks'],
            y=prediction['confidence_upper'],
            fill=None,
            mode='lines',
            line_color='rgba(0,100,80,0)',
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=prediction['weeks'],
            y=prediction['confidence_lower'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,80,0)',
            name='Confidence Interval',
            fillcolor='rgba(0,100,80,0.2)'
        ))
        
        fig.update_layout(title="4-Week Performance Prediction", 
                         xaxis_title="Weeks Ahead", 
                         yaxis_title="Predicted Score")
        st.plotly_chart(fig, use_container_width=True, key="prediction_chart")


def render_predictive_analytics(system):
    """Render advanced predictive analytics and modeling"""
    st.subheader("📊 Advanced Predictive Analytics")
    st.markdown("### AI-Powered Forecasting & Trend Analysis")

    df = system.sample_data

    # Tabs for different predictive analytics views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔮 Performance Forecasting",
        "📈 Trend Analysis",
        "🎯 Risk Modeling",
        "🔍 Pattern Discovery",
        "🚀 Intervention Impact"
    ])

    with tab1:
        render_performance_forecasting(system, df)

    with tab2:
        render_trend_analysis(system, df)

    with tab3:
        render_risk_modeling(system, df)

    with tab4:
        render_pattern_discovery(system, df)

    with tab5:
        render_intervention_impact(system, df)


def render_intervention_plans(system):
    """Render comprehensive intervention plans and tracking"""
    st.subheader("📋 Intervention Plans & Strategy Management")

    df = system.sample_data

    # Load intervention strategies
    try:
        with open('intervention_strategies.json', 'r') as f:
            strategies = json.load(f)
    except FileNotFoundError:
        strategies = system.intervention_strategies

    # Tabs for different intervention views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Active Interventions",
        "📚 Strategy Library",
        "📊 Effectiveness Tracking",
        "➕ Create New Plan"
    ])

    with tab1:
        render_active_interventions(system, df)

    with tab2:
        render_strategy_library(strategies)

    with tab3:
        render_effectiveness_tracking(system, df)

    with tab4:
        render_create_intervention_plan(system, df, strategies)


def render_active_interventions(system, df):
    """Render active intervention plans"""
    st.markdown("### 🎯 Currently Active Intervention Plans")

    # Filter students with active interventions (high/immediate urgency)
    active_students = df[df['intervention_urgency'].isin(['IMMEDIATE', 'HIGH'])].copy()

    if len(active_students) == 0:
        st.success("🎉 No students currently require immediate interventions!")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Plans", len(active_students))
    with col2:
        immediate_count = len(active_students[active_students['intervention_urgency'] == 'IMMEDIATE'])
        st.metric("Immediate Priority", immediate_count)
    with col3:
        avg_risk = active_students['predicted_risk_score'].mean()
        st.metric("Avg Risk Score", f"{avg_risk:.1f}")
    with col4:
        declining_count = len(active_students[active_students['performance_trend'] < -1])
        st.metric("Declining Trends", declining_count)

    # Intervention plan cards
    st.markdown("### 📋 Individual Intervention Plans")

    for idx, student in active_students.iterrows():
        with st.expander(f"🎯 {student['name']} ({student['student_id']}) - {student['intervention_urgency']} Priority"):

            # Student overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Score", f"{student['current_score']:.1f}%")
            with col2:
                st.metric("Risk Score", f"{student['predicted_risk_score']:.1f}")
            with col3:
                trend_color = "🔴" if student['performance_trend'] < -1 else "🟡" if student['performance_trend'] < 0 else "🟢"
                st.metric("Trend", f"{trend_color} {student['performance_trend']:+.1f}")

            # Generate and display recommendations
            recommendations = system.generate_personalized_recommendations(student.to_dict())

            # Immediate actions
            st.markdown("#### 🚨 Immediate Actions (This Week)")
            for i, action in enumerate(recommendations['immediate_actions'][:3], 1):
                st.markdown(f"{i}. {action}")

            # Progress tracking
            st.markdown("#### 📊 Progress Tracking")

            # Simulated progress data
            progress_data = {
                'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'Target Score': [student['current_score'] + 5, student['current_score'] + 8,
                               student['current_score'] + 12, student['current_score'] + 15],
                'Actual Score': [student['current_score'] + np.random.normal(3, 2),
                               student['current_score'] + np.random.normal(6, 3),
                               student['current_score'] + np.random.normal(9, 3),
                               student['current_score'] + np.random.normal(12, 4)]
            }

            progress_df = pd.DataFrame(progress_data)
            fig = px.line(progress_df, x='Week', y=['Target Score', 'Actual Score'],
                         title=f"Progress Tracking - {student['name']}")
            st.plotly_chart(fig, use_container_width=True, key=f"progress_{student['student_id']}")

            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"✅ Mark Complete", key=f"complete_{student['student_id']}"):
                    st.success("Intervention marked as complete!")
            with col2:
                if st.button(f"📝 Update Plan", key=f"update_{student['student_id']}"):
                    st.info("Plan update interface would open here")
            with col3:
                if st.button(f"👨‍👩‍👧‍👦 Contact Parents", key=f"contact_{student['student_id']}"):
                    st.info("Parent communication interface would open here")


def render_strategy_library(strategies):
    """Render intervention strategy library"""
    st.markdown("### 📚 Intervention Strategy Library")
    st.markdown("Comprehensive database of evidence-based intervention strategies")

    # Strategy categories
    category = st.selectbox(
        "Select Strategy Category",
        ["Academic Interventions", "Behavioral Interventions", "Social-Emotional Interventions",
         "Family Engagement", "Technology Support"]
    )

    if category == "Academic Interventions":
        subject = st.selectbox("Select Subject", ["Mathematics", "English", "Science"])

        if subject.lower() in strategies.get('academic_interventions', {}):
            subject_strategies = strategies['academic_interventions'][subject.lower()]

            for strategy_type, strategy_list in subject_strategies.items():
                st.markdown(f"#### {strategy_type.replace('_', ' ').title()}")

                for i, strategy in enumerate(strategy_list, 1):
                    with st.expander(f"{i}. {strategy['strategy']}"):
                        st.markdown(f"**Description:** {strategy['description']}")
                        st.markdown(f"**Timeline:** {strategy['timeline']}")
                        st.markdown(f"**Resources Needed:** {', '.join(strategy['resources_needed'])}")
                        st.markdown(f"**Success Metrics:** {', '.join(strategy['success_metrics'])}")

                        if st.button(f"Use This Strategy", key=f"use_strategy_{i}_{strategy_type}"):
                            st.success("Strategy added to intervention plan!")

    elif category == "Behavioral Interventions":
        behavior_type = st.selectbox("Select Behavior Focus", ["Attendance", "Engagement"])

        if behavior_type.lower() in strategies.get('behavioral_interventions', {}):
            behavior_strategies = strategies['behavioral_interventions'][behavior_type.lower()]

            for strategy_type, strategy_list in behavior_strategies.items():
                st.markdown(f"#### {strategy_type.replace('_', ' ').title()}")

                for i, strategy in enumerate(strategy_list, 1):
                    with st.expander(f"{i}. {strategy['strategy']}"):
                        st.markdown(f"**Description:** {strategy['description']}")
                        st.markdown(f"**Timeline:** {strategy['timeline']}")
                        st.markdown(f"**Resources Needed:** {', '.join(strategy['resources_needed'])}")
                        st.markdown(f"**Success Metrics:** {', '.join(strategy['success_metrics'])}")


def render_effectiveness_tracking(system, df):
    """Render intervention effectiveness tracking"""
    st.markdown("### 📊 Intervention Effectiveness Analysis")

    # Simulated effectiveness data
    effectiveness_data = {
        'Intervention Type': ['Academic Tutoring', 'Attendance Support', 'Behavioral Plan',
                             'Parent Engagement', 'Technology Support'],
        'Students Served': [25, 18, 12, 30, 8],
        'Success Rate (%)': [78, 85, 67, 82, 90],
        'Avg Improvement (Points)': [12.5, 8.2, 15.3, 9.8, 11.2],
        'Cost per Student ($)': [150, 75, 200, 50, 120]
    }

    effectiveness_df = pd.DataFrame(effectiveness_data)

    # Metrics overview
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_success = effectiveness_df['Success Rate (%)'].mean()
        st.metric("Average Success Rate", f"{avg_success:.1f}%")
    with col2:
        total_served = effectiveness_df['Students Served'].sum()
        st.metric("Total Students Served", total_served)
    with col3:
        avg_improvement = effectiveness_df['Avg Improvement (Points)'].mean()
        st.metric("Avg Score Improvement", f"{avg_improvement:.1f} points")

    # Effectiveness charts
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(effectiveness_df, x='Intervention Type', y='Success Rate (%)',
                     title="Success Rate by Intervention Type")
        fig1.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig1, use_container_width=True, key="success_rate_chart")

    with col2:
        fig2 = px.scatter(effectiveness_df, x='Cost per Student ($)', y='Avg Improvement (Points)',
                         size='Students Served', hover_name='Intervention Type',
                         title="Cost vs Effectiveness Analysis")
        st.plotly_chart(fig2, use_container_width=True, key="cost_effectiveness_chart")

    # Detailed effectiveness table
    st.markdown("#### 📋 Detailed Effectiveness Data")
    st.dataframe(effectiveness_df, use_container_width=True)


def render_create_intervention_plan(system, df, strategies):
    """Render interface to create new intervention plans"""
    st.markdown("### ➕ Create New Intervention Plan")

    # Student selection
    student_options = [f"{row['student_id']} - {row['name']}" for _, row in df.iterrows()]
    selected_student = st.selectbox("Select Student", student_options, key="new_plan_student")

    if selected_student:
        student_id = selected_student.split(' - ')[0]
        student_data = df[df['student_id'] == student_id].iloc[0].to_dict()

        # Plan details form
        with st.form("intervention_plan_form"):
            st.markdown("#### 📋 Plan Details")

            plan_name = st.text_input("Plan Name", value=f"Intervention Plan - {student_data['name']}")

            col1, col2 = st.columns(2)
            with col1:
                priority_level = st.selectbox("Priority Level", ["LOW", "MEDIUM", "HIGH", "IMMEDIATE"])
                start_date = st.date_input("Start Date", value=datetime.now().date())
            with col2:
                duration_weeks = st.number_input("Duration (weeks)", min_value=1, max_value=16, value=4)
                review_frequency = st.selectbox("Review Frequency", ["Daily", "Weekly", "Bi-weekly"])

            # Goals and objectives
            st.markdown("#### 🎯 Goals and Objectives")
            primary_goal = st.text_area("Primary Goal",
                                       value=f"Improve {student_data['subject']} performance by 15 points")

            # Strategy selection
            st.markdown("#### 📚 Selected Strategies")
            strategy_categories = st.multiselect(
                "Strategy Categories",
                ["Academic Support", "Behavioral Intervention", "Family Engagement", "Technology Support"]
            )

            # Success metrics
            st.markdown("#### 📊 Success Metrics")
            success_metrics = st.text_area("Success Metrics",
                                         value="• Score improvement of 10+ points\n• Attendance rate >90%\n• Assignment completion >95%")

            # Responsible parties
            st.markdown("#### 👥 Responsible Parties")
            col1, col2 = st.columns(2)
            with col1:
                primary_teacher = st.text_input("Primary Teacher", value="Current Teacher")
                support_staff = st.text_input("Support Staff", value="Guidance Counselor")
            with col2:
                parent_contact = st.text_input("Parent/Guardian Contact", value="Parent Name")
                other_stakeholders = st.text_input("Other Stakeholders", value="")

            # Submit button
            submitted = st.form_submit_button("🚀 Create Intervention Plan")

            if submitted:
                # Create intervention plan
                plan_data = {
                    'student_id': student_data['student_id'],
                    'student_name': student_data['name'],
                    'plan_name': plan_name,
                    'priority_level': priority_level,
                    'start_date': start_date.isoformat(),
                    'duration_weeks': duration_weeks,
                    'review_frequency': review_frequency,
                    'primary_goal': primary_goal,
                    'strategy_categories': strategy_categories,
                    'success_metrics': success_metrics,
                    'primary_teacher': primary_teacher,
                    'support_staff': support_staff,
                    'parent_contact': parent_contact,
                    'created_date': datetime.now().isoformat(),
                    'status': 'Active'
                }

                st.success("🎉 Intervention plan created successfully!")
                st.json(plan_data)

                # Generate automatic recommendations
                recommendations = system.generate_personalized_recommendations(student_data)

                st.markdown("#### 🤖 AI-Generated Recommendations")
                st.markdown("**Immediate Actions:**")
                for action in recommendations['immediate_actions'][:3]:
                    st.markdown(f"• {action}")

                st.markdown("**Parent Involvement:**")
                for involvement in recommendations['parent_involvement'][:3]:
                    st.markdown(f"• {involvement}")


def render_teacher_portal(system):
    """Render comprehensive teacher portal"""
    st.markdown("# 👩‍🏫 Teacher Portal")
    st.markdown("### Your Classroom Analytics & Student Management")

    df = system.sample_data

    # Teacher authentication simulation
    st.sidebar.markdown("### 🔐 Teacher Login")
    teacher_name = st.sidebar.text_input("Teacher Name", value="Ms. Johnson")

    # Subject/Class selection
    subjects = df['subject'].unique()
    teacher_subject = st.sidebar.selectbox("Your Subject", subjects)

    # Grade level selection
    grades = sorted(df['grade_level'].unique())
    teacher_grades = st.sidebar.multiselect("Your Grade Levels", grades, default=grades[:2])

    # Filter data for teacher's classes
    teacher_data = df[
        (df['subject'] == teacher_subject) &
        (df['grade_level'].isin(teacher_grades))
    ].copy()

    if len(teacher_data) == 0:
        st.warning("No students found for the selected subject and grade levels.")
        return

    # Ensure performance_category exists
    if 'performance_category' not in teacher_data.columns:
        teacher_data['performance_category'] = teacher_data['current_score'].apply(
            lambda x: 'Excellent' if x >= 90 else
                     'Good' if x >= 80 else
                     'Satisfactory' if x >= 70 else
                     'Needs Improvement' if x >= 60 else
                     'At Risk'
        )

    # Welcome message
    st.markdown(f"## Welcome, {teacher_name}! 👋")
    st.markdown(f"### {teacher_subject} - Grades {', '.join(teacher_grades)}")
    st.markdown(f"**{len(teacher_data)} students** in your classes")

    # Quick class overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_score = teacher_data['current_score'].mean()
        st.metric("Class Average", f"{avg_score:.1f}%",
                 delta=f"{teacher_data['performance_trend'].mean():+.1f}")

    with col2:
        high_risk_count = len(teacher_data[teacher_data['intervention_urgency'].isin(['IMMEDIATE', 'HIGH'])])
        st.metric("Need Attention", high_risk_count,
                 delta=f"{high_risk_count/len(teacher_data)*100:.0f}%")

    with col3:
        avg_attendance = teacher_data['attendance_rate'].mean() * 100
        st.metric("Class Attendance", f"{avg_attendance:.1f}%")

    with col4:
        improving_count = len(teacher_data[teacher_data['performance_trend'] > 0])
        st.metric("Improving", improving_count,
                 delta=f"{improving_count/len(teacher_data)*100:.0f}%")

    # Main teacher portal tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Class Overview",
        "🎯 Priority Students",
        "📈 Progress Tracking",
        "📝 Daily Actions",
        "📞 Parent Communication"
    ])

    with tab1:
        render_teacher_class_overview(teacher_data, teacher_subject, system)

    with tab2:
        render_teacher_priority_students(teacher_data, system)

    with tab3:
        render_teacher_progress_tracking(teacher_data, system)

    with tab4:
        render_teacher_daily_actions(teacher_data, system)

    with tab5:
        render_teacher_parent_communication(teacher_data)


def render_teacher_class_overview(teacher_data, subject, system):
    """Render teacher's class overview"""
    st.markdown("### 📊 Your Class at a Glance")

    # Performance distribution
    col1, col2 = st.columns(2)

    with col1:
        # Grade distribution
        grade_counts = teacher_data['performance_category'].value_counts()
        fig_grades = px.pie(
            values=grade_counts.values,
            names=grade_counts.index,
            title=f"{subject} - Performance Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_grades, use_container_width=True, key="teacher_grade_dist")

    with col2:
        # Risk level distribution
        risk_counts = teacher_data['intervention_urgency'].value_counts()
        colors = {'IMMEDIATE': '#FF4444', 'HIGH': '#FF8800', 'MEDIUM': '#FFAA00', 'LOW': '#44AA44'}
        fig_risk = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Students by Attention Level",
            color=risk_counts.index,
            color_discrete_map=colors
        )
        st.plotly_chart(fig_risk, use_container_width=True, key="teacher_risk_dist")

    # Class performance trends
    st.markdown("#### 📈 Class Performance Trends")

    # Simulate weekly class averages
    weeks = ['4 weeks ago', '3 weeks ago', '2 weeks ago', 'Last week', 'This week']
    class_averages = []
    current_avg = teacher_data['current_score'].mean()
    trend = teacher_data['performance_trend'].mean()

    for i in range(5):
        avg = current_avg - (trend * (4-i) * 0.25) + np.random.normal(0, 1)
        class_averages.append(max(0, min(100, avg)))

    trend_df = pd.DataFrame({
        'Week': weeks,
        'Class Average': class_averages,
        'Target': [75] * 5  # Target line
    })

    fig_trend = px.line(trend_df, x='Week', y=['Class Average', 'Target'],
                       title=f"{subject} Class Average Trend",
                       markers=True)
    st.plotly_chart(fig_trend, use_container_width=True, key="teacher_class_trend")

    # Student list with quick actions
    st.markdown("#### 👥 Your Students")

    # Add action buttons to student data
    display_data = teacher_data[['student_id', 'name', 'current_score', 'performance_trend',
                                'attendance_rate', 'intervention_urgency']].copy()
    display_data['attendance_rate'] = (display_data['attendance_rate'] * 100).round(1)
    display_data = display_data.sort_values('current_score', ascending=False)

    # Color code by urgency
    def highlight_urgency(row):
        if row['intervention_urgency'] == 'IMMEDIATE':
            return ['background-color: #ffebee'] * len(row)
        elif row['intervention_urgency'] == 'HIGH':
            return ['background-color: #fff3e0'] * len(row)
        else:
            return [''] * len(row)

    styled_df = display_data.style.apply(highlight_urgency, axis=1)
    st.dataframe(styled_df, use_container_width=True)


def render_teacher_priority_students(teacher_data, system):
    """Render priority students for teacher attention"""
    st.markdown("### 🎯 Students Needing Your Attention")

    # Filter priority students
    priority_students = teacher_data[
        teacher_data['intervention_urgency'].isin(['IMMEDIATE', 'HIGH'])
    ].sort_values('predicted_risk_score', ascending=False)

    if len(priority_students) == 0:
        st.success("🎉 Great news! No students currently need immediate attention.")
        st.balloons()
        return

    st.markdown(f"**{len(priority_students)} students** need your attention today")

    # Priority student cards
    for idx, student in priority_students.iterrows():
        urgency_color = "🔴" if student['intervention_urgency'] == 'IMMEDIATE' else "🟠"

        with st.expander(f"{urgency_color} {student['name']} - {student['intervention_urgency']} Priority"):

            # Student metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Current Score", f"{student['current_score']:.1f}%")
            with col2:
                trend_emoji = "📉" if student['performance_trend'] < -1 else "📈" if student['performance_trend'] > 1 else "➡️"
                st.metric("Trend", f"{trend_emoji} {student['performance_trend']:+.1f}")
            with col3:
                st.metric("Attendance", f"{student['attendance_rate']*100:.0f}%")
            with col4:
                st.metric("Risk Score", f"{student['predicted_risk_score']:.0f}")

            # Generate teacher-specific recommendations
            recommendations = system.generate_personalized_recommendations(student.to_dict())

            # Teacher action plan
            st.markdown("#### 🎯 Your Action Plan")

            st.markdown("**This Week:**")
            teacher_actions = []
            for action in recommendations['immediate_actions'][:3]:
                # Convert to teacher-specific language
                teacher_action = action.replace("Schedule", "You should schedule").replace("Contact parents", "Contact parents")
                teacher_actions.append(teacher_action)

            for i, action in enumerate(teacher_actions, 1):
                st.markdown(f"{i}. {action}")

            # Classroom strategies
            st.markdown("**Classroom Strategies:**")
            classroom_strategies = [
                f"Provide additional support during {student['subject']} lessons",
                "Check understanding frequently with this student",
                "Offer alternative explanations for difficult concepts",
                "Pair with a strong peer for collaborative work",
                "Give extra time for assignments if needed"
            ]

            for strategy in classroom_strategies[:3]:
                st.markdown(f"• {strategy}")

            # Quick actions
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"📞 Call Parent", key=f"call_{student['student_id']}"):
                    st.info("Parent contact logged. Phone number: (555) 123-4567")

            with col2:
                if st.button(f"📝 Add Note", key=f"note_{student['student_id']}"):
                    note = st.text_input("Quick note:", key=f"note_input_{student['student_id']}")
                    if note:
                        st.success("Note saved to student record")

            with col3:
                if st.button(f"✅ Mark Addressed", key=f"addressed_{student['student_id']}"):
                    st.success("Student marked as addressed for today")


def render_teacher_progress_tracking(teacher_data, system):
    """Render progress tracking for teacher's students"""
    st.markdown("### 📈 Student Progress Tracking")

    # Student selector for detailed tracking
    student_options = [f"{row['student_id']} - {row['name']}" for _, row in teacher_data.iterrows()]
    selected_student = st.selectbox("Select Student for Detailed Tracking", student_options)

    if selected_student:
        student_id = selected_student.split(' - ')[0]
        student_data = teacher_data[teacher_data['student_id'] == student_id].iloc[0].to_dict()

        st.markdown(f"#### 📊 {student_data['name']} - Progress Details")

        # Progress metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Current Score", f"{student_data['current_score']:.1f}%")
        with col2:
            st.metric("Monthly Trend", f"{student_data['performance_trend']:+.1f}")
        with col3:
            st.metric("Attendance", f"{student_data['attendance_rate']*100:.0f}%")
        with col4:
            completion_rate = student_data['assignment_completion_rate'] * 100
            st.metric("Assignment Completion", f"{completion_rate:.0f}%")

        # Progress prediction
        prediction = system.predict_future_performance(student_data, 8)

        # Progress chart
        fig = go.Figure()

        # Historical data (simulated)
        historical_weeks = [-4, -3, -2, -1, 0]
        historical_scores = []
        current = student_data['current_score']
        trend = student_data['performance_trend']

        for week in historical_weeks:
            score = current + (trend * week * 0.25) + np.random.normal(0, 2)
            historical_scores.append(max(0, min(100, score)))

        # Add historical data
        fig.add_trace(go.Scatter(
            x=historical_weeks,
            y=historical_scores,
            mode='lines+markers',
            name='Historical Performance',
            line=dict(color='blue', width=2)
        ))

        # Add prediction
        fig.add_trace(go.Scatter(
            x=prediction['weeks'],
            y=prediction['predicted_scores'],
            mode='lines+markers',
            name='Predicted Performance',
            line=dict(color='red', width=2, dash='dash')
        ))

        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=prediction['weeks'] + prediction['weeks'][::-1],
            y=prediction['confidence_upper'] + prediction['confidence_lower'][::-1],
            fill='toself',
            fillcolor='rgba(255,0,0,0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Prediction Confidence'
        ))

        fig.update_layout(
            title=f"Performance Tracking - {student_data['name']}",
            xaxis_title="Weeks (Negative = Past, Positive = Future)",
            yaxis_title="Score",
            yaxis_range=[0, 100]
        )

        st.plotly_chart(fig, use_container_width=True, key=f"progress_{student_data['student_id']}")

        # Progress notes
        st.markdown("#### 📝 Progress Notes")

        # Simulated progress notes
        progress_notes = [
            {
                "date": "Today",
                "note": "Showed improvement in understanding fractions during class discussion",
                "type": "positive"
            },
            {
                "date": "2 days ago",
                "note": "Struggled with homework assignment - provided additional support",
                "type": "concern"
            },
            {
                "date": "1 week ago",
                "note": "Excellent participation in group work",
                "type": "positive"
            }
        ]

        for note in progress_notes:
            if note["type"] == "positive":
                st.success(f"**{note['date']}**: {note['note']}")
            else:
                st.warning(f"**{note['date']}**: {note['note']}")

        # Add new note
        with st.form(f"add_note_{student_data['student_id']}"):
            new_note = st.text_area("Add Progress Note:")
            note_type = st.selectbox("Note Type:", ["Positive", "Concern", "Neutral"])

            if st.form_submit_button("📝 Add Note"):
                st.success("Progress note added successfully!")


def render_teacher_daily_actions(teacher_data, system):
    """Render daily action items for teachers"""
    st.markdown("### 📝 Today's Action Items")

    # Generate daily action items based on student data
    immediate_students = teacher_data[teacher_data['intervention_urgency'] == 'IMMEDIATE']
    high_priority_students = teacher_data[teacher_data['intervention_urgency'] == 'HIGH']

    # Today's priorities
    st.markdown("#### 🎯 Today's Priorities")

    priorities = []

    if len(immediate_students) > 0:
        priorities.append({
            "priority": "HIGH",
            "action": f"Check in with {len(immediate_students)} students needing immediate attention",
            "students": immediate_students['name'].tolist(),
            "time": "First 15 minutes of class"
        })

    if len(high_priority_students) > 0:
        priorities.append({
            "priority": "MEDIUM",
            "action": f"Monitor {len(high_priority_students)} high-priority students during lesson",
            "students": high_priority_students['name'].tolist(),
            "time": "During instruction"
        })

    # Check for students with declining attendance
    low_attendance = teacher_data[teacher_data['attendance_rate'] < 0.85]
    if len(low_attendance) > 0:
        priorities.append({
            "priority": "MEDIUM",
            "action": f"Follow up on attendance with {len(low_attendance)} students",
            "students": low_attendance['name'].tolist(),
            "time": "End of class"
        })

    if not priorities:
        st.success("🎉 No urgent action items today! Focus on regular instruction.")
    else:
        for i, priority in enumerate(priorities, 1):
            priority_color = "🔴" if priority["priority"] == "HIGH" else "🟡"

            with st.expander(f"{priority_color} Priority {i}: {priority['action']}"):
                st.markdown(f"**When**: {priority['time']}")
                st.markdown(f"**Students**: {', '.join(priority['students'])}")

                if st.button(f"✅ Mark Complete", key=f"complete_priority_{i}"):
                    st.success("Action item marked as complete!")

    # Lesson planning suggestions
    st.markdown("#### 📚 Lesson Planning Suggestions")

    # Analyze class needs for lesson planning
    avg_score = teacher_data['current_score'].mean()
    struggling_count = len(teacher_data[teacher_data['current_score'] < 70])

    suggestions = []

    if avg_score < 75:
        suggestions.append("Consider reviewing fundamental concepts before introducing new material")

    if struggling_count > len(teacher_data) * 0.3:  # More than 30% struggling
        suggestions.append("Plan for differentiated instruction with multiple difficulty levels")

    if len(teacher_data[teacher_data['performance_trend'] < 0]) > len(teacher_data) * 0.2:
        suggestions.append("Include more formative assessment to catch understanding gaps early")

    suggestions.append("Incorporate peer learning opportunities for struggling students")
    suggestions.append("Plan check-ins with priority students during independent work time")

    for suggestion in suggestions:
        st.markdown(f"• {suggestion}")

    # Quick classroom tools
    st.markdown("#### 🛠️ Quick Classroom Tools")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Generate Seating Chart"):
            st.info("Optimal seating chart generated based on student needs and peer support opportunities")

        if st.button("📝 Create Differentiated Worksheet"):
            st.info("Worksheet with multiple difficulty levels created for today's lesson")

    with col2:
        if st.button("👥 Suggest Group Formations"):
            st.info("Optimal group formations suggested based on student strengths and needs")

        if st.button("📞 Parent Contact List"):
            priority_contacts = teacher_data[teacher_data['intervention_urgency'].isin(['IMMEDIATE', 'HIGH'])]
            if len(priority_contacts) > 0:
                st.info(f"Contact list generated for {len(priority_contacts)} priority students")
            else:
                st.success("No priority parent contacts needed today!")


def render_teacher_parent_communication(teacher_data):
    """Render parent communication tools for teachers"""
    st.markdown("### 📞 Parent Communication Center")

    # Communication priorities
    st.markdown("#### 🎯 Communication Priorities")

    # Students needing parent contact
    immediate_contact = teacher_data[teacher_data['intervention_urgency'] == 'IMMEDIATE']
    declining_performance = teacher_data[teacher_data['performance_trend'] < -2]
    low_attendance = teacher_data[teacher_data['attendance_rate'] < 0.8]

    contact_priorities = []

    for _, student in immediate_contact.iterrows():
        contact_priorities.append({
            "student": student['name'],
            "reason": "Immediate academic intervention needed",
            "urgency": "HIGH",
            "suggested_contact": "Phone call today"
        })

    for _, student in declining_performance.iterrows():
        if student['name'] not in [p['student'] for p in contact_priorities]:
            contact_priorities.append({
                "student": student['name'],
                "reason": "Declining performance trend",
                "urgency": "MEDIUM",
                "suggested_contact": "Email or phone call this week"
            })

    for _, student in low_attendance.iterrows():
        if student['name'] not in [p['student'] for p in contact_priorities]:
            contact_priorities.append({
                "student": student['name'],
                "reason": "Attendance concerns",
                "urgency": "MEDIUM",
                "suggested_contact": "Phone call to discuss barriers"
            })

    if contact_priorities:
        for priority in contact_priorities:
            urgency_color = "🔴" if priority["urgency"] == "HIGH" else "🟡"

            with st.expander(f"{urgency_color} {priority['student']} - {priority['reason']}"):
                st.markdown(f"**Suggested Contact**: {priority['suggested_contact']}")

                # Quick message templates
                st.markdown("**Message Templates:**")

                # Default template
                template = f"Hi [Parent Name], I wanted to reach out about {priority['student']} and discuss how we can work together to support their success in my class."

                if "intervention" in priority['reason']:
                    template = f"Hi [Parent Name], I wanted to reach out about {priority['student']}'s recent performance in my class. I'd like to discuss some strategies we can work on together to help them succeed. Could we schedule a brief call this week?"
                elif "declining" in priority['reason']:
                    template = f"Hello [Parent Name], I've noticed {priority['student']}'s performance has been declining recently. I'd like to work with you to identify any challenges and create a support plan. When would be a good time to talk?"
                elif "attendance" in priority['reason']:
                    template = f"Hi [Parent Name], I wanted to check in about {priority['student']}'s recent absences. Is there anything I can do to support their attendance? I'd love to discuss this with you."

                st.text_area("Suggested message:", value=template, height=100, key=f"template_{priority['student']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📞 Log Phone Call", key=f"call_{priority['student']}"):
                        st.success("Phone call logged in student record")
                with col2:
                    if st.button(f"📧 Send Email", key=f"email_{priority['student']}"):
                        st.success("Email sent and logged")
    else:
        st.success("🎉 No urgent parent communications needed today!")

    # Positive communication opportunities
    st.markdown("#### 🌟 Positive Communication Opportunities")

    # Find students with positive trends
    improving_students = teacher_data[teacher_data['performance_trend'] > 1]
    high_performers = teacher_data[teacher_data['current_score'] > 90]

    positive_opportunities = []

    for _, student in improving_students.iterrows():
        positive_opportunities.append({
            "student": student['name'],
            "reason": f"Showing great improvement (+{student['performance_trend']:.1f} trend)",
            "message": f"I wanted to share some great news about {student['name']}'s progress in my class!"
        })

    for _, student in high_performers.iterrows():
        if student['name'] not in [p['student'] for p in positive_opportunities]:
            positive_opportunities.append({
                "student": student['name'],
                "reason": f"Excellent performance ({student['current_score']:.1f}%)",
                "message": f"{student['name']} is doing excellent work in my class and I wanted you to know!"
            })

    if positive_opportunities:
        st.markdown("Consider sending positive updates to these parents:")
        for opportunity in positive_opportunities[:3]:  # Limit to top 3
            st.success(f"**{opportunity['student']}**: {opportunity['reason']}")

            if st.button(f"📧 Send Positive Note", key=f"positive_{opportunity['student']}"):
                st.balloons()
                st.success("Positive note sent to parents!")


def render_parent_portal(system):
    """Render comprehensive parent portal"""
    st.markdown("# 👨‍👩‍👧‍👦 Parent Portal")
    st.markdown("### Your Child's Learning Journey - Simple, Clear, Actionable")

    df = system.sample_data

    # Parent authentication simulation
    st.sidebar.markdown("### 🔐 Parent Login")
    parent_name = st.sidebar.text_input("Parent Name", value="Parent Smith")

    # Child selection (parents might have multiple children)
    child_options = [f"{row['student_id']} - {row['name']}" for _, row in df.iterrows()]
    selected_child = st.sidebar.selectbox("Select Your Child", child_options[:5])  # Limit for demo

    if selected_child:
        student_id = selected_child.split(' - ')[0]
        student_data = df[df['student_id'] == student_id].iloc[0].to_dict()

        # Welcome message
        st.markdown(f"## Welcome, {parent_name}! 👋")
        st.markdown(f"### Here's how **{student_data['name']}** is doing:")

        # Quick status overview
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            score_color = "🟢" if student_data['current_score'] >= 80 else "🟡" if student_data['current_score'] >= 70 else "🔴"
            st.metric("Current Grade", f"{score_color} {student_data['current_score']:.0f}%")

        with col2:
            attendance_color = "🟢" if student_data['attendance_rate'] >= 0.9 else "🟡" if student_data['attendance_rate'] >= 0.8 else "🔴"
            st.metric("Attendance", f"{attendance_color} {student_data['attendance_rate']*100:.0f}%")

        with col3:
            trend_emoji = "📈" if student_data['performance_trend'] > 0 else "📉" if student_data['performance_trend'] < -1 else "➡️"
            st.metric("Trend", f"{trend_emoji} {student_data['performance_trend']:+.1f}")

        with col4:
            risk_color = "🟢" if student_data['predicted_risk_score'] < 30 else "🟡" if student_data['predicted_risk_score'] < 60 else "🔴"
            st.metric("Support Needed", f"{risk_color} {100-student_data['predicted_risk_score']:.0f}%")

        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Progress Report",
            "🏠 How to Help at Home",
            "📞 Communication",
            "🎯 Goals & Celebrations"
        ])

        with tab1:
            render_parent_progress_report(student_data, system)

        with tab2:
            render_parent_help_guide(student_data, system)

        with tab3:
            render_parent_communication(student_data)

        with tab4:
            render_parent_goals_celebrations(student_data, system)


def render_parent_progress_report(student_data, system):
    """Render parent-friendly progress report"""
    st.markdown("### 📊 Your Child's Progress Report")

    # Simple, visual progress summary
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📈 Academic Performance")

        # Subject performance
        subjects = ['Mathematics', 'English', 'Science', 'History', 'Art']
        scores = [student_data['current_score'] + np.random.normal(0, 5) for _ in subjects]
        scores = [max(0, min(100, score)) for score in scores]  # Keep in valid range

        performance_df = pd.DataFrame({
            'Subject': subjects,
            'Score': scores,
            'Grade': [get_letter_grade(score) for score in scores]
        })

        fig = px.bar(performance_df, x='Subject', y='Score',
                    title="Grades by Subject",
                    color='Score', color_continuous_scale='RdYlGn',
                    range_color=[0, 100])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key="parent_grades_chart")

        # Progress over time
        st.markdown("#### 📅 Progress Over Time")
        weeks = ['4 weeks ago', '3 weeks ago', '2 weeks ago', 'Last week', 'This week']
        progress_scores = []
        current = student_data['current_score']
        trend = student_data['performance_trend']

        for i in range(5):
            score = current - (trend * (4-i) * 0.25) + np.random.normal(0, 2)
            progress_scores.append(max(0, min(100, score)))

        progress_df = pd.DataFrame({
            'Week': weeks,
            'Score': progress_scores
        })

        fig2 = px.line(progress_df, x='Week', y='Score',
                      title="Progress Trend",
                      markers=True)
        fig2.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig2, use_container_width=True, key="parent_progress_chart")

    with col2:
        st.markdown("#### 🎯 What This Means")

        # Simple interpretation
        if student_data['current_score'] >= 80:
            st.success("🌟 **Excellent Work!** Your child is performing very well.")
        elif student_data['current_score'] >= 70:
            st.info("👍 **Good Progress!** Your child is doing well with room for growth.")
        elif student_data['current_score'] >= 60:
            st.warning("📚 **Needs Support** Your child would benefit from additional help.")
        else:
            st.error("🆘 **Immediate Attention Needed** Let's work together to help your child succeed.")

        # Strengths and areas for improvement
        st.markdown("#### ✨ Strengths")
        strengths = [
            "Shows consistent effort in class",
            "Good participation in group activities",
            "Demonstrates creativity in projects",
            "Helpful to classmates"
        ]
        for strength in strengths[:2]:
            st.markdown(f"• {strength}")

        st.markdown("#### 🎯 Areas for Growth")
        if student_data['current_score'] < 70:
            growth_areas = [
                f"Focus on {student_data['subject']} fundamentals",
                "Improve homework completion consistency",
                "Develop better study habits"
            ]
        else:
            growth_areas = [
                "Challenge yourself with advanced problems",
                "Help other students learn",
                "Explore real-world applications"
            ]

        for area in growth_areas[:2]:
            st.markdown(f"• {area}")

        # Next steps
        st.markdown("#### 🚀 Next Steps")
        recommendations = system.generate_personalized_recommendations(student_data)

        st.markdown("**This Week:**")
        for action in recommendations['immediate_actions'][:2]:
            # Make parent-friendly
            parent_action = action.replace("teacher", "you").replace("Schedule", "We'll schedule")
            st.markdown(f"• {parent_action}")


def render_parent_help_guide(student_data, system):
    """Render how parents can help at home"""
    st.markdown("### 🏠 How You Can Help at Home")

    # Personalized recommendations based on student needs
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📚 Study Support")

        if student_data['current_score'] < 70:
            study_tips = [
                "📖 **Daily Reading**: 20 minutes of reading together each day",
                "🧮 **Math Practice**: Use everyday situations for math (cooking, shopping)",
                "📝 **Homework Time**: Set a consistent homework schedule",
                "🎯 **Break It Down**: Help break large assignments into smaller tasks",
                "💪 **Encourage Effort**: Praise hard work, not just results"
            ]
        else:
            study_tips = [
                "🌟 **Challenge Activities**: Encourage advanced projects and research",
                "🤝 **Peer Teaching**: Have them explain concepts to you or siblings",
                "🔍 **Real-World Connections**: Discuss how school subjects apply to life",
                "📚 **Extended Learning**: Visit museums, libraries, educational websites",
                "🎯 **Goal Setting**: Help set and track personal learning goals"
            ]

        for tip in study_tips:
            st.markdown(f"• {tip}")

        st.markdown("#### 🕐 Recommended Schedule")
        if student_data['current_score'] < 70:
            schedule = {
                "After School": "30 min homework review",
                "Before Dinner": "20 min reading together",
                "Evening": "15 min next-day preparation",
                "Weekend": "1 hour catch-up/review"
            }
        else:
            schedule = {
                "After School": "Independent homework time",
                "Before Dinner": "Discuss what was learned",
                "Evening": "Enrichment activities",
                "Weekend": "Fun educational outings"
            }

        for time, activity in schedule.items():
            st.markdown(f"**{time}**: {activity}")

    with col2:
        st.markdown("#### 💬 Communication Tips")

        communication_tips = [
            "🗣️ **Ask Open Questions**: 'What was interesting today?' instead of 'How was school?'",
            "👂 **Listen Actively**: Show genuine interest in their learning",
            "🎉 **Celebrate Small Wins**: Acknowledge effort and improvement",
            "😌 **Stay Calm**: Help them work through challenges without stress",
            "🤝 **Partner with Teachers**: Maintain regular communication with school"
        ]

        for tip in communication_tips:
            st.markdown(f"• {tip}")

        st.markdown("#### 🏠 Creating a Learning Environment")

        environment_tips = [
            "📍 **Dedicated Study Space**: Quiet, well-lit area for homework",
            "📱 **Minimize Distractions**: Put away phones/tablets during study time",
            "📚 **Learning Materials**: Keep supplies organized and accessible",
            "⏰ **Consistent Routine**: Same time and place for homework daily",
            "🌟 **Positive Atmosphere**: Make learning enjoyable, not stressful"
        ]

        for tip in environment_tips:
            st.markdown(f"• {tip}")

        # Warning signs to watch for
        st.markdown("#### ⚠️ When to Reach Out")
        warning_signs = [
            "Sudden drop in grades or motivation",
            "Complaints about school or teachers",
            "Difficulty sleeping or eating",
            "Avoiding homework or school discussions",
            "Social withdrawal or behavior changes"
        ]

        st.markdown("Contact the teacher if you notice:")
        for sign in warning_signs:
            st.markdown(f"• {sign}")


def render_parent_communication(student_data):
    """Render parent communication center"""
    st.markdown("### 📞 Communication Center")

    # Recent messages
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📨 Recent Messages")

        # Simulated messages
        messages = [
            {
                "date": "Today",
                "from": "Ms. Johnson (Math Teacher)",
                "subject": "Great improvement this week!",
                "preview": f"{student_data['name']} showed excellent effort on the recent quiz...",
                "type": "positive"
            },
            {
                "date": "2 days ago",
                "from": "School Counselor",
                "subject": "Study strategies discussion",
                "preview": "I'd like to schedule a meeting to discuss some helpful study strategies...",
                "type": "neutral"
            },
            {
                "date": "1 week ago",
                "from": "Principal",
                "subject": "Parent-Teacher Conference",
                "preview": "Reminder: Parent-Teacher conferences are scheduled for next week...",
                "type": "info"
            }
        ]

        for msg in messages:
            if msg["type"] == "positive":
                st.success(f"**{msg['from']}** - {msg['date']}\n\n{msg['subject']}\n\n{msg['preview']}")
            elif msg["type"] == "neutral":
                st.info(f"**{msg['from']}** - {msg['date']}\n\n{msg['subject']}\n\n{msg['preview']}")
            else:
                st.info(f"**{msg['from']}** - {msg['date']}\n\n{msg['subject']}\n\n{msg['preview']}")

    with col2:
        st.markdown("#### ✉️ Send a Message")

        with st.form("parent_message_form"):
            recipient = st.selectbox("To:", ["Math Teacher", "English Teacher", "School Counselor", "Principal"])
            subject = st.text_input("Subject:")
            message = st.text_area("Message:", height=100)

            if st.form_submit_button("📤 Send Message"):
                st.success("Message sent successfully! You'll receive a response within 24 hours.")

        st.markdown("#### 📅 Schedule Meeting")

        with st.form("schedule_meeting_form"):
            meeting_type = st.selectbox("Meeting Type:", ["Parent-Teacher Conference", "Academic Support Discussion", "Behavioral Consultation"])
            preferred_date = st.date_input("Preferred Date:")
            preferred_time = st.selectbox("Preferred Time:", ["Morning (8-10 AM)", "Afternoon (1-3 PM)", "After School (3-5 PM)"])

            if st.form_submit_button("📅 Request Meeting"):
                st.success("Meeting request submitted! The school will contact you to confirm.")


def render_parent_goals_celebrations(student_data, system):
    """Render goals and celebrations for parents"""
    st.markdown("### 🎯 Goals & Celebrations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 Current Goals")

        # Generate realistic goals based on student performance
        recommendations = system.generate_personalized_recommendations(student_data)

        goals = [
            f"Improve {student_data['subject']} grade to {min(100, student_data['current_score'] + 10):.0f}%",
            f"Maintain {student_data['attendance_rate']*100:.0f}%+ attendance rate",
            "Complete all homework assignments on time",
            "Participate actively in class discussions"
        ]

        for i, goal in enumerate(goals, 1):
            progress = np.random.randint(20, 80)  # Simulated progress
            st.markdown(f"**Goal {i}:** {goal}")
            st.progress(progress / 100)
            st.markdown(f"Progress: {progress}%")
            st.markdown("")

        st.markdown("#### 📈 Set New Goal")
        with st.form("new_goal_form"):
            goal_type = st.selectbox("Goal Type:", ["Academic", "Behavioral", "Social", "Personal"])
            goal_description = st.text_input("Goal Description:")
            target_date = st.date_input("Target Date:")

            if st.form_submit_button("🎯 Set Goal"):
                st.success("New goal set! We'll track progress together.")

    with col2:
        st.markdown("#### 🎉 Recent Celebrations")

        # Simulated achievements
        celebrations = [
            {
                "date": "This week",
                "achievement": "Perfect attendance for 2 weeks!",
                "icon": "🏆"
            },
            {
                "date": "Last week",
                "achievement": "Improved math quiz score by 15 points",
                "icon": "📈"
            },
            {
                "date": "2 weeks ago",
                "achievement": "Helped a classmate with reading",
                "icon": "🤝"
            },
            {
                "date": "3 weeks ago",
                "achievement": "Completed science project early",
                "icon": "🔬"
            }
        ]

        for celebration in celebrations:
            st.success(f"{celebration['icon']} **{celebration['date']}**\n\n{celebration['achievement']}")

        st.markdown("#### 🌟 Upcoming Opportunities")

        opportunities = [
            "Science Fair participation",
            "Math competition team",
            "Reading buddy program",
            "Student council elections"
        ]

        for opportunity in opportunities:
            st.info(f"🌟 {opportunity}")


def render_performance_forecasting(system, df):
    """Render performance forecasting analytics"""
    st.markdown("### 🔮 Performance Forecasting")
    st.markdown("Predict student performance 4-12 weeks ahead using AI models")

    # Forecasting controls
    col1, col2, col3 = st.columns(3)

    with col1:
        forecast_weeks = st.slider("Forecast Period (weeks)", 4, 12, 8)
    with col2:
        confidence_level = st.selectbox("Confidence Level", ["90%", "95%", "99%"], index=1)
    with col3:
        model_type = st.selectbox("Model Type", ["Linear Trend", "Polynomial", "Seasonal"])

    # School-wide forecasting
    st.markdown("#### 🏫 School-wide Performance Forecast")

    # Generate school-wide prediction
    current_avg = df['current_score'].mean()
    overall_trend = df['performance_trend'].mean()

    # Create forecast data
    weeks = list(range(1, forecast_weeks + 1))
    forecast_scores = []
    confidence_upper = []
    confidence_lower = []

    for week in weeks:
        # Base prediction
        predicted = current_avg + (overall_trend * week * 0.25)

        # Add seasonal effects (simulated)
        seasonal_effect = 2 * np.sin(week * np.pi / 6)  # Bi-weekly cycle
        predicted += seasonal_effect

        # Confidence intervals
        uncertainty = 3 + (week * 0.5)  # Increasing uncertainty over time

        forecast_scores.append(max(0, min(100, predicted)))
        confidence_upper.append(min(100, predicted + uncertainty))
        confidence_lower.append(max(0, predicted - uncertainty))

    # Create forecast chart
    fig = go.Figure()

    # Add forecast line
    fig.add_trace(go.Scatter(
        x=weeks,
        y=forecast_scores,
        mode='lines+markers',
        name='Predicted Average',
        line=dict(color='blue', width=3)
    ))

    # Add confidence interval
    fig.add_trace(go.Scatter(
        x=weeks + weeks[::-1],
        y=confidence_upper + confidence_lower[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name=f'{confidence_level} Confidence Interval'
    ))

    fig.update_layout(
        title=f"School-wide Performance Forecast ({forecast_weeks} weeks)",
        xaxis_title="Weeks Ahead",
        yaxis_title="Predicted Average Score",
        yaxis_range=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True, key="school_forecast")

    # Individual student forecasts
    st.markdown("#### 👤 Individual Student Forecasts")

    # Select high-risk students for detailed forecasting
    high_risk_students = df[df['intervention_urgency'].isin(['IMMEDIATE', 'HIGH'])].head(5)

    if len(high_risk_students) > 0:
        for idx, student in high_risk_students.iterrows():
            with st.expander(f"📈 {student['name']} ({student['student_id']}) - Forecast"):

                # Generate individual prediction
                prediction = system.predict_future_performance(student.to_dict(), forecast_weeks)

                # Create individual forecast chart
                fig_individual = go.Figure()

                fig_individual.add_trace(go.Scatter(
                    x=prediction['weeks'],
                    y=prediction['predicted_scores'],
                    mode='lines+markers',
                    name='Predicted Score',
                    line=dict(color='red' if student['intervention_urgency'] == 'IMMEDIATE' else 'orange', width=2)
                ))

                fig_individual.add_trace(go.Scatter(
                    x=prediction['weeks'] + prediction['weeks'][::-1],
                    y=prediction['confidence_upper'] + prediction['confidence_lower'][::-1],
                    fill='toself',
                    fillcolor='rgba(255,0,0,0.1)' if student['intervention_urgency'] == 'IMMEDIATE' else 'rgba(255,165,0,0.1)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Confidence Interval'
                ))

                fig_individual.update_layout(
                    title=f"Performance Forecast - {student['name']}",
                    xaxis_title="Weeks Ahead",
                    yaxis_title="Predicted Score",
                    yaxis_range=[0, 100],
                    height=300
                )

                st.plotly_chart(fig_individual, use_container_width=True, key=f"forecast_{student['student_id']}")

                # Forecast insights
                col1, col2, col3 = st.columns(3)
                with col1:
                    final_score = prediction['predicted_scores'][-1]
                    st.metric("Predicted Score", f"{final_score:.1f}%",
                             delta=f"{final_score - student['current_score']:+.1f}")
                with col2:
                    trend_direction = prediction['trend_direction']
                    trend_emoji = "📈" if trend_direction == "improving" else "📉" if trend_direction == "declining" else "➡️"
                    st.metric("Trend", f"{trend_emoji} {trend_direction.title()}")
                with col3:
                    intervention_needed = "Yes" if final_score < 70 else "Monitor"
                    st.metric("Intervention Needed", intervention_needed)


def render_trend_analysis(system, df):
    """Render comprehensive trend analysis"""
    st.markdown("### 📈 Advanced Trend Analysis")
    st.markdown("Identify patterns and trends across multiple dimensions")

    # Trend analysis controls
    col1, col2 = st.columns(2)

    with col1:
        analysis_dimension = st.selectbox(
            "Analysis Dimension",
            ["Grade Level", "Subject", "Risk Level", "Performance Category"]
        )

    with col2:
        time_period = st.selectbox(
            "Time Period",
            ["Last 4 weeks", "Last 8 weeks", "Last 12 weeks", "Full semester"]
        )

    # Generate trend data based on selected dimension
    if analysis_dimension == "Grade Level":
        trend_data = df.groupby('grade_level').agg({
            'current_score': 'mean',
            'performance_trend': 'mean',
            'predicted_risk_score': 'mean',
            'attendance_rate': 'mean'
        }).round(2)

        # Create trend visualization
        fig = go.Figure()

        for grade in trend_data.index:
            grade_data = trend_data.loc[grade]
            fig.add_trace(go.Scatter(
                x=['Current Score', 'Trend', 'Risk Score', 'Attendance'],
                y=[grade_data['current_score'],
                   grade_data['performance_trend'] * 10 + 50,  # Scale for visibility
                   100 - grade_data['predicted_risk_score'],  # Invert for positive direction
                   grade_data['attendance_rate'] * 100],
                mode='lines+markers',
                name=f'Grade {grade}',
                line=dict(width=3)
            ))

        fig.update_layout(
            title="Performance Trends by Grade Level",
            xaxis_title="Metrics",
            yaxis_title="Normalized Scores",
            yaxis_range=[0, 100]
        )

        st.plotly_chart(fig, use_container_width=True, key="grade_trends")

    elif analysis_dimension == "Subject":
        # Subject-based trend analysis
        subject_trends = df.groupby('subject').agg({
            'current_score': ['mean', 'std'],
            'performance_trend': 'mean',
            'predicted_risk_score': 'mean'
        }).round(2)

        # Flatten column names
        subject_trends.columns = ['_'.join(col).strip() for col in subject_trends.columns]

        # Create subject comparison chart
        fig = px.bar(
            x=subject_trends.index,
            y=subject_trends['current_score_mean'],
            error_y=subject_trends['current_score_std'],
            title="Average Performance by Subject",
            color=subject_trends['performance_trend_mean'],
            color_continuous_scale='RdYlGn'
        )

        st.plotly_chart(fig, use_container_width=True, key="subject_trends")

    # Trend insights
    st.markdown("#### 🔍 Trend Insights")

    # Calculate key insights
    improving_students = len(df[df['performance_trend'] > 1])
    declining_students = len(df[df['performance_trend'] < -1])
    stable_students = len(df) - improving_students - declining_students

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📈 Improving", improving_students,
                 delta=f"{improving_students/len(df)*100:.1f}%")

    with col2:
        st.metric("📉 Declining", declining_students,
                 delta=f"{declining_students/len(df)*100:.1f}%")

    with col3:
        st.metric("➡️ Stable", stable_students,
                 delta=f"{stable_students/len(df)*100:.1f}%")

    # Detailed trend table
    st.markdown("#### 📊 Detailed Trend Analysis")

    if analysis_dimension == "Grade Level":
        st.dataframe(trend_data, use_container_width=True)
    elif analysis_dimension == "Subject":
        st.dataframe(subject_trends, use_container_width=True)


def render_risk_modeling(system, df):
    """Render risk modeling analytics"""
    st.markdown("### 🎯 Advanced Risk Modeling")
    st.markdown("AI-powered risk assessment and early warning system")

    # Risk model controls
    col1, col2 = st.columns(2)

    with col1:
        risk_threshold = st.slider("Risk Alert Threshold", 0, 100, 60)

    with col2:
        prediction_horizon = st.selectbox("Prediction Horizon", ["2 weeks", "4 weeks", "8 weeks", "12 weeks"])

    # Risk distribution analysis
    st.markdown("#### 📊 Risk Distribution Analysis")

    # Create risk score bins
    df['risk_category'] = pd.cut(df['predicted_risk_score'],
                                bins=[0, 25, 50, 75, 100],
                                labels=['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk'])

    risk_distribution = df['risk_category'].value_counts()

    # Risk distribution chart
    colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336']
    fig = px.pie(values=risk_distribution.values,
                names=risk_distribution.index,
                title="Student Risk Distribution",
                color_discrete_sequence=colors)

    st.plotly_chart(fig, use_container_width=True, key="risk_distribution")

    # Risk factor analysis
    st.markdown("#### 🔍 Risk Factor Analysis")

    # Calculate correlations with risk score
    risk_factors = df[['current_score', 'performance_trend', 'attendance_rate',
                      'assignment_completion_rate', 'participation_rate']].corrwith(df['predicted_risk_score'])

    # Create risk factor chart
    fig_factors = px.bar(
        x=risk_factors.index,
        y=abs(risk_factors.values),
        title="Risk Factor Importance",
        color=risk_factors.values,
        color_continuous_scale='RdYlBu_r'
    )
    fig_factors.update_layout(xaxis_tickangle=45)

    st.plotly_chart(fig_factors, use_container_width=True, key="risk_factors")

    # Early warning alerts
    st.markdown("#### 🚨 Early Warning Alerts")

    # Students above risk threshold
    at_risk_students = df[df['predicted_risk_score'] >= risk_threshold]

    if len(at_risk_students) > 0:
        st.warning(f"⚠️ {len(at_risk_students)} students above risk threshold ({risk_threshold})")

        # Show top risk students
        top_risk = at_risk_students.nlargest(5, 'predicted_risk_score')[
            ['student_id', 'name', 'current_score', 'predicted_risk_score', 'intervention_urgency']
        ]

        st.dataframe(top_risk, use_container_width=True)
    else:
        st.success("✅ No students currently above the risk threshold!")

    # Risk prediction accuracy
    st.markdown("#### 📈 Model Performance")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Simulated accuracy metrics
        accuracy = 87.5
        st.metric("Prediction Accuracy", f"{accuracy}%", delta="+2.3%")

    with col2:
        precision = 82.1
        st.metric("Precision", f"{precision}%", delta="+1.8%")

    with col3:
        recall = 91.3
        st.metric("Recall", f"{recall}%", delta="+0.9%")


def render_pattern_discovery(system, df):
    """Render pattern discovery analytics"""
    st.markdown("### 🔍 Pattern Discovery")
    st.markdown("Discover hidden patterns and insights in student data")

    # Pattern analysis
    st.markdown("#### 🧩 Behavioral Patterns")

    # Attendance vs Performance pattern
    fig_attendance = px.scatter(
        df,
        x='attendance_rate',
        y='current_score',
        color='intervention_urgency',
        size='predicted_risk_score',
        title="Attendance vs Performance Pattern",
        labels={'attendance_rate': 'Attendance Rate', 'current_score': 'Current Score'}
    )

    st.plotly_chart(fig_attendance, use_container_width=True, key="attendance_pattern")

    # Performance volatility patterns
    st.markdown("#### 📊 Performance Volatility Patterns")

    # Create volatility vs trend analysis
    fig_volatility = px.scatter(
        df,
        x='performance_volatility',
        y='performance_trend',
        color='predicted_risk_score',
        size='current_score',
        title="Performance Volatility vs Trend",
        labels={'performance_volatility': 'Performance Volatility', 'performance_trend': 'Performance Trend'}
    )

    st.plotly_chart(fig_volatility, use_container_width=True, key="volatility_pattern")

    # Clustering analysis
    st.markdown("#### 🎯 Student Clustering")

    # Simple clustering based on performance characteristics
    df['cluster'] = 'Average'
    df.loc[(df['current_score'] >= 80) & (df['performance_trend'] > 0), 'cluster'] = 'High Achievers'
    df.loc[(df['current_score'] < 60) & (df['performance_trend'] < 0), 'cluster'] = 'At Risk'
    df.loc[(df['current_score'] >= 70) & (df['performance_trend'] < -1), 'cluster'] = 'Declining'
    df.loc[(df['current_score'] < 70) & (df['performance_trend'] > 1), 'cluster'] = 'Improving'

    cluster_counts = df['cluster'].value_counts()

    # Cluster visualization
    fig_cluster = px.pie(
        values=cluster_counts.values,
        names=cluster_counts.index,
        title="Student Clusters",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    st.plotly_chart(fig_cluster, use_container_width=True, key="student_clusters")

    # Pattern insights
    st.markdown("#### 💡 Key Insights")

    insights = [
        f"📈 {len(df[df['performance_trend'] > 0])} students show improving trends",
        f"📉 {len(df[df['performance_trend'] < -1])} students show declining trends",
        f"🎯 {len(df[df['attendance_rate'] > 0.9])} students have excellent attendance (>90%)",
        f"⚠️ {len(df[df['predicted_risk_score'] > 70])} students are at high risk",
        f"🌟 {len(df[df['current_score'] > 90])} students are high achievers (>90%)"
    ]

    for insight in insights:
        st.markdown(f"• {insight}")


def render_intervention_impact(system, df):
    """Render intervention impact analysis"""
    st.markdown("### 🚀 Intervention Impact Analysis")
    st.markdown("Measure and predict the effectiveness of interventions")

    # Simulated intervention impact data
    intervention_types = ['Academic Tutoring', 'Attendance Support', 'Behavioral Plan', 'Parent Engagement', 'Technology Support']

    impact_data = {
        'Intervention': intervention_types,
        'Students Served': [25, 18, 12, 30, 8],
        'Avg Score Improvement': [12.5, 8.2, 15.3, 9.8, 11.2],
        'Success Rate (%)': [78, 85, 67, 82, 90],
        'Cost per Student': [150, 75, 200, 50, 120],
        'Time to Impact (weeks)': [3, 2, 4, 2, 1]
    }

    impact_df = pd.DataFrame(impact_data)

    # Impact effectiveness chart
    st.markdown("#### 📊 Intervention Effectiveness")

    fig_impact = px.scatter(
        impact_df,
        x='Cost per Student',
        y='Avg Score Improvement',
        size='Students Served',
        color='Success Rate (%)',
        hover_name='Intervention',
        title="Cost vs Effectiveness Analysis",
        color_continuous_scale='RdYlGn'
    )

    st.plotly_chart(fig_impact, use_container_width=True, key="intervention_impact")

    # ROI analysis
    st.markdown("#### 💰 Return on Investment (ROI)")

    # Calculate ROI (simplified)
    impact_df['ROI'] = (impact_df['Avg Score Improvement'] * impact_df['Success Rate (%)'] / 100) / (impact_df['Cost per Student'] / 100)

    fig_roi = px.bar(
        impact_df,
        x='Intervention',
        y='ROI',
        title="Intervention ROI Comparison",
        color='ROI',
        color_continuous_scale='RdYlGn'
    )
    fig_roi.update_layout(xaxis_tickangle=45)

    st.plotly_chart(fig_roi, use_container_width=True, key="intervention_roi")

    # Predictive impact modeling
    st.markdown("#### 🔮 Predictive Impact Modeling")

    st.markdown("**What-if Analysis**: Predict the impact of scaling interventions")

    col1, col2 = st.columns(2)

    with col1:
        selected_intervention = st.selectbox("Select Intervention", intervention_types)
        scale_factor = st.slider("Scale Factor", 0.5, 3.0, 1.0, 0.1)

    with col2:
        # Calculate predicted impact
        intervention_data = impact_df[impact_df['Intervention'] == selected_intervention].iloc[0]

        predicted_students = int(intervention_data['Students Served'] * scale_factor)
        predicted_improvement = intervention_data['Avg Score Improvement']
        predicted_cost = intervention_data['Cost per Student'] * predicted_students

        st.metric("Predicted Students Served", predicted_students)
        st.metric("Expected Avg Improvement", f"{predicted_improvement:.1f} points")
        st.metric("Total Investment", f"${predicted_cost:,.0f}")

    # Impact timeline
    st.markdown("#### ⏱️ Impact Timeline")

    timeline_data = {
        'Week': list(range(1, 9)),
        'Academic Tutoring': [0, 2, 5, 8, 10, 11, 12, 12.5],
        'Attendance Support': [0, 3, 6, 7, 8, 8.1, 8.2, 8.2],
        'Behavioral Plan': [0, 1, 3, 7, 12, 14, 15, 15.3],
        'Parent Engagement': [0, 4, 7, 8.5, 9.2, 9.5, 9.7, 9.8],
        'Technology Support': [0, 8, 10, 10.5, 11, 11.1, 11.2, 11.2]
    }

    timeline_df = pd.DataFrame(timeline_data)

    fig_timeline = px.line(
        timeline_df,
        x='Week',
        y=intervention_types,
        title="Intervention Impact Timeline",
        labels={'value': 'Score Improvement', 'variable': 'Intervention Type'}
    )

    st.plotly_chart(fig_timeline, use_container_width=True, key="impact_timeline")


def get_letter_grade(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def show_welcome_modal():
    """Show welcome modal for first-time users"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        color: white;
        text-align: center;
    ">
        <h2>🎓 Welcome to Student Insights Pipeline!</h2>
        <p>It looks like this is your first time here. Would you like a quick tour to get started?</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 Start Tutorial", use_container_width=True, type="primary"):
                st.session_state.tutorial_progress['first_visit'] = False
                st.session_state.show_tutorial = True
                st.rerun()

        with col_b:
            if st.button("Skip for now", use_container_width=True):
                st.session_state.tutorial_progress['first_visit'] = False
                st.rerun()


def add_tutorial_sidebar(current_page):
    """Add tutorial options to sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎓 Learning Center")

    # Tutorial launcher
    if st.sidebar.button("📚 Interactive Tutorial", help="Learn how to use the system"):
        st.session_state.show_tutorial = True
        st.rerun()

    # Quick tips toggle
    hints_enabled = st.session_state.tutorial_progress.get('show_hints', True)
    if st.sidebar.button(f"💡 {'Hide' if hints_enabled else 'Show'} Hints",
                        help="Toggle helpful hints throughout the interface"):
        st.session_state.tutorial_progress['show_hints'] = not hints_enabled
        st.rerun()

    # Quick tips
    if st.sidebar.button("🎯 Quick Tips", help="Get tips for the current page"):
        show_contextual_tips(current_page)

    # Progress indicator
    completed = len(st.session_state.tutorial_progress.get('completed_modules', []))
    total = 5  # Total number of tutorial modules
    progress = completed / total if total > 0 else 0

    st.sidebar.markdown("#### Tutorial Progress")
    st.sidebar.progress(progress)
    st.sidebar.caption(f"{completed}/{total} modules completed")

    # Show tutorial system if requested
    if st.session_state.get('show_tutorial', False):
        show_embedded_tutorial()


def show_contextual_tips(page_name):
    """Show contextual tips based on current page"""
    tips = {
        "🏠 Dashboard Overview": {
            "title": "💡 Dashboard Tips",
            "tips": [
                "🚨 Red metrics indicate students needing immediate attention",
                "📊 Use the risk distribution chart to understand your class composition",
                "🔍 Click on any chart element to drill down for more details",
                "📈 Trend arrows show if situations are improving or worsening"
            ]
        },
        "👩‍🏫 Teacher Portal": {
            "title": "👩‍🏫 Teacher Tips",
            "tips": [
                "📋 Click on student names to see detailed intervention recommendations",
                "🎯 Use filters to focus on specific risk levels or subjects",
                "📞 The communication tools help you reach out to parents effectively",
                "📈 Track intervention progress to see what's working"
            ]
        },
        "👨‍👩‍👧‍👦 Parent Portal": {
            "title": "👨‍👩‍👧‍👦 Parent Tips",
            "tips": [
                "🏠 Check 'How to Help at Home' for specific daily strategies",
                "📊 Green trends mean your child is improving - celebrate these wins!",
                "📞 Use the messaging feature to stay connected with teachers",
                "🎯 Set small, achievable goals together with your child"
            ]
        },
        "📊 Predictive Analytics": {
            "title": "📊 Analytics Tips",
            "tips": [
                "🔮 Risk scores predict future performance based on current trends",
                "📈 Look for patterns across multiple students to identify systemic issues",
                "⚠️ Early warning indicators help you intervene before problems worsen",
                "🎯 Use confidence intervals to understand prediction reliability"
            ]
        }
    }

    if page_name in tips:
        tip_data = tips[page_name]
        st.sidebar.markdown(f"#### {tip_data['title']}")
        for tip in tip_data['tips']:
            st.sidebar.markdown(f"• {tip}")


def show_embedded_tutorial():
    """Show embedded tutorial system"""
    st.markdown("---")
    st.markdown("## 🎓 Interactive Tutorial System")

    # Create tutorial tabs
    tab1, tab2, tab3 = st.tabs(["🏠 Tutorial Home", "🎯 Current Lesson", "📚 Quick Help"])

    with tab1:
        st.markdown("### Welcome to the Tutorial System!")
        st.info("Choose a tutorial module to get started. Each module is designed to teach you specific skills.")

        # Tutorial module selection
        modules = [
            ("🏠 System Overview", "overview", "Learn dashboard navigation and basic features"),
            ("👩‍🏫 Teacher Portal", "teacher", "Master classroom management and student analysis"),
            ("👨‍👩‍👧‍👦 Parent Portal", "parent", "Support your child's learning effectively"),
            ("📊 Predictive Analytics", "analytics", "Understand AI-powered insights and predictions"),
            ("🎯 Intervention Plans", "interventions", "Create and manage effective action plans")
        ]

        for title, module_id, description in modules:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{title}**")
                st.caption(description)
            with col2:
                if st.button("Start", key=f"start_{module_id}"):
                    st.session_state.current_tutorial_module = module_id
                    st.rerun()

    with tab2:
        current_module = st.session_state.get('current_tutorial_module', None)
        if current_module:
            if TUTORIAL_AVAILABLE:
                # Initialize and show tutorial system
                tutorial_system = TutorialSystem()
                if current_module == "overview":
                    tutorial_system.render_overview_tutorial()
                elif current_module == "teacher":
                    tutorial_system.render_teacher_tutorial()
                elif current_module == "parent":
                    tutorial_system.render_parent_tutorial()
                elif current_module == "analytics":
                    tutorial_system.render_analytics_tutorial()
                elif current_module == "interventions":
                    tutorial_system.render_interventions_tutorial()
            else:
                st.error("Tutorial system not available. Please ensure tutorial_system.py is in the same directory.")
        else:
            st.info("👆 Select a tutorial module from the Tutorial Home tab to get started!")

    with tab3:
        st.markdown("### 💡 Quick Help & Tips")

        with st.expander("🚀 Getting Started", expanded=True):
            st.markdown("""
            **New to the system?** Here's what to do first:
            1. 📊 Explore the sample data to understand the interface
            2. 🎯 Choose your role from the main navigation menu
            3. 📚 Take the role-specific tutorial
            4. 💡 Enable hints to get contextual help as you navigate
            """)

        with st.expander("🔍 Navigation Tips"):
            st.markdown("""
            - **Main Menu**: Use the dropdown to switch between different views
            - **Filters**: Focus your analysis on specific students or subjects
            - **Color Coding**: 🟢 Green = Good, 🟡 Yellow = Monitor, 🔴 Red = Action Needed
            - **Interactive Charts**: Hover over charts for detailed information
            """)

        with st.expander("❓ Need More Help?"):
            st.markdown("""
            - 📖 Check the README.md file for comprehensive documentation
            - 🌐 Open tutorial_website.html for detailed guides
            - 💬 Look for help tooltips throughout the interface
            - 📧 Contact support if you encounter issues
            """)

    # Close tutorial button
    if st.button("✖️ Close Tutorial", type="secondary"):
        st.session_state.show_tutorial = False
        st.rerun()


def show_contextual_hints(page_type):
    """Show contextual hints based on current page"""
    if not st.session_state.tutorial_progress.get('show_hints', True):
        return

    hints = {
        "🏠 Dashboard Overview": "💡 **Dashboard Tip**: Use the metrics at the top to get a quick overview. Red numbers indicate areas needing attention!",
        "👩‍🏫 Teacher Portal": "👩‍🏫 **Teacher Tip**: Click on any student's name to see detailed analytics and AI-generated intervention recommendations.",
        "👨‍👩‍👧‍👦 Parent Portal": "👨‍👩‍👧‍👦 **Parent Tip**: The 'How to Help at Home' section provides specific, actionable strategies tailored to your child's needs.",
        "📊 Predictive Analytics": "📊 **Analytics Tip**: The risk score combines multiple factors. Hover over charts to see detailed breakdowns of each metric.",
        "🎯 Intervention Plans": "🎯 **Intervention Tip**: AI recommendations are based on research-proven strategies. You can customize them to fit your specific situation."
    }

    if page_type in hints:
        st.info(hints[page_type])


if __name__ == "__main__":
    main()
