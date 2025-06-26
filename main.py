#!/usr/bin/env python3
"""
Student Insights Pipeline - Main Application
Organized with proper separation of concerns
"""

import streamlit as st
import sys
import os

# Add app directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import core components
from app.core.predictive_system import PredictiveInterventionSystem
from app.ui.dashboard import render_dashboard_overview, render_student_selector
from app.ui.student_analysis import render_individual_student
from app.tutorials.tutorial_manager import TutorialManager

# Page configuration
st.set_page_config(
    page_title="Student Insights Pipeline",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main application entry point"""
    
    # Initialize core system
    system = PredictiveInterventionSystem()
    
    # Initialize tutorial manager
    tutorial_manager = TutorialManager()
    
    # Show welcome modal for first-time users
    if tutorial_manager.check_first_time_user():
        tutorial_manager.show_welcome_modal()
    
    # Main navigation
    st.sidebar.header("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose View",
        [
            "🏠 Dashboard Overview", 
            "👤 Individual Student", 
            "📊 Predictive Analytics", 
            "📋 Intervention Plans", 
            "👩‍🏫 Teacher Portal", 
            "👨‍👩‍👧‍👦 Parent Portal"
        ]
    )
    
    # Add tutorial sidebar
    tutorial_manager.add_tutorial_sidebar(page)
    
    # Show contextual hints if enabled
    tutorial_manager.show_contextual_hints(page)
    
    # Route to appropriate page
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


def render_predictive_analytics(system):
    """Render predictive analytics page"""
    st.title("📊 Predictive Analytics")
    st.markdown("### AI-Powered Student Success Predictions")
    
    # This would contain the predictive analytics UI
    st.info("🚧 Predictive Analytics page - Implementation in progress")
    
    # Placeholder content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Risk Prediction Model")
        st.markdown("- Machine learning algorithms analyze multiple factors")
        st.markdown("- Early warning system for at-risk students")
        st.markdown("- Confidence intervals for predictions")
    
    with col2:
        st.markdown("#### Trend Analysis")
        st.markdown("- Performance trajectory modeling")
        st.markdown("- Intervention effectiveness tracking")
        st.markdown("- Comparative analytics across cohorts")


def render_intervention_plans(system):
    """Render intervention plans page"""
    st.title("📋 Intervention Plans")
    st.markdown("### Create and Manage Student Support Plans")
    
    # This would contain the intervention planning UI
    st.info("🚧 Intervention Plans page - Implementation in progress")
    
    # Placeholder content
    st.markdown("#### Available Features:")
    st.markdown("- AI-generated intervention recommendations")
    st.markdown("- Customizable action plans")
    st.markdown("- Progress tracking and monitoring")
    st.markdown("- Collaboration tools for teachers and parents")


def render_teacher_portal(system):
    """Render teacher portal page"""
    st.title("👩‍🏫 Teacher Portal")
    st.markdown("### Classroom Management and Student Support")
    
    # This would contain the teacher-specific UI
    st.info("🚧 Teacher Portal page - Implementation in progress")
    
    # Placeholder content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Class Overview")
        st.markdown("- Monitor all students at once")
        st.markdown("- Risk assessment dashboard")
        st.markdown("- Performance trends")
    
    with col2:
        st.markdown("#### Teacher Tools")
        st.markdown("- Individual student analysis")
        st.markdown("- Intervention planning")
        st.markdown("- Parent communication")


def render_parent_portal(system):
    """Render parent portal page"""
    st.title("👨‍👩‍👧‍👦 Parent Portal")
    st.markdown("### Support Your Child's Learning Journey")
    
    # This would contain the parent-specific UI
    st.info("🚧 Parent Portal page - Implementation in progress")
    
    # Placeholder content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Your Child's Progress")
        st.markdown("- Performance reports")
        st.markdown("- Goal tracking")
        st.markdown("- Achievement celebrations")
    
    with col2:
        st.markdown("#### Home Support")
        st.markdown("- Personalized strategies")
        st.markdown("- Daily activity suggestions")
        st.markdown("- Communication with teachers")


if __name__ == "__main__":
    main()
