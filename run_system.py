#!/usr/bin/env python3
"""
Simple launcher for the Student Insights Pipeline with Tutorial Integration
This script handles the setup and launch automatically
"""

import subprocess
import sys
import os
import time
import webbrowser

def check_and_install_requirements():
    """Check and install required packages"""
    required_packages = [
        'streamlit',
        'plotly', 
        'pandas',
        'numpy',
        'boto3'
    ]
    
    print("🔍 Checking required packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            print("Please try running: pip install streamlit plotly pandas numpy boto3")
            return False
    
    return True

def launch_streamlit_app():
    """Launch the Streamlit application"""
    print("\n🚀 Starting Student Insights Pipeline with Tutorial Integration...")
    print("=" * 60)
    
    # Check if main file exists
    if not os.path.exists('predictive_intervention_system.py'):
        print("❌ Error: predictive_intervention_system.py not found!")
        print("Please make sure you're in the correct directory.")
        return False
    
    try:
        # Launch Streamlit
        print("🌐 Starting web server...")
        print("📊 Dashboard will open automatically in your browser")
        print("🎓 Tutorial features are integrated and ready!")
        print()
        print("💡 Features available:")
        print("  • 📚 Interactive tutorials for first-time users")
        print("  • 💡 Contextual hints throughout the interface")
        print("  • 🎯 Role-specific guidance (Teacher/Parent/Admin)")
        print("  • 📈 Step-by-step learning modules")
        print()
        print("🔗 URL: http://localhost:8501")
        print("⏹️  To stop: Press Ctrl+C in this terminal")
        print()
        
        # Wait a moment then open browser
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open('http://localhost:8501')
                print("🌐 Browser opened automatically!")
            except Exception:
                print("⚠️ Could not open browser automatically")
                print("📖 Please open http://localhost:8501 in your browser")
        
        # Start browser opener in background
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'predictive_intervention_system.py',
            '--server.port=8501',
            '--server.headless=false'
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping application...")
        print("✅ Application stopped successfully!")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Python is installed correctly")
        print("2. Try: pip install streamlit plotly pandas numpy boto3")
        print("3. Run: python -m streamlit run predictive_intervention_system.py")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🎓 STUDENT INSIGHTS PIPELINE - TUTORIAL INTEGRATED")
    print("=" * 60)
    print()
    print("Welcome! This launcher will:")
    print("1. ✅ Check and install required packages")
    print("2. 🚀 Launch the main system with tutorial integration")
    print("3. 🌐 Open your browser automatically")
    print()
    
    # Check and install requirements
    if not check_and_install_requirements():
        print("\n❌ Setup failed. Please install requirements manually.")
        input("Press Enter to exit...")
        return
    
    print("\n✅ All requirements satisfied!")
    
    # Launch the application
    if not launch_streamlit_app():
        print("\n❌ Failed to launch application.")
        input("Press Enter to exit...")
        return
    
    print("\n👋 Thank you for using Student Insights Pipeline!")

if __name__ == "__main__":
    main()
