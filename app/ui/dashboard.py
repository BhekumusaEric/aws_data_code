#!/usr/bin/env python3
"""
Dashboard UI Components
Main dashboard views and visualizations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any


def render_dashboard_overview(system):
    """Render the main dashboard overview"""
    st.title("🏠 Dashboard Overview")
    st.markdown("### Real-time Student Performance Analytics")

    # AWS Health Status Indicator
    render_aws_health_indicator()
    
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")
    
    # Get unique values for filters
    data = system.sample_data
    grade_levels = sorted(data['grade_level'].unique())
    subjects = sorted(data['subject'].unique())
    risk_levels = ['Low', 'Medium', 'High']
    
    selected_grades = st.sidebar.multiselect("Grade Levels", grade_levels, default=grade_levels)
    selected_subjects = st.sidebar.multiselect("Subjects", subjects, default=subjects)
    selected_risks = st.sidebar.multiselect("Risk Levels", risk_levels, default=risk_levels)
    
    # Apply filters
    filters = {
        'grade_levels': selected_grades,
        'subjects': selected_subjects,
        'risk_levels': selected_risks
    }
    
    # Get filtered data and metrics
    filtered_data = system.get_student_data(filters)
    metrics = system.get_dashboard_metrics(filters)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Students", 
            metrics['total_students'],
            help="Total number of students in filtered view"
        )
    
    with col2:
        high_risk_count = metrics['risk_distribution']['high']
        st.metric(
            "High Risk Students", 
            high_risk_count,
            delta=f"{high_risk_count/metrics['total_students']*100:.1f}%" if metrics['total_students'] > 0 else "0%",
            delta_color="inverse",
            help="Students requiring immediate intervention"
        )
    
    with col3:
        avg_score = metrics['performance_metrics']['average_score']
        st.metric(
            "Average Score", 
            f"{avg_score:.1f}%",
            help="Average academic performance across all students"
        )
    
    with col4:
        avg_attendance = metrics['performance_metrics']['average_attendance']
        st.metric(
            "Average Attendance", 
            f"{avg_attendance:.1f}%",
            help="Average attendance rate across all students"
        )
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk Distribution Pie Chart
        risk_data = pd.DataFrame([
            {'Risk Level': 'Low Risk', 'Count': metrics['risk_distribution']['low']},
            {'Risk Level': 'Medium Risk', 'Count': metrics['risk_distribution']['medium']},
            {'Risk Level': 'High Risk', 'Count': metrics['risk_distribution']['high']}
        ])
        
        fig_pie = px.pie(
            risk_data, 
            values='Count', 
            names='Risk Level',
            title="Risk Level Distribution",
            color_discrete_map={
                'Low Risk': '#2E8B57',
                'Medium Risk': '#FFD700', 
                'High Risk': '#DC143C'
            }
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Performance vs Attendance Scatter
        fig_scatter = px.scatter(
            filtered_data,
            x='attendance_rate',
            y='current_score',
            color='risk_level',
            size='assignment_completion_rate',
            hover_data=['name', 'subject', 'grade_level'],
            title="Performance vs Attendance",
            labels={
                'attendance_rate': 'Attendance Rate',
                'current_score': 'Current Score (%)',
                'risk_level': 'Risk Level'
            },
            color_discrete_map={
                'Low': '#2E8B57',
                'Medium': '#FFD700',
                'High': '#DC143C'
            }
        )
        fig_scatter.update_layout(xaxis_tickformat='.0%')
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Trends Analysis
    st.markdown("### 📈 Performance Trends")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        improving = metrics['trends']['improving']
        st.metric("Improving Students", improving, f"{improving/metrics['total_students']*100:.1f}%" if metrics['total_students'] > 0 else "0%")
    
    with col2:
        declining = metrics['trends']['declining']
        st.metric("Declining Students", declining, f"{declining/metrics['total_students']*100:.1f}%" if metrics['total_students'] > 0 else "0%", delta_color="inverse")
    
    with col3:
        stable = metrics['trends']['stable']
        st.metric("Stable Students", stable, f"{stable/metrics['total_students']*100:.1f}%" if metrics['total_students'] > 0 else "0%")
    
    # Subject Performance Breakdown
    st.markdown("### 📚 Subject Performance Breakdown")
    
    subject_performance = filtered_data.groupby('subject').agg({
        'current_score': 'mean',
        'attendance_rate': 'mean',
        'assignment_completion_rate': 'mean',
        'risk_score': 'mean'
    }).round(2)
    
    subject_performance.columns = ['Avg Score', 'Avg Attendance', 'Avg Completion', 'Avg Risk Score']
    subject_performance['Avg Attendance'] = (subject_performance['Avg Attendance'] * 100).round(1)
    subject_performance['Avg Completion'] = (subject_performance['Avg Completion'] * 100).round(1)
    
    st.dataframe(subject_performance, use_container_width=True)
    
    # Recent Activity
    st.markdown("### 🕒 Recent Activity")
    
    # Sort by last updated and show recent changes
    recent_data = filtered_data.nlargest(10, 'last_updated')[['name', 'subject', 'current_score', 'risk_level', 'last_updated']]
    recent_data['last_updated'] = recent_data['last_updated'].dt.strftime('%Y-%m-%d')
    recent_data.columns = ['Student', 'Subject', 'Score', 'Risk Level', 'Last Updated']
    
    st.dataframe(recent_data, use_container_width=True)
    
    # Action Items
    st.markdown("### ⚡ Immediate Action Items")
    
    # High risk students needing immediate attention
    high_risk_students = filtered_data[filtered_data['risk_level'] == 'High'].nsmallest(5, 'current_score')
    
    if not high_risk_students.empty:
        for _, student in high_risk_students.iterrows():
            with st.expander(f"🚨 {student['name']} - {student['subject']} (Score: {student['current_score']:.1f}%)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Current Status:**
                    - Score: {student['current_score']:.1f}%
                    - Attendance: {student['attendance_rate']*100:.1f}%
                    - Assignment Completion: {student['assignment_completion_rate']*100:.1f}%
                    - Risk Score: {student['risk_score']:.1f}/100
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Recommended Actions:**
                    - Schedule immediate teacher meeting
                    - Contact parents/guardians
                    - Implement tutoring support
                    - Monitor daily attendance
                    """)
                
                if st.button(f"Create Intervention Plan for {student['name']}", key=f"intervention_{student['student_id']}"):
                    st.session_state.selected_student = student['student_id']
                    st.session_state.current_page = "📋 Intervention Plans"
                    st.rerun()
    else:
        st.success("🎉 No high-risk students requiring immediate attention!")


