#!/usr/bin/env python3
"""
Individual Student Analysis UI Components
Detailed student performance analysis and recommendations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any


def render_individual_student(system):
    """Render individual student analysis page"""
    st.title("👤 Individual Student Analysis")
    
    # Student selection
    selected_student_id = render_student_selector(system)
    
    if selected_student_id:
        student_data = system.get_student_by_id(selected_student_id)
        
        if student_data:
            render_student_profile(student_data, system)
            render_performance_analysis(student_data, system)
            render_predictions(student_data, system)
            render_recommendations(student_data, system)
        else:
            st.error("Student data not found")
    else:
        st.info("👆 Please select a student from the sidebar to view detailed analysis")


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


def render_student_profile(student_data: Dict, system):
    """Render student profile header"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"## {student_data['name']}")
        st.markdown(f"**Subject:** {student_data['subject']} | **Grade:** {student_data['grade_level']}")
        
        # Risk level with color coding
        risk_level = student_data['risk_level']
        if risk_level == 'High':
            st.error(f"🚨 Risk Level: {risk_level}")
        elif risk_level == 'Medium':
            st.warning(f"⚠️ Risk Level: {risk_level}")
        else:
            st.success(f"✅ Risk Level: {risk_level}")
    
    with col2:
        st.metric("Current Score", f"{student_data['current_score']:.1f}%")
        st.metric("Risk Score", f"{student_data['risk_score']:.1f}/100")
    
    with col3:
        st.metric("Attendance", f"{student_data['attendance_rate']*100:.1f}%")
        st.metric("Completion Rate", f"{student_data['assignment_completion_rate']*100:.1f}%")


