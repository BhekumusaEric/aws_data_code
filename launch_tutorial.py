#!/usr/bin/env python3
"""
Tutorial Launcher for Student Insights Pipeline
Easy access to all tutorial and learning resources
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🎓 STUDENT INSIGHTS PIPELINE - LEARNING CENTER")
    print("=" * 60)
    print()
    print("Welcome to the comprehensive tutorial system!")
    print("Choose how you'd like to learn about the platform:")
    print()


def show_menu():
    """Show main menu options"""
    options = [
        "🚀 Launch Main System (predictive_intervention_system.py)",
        "🌐 Open Tutorial Website (HTML)",
        "💡 Quick Start Guide",
        "📖 View Documentation",
        "🔧 Troubleshooting Help",
        "❌ Exit"
    ]
    
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print()


def launch_main_system():
    """Launch the main predictive intervention system"""
    print("🚀 Starting Student Insights Pipeline...")
    print("📚 Tutorial features are built-in and ready to use!")
    print()

    try:
        # Check if the main system file exists
        if not os.path.exists('predictive_intervention_system.py'):
            print("❌ Error: predictive_intervention_system.py not found!")
            print("Please make sure you're in the correct directory.")
            return False

        print("🎯 Features included in the main system:")
        print("  • 🎓 Interactive tutorials for first-time users")
        print("  • 💡 Contextual hints throughout the interface")
        print("  • 🎯 Role-specific guidance (Teacher/Parent/Admin)")
        print("  • 📈 Step-by-step learning modules")
        print("  • 📚 Built-in help system")
        print()
        print("🌐 Opening at: http://localhost:8501")
        print("⏹️  To stop: Press Ctrl+C")
        print()

        # Launch the main system
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            'predictive_intervention_system.py',
            '--server.port=8501'
        ])

    except Exception as e:
        print(f"❌ Error launching system: {e}")
        print("\n🔧 Try these alternatives:")
        print("1. python -m streamlit run predictive_intervention_system.py")
        print("2. py -m streamlit run predictive_intervention_system.py")
        print("3. Use run_tutorial_system.bat (Windows)")
        return False

    return True


def show_troubleshooting():
    """Show troubleshooting guide"""
    print("🔧 TROUBLESHOOTING GUIDE")
    print("=" * 40)
    print()
    print("❌ Common Issues and Solutions:")
    print()
    print("1. 'streamlit' is not recognized:")
    print("   Solution: Use 'python -m streamlit' or 'py -m streamlit'")
    print()
    print("2. Port 8501 is already in use:")
    print("   Solution: Use --server.port=8502 or kill existing process")
    print("   Command: python -m streamlit run predictive_intervention_system.py --server.port=8502")
    print()
    print("3. Module not found errors:")
    print("   Solution: Install requirements")
    print("   Command: pip install streamlit plotly pandas numpy boto3")
    print()
    print("4. Python not found:")
    print("   Solution: Install Python 3.9+ from python.org")
    print("   Or try 'py' instead of 'python'")
    print()
    print("5. Browser doesn't open automatically:")
    print("   Solution: Manually open http://localhost:8501")
    print()
    print("✅ Quick Commands to Try:")
    print("   • python -m streamlit run predictive_intervention_system.py")
    print("   • py -m streamlit run predictive_intervention_system.py")
    print("   • .\\run_tutorial_system.bat (Windows)")
    print()
    print("📧 Still having issues? Check README.md for more help.")
    print()


def open_tutorial_website():
    """Open the tutorial website"""
    print("🌐 Opening Tutorial Website...")
    
    try:
        # Check if HTML file exists
        html_file = Path('tutorial_website.html')
        if not html_file.exists():
            print("❌ Error: tutorial_website.html not found!")
            return False
        
        # Open in browser
        webbrowser.open(f'file://{html_file.absolute()}')
        print("✅ Tutorial website opened in your browser!")
        
    except Exception as e:
        print(f"❌ Error opening website: {e}")
        return False
    
    return True


def show_quick_start():
    """Show quick start guide"""
    print("💡 QUICK START GUIDE")
    print("=" * 40)
    print()
    print("🎯 For First-Time Users:")
    print("1. Choose option 1 to launch predictive_intervention_system.py")
    print("2. When it opens, you'll see a welcome banner - click '🚀 Start Tutorial'")
    print("3. Or use the '📚 Interactive Tutorial' button in the sidebar Learning Center")
    print("4. Start with the 'System Overview' tutorial")
    print("5. Then choose your role-specific tutorial (Teacher/Parent/Admin)")
    print()
    print("👩‍🏫 For Teachers:")
    print("• Focus on the Teacher Portal tutorial")
    print("• Learn about risk assessment and intervention planning")
    print("• Practice with the sample student data")
    print()
    print("👨‍👩‍👧‍👦 For Parents:")
    print("• Start with the Parent Portal tutorial")
    print("• Learn how to support your child at home")
    print("• Understand progress reports and communication tools")
    print()
    print("📊 For Administrators:")
    print("• Begin with System Overview and Analytics tutorials")
    print("• Focus on system-wide insights and reporting")
    print("• Learn about intervention effectiveness tracking")
    print()
    print("🔧 System Requirements:")
    print("• Python 3.9 or higher")
    print("• All dependencies installed (pip install -r requirements.txt)")
    print("• Web browser (Chrome, Firefox, Safari, Edge)")
    print()
    print("❓ Need Help?")
    print("• Check the troubleshooting section in README.md")
    print("• Use the tutorial website for comprehensive guides")
    print("• Look for the 💡 help buttons throughout the interface")
    print()


def show_documentation():
    """Show documentation options"""
    print("📖 DOCUMENTATION & RESOURCES")
    print("=" * 40)
    print()
    print("Available documentation:")
    print()
    
    docs = [
        ("README.md", "Main project documentation and setup guide"),
        ("RUN_INSTRUCTIONS.md", "Detailed deployment and usage instructions"),
        ("tutorial_website.html", "Comprehensive web-based tutorial"),
        ("tutorial_system.py", "Interactive tutorial system code"),
        ("tutorial_integration.py", "Tutorial integration for main app")
    ]
    
    for doc, description in docs:
        if os.path.exists(doc):
            print(f"✅ {doc} - {description}")
        else:
            print(f"❌ {doc} - {description} (not found)")
    
    print()
    print("📚 Tutorial Modules Available:")
    modules = [
        "🏠 System Overview - Dashboard navigation and basic features",
        "👩‍🏫 Teacher Portal - Classroom management and student analysis", 
        "👨‍👩‍👧‍👦 Parent Portal - Supporting your child's learning",
        "📊 Predictive Analytics - Understanding AI-powered insights",
        "🎯 Intervention Plans - Creating and managing action plans"
    ]
    
    for module in modules:
        print(f"  • {module}")
    
    print()


def main():
    """Main launcher function"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            print()
            
            if choice == '1':
                launch_main_system()
                break
            elif choice == '2':
                open_tutorial_website()
                input("\nPress Enter to continue...")
            elif choice == '3':
                show_quick_start()
                input("\nPress Enter to continue...")
            elif choice == '4':
                show_documentation()
                input("\nPress Enter to continue...")
            elif choice == '5':
                show_troubleshooting()
                input("\nPress Enter to continue...")
            elif choice == '6':
                print("👋 Thank you for using Student Insights Pipeline!")
                print("Happy learning and teaching! 🎓")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-6.")
                print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
