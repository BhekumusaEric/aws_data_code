#!/usr/bin/env python3
"""
Student Insights Pipeline - Interactive Tutorial System
Educational platform to guide first-time users through the system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

class TutorialSystem:
    """Interactive tutorial system for the Student Insights Pipeline"""
    
    def __init__(self):
        self.tutorial_data = self.load_tutorial_data()
        self.sample_student_data = self.generate_sample_data()
    
    def load_tutorial_data(self):
        """Load tutorial content and structure"""
        return {
            "welcome": {
                "title": "Welcome to Student Insights Pipeline! 🎓",
                "description": "Learn how to use our AI-powered system to help students succeed",
                "steps": 6,
                "estimated_time": "15 minutes"
            },
            "modules": [
                {
                    "id": "overview",
                    "title": "🏠 System Overview",
                    "description": "Understanding the dashboard and main features",
                    "duration": "3 min",
                    "interactive": True
                },
                {
                    "id": "teacher_portal",
                    "title": "👩‍🏫 Teacher Portal",
                    "description": "Managing your classroom and individual students",
                    "duration": "4 min",
                    "interactive": True
                },
                {
                    "id": "parent_portal",
                    "title": "👨‍👩‍👧‍👦 Parent Portal",
                    "description": "Supporting your child's learning at home",
                    "duration": "3 min",
                    "interactive": True
                },
                {
                    "id": "analytics",
                    "title": "📊 Predictive Analytics",
                    "description": "Understanding risk assessment and predictions",
                    "duration": "3 min",
                    "interactive": True
                },
                {
                    "id": "interventions",
                    "title": "🎯 Intervention Plans",
                    "description": "Creating and managing action plans",
                    "duration": "2 min",
                    "interactive": True
                }
            ]
        }
    
    def generate_sample_data(self):
        """Generate sample data for tutorial demonstrations"""
        students = [
            {"name": "Emma Johnson", "grade": "9", "risk": "Low", "score": 87, "trend": "+5"},
            {"name": "Marcus Chen", "grade": "9", "risk": "High", "score": 62, "trend": "-8"},
            {"name": "Sofia Rodriguez", "grade": "9", "risk": "Medium", "score": 74, "trend": "+2"},
            {"name": "Alex Thompson", "grade": "9", "risk": "Low", "score": 91, "trend": "+3"},
        ]
        return pd.DataFrame(students)
    
    def render_tutorial_home(self):
        """Render the main tutorial homepage"""
        st.markdown("# 🎓 Student Insights Pipeline Tutorial")
        st.markdown("### Learn how to transform student outcomes with data-driven insights!")
        
        # Welcome section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            Welcome to your comprehensive guide for using the Student Insights Pipeline! 
            This interactive tutorial will teach you everything you need to know to:
            
            ✅ **Navigate the dashboard** like a pro  
            ✅ **Identify at-risk students** before they fall behind  
            ✅ **Create personalized intervention plans** that work  
            ✅ **Engage parents** with actionable insights  
            ✅ **Track progress** and measure success  
            """)
            
            # Progress tracking
            if 'tutorial_progress' not in st.session_state:
                st.session_state.tutorial_progress = {}
            
            completed_modules = len([k for k, v in st.session_state.tutorial_progress.items() if v])
            total_modules = len(self.tutorial_data["modules"])
            progress = completed_modules / total_modules if total_modules > 0 else 0
            
            st.progress(progress)
            st.caption(f"Progress: {completed_modules}/{total_modules} modules completed")
        
        with col2:
            st.info(f"""
            **⏱️ Total Time:** {self.tutorial_data['welcome']['estimated_time']}  
            **📚 Modules:** {len(self.tutorial_data['modules'])}  
            **🎯 Interactive:** Yes  
            **💡 Skill Level:** Beginner-friendly
            """)
        
        st.markdown("---")
        
        # Tutorial modules grid
        st.markdown("## 📚 Tutorial Modules")
        
        cols = st.columns(2)
        for i, module in enumerate(self.tutorial_data["modules"]):
            with cols[i % 2]:
                # Check if module is completed
                is_completed = st.session_state.tutorial_progress.get(module["id"], False)
                status_icon = "✅" if is_completed else "⏳"
                
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0;">
                        <h4>{status_icon} {module['title']}</h4>
                        <p>{module['description']}</p>
                        <small>⏱️ {module['duration']} | 🎮 Interactive</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Start Module", key=f"start_{module['id']}"):
                        st.session_state.current_tutorial = module['id']
                        st.rerun()
        
        # Quick start section
        st.markdown("---")
        st.markdown("## 🚀 Quick Start Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 I'm a Teacher", use_container_width=True):
                st.session_state.current_tutorial = "teacher_portal"
                st.rerun()
        
        with col2:
            if st.button("👨‍👩‍👧‍👦 I'm a Parent", use_container_width=True):
                st.session_state.current_tutorial = "parent_portal"
                st.rerun()
        
        with col3:
            if st.button("📊 Show Me Analytics", use_container_width=True):
                st.session_state.current_tutorial = "analytics"
                st.rerun()
    
    def render_overview_tutorial(self):
        """Tutorial for system overview"""
        st.markdown("# 🏠 System Overview Tutorial")
        
        # Step-by-step walkthrough
        step = st.session_state.get('tutorial_step', 1)
        
        if step == 1:
            st.markdown("## Step 1: Understanding the Dashboard")
            st.info("👋 Welcome! Let's start with the main dashboard layout.")
            
            # Mock dashboard preview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Students", "156", "+12")
            with col2:
                st.metric("At Risk", "23", "-5")
            with col3:
                st.metric("Interventions Active", "18", "+3")
            
            st.markdown("""
            **What you're seeing:**
            - **Total Students**: All students in your system
            - **At Risk**: Students needing immediate attention
            - **Interventions Active**: Current support programs running
            """)
            
            if st.button("Next: Navigation Menu →"):
                st.session_state.tutorial_step = 2
                st.rerun()
        
        elif step == 2:
            st.markdown("## Step 2: Navigation Menu")
            st.info("🧭 The sidebar contains all the main features you'll use.")
            
            # Mock sidebar
            with st.sidebar:
                st.markdown("### 📊 Dashboard Controls")
                st.selectbox("Choose View", ["🏠 Dashboard Overview", "👩‍🏫 Teacher Portal", "👨‍👩‍👧‍👦 Parent Portal"])
                st.markdown("### 🔍 Filters")
                st.multiselect("Grade Levels", ["9", "10", "11", "12"])
                st.multiselect("Subjects", ["Math", "Science", "English"])
            
            st.markdown("""
            **Navigation Tips:**
            - Use the **dropdown menu** to switch between different views
            - **Filters** help you focus on specific students or subjects
            - Each view is designed for different user roles
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous"):
                    st.session_state.tutorial_step = 1
                    st.rerun()
            with col2:
                if st.button("Next: Sample Data →"):
                    st.session_state.tutorial_step = 3
                    st.rerun()
        
        elif step == 3:
            st.markdown("## Step 3: Understanding Student Data")
            st.info("📊 Let's look at how student information is displayed.")
            
            # Show sample data
            st.dataframe(self.sample_student_data, use_container_width=True)
            
            st.markdown("""
            **Key Information:**
            - **Risk Level**: AI-calculated assessment (Low/Medium/High)
            - **Score**: Current academic performance
            - **Trend**: Recent performance change (+/- points)
            
            **Color Coding:**
            - 🟢 **Green**: Students performing well
            - 🟡 **Yellow**: Students needing monitoring
            - 🔴 **Red**: Students requiring immediate intervention
            """)
            
            # Interactive element
            selected_student = st.selectbox("Try selecting a student:", self.sample_student_data['name'].tolist())
            if selected_student:
                student_data = self.sample_student_data[self.sample_student_data['name'] == selected_student].iloc[0]
                st.success(f"Great! You selected {selected_student} - Risk Level: {student_data['risk']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous"):
                    st.session_state.tutorial_step = 2
                    st.rerun()
            with col2:
                if st.button("Complete Overview Tutorial ✅"):
                    st.session_state.tutorial_progress["overview"] = True
                    st.session_state.tutorial_step = 1
                    st.success("🎉 Overview tutorial completed!")
                    if st.button("Return to Tutorial Home"):
                        st.session_state.current_tutorial = None
                        st.rerun()
    
    def render_teacher_tutorial(self):
        """Tutorial for teacher portal"""
        st.markdown("# 👩‍🏫 Teacher Portal Tutorial")
        
        step = st.session_state.get('teacher_tutorial_step', 1)
        
        if step == 1:
            st.markdown("## Welcome, Teacher! 👋")
            st.info("Let's explore how to manage your classroom effectively.")
            
            st.markdown("""
            As a teacher, you can:
            - 📊 **Monitor** all students in your class
            - 🎯 **Identify** students who need extra support
            - 📋 **Create** personalized intervention plans
            - 👨‍👩‍👧‍👦 **Communicate** with parents
            - 📈 **Track** progress over time
            """)
            
            if st.button("Let's Start! →"):
                st.session_state.teacher_tutorial_step = 2
                st.rerun()
        
        elif step == 2:
            st.markdown("## Step 1: Class Overview")
            st.info("👀 Get a quick snapshot of your entire class.")
            
            # Mock class overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Class Size", "28")
            with col2:
                st.metric("Average Score", "78.5", "+2.1")
            with col3:
                st.metric("At Risk", "6", "-1")
            with col4:
                st.metric("Improving", "15", "+3")
            
            # Risk distribution chart
            risk_data = pd.DataFrame({
                'Risk Level': ['Low Risk', 'Medium Risk', 'High Risk'],
                'Count': [16, 6, 6]
            })
            fig = px.pie(risk_data, values='Count', names='Risk Level', 
                        title="Class Risk Distribution",
                        color_discrete_map={'Low Risk': 'green', 'Medium Risk': 'orange', 'High Risk': 'red'})
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("Next: Individual Students →"):
                st.session_state.teacher_tutorial_step = 3
                st.rerun()
        
        # Continue with more steps...
        elif step == 3:
            st.markdown("## Step 2: Individual Student Analysis")
            st.info("🔍 Dive deep into individual student performance.")
            
            # Student selection
            selected_student = st.selectbox("Select a student to analyze:", 
                                          ["Marcus Chen (High Risk)", "Sofia Rodriguez (Medium Risk)", "Emma Johnson (Low Risk)"])
            
            if "Marcus Chen" in selected_student:
                st.warning("⚠️ Marcus Chen - High Risk Student")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Score", "62%", "-8 pts")
                    st.metric("Attendance", "78%", "-12%")
                with col2:
                    st.metric("Assignment Completion", "65%", "-15%")
                    st.metric("Risk Score", "85/100", "+10")
                
                st.markdown("### 🎯 AI Recommendations:")
                st.markdown("""
                1. **Immediate**: Schedule one-on-one meeting
                2. **This Week**: Contact parents about attendance
                3. **Ongoing**: Pair with study buddy for math support
                4. **Monitor**: Check in daily for next 2 weeks
                """)
                
                if st.button("Create Intervention Plan"):
                    st.success("✅ Intervention plan created for Marcus!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous"):
                    st.session_state.teacher_tutorial_step = 2
                    st.rerun()
            with col2:
                if st.button("Complete Teacher Tutorial ✅"):
                    st.session_state.tutorial_progress["teacher_portal"] = True
                    st.success("🎉 Teacher tutorial completed!")
                    if st.button("Return to Tutorial Home"):
                        st.session_state.current_tutorial = None
                        st.rerun()
    
    def render_parent_tutorial(self):
        """Tutorial for parent portal"""
        st.markdown("# 👨‍👩‍👧‍👦 Parent Portal Tutorial")
        
        st.info("👋 Welcome, Parents! Learn how to support your child's learning journey.")
        
        # Parent name input
        parent_name = st.text_input("Enter your name:", placeholder="e.g., Sarah Johnson")
        child_name = st.selectbox("Select your child:", ["Emma Johnson", "Marcus Chen", "Sofia Rodriguez"])
        
        if parent_name and child_name:
            st.markdown(f"## Welcome, {parent_name}! 👋")
            st.markdown(f"### Here's how **{child_name}** is doing:")
            
            # Mock child data based on selection
            if child_name == "Marcus Chen":
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Grade", "🟡 62%")
                with col2:
                    st.metric("Attendance", "🔴 78%")
                with col3:
                    st.metric("Trend", "📉 -8 pts")
                
                st.warning("⚠️ Your child needs some extra support right now.")
                
                st.markdown("### 🏠 How You Can Help at Home:")
                st.markdown("""
                1. **📚 Study Schedule**: Set up a consistent homework time (7-8 PM works well)
                2. **📱 Limit Distractions**: Create a phone-free study zone
                3. **👥 Study Group**: Connect with Emma's parents for peer support
                4. **📞 Teacher Check-in**: Schedule a meeting with Ms. Rodriguez this week
                """)
                
                st.markdown("### 📈 This Week's Goals:")
                st.markdown("""
                - ✅ Complete all math assignments
                - ✅ Attend all classes (no absences)
                - ✅ Spend 30 minutes on reading daily
                """)
            
            elif child_name == "Emma Johnson":
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Grade", "🟢 87%")
                with col2:
                    st.metric("Attendance", "🟢 96%")
                with col3:
                    st.metric("Trend", "📈 +5 pts")
                
                st.success("🎉 Your child is doing great! Keep up the excellent work.")
                
                st.markdown("### 🌟 Ways to Keep the Momentum:")
                st.markdown("""
                1. **🎯 Challenge Goals**: Consider advanced reading or math challenges
                2. **👥 Peer Mentoring**: Emma could help other students (builds leadership)
                3. **🏆 Celebrate Success**: Acknowledge her hard work and improvement
                4. **📚 Enrichment**: Explore extracurricular activities in her strong subjects
                """)
            
            # Communication section
            st.markdown("### 📞 Communication with Teachers")
            message = st.text_area("Send a message to your child's teacher:", 
                                  placeholder="Hi Ms. Rodriguez, I wanted to check in about...")
            if st.button("Send Message"):
                st.success("✅ Message sent to teacher!")
            
            if st.button("Complete Parent Tutorial ✅"):
                st.session_state.tutorial_progress["parent_portal"] = True
                st.success("🎉 Parent tutorial completed!")
    
    def render_analytics_tutorial(self):
        """Tutorial for predictive analytics"""
        st.markdown("# 📊 Predictive Analytics Tutorial")
        
        st.info("🔮 Learn how AI helps predict and prevent student struggles.")
        
        st.markdown("## Understanding Risk Assessment")
        
        # Risk score explanation
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Risk Score Components")
            components = pd.DataFrame({
                'Factor': ['Academic Performance', 'Attendance Rate', 'Assignment Completion', 'Engagement Level', 'Historical Trends'],
                'Weight': [30, 25, 20, 15, 10],
                'Marcus Score': [45, 35, 40, 50, 30],
                'Emma Score': [90, 95, 88, 85, 92]
            })
            st.dataframe(components)
        
        with col2:
            st.markdown("### 📈 Risk Prediction Model")
            # Mock prediction chart
            dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
            marcus_risk = [30, 35, 45, 50, 60, 70, 75, 80, 85, 82, 78, 75]
            emma_risk = [15, 12, 10, 8, 12, 15, 18, 16, 14, 12, 10, 8]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=marcus_risk, name='Marcus (High Risk)', line=dict(color='red')))
            fig.add_trace(go.Scatter(x=dates, y=emma_risk, name='Emma (Low Risk)', line=dict(color='green')))
            fig.update_layout(title='Risk Score Trends', yaxis_title='Risk Score (0-100)')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("## 🚨 Early Warning System")
        st.markdown("""
        The system automatically flags students when:
        - **Risk score increases** by 15+ points in a month
        - **Attendance drops** below 80%
        - **Grade trends** show consistent decline
        - **Multiple factors** combine to indicate risk
        """)
        
        # Interactive prediction
        st.markdown("### 🎮 Try the Predictor")
        attendance = st.slider("Attendance Rate (%)", 0, 100, 85)
        current_grade = st.slider("Current Grade (%)", 0, 100, 75)
        assignment_completion = st.slider("Assignment Completion (%)", 0, 100, 80)
        
        # Simple risk calculation
        risk_score = max(0, 100 - (attendance * 0.3 + current_grade * 0.4 + assignment_completion * 0.3))
        
        if risk_score < 30:
            st.success(f"✅ Low Risk ({risk_score:.0f}/100) - Student is performing well")
        elif risk_score < 60:
            st.warning(f"⚠️ Medium Risk ({risk_score:.0f}/100) - Monitor closely")
        else:
            st.error(f"🚨 High Risk ({risk_score:.0f}/100) - Immediate intervention needed")
        
        if st.button("Complete Analytics Tutorial ✅"):
            st.session_state.tutorial_progress["analytics"] = True
            st.success("🎉 Analytics tutorial completed!")
    
    def render_interventions_tutorial(self):
        """Tutorial for intervention plans"""
        st.markdown("# 🎯 Intervention Plans Tutorial")
        
        st.info("📋 Learn how to create and manage effective action plans.")
        
        st.markdown("## Creating an Intervention Plan")
        
        # Step-by-step intervention creation
        student_name = st.selectbox("Select student for intervention:", ["Marcus Chen", "Sofia Rodriguez"])
        
        if student_name:
            st.markdown(f"### Creating plan for {student_name}")
            
            # AI-generated suggestions
            st.markdown("#### 🤖 AI-Generated Recommendations:")
            if student_name == "Marcus Chen":
                recommendations = [
                    "Schedule daily check-ins for attendance monitoring",
                    "Implement peer tutoring for math support",
                    "Contact parents about home study environment",
                    "Provide additional practice materials for weak areas",
                    "Set up weekly progress review meetings"
                ]
            else:
                recommendations = [
                    "Provide additional challenging materials",
                    "Encourage participation in study groups as a mentor",
                    "Monitor for signs of boredom or disengagement",
                    "Consider advanced placement opportunities"
                ]
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
            
            # Customization
            st.markdown("#### ✏️ Customize Your Plan:")
            priority = st.selectbox("Priority Level:", ["High", "Medium", "Low"])
            timeline = st.selectbox("Timeline:", ["This Week", "This Month", "This Quarter"])
            responsible = st.multiselect("Responsible Parties:", ["Teacher", "Parent", "Student", "Counselor"])
            
            custom_action = st.text_area("Add custom action:", placeholder="Enter specific action for this student...")
            
            if st.button("Create Intervention Plan"):
                st.success("✅ Intervention plan created successfully!")
                
                # Show created plan
                st.markdown("#### 📋 Your Intervention Plan:")
                st.info(f"""
                **Student:** {student_name}  
                **Priority:** {priority}  
                **Timeline:** {timeline}  
                **Responsible:** {', '.join(responsible)}  
                
                **Actions:**
                {chr(10).join([f"• {rec}" for rec in recommendations[:3]])}
                {f"• {custom_action}" if custom_action else ""}
                """)
        
        if st.button("Complete Interventions Tutorial ✅"):
            st.session_state.tutorial_progress["interventions"] = True
            st.success("🎉 Interventions tutorial completed!")


def main():
    """Main tutorial application"""
    st.set_page_config(
        page_title="Student Insights Tutorial",
        page_icon="🎓",
        layout="wide"
    )
    
    tutorial = TutorialSystem()
    
    # Check which tutorial to show
    current_tutorial = st.session_state.get('current_tutorial', None)
    
    if current_tutorial is None:
        tutorial.render_tutorial_home()
    elif current_tutorial == "overview":
        tutorial.render_overview_tutorial()
    elif current_tutorial == "teacher_portal":
        tutorial.render_teacher_tutorial()
    elif current_tutorial == "parent_portal":
        tutorial.render_parent_tutorial()
    elif current_tutorial == "analytics":
        tutorial.render_analytics_tutorial()
    elif current_tutorial == "interventions":
        tutorial.render_interventions_tutorial()
    
    # Back to home button
    if current_tutorial is not None:
        st.sidebar.markdown("---")
        if st.sidebar.button("🏠 Back to Tutorial Home"):
            st.session_state.current_tutorial = None
            st.rerun()


def add_tutorial_to_main_app():
    """Function to add tutorial functionality to the main predictive intervention system"""

    # Add tutorial option to sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎓 Learning Center")

    if st.sidebar.button("📚 Interactive Tutorial", help="Learn how to use the system"):
        st.session_state.show_tutorial_system = True
        st.rerun()

    if st.sidebar.button("💡 Quick Tips", help="Get helpful tips for current page"):
        st.session_state.show_quick_tips = True
        st.rerun()

    if st.sidebar.button("🌐 Tutorial Website", help="Open comprehensive tutorial website"):
        st.sidebar.markdown("[🌐 Open Tutorial Website](tutorial_website.html)")

    # Show tutorial system if requested
    if st.session_state.get('show_tutorial_system', False):
        tutorial = TutorialSystem()

        # Create tabs for different tutorial sections
        tab1, tab2, tab3 = st.tabs(["🏠 Tutorial Home", "🎯 Interactive Lessons", "📚 Help & Tips"])

        with tab1:
            tutorial.render_tutorial_home()

        with tab2:
            current_tutorial = st.session_state.get('current_tutorial', None)
            if current_tutorial == "overview":
                tutorial.render_overview_tutorial()
            elif current_tutorial == "teacher_portal":
                tutorial.render_teacher_tutorial()
            elif current_tutorial == "parent_portal":
                tutorial.render_parent_tutorial()
            elif current_tutorial == "analytics":
                tutorial.render_analytics_tutorial()
            elif current_tutorial == "interventions":
                tutorial.render_interventions_tutorial()
            else:
                st.info("👆 Select a tutorial from the Tutorial Home tab to get started!")

        with tab3:
            st.markdown("## 💡 Quick Help & Tips")

            with st.expander("🚀 Getting Started", expanded=True):
                st.markdown("""
                **New to the system?** Here's what to do first:
                1. 📊 Explore the sample data to understand the interface
                2. 🎯 Choose your role (Teacher/Parent/Admin) from the sidebar
                3. 📚 Take the role-specific tutorial
                4. 💡 Enable hints to get contextual help as you navigate
                """)

            with st.expander("🔍 Navigation Tips"):
                st.markdown("""
                - **Sidebar Menu**: Switch between different views and features
                - **Filters**: Use grade level and subject filters to focus your analysis
                - **Color Coding**: 🟢 Green = Good, 🟡 Yellow = Monitor, 🔴 Red = Action Needed
                - **Interactive Charts**: Hover over charts for detailed information
                """)

            with st.expander("👩‍🏫 For Teachers"):
                st.markdown("""
                - **Class Overview**: Start here to see all your students at once
                - **Individual Analysis**: Click on student names for detailed insights
                - **Intervention Plans**: Use AI recommendations as starting points
                - **Parent Communication**: Built-in tools help you share insights with families
                """)

            with st.expander("👨‍👩‍👧‍👦 For Parents"):
                st.markdown("""
                - **Progress Reports**: Check your child's performance trends
                - **Home Support**: Get specific strategies tailored to your child's needs
                - **Goal Setting**: Work with teachers to set and track academic goals
                - **Communication**: Stay connected with your child's teachers
                """)

        # Close tutorial button
        if st.button("✖️ Close Tutorial", type="secondary"):
            st.session_state.show_tutorial_system = False
            st.rerun()


if __name__ == "__main__":
    main()