def render_performance_analysis(student_data: Dict, system):
    """Render detailed performance analysis"""
    st.markdown("### 📊 Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Historical performance chart
        historical_scores = student_data['historical_scores']
        months = list(range(1, len(historical_scores) + 1))
        
        fig_history = go.Figure()
        fig_history.add_trace(go.Scatter(
            x=months,
            y=historical_scores,
            mode='lines+markers',
            name='Performance',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        # Add trend line
        z = np.polyfit(months, historical_scores, 1)
        p = np.poly1d(z)
        fig_history.add_trace(go.Scatter(
            x=months,
            y=p(months),
            mode='lines',
            name='Trend',
            line=dict(color='red', dash='dash')
        ))
        
        fig_history.update_layout(
            title="Performance History (Last 6 Months)",
            xaxis_title="Months Ago",
            yaxis_title="Score (%)",
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig_history, use_container_width=True)
    
    with col2:
        # Performance breakdown radar chart
        categories = ['Current Score', 'Attendance', 'Completion Rate', 'Engagement', 'Support Level']
        values = [
            student_data['current_score'],
            student_data['attendance_rate'] * 100,
            student_data['assignment_completion_rate'] * 100,
            student_data['engagement_level'] * 100,
            student_data['support_level'] * 100
        ]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Student Performance'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title="Performance Breakdown",
            showlegend=False
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Performance insights
    st.markdown("#### 🔍 Performance Insights")
    
    trend = student_data['performance_trend']
    volatility = student_data['performance_volatility']
    
    insights = []
    
    if trend > 1:
        insights.append("📈 **Positive Trend**: Performance is improving consistently")
    elif trend < -1:
        insights.append("📉 **Declining Trend**: Performance is decreasing - intervention needed")
    else:
        insights.append("📊 **Stable Performance**: Performance is relatively stable")
    
    if volatility > 10:
        insights.append("⚠️ **High Variability**: Performance is inconsistent - may indicate external factors")
    elif volatility < 5:
        insights.append("✅ **Consistent Performance**: Student shows stable performance patterns")
    
    if student_data['attendance_rate'] < 0.85:
        insights.append("🚨 **Attendance Concern**: Low attendance may be impacting performance")
    
    if student_data['assignment_completion_rate'] < 0.80:
        insights.append("📝 **Assignment Issues**: Low completion rate needs attention")
    
    for insight in insights:
        st.markdown(f"- {insight}")


def render_predictions(student_data: Dict, system):
    """Render performance predictions"""
    st.markdown("### 🔮 Performance Predictions")
    
    predictions = system.predict_future_performance(student_data, months_ahead=6)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Prediction chart
        pred_data = predictions['predictions']
        months = [p['month'] for p in pred_data]
        predicted_scores = [p['predicted_score'] for p in pred_data]
        lower_bounds = [p['lower_bound'] for p in pred_data]
        upper_bounds = [p['upper_bound'] for p in pred_data]
        
        fig_pred = go.Figure()
        
        # Add prediction line
        fig_pred.add_trace(go.Scatter(
            x=months,
            y=predicted_scores,
            mode='lines+markers',
            name='Predicted Score',
            line=dict(color='green', width=3)
        ))
        
        # Add confidence interval
        fig_pred.add_trace(go.Scatter(
            x=months + months[::-1],
            y=upper_bounds + lower_bounds[::-1],
            fill='toself',
            fillcolor='rgba(0,255,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Interval'
        ))
        
        fig_pred.update_layout(
            title="6-Month Performance Prediction",
            xaxis_title="Months Ahead",
            yaxis_title="Predicted Score (%)",
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig_pred, use_container_width=True)
    
    with col2:
        # Prediction summary
        st.markdown("#### 📋 Prediction Summary")
        
        trend_direction = predictions['trend_direction']
        confidence_level = predictions['confidence_level']
        
        if trend_direction == 'improving':
            st.success(f"📈 **Trend**: {trend_direction.title()}")
        elif trend_direction == 'declining':
            st.error(f"📉 **Trend**: {trend_direction.title()}")
        else:
            st.info(f"📊 **Trend**: {trend_direction.title()}")
        
        st.info(f"🎯 **Confidence**: {confidence_level.title()}")
        
        # Show specific predictions
        st.markdown("**Predicted Scores:**")
        for pred in pred_data[:3]:  # Show first 3 months
            confidence = pred['confidence']
            st.markdown(f"Month {pred['month']}: {pred['predicted_score']:.1f}% (±{(pred['upper_bound']-pred['lower_bound'])/2:.1f}%)")


def render_recommendations(student_data: Dict, system):
    """Render intervention recommendations"""
    st.markdown("### 🎯 Intervention Recommendations")
    
    recommendations = system.generate_intervention_recommendations(student_data)
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            priority_color = {
                'High': '🔴',
                'Medium': '🟡', 
                'Low': '🟢'
            }
            
            with st.expander(f"{priority_color[rec['priority']]} {rec['category']}: {rec['intervention'].title()} ({rec['priority']} Priority)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Description:** {rec['description']}")
                    st.markdown(f"**Expected Improvement:** {rec['expected_improvement']}")
                    st.markdown(f"**Timeline:** {rec['timeline']}")
                
                with col2:
                    st.markdown("**Resources Needed:**")
                    for resource in rec['resources_needed']:
                        st.markdown(f"- {resource}")
                    
                    st.markdown("**Success Indicators:**")
                    for indicator in rec['success_indicators']:
                        st.markdown(f"- {indicator}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Implement Plan", key=f"implement_{i}"):
                        st.success("✅ Intervention plan added to student record")
                
                with col2:
                    if st.button(f"Schedule Meeting", key=f"schedule_{i}"):
                        st.info("📅 Meeting scheduled with relevant parties")
                
                with col3:
                    if st.button(f"Contact Parents", key=f"contact_{i}"):
                        st.info("📞 Parent communication initiated")
    
    else:
        st.success("🎉 No immediate interventions needed - student is performing well!")
    
    # Action buttons
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📧 Email Teacher", use_container_width=True):
            st.toast("Email sent to teacher")
    
    with col2:
        if st.button("📞 Call Parents", use_container_width=True):
            st.toast("Parent contact logged")
    
    with col3:
        if st.button("📅 Schedule Meeting", use_container_width=True):
            st.toast("Meeting scheduled")
    
    with col4:
        if st.button("📊 Generate Report", use_container_width=True):
            st.toast("Report generated")
