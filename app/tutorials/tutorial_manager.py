#!/usr/bin/env python3
"""
Tutorial Manager
Handles tutorial integration and user guidance
"""

import streamlit as st
from typing import Dict, List, Any


class TutorialManager:
    """Manages tutorial system integration"""
    
    def __init__(self):
        self.initialize_tutorial_state()
    
    def initialize_tutorial_state(self):
        """Initialize tutorial session state"""
        if 'tutorial_progress' not in st.session_state:
            st.session_state.tutorial_progress = {
                'first_visit': True,
                'completed_modules': [],
                'show_hints': True,
                'user_role': None,
                'current_module': None
            }
    
    def check_first_time_user(self) -> bool:
        """Check if this is a first-time user"""
        return st.session_state.tutorial_progress.get('first_visit', True)
    
    def show_welcome_modal(self):
        """Show welcome modal for first-time users"""
        if self.check_first_time_user():
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
    
    def add_tutorial_sidebar(self, current_page: str):
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
            self.show_contextual_tips(current_page)
        
        # Progress indicator
        completed = len(st.session_state.tutorial_progress.get('completed_modules', []))
        total = 5  # Total number of tutorial modules
        progress = completed / total if total > 0 else 0
        
        st.sidebar.markdown("#### Tutorial Progress")
        st.sidebar.progress(progress)
        st.sidebar.caption(f"{completed}/{total} modules completed")
        
        # Show tutorial system if requested
        if st.session_state.get('show_tutorial', False):
            self.show_embedded_tutorial()
    
    def show_contextual_hints(self, page_name: str):
        """Show contextual hints based on current page"""
        if not st.session_state.tutorial_progress.get('show_hints', True):
            return
        
        hints = {
            "🏠 Dashboard Overview": "💡 **Dashboard Tip**: Use the metrics at the top to get a quick overview. Red numbers indicate areas needing attention!",
            "👩‍🏫 Teacher Portal": "👩‍🏫 **Teacher Tip**: Click on any student's name to see detailed analytics and AI-generated intervention recommendations.",
            "👨‍👩‍👧‍👦 Parent Portal": "👨‍👩‍👧‍👦 **Parent Tip**: The 'How to Help at Home' section provides specific, actionable strategies tailored to your child's needs.",
            "📊 Predictive Analytics": "📊 **Analytics Tip**: The risk score combines multiple factors. Hover over charts to see detailed breakdowns of each metric.",
            "🎯 Intervention Plans": "🎯 **Intervention Tip**: AI recommendations are based on research-proven strategies. You can customize them to fit your specific situation.",
            "👤 Individual Student": "👤 **Student Analysis Tip**: Use the historical performance chart to identify patterns and the prediction chart to plan interventions."
        }
        
        if page_name in hints:
            st.info(hints[page_name])
    
    def show_contextual_tips(self, page_name: str):
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
    
    def show_embedded_tutorial(self):
        """Show embedded tutorial system"""
        st.markdown("---")
        st.markdown("## 🎓 Interactive Tutorial System")
        
        # Create tutorial tabs
        tab1, tab2, tab3 = st.tabs(["🏠 Tutorial Home", "🎯 Current Lesson", "📚 Quick Help"])
        
        with tab1:
            self.render_tutorial_home()
        
        with tab2:
            self.render_current_lesson()
        
        with tab3:
            self.render_quick_help()
        
        # Close tutorial button
        if st.button("✖️ Close Tutorial", type="secondary"):
            st.session_state.show_tutorial = False
            st.rerun()
    
    def render_tutorial_home(self):
        """Render tutorial home page"""
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
                    st.session_state.tutorial_progress['current_module'] = module_id
                    st.rerun()
    
    def render_current_lesson(self):
        """Render current tutorial lesson"""
        current_module = st.session_state.tutorial_progress.get('current_module', None)
        
        if current_module:
            if current_module == "overview":
                self.render_overview_tutorial()
            elif current_module == "teacher":
                self.render_teacher_tutorial()
            elif current_module == "parent":
                self.render_parent_tutorial()
            elif current_module == "analytics":
                self.render_analytics_tutorial()
            elif current_module == "interventions":
                self.render_interventions_tutorial()
        else:
            st.info("👆 Select a tutorial module from the Tutorial Home tab to get started!")
    
    def render_quick_help(self):
        """Render quick help section"""
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
    
    def render_overview_tutorial(self):
        """Render system overview tutorial"""
        st.markdown("## 🏠 System Overview Tutorial")
        st.info("This tutorial covers the main dashboard and navigation features.")
        
        # Tutorial content would go here
        st.markdown("### Dashboard Navigation")
        st.markdown("- Use the sidebar to switch between different views")
        st.markdown("- The main dashboard shows key metrics and alerts")
        st.markdown("- Filters help you focus on specific student groups")
        
        if st.button("Mark as Complete"):
            if 'overview' not in st.session_state.tutorial_progress['completed_modules']:
                st.session_state.tutorial_progress['completed_modules'].append('overview')
            st.success("✅ Overview tutorial completed!")
    
    def render_teacher_tutorial(self):
        """Render teacher portal tutorial"""
        st.markdown("## 👩‍🏫 Teacher Portal Tutorial")
        st.info("Learn how to effectively manage your classroom and support individual students.")
        
        # Tutorial content
        st.markdown("### Key Features for Teachers")
        st.markdown("- Class overview with risk assessment")
        st.markdown("- Individual student analysis")
        st.markdown("- Intervention planning tools")
        st.markdown("- Parent communication features")
        
        if st.button("Mark as Complete"):
            if 'teacher' not in st.session_state.tutorial_progress['completed_modules']:
                st.session_state.tutorial_progress['completed_modules'].append('teacher')
            st.success("✅ Teacher tutorial completed!")
    
    def render_parent_tutorial(self):
        """Render parent portal tutorial"""
        st.markdown("## 👨‍👩‍👧‍👦 Parent Portal Tutorial")
        st.info("Discover how to support your child's learning at home.")
        
        # Tutorial content
        st.markdown("### Supporting Your Child")
        st.markdown("- Understanding progress reports")
        st.markdown("- Home support strategies")
        st.markdown("- Communication with teachers")
        st.markdown("- Goal setting and tracking")
        
        if st.button("Mark as Complete"):
            if 'parent' not in st.session_state.tutorial_progress['completed_modules']:
                st.session_state.tutorial_progress['completed_modules'].append('parent')
            st.success("✅ Parent tutorial completed!")
    
    def render_analytics_tutorial(self):
        """Render analytics tutorial"""
        st.markdown("## 📊 Predictive Analytics Tutorial")
        st.info("Learn how to interpret AI-powered insights and predictions.")
        
        # Tutorial content
        st.markdown("### Understanding Analytics")
        st.markdown("- Risk score interpretation")
        st.markdown("- Performance trend analysis")
        st.markdown("- Prediction confidence levels")
        st.markdown("- Early warning indicators")
        
        if st.button("Mark as Complete"):
            if 'analytics' not in st.session_state.tutorial_progress['completed_modules']:
                st.session_state.tutorial_progress['completed_modules'].append('analytics')
            st.success("✅ Analytics tutorial completed!")
    
    def render_interventions_tutorial(self):
        """Render interventions tutorial"""
        st.markdown("## 🎯 Intervention Plans Tutorial")
        st.info("Learn to create and manage effective intervention strategies.")
        
        # Tutorial content
        st.markdown("### Creating Interventions")
        st.markdown("- AI-generated recommendations")
        st.markdown("- Customizing action plans")
        st.markdown("- Tracking effectiveness")
        st.markdown("- Collaboration tools")
        
        if st.button("Mark as Complete"):
            if 'interventions' not in st.session_state.tutorial_progress['completed_modules']:
                st.session_state.tutorial_progress['completed_modules'].append('interventions')
            st.success("✅ Interventions tutorial completed!")
