#!/usr/bin/env python3
"""
Tutorial Integration Module
Embeds tutorial functionality into the main predictive intervention system
"""

import streamlit as st
import json
from datetime import datetime

class TutorialIntegration:
    """Integrates tutorial system into main application"""
    
    def __init__(self):
        self.tutorial_config = self.load_tutorial_config()
        self.initialize_user_progress()
    
    def load_tutorial_config(self):
        """Load tutorial configuration"""
        return {
            "first_time_user": True,
            "show_hints": True,
            "tutorial_mode": False,
            "completed_tutorials": [],
            "user_role": None
        }
    
    def initialize_user_progress(self):
        """Initialize user progress tracking"""
        if 'tutorial_progress' not in st.session_state:
            st.session_state.tutorial_progress = {
                'first_visit': True,
                'completed_modules': [],
                'current_step': 0,
                'user_role': None,
                'show_hints': True
            }
    
    def check_first_time_user(self):
        """Check if this is a first-time user"""
        return st.session_state.tutorial_progress.get('first_visit', True)
    
    def show_welcome_modal(self):
        """Show welcome modal for first-time users"""
        if self.check_first_time_user():
            with st.container():
                st.markdown("""
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.5);
                    z-index: 999;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                ">
                    <div style="
                        background: white;
                        padding: 30px;
                        border-radius: 15px;
                        max-width: 500px;
                        text-align: center;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                    ">
                        <h2>🎓 Welcome to Student Insights Pipeline!</h2>
                        <p>It looks like this is your first time here. Would you like a quick tour?</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🚀 Start Tutorial", use_container_width=True):
                        st.session_state.tutorial_progress['first_visit'] = False
                        st.session_state.show_tutorial = True
                        st.rerun()
                    
                    if st.button("Skip for now", use_container_width=True):
                        st.session_state.tutorial_progress['first_visit'] = False
                        st.rerun()
    
    def add_tutorial_sidebar(self):
        """Add tutorial options to sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎓 Learning Center")
        
        if st.sidebar.button("📚 Interactive Tutorial"):
            st.session_state.show_tutorial = True
            st.rerun()
        
        if st.sidebar.button("💡 Show Hints", help="Toggle helpful hints throughout the interface"):
            st.session_state.tutorial_progress['show_hints'] = not st.session_state.tutorial_progress.get('show_hints', True)
            st.rerun()
        
        if st.sidebar.button("🎯 Quick Tips"):
            st.session_state.show_quick_tips = True
            st.rerun()
        
        # Progress indicator
        completed = len(st.session_state.tutorial_progress.get('completed_modules', []))
        total = 5  # Total number of tutorial modules
        progress = completed / total
        
        st.sidebar.markdown("#### Tutorial Progress")
        st.sidebar.progress(progress)
        st.sidebar.caption(f"{completed}/{total} modules completed")
    
    def show_contextual_hints(self, page_type):
        """Show contextual hints based on current page"""
        if not st.session_state.tutorial_progress.get('show_hints', True):
            return
        
        hints = {
            "dashboard": {
                "title": "💡 Dashboard Tip",
                "content": "Use the metrics at the top to get a quick overview of your students' performance. Red numbers indicate areas needing attention!"
            },
            "teacher_portal": {
                "title": "👩‍🏫 Teacher Tip", 
                "content": "Click on any student's name to see detailed analytics and AI-generated intervention recommendations."
            },
            "parent_portal": {
                "title": "👨‍👩‍👧‍👦 Parent Tip",
                "content": "The 'How to Help at Home' section provides specific, actionable strategies tailored to your child's needs."
            },
            "analytics": {
                "title": "📊 Analytics Tip",
                "content": "The risk score combines multiple factors. Hover over charts to see detailed breakdowns of each metric."
            },
            "interventions": {
                "title": "🎯 Intervention Tip",
                "content": "AI recommendations are based on research-proven strategies. You can customize them to fit your specific situation."
            }
        }
        
        if page_type in hints:
            hint = hints[page_type]
            st.info(f"**{hint['title']}**: {hint['content']}")
    
    def show_feature_spotlight(self, feature_name, description, location):
        """Highlight specific features for new users"""
        if st.session_state.tutorial_progress.get('show_hints', True):
            with st.expander(f"✨ Feature Spotlight: {feature_name}", expanded=False):
                st.markdown(f"**{description}**")
                st.markdown(f"📍 *Location: {location}*")
    
    def show_quick_tips_modal(self):
        """Show quick tips modal"""
        if st.session_state.get('show_quick_tips', False):
            st.markdown("## 🎯 Quick Tips")
            
            tips = [
                "🔍 **Use Filters**: Narrow down data by grade level or subject for focused analysis",
                "📊 **Check Trends**: Look for the +/- indicators to see if students are improving or declining",
                "⚠️ **Priority Colors**: Red = Urgent, Yellow = Monitor, Green = On Track",
                "👥 **Parent Communication**: Use the built-in messaging to keep families informed",
                "📈 **Track Progress**: Regular check-ins help measure intervention effectiveness",
                "🎯 **AI Recommendations**: The system learns from successful interventions to improve suggestions"
            ]
            
            for tip in tips:
                st.markdown(f"• {tip}")
            
            if st.button("Got it! 👍"):
                st.session_state.show_quick_tips = False
                st.rerun()
    
    def add_help_tooltips(self):
        """Add help tooltips throughout the interface"""
        tooltip_style = """
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: white;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """
        st.markdown(tooltip_style, unsafe_allow_html=True)
    
    def create_guided_tour_overlay(self, step_number, total_steps, element_id, title, description):
        """Create guided tour overlay for specific elements"""
        if st.session_state.get('guided_tour_active', False):
            overlay_html = f"""
            <div id="tour-overlay-{step_number}" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.7);
                z-index: 1000;
                display: flex;
                justify-content: center;
                align-items: center;
            ">
                <div style="
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    max-width: 400px;
                    text-align: center;
                ">
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <div style="margin-top: 15px;">
                        <small>Step {step_number} of {total_steps}</small>
                    </div>
                </div>
            </div>
            """
            st.markdown(overlay_html, unsafe_allow_html=True)
    
    def show_onboarding_checklist(self):
        """Show onboarding checklist for new users"""
        if st.session_state.tutorial_progress.get('first_visit', True):
            st.sidebar.markdown("### 🎯 Getting Started Checklist")
            
            checklist_items = [
                ("Take the tutorial", "tutorial_completed"),
                ("Explore sample data", "sample_data_viewed"),
                ("Try teacher portal", "teacher_portal_visited"),
                ("Check parent view", "parent_portal_visited"),
                ("Review analytics", "analytics_viewed")
            ]
            
            for item, key in checklist_items:
                completed = st.session_state.tutorial_progress.get(key, False)
                icon = "✅" if completed else "⏳"
                st.sidebar.markdown(f"{icon} {item}")
    
    def track_user_interaction(self, action, details=None):
        """Track user interactions for tutorial improvement"""
        if 'user_interactions' not in st.session_state:
            st.session_state.user_interactions = []
        
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details or {}
        }
        
        st.session_state.user_interactions.append(interaction)
    
    def show_tutorial_launcher(self):
        """Show floating tutorial launcher button"""
        launcher_html = """
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 999;
        ">
            <button onclick="startTutorial()" style="
                background: #ff6b6b;
                color: white;
                border: none;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                🎓
            </button>
        </div>
        
        <script>
        function startTutorial() {
            // This would trigger the tutorial in Streamlit
            alert('Tutorial starting...');
        }
        </script>
        """
        st.markdown(launcher_html, unsafe_allow_html=True)
    
    def generate_personalized_tips(self, user_role, usage_pattern):
        """Generate personalized tips based on user behavior"""
        tips = {
            "teacher": [
                "💡 Set up weekly review sessions using the progress tracking features",
                "🎯 Use the bulk intervention tool to help multiple students at once",
                "📊 Export reports before parent-teacher conferences"
            ],
            "parent": [
                "🏠 Check the 'Home Support' section for daily activity suggestions",
                "📱 Set up notifications for important updates about your child",
                "👥 Connect with other parents through the community features"
            ],
            "admin": [
                "📈 Use the system-wide analytics to identify trends across classes",
                "👥 Monitor teacher engagement with intervention recommendations",
                "📊 Generate monthly reports for school board presentations"
            ]
        }
        
        return tips.get(user_role, ["💡 Explore all the features to get the most out of the system!"])
    
    def show_progress_celebration(self, milestone):
        """Show celebration when user reaches milestones"""
        celebrations = {
            "first_login": "🎉 Welcome! You've taken the first step toward data-driven student success!",
            "tutorial_complete": "🏆 Tutorial completed! You're now ready to help students succeed!",
            "first_intervention": "🎯 Great job creating your first intervention plan!",
            "week_active": "⭐ You've been actively using the system for a week - students benefit from your dedication!"
        }
        
        if milestone in celebrations:
            st.balloons()
            st.success(celebrations[milestone])


def integrate_tutorial_into_main_app():
    """Function to integrate tutorial system into main predictive intervention system"""
    tutorial = TutorialIntegration()
    
    # Show welcome modal for first-time users
    if tutorial.check_first_time_user():
        tutorial.show_welcome_modal()
    
    # Add tutorial sidebar
    tutorial.add_tutorial_sidebar()
    
    # Add help tooltips
    tutorial.add_help_tooltips()
    
    # Show onboarding checklist
    tutorial.show_onboarding_checklist()
    
    # Show quick tips if requested
    tutorial.show_quick_tips_modal()
    
    return tutorial


# Usage example for integration:
"""
# Add this to your main predictive_intervention_system.py file:

from tutorial_integration import integrate_tutorial_into_main_app

def main():
    # Initialize tutorial system
    tutorial = integrate_tutorial_into_main_app()
    
    # Your existing main app code here...
    
    # Add contextual hints based on current page
    current_page = st.session_state.get('current_page', 'dashboard')
    tutorial.show_contextual_hints(current_page)
    
    # Track user interactions
    tutorial.track_user_interaction('page_view', {'page': current_page})
"""