def render_performance_charts(data: pd.DataFrame):
    """Render additional performance visualization charts"""
    
    # Grade Level Performance
    st.markdown("### 📊 Performance by Grade Level")
    
    grade_performance = data.groupby('grade_level').agg({
        'current_score': ['mean', 'std'],
        'risk_score': 'mean'
    }).round(2)
    
    grade_performance.columns = ['Avg Score', 'Score StdDev', 'Avg Risk Score']
    
    fig_grade = px.bar(
        x=grade_performance.index,
        y=grade_performance['Avg Score'],
        error_y=grade_performance['Score StdDev'],
        title="Average Performance by Grade Level",
        labels={'x': 'Grade Level', 'y': 'Average Score (%)'}
    )
    
    st.plotly_chart(fig_grade, use_container_width=True)
    
    # Performance Distribution Histogram
    st.markdown("### 📈 Score Distribution")
    
    fig_hist = px.histogram(
        data,
        x='current_score',
        color='risk_level',
        title="Score Distribution by Risk Level",
        labels={'current_score': 'Current Score (%)', 'count': 'Number of Students'},
        color_discrete_map={
            'Low': '#2E8B57',
            'Medium': '#FFD700',
            'High': '#DC143C'
        }
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)


def render_alerts_and_notifications():
    """Render alerts and notification system"""
    st.markdown("### 🔔 System Alerts")
    
    # Sample alerts - in a real system, these would come from the database
    alerts = [
        {
            'type': 'warning',
            'message': '5 students have missed more than 3 consecutive days',
            'action': 'Review attendance patterns',
            'priority': 'High'
        },
        {
            'type': 'info',
            'message': 'New intervention strategies available for Math support',
            'action': 'Review new strategies',
            'priority': 'Medium'
        },
        {
            'type': 'success',
            'message': '12 students showed improvement this week',
            'action': 'Celebrate successes',
            'priority': 'Low'
        }
    ]
    
    for alert in alerts:
        if alert['type'] == 'warning':
            st.warning(f"⚠️ **{alert['priority']} Priority**: {alert['message']}")
        elif alert['type'] == 'info':
            st.info(f"ℹ️ **{alert['priority']} Priority**: {alert['message']}")
        elif alert['type'] == 'success':
            st.success(f"✅ **{alert['priority']} Priority**: {alert['message']}")
        
        if st.button(alert['action'], key=f"alert_{alert['message'][:20]}"):
            st.toast(f"Action taken: {alert['action']}")


