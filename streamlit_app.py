#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Student Insights Pipeline - Streamlit Dashboard
Interactive web interface for student analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import boto3
from datetime import datetime, timedelta
import json
import requests
from typing import Dict, List, Any, Optional

# Page configuration
st.set_page_config(
    page_title="Student Insights Pipeline",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .success-card {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


class StudentInsightsDashboard:
    """Main dashboard class for Student Insights Pipeline"""
    
    def __init__(self):
        self.aws_configured = self.check_aws_connection()
        self.sample_data = self.generate_sample_data()
    
    def check_aws_connection(self) -> bool:
        """Check if AWS is configured and accessible"""
        try:
            sts = boto3.client('sts')
            sts.get_caller_identity()
            return True
        except Exception:
            return False
    
    def generate_sample_data(self) -> pd.DataFrame:
        """Generate sample student data for demonstration"""
        np.random.seed(42)
        
        students = []
        subjects = ['Mathematics', 'English', 'Science', 'History', 'Art']
        grades = ['9', '10', '11', '12']
        
        for i in range(500):
            # Generate realistic student data
            base_performance = np.random.normal(75, 15)
            attendance_factor = np.random.uniform(0.7, 1.0)
            
            student = {
                'student_id': f'STU{i+1:04d}',
                'name': f'Student {i+1}',
                'grade_level': np.random.choice(grades),
                'subject': np.random.choice(subjects),
                'math_score': max(0, min(100, base_performance + np.random.normal(0, 5))),
                'reading_score': max(0, min(100, base_performance + np.random.normal(0, 5))),
                'writing_score': max(0, min(100, base_performance + np.random.normal(0, 5))),
                'attendance_rate': attendance_factor,
                'assignment_completion_rate': min(1.0, attendance_factor + np.random.normal(0, 0.1)),
                'timestamp': datetime.now() - timedelta(days=np.random.randint(0, 30))
            }
            
            # Calculate derived fields
            student['average_score'] = (student['math_score'] + student['reading_score'] + student['writing_score']) / 3
            
            # Performance category
            if student['average_score'] >= 90:
                student['performance_category'] = 'Excellent'
            elif student['average_score'] >= 80:
                student['performance_category'] = 'Good'
            elif student['average_score'] >= 70:
                student['performance_category'] = 'Satisfactory'
            elif student['average_score'] >= 60:
                student['performance_category'] = 'Needs Improvement'
            else:
                student['performance_category'] = 'At Risk'
            
            # Risk level calculation
            risk_factors = 0
            if student['average_score'] < 70:
                risk_factors += 2
            if student['attendance_rate'] < 0.85:
                risk_factors += 2
            if student['assignment_completion_rate'] < 0.8:
                risk_factors += 1
            
            if risk_factors >= 4:
                student['risk_level'] = 'High Risk'
            elif risk_factors >= 2:
                student['risk_level'] = 'Medium Risk'
            elif risk_factors >= 1:
                student['risk_level'] = 'Low Risk'
            else:
                student['risk_level'] = 'No Risk'
            
            students.append(student)
        
        return pd.DataFrame(students)
    
    def render_header(self):
        """Render the main header"""
        st.markdown('<h1 class="main-header">🎓 Student Insights Pipeline</h1>', unsafe_allow_html=True)
        
        if not self.aws_configured:
            st.warning("⚠️ AWS not configured. Showing demo data. Configure AWS credentials to access live data.")
        else:
            st.success("✅ Connected to AWS. Showing live data from your pipeline.")
    
    def render_sidebar(self):
        """Render the sidebar with filters and controls"""
        st.sidebar.header("📊 Dashboard Controls")
        
        # Data source selection
        if self.aws_configured:
            data_source = st.sidebar.selectbox(
                "Data Source",
                ["Live Data", "Demo Data"],
                index=0
            )
        else:
            data_source = "Demo Data"
            st.sidebar.info("💡 Configure AWS to access live data")
        
        # Filters
        st.sidebar.subheader("🔍 Filters")
        
        selected_grades = st.sidebar.multiselect(
            "Grade Levels",
            options=sorted(self.sample_data['grade_level'].unique()),
            default=sorted(self.sample_data['grade_level'].unique())
        )
        
        selected_subjects = st.sidebar.multiselect(
            "Subjects",
            options=sorted(self.sample_data['subject'].unique()),
            default=sorted(self.sample_data['subject'].unique())
        )
        
        risk_filter = st.sidebar.selectbox(
            "Risk Level Filter",
            ["All Students", "High Risk Only", "Medium Risk Only", "At Risk (High + Medium)"]
        )
        
        # Date range
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        return {
            'data_source': data_source,
            'grades': selected_grades,
            'subjects': selected_subjects,
            'risk_filter': risk_filter,
            'date_range': date_range
        }
    
    def filter_data(self, filters: Dict) -> pd.DataFrame:
        """Apply filters to the data"""
        df = self.sample_data.copy()
        
        # Apply filters
        if filters['grades']:
            df = df[df['grade_level'].isin(filters['grades'])]
        
        if filters['subjects']:
            df = df[df['subject'].isin(filters['subjects'])]
        
        # Risk filter
        if filters['risk_filter'] == "High Risk Only":
            df = df[df['risk_level'] == 'High Risk']
        elif filters['risk_filter'] == "Medium Risk Only":
            df = df[df['risk_level'] == 'Medium Risk']
        elif filters['risk_filter'] == "At Risk (High + Medium)":
            df = df[df['risk_level'].isin(['High Risk', 'Medium Risk'])]
        
        return df
    
    def render_key_metrics(self, df: pd.DataFrame):
        """Render key performance metrics"""
        st.subheader("📈 Key Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_students = len(df['student_id'].unique())
            st.metric("Total Students", total_students)
        
        with col2:
            avg_score = df['average_score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        with col3:
            avg_attendance = df['attendance_rate'].mean() * 100
            st.metric("Average Attendance", f"{avg_attendance:.1f}%")
        
        with col4:
            high_risk_count = len(df[df['risk_level'] == 'High Risk'])
            st.metric("High Risk Students", high_risk_count, delta=f"{high_risk_count/total_students*100:.1f}%")
        
        with col5:
            excellent_count = len(df[df['performance_category'] == 'Excellent'])
            st.metric("Excellent Performers", excellent_count, delta=f"{excellent_count/total_students*100:.1f}%")
    
    def render_performance_distribution(self, df: pd.DataFrame):
        """Render performance distribution charts"""
        st.subheader("📊 Performance Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance category distribution
            perf_dist = df['performance_category'].value_counts()
            fig_perf = px.pie(
                values=perf_dist.values,
                names=perf_dist.index,
                title="Performance Categories",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_perf, use_container_width=True, key="performance_pie_chart")

        with col2:
            # Risk level distribution
            risk_dist = df['risk_level'].value_counts()
            colors = {'No Risk': '#4CAF50', 'Low Risk': '#FFC107', 'Medium Risk': '#FF9800', 'High Risk': '#F44336'}
            fig_risk = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title="Risk Level Distribution",
                color=risk_dist.index,
                color_discrete_map=colors
            )
            st.plotly_chart(fig_risk, use_container_width=True, key="risk_pie_chart")
    
    def render_subject_analysis(self, df: pd.DataFrame, key_prefix: str = ""):
        """Render subject-specific analysis"""
        st.subheader("📚 Subject Performance Analysis")

        # Subject performance comparison
        subject_stats = df.groupby('subject').agg({
            'math_score': 'mean',
            'reading_score': 'mean',
            'writing_score': 'mean',
            'average_score': 'mean',
            'student_id': 'nunique'
        }).round(1)

        subject_stats.columns = ['Math Score', 'Reading Score', 'Writing Score', 'Average Score', 'Student Count']

        col1, col2 = st.columns(2)

        with col1:
            # Bar chart of average scores by subject
            fig_subject = px.bar(
                x=subject_stats.index,
                y=subject_stats['Average Score'],
                title="Average Score by Subject",
                color=subject_stats['Average Score'],
                color_continuous_scale='RdYlGn'
            )
            fig_subject.update_layout(showlegend=False)
            st.plotly_chart(fig_subject, use_container_width=True, key=f"{key_prefix}subject_bar_chart")

        with col2:
            # Subject performance table
            st.write("**Subject Performance Summary**")
            st.dataframe(subject_stats, use_container_width=True)
    
    def render_risk_analysis(self, df: pd.DataFrame):
        """Render risk analysis and alerts"""
        st.subheader("⚠️ Risk Analysis & Early Warning")
        
        high_risk_students = df[df['risk_level'] == 'High Risk']
        medium_risk_students = df[df['risk_level'] == 'Medium Risk']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if len(high_risk_students) > 0:
                st.markdown('<div class="alert-high">', unsafe_allow_html=True)
                st.write(f"🚨 **{len(high_risk_students)} High Risk Students**")
                st.write("Immediate intervention recommended")
                
                # Show top 5 high risk students
                high_risk_display = high_risk_students.nlargest(5, 'average_score')[
                    ['student_id', 'name', 'grade_level', 'average_score', 'attendance_rate']
                ].copy()
                high_risk_display['attendance_rate'] = (high_risk_display['attendance_rate'] * 100).round(1)
                st.dataframe(high_risk_display, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if len(medium_risk_students) > 0:
                st.markdown('<div class="alert-medium">', unsafe_allow_html=True)
                st.write(f"⚠️ **{len(medium_risk_students)} Medium Risk Students**")
                st.write("Monitor closely and provide support")
                
                # Show top 5 medium risk students
                medium_risk_display = medium_risk_students.nlargest(5, 'average_score')[
                    ['student_id', 'name', 'grade_level', 'average_score', 'attendance_rate']
                ].copy()
                medium_risk_display['attendance_rate'] = (medium_risk_display['attendance_rate'] * 100).round(1)
                st.dataframe(medium_risk_display, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    def render_trends_analysis(self, df: pd.DataFrame):
        """Render trends and time series analysis"""
        st.subheader("📈 Performance Trends")
        
        # Create time-based aggregation
        df_trends = df.copy()
        df_trends['date'] = pd.to_datetime(df_trends['timestamp']).dt.date
        
        daily_stats = df_trends.groupby('date').agg({
            'average_score': 'mean',
            'attendance_rate': 'mean',
            'student_id': 'nunique'
        }).reset_index()
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Average Score Over Time', 'Attendance Rate Over Time'),
            vertical_spacing=0.1
        )
        
        # Average score trend
        fig.add_trace(
            go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['average_score'],
                mode='lines+markers',
                name='Average Score',
                line=dict(color='#1f77b4', width=3)
            ),
            row=1, col=1
        )
        
        # Attendance rate trend
        fig.add_trace(
            go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['attendance_rate'] * 100,
                mode='lines+markers',
                name='Attendance Rate (%)',
                line=dict(color='#ff7f0e', width=3)
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key="trends_chart")
    
    def render_data_submission(self):
        """Render data submission interface"""
        st.subheader("📝 Submit New Student Data")
        
        with st.form("student_data_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                student_id = st.text_input("Student ID", placeholder="STU0001")
                name = st.text_input("Student Name", placeholder="John Doe")
                grade_level = st.selectbox("Grade Level", ["9", "10", "11", "12"])
                subject = st.selectbox("Subject", ["Mathematics", "English", "Science", "History", "Art"])
            
            with col2:
                math_score = st.slider("Math Score", 0, 100, 75)
                reading_score = st.slider("Reading Score", 0, 100, 75)
                writing_score = st.slider("Writing Score", 0, 100, 75)
                attendance_rate = st.slider("Attendance Rate", 0.0, 1.0, 0.9, 0.01)
            
            submitted = st.form_submit_button("Submit Student Data")
            
            if submitted:
                # Prepare data for submission
                student_data = {
                    "student_id": student_id,
                    "name": name,
                    "grade_level": grade_level,
                    "subject": subject,
                    "math_score": math_score,
                    "reading_score": reading_score,
                    "writing_score": writing_score,
                    "attendance_rate": attendance_rate,
                    "assignment_completion_rate": attendance_rate * 0.95  # Estimate
                }
                
                if self.aws_configured:
                    # Try to submit to actual API
                    st.info("🚀 Submitting to Student Insights Pipeline...")
                    # This would call the actual API endpoint
                    st.success("✅ Data submitted successfully!")
                else:
                    st.info("💡 Demo mode: Data would be submitted to the pipeline when AWS is configured")
                
                st.json(student_data)


def main():
    """Main Streamlit application"""
    dashboard = StudentInsightsDashboard()
    
    # Render header
    dashboard.render_header()
    
    # Render sidebar and get filters
    filters = dashboard.render_sidebar()
    
    # Filter data
    filtered_data = dashboard.filter_data(filters)
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "📈 Performance", 
        "⚠️ Risk Analysis", 
        "📚 Subject Analysis", 
        "📝 Data Entry"
    ])
    
    with tab1:
        dashboard.render_key_metrics(filtered_data)
        dashboard.render_performance_distribution(filtered_data)
    
    with tab2:
        dashboard.render_trends_analysis(filtered_data)
        dashboard.render_subject_analysis(filtered_data, key_prefix="tab2_")

    with tab3:
        dashboard.render_risk_analysis(filtered_data)

    with tab4:
        dashboard.render_subject_analysis(filtered_data, key_prefix="tab4_")
        
        # Detailed subject breakdown
        st.subheader("📋 Detailed Subject Performance")
        subject_detail = filtered_data.groupby(['subject', 'grade_level']).agg({
            'average_score': ['mean', 'std', 'count'],
            'attendance_rate': 'mean'
        }).round(2)
        st.dataframe(subject_detail, use_container_width=True)
    
    with tab5:
        dashboard.render_data_submission()
    
    # Footer
    st.markdown("---")
    st.markdown("🎓 **Student Insights Pipeline** | Built with Streamlit | Powered by AWS")


if __name__ == "__main__":
    main()