def render_quick_actions():
    """Render quick action buttons"""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Generate Report", use_container_width=True):
            st.toast("Report generation started...")
    
    with col2:
        if st.button("📧 Send Alerts", use_container_width=True):
            st.toast("Alerts sent to relevant teachers...")
    
    with col3:
        if st.button("📅 Schedule Meetings", use_container_width=True):
            st.toast("Meeting scheduler opened...")
    
    with col4:
        if st.button("📈 Export Data", use_container_width=True):
            st.toast("Data export prepared...")


def render_aws_health_indicator():
    """Render a quick AWS health status indicator"""
    try:
        from app.utils.aws_health_checker import AWSHealthChecker

        # Quick health check (lightweight)
        health_checker = AWSHealthChecker()

        # Just check credentials for quick indicator
        creds_status = health_checker.check_aws_credentials()

        if creds_status['status'] == 'healthy':
            st.success("☁️ **AWS Services Connected** | [View Details →](/?page=AWS+Health+Monitor)")
        else:
            st.error("☁️ **AWS Connection Issue** | [Troubleshoot →](/?page=AWS+Health+Monitor)")

    except Exception as e:
        st.warning("☁️ **AWS Status Unknown** | [Check Health →](/?page=AWS+Health+Monitor)")


def render_student_selector(system):
    """Render student selection interface"""
    st.sidebar.markdown("### 👤 Select Student")

    # Get all students
    students = system.sample_data[['student_id', 'name', 'subject', 'grade_level', 'risk_level']].copy()
    students['display_name'] = students['name'] + ' (' + students['subject'] + ', Grade ' + students['grade_level'] + ')'

    # Filter options
    grade_filter = st.sidebar.selectbox("Filter by Grade", ['All'] + sorted(students['grade_level'].unique()))
    risk_filter = st.sidebar.selectbox("Filter by Risk Level", ['All', 'High', 'Medium', 'Low'])

    # Apply filters
    filtered_students = students.copy()
    if grade_filter != 'All':
        filtered_students = filtered_students[filtered_students['grade_level'] == grade_filter]
    if risk_filter != 'All':
        filtered_students = filtered_students[filtered_students['risk_level'] == risk_filter]

    # Student selection
    if not filtered_students.empty:
        selected_display = st.sidebar.selectbox(
            "Choose Student",
            filtered_students['display_name'].tolist(),
            help="Select a student to view detailed analysis"
        )

        # Get selected student ID
        selected_student_id = filtered_students[filtered_students['display_name'] == selected_display]['student_id'].iloc[0]
        return selected_student_id
    else:
        st.sidebar.warning("No students match the selected filters")
        return None
