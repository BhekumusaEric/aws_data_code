#!/usr/bin/env python3
"""
Student Insights Pipeline - Dashboard Launcher
Launch the Streamlit dashboard
"""

import subprocess
import sys
import os
import webbrowser
import time


def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Starting Student Insights Dashboard...")
    print("=" * 50)
    
    # Check if streamlit is available
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} is available")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'streamlit', 'plotly', '--user'])
        print("✅ Streamlit installed!")
    
    # Check if the app file exists
    if not os.path.exists('streamlit_app.py'):
        print("❌ streamlit_app.py not found!")
        return False
    
    print("✅ Dashboard app found")
    print()
    print("🌐 Starting web server...")
    print("📊 Dashboard will open in your browser automatically")
    print("🔗 URL: http://localhost:8501")
    print()
    print("💡 To stop the dashboard, press Ctrl+C in this terminal")
    print()
    
    # Launch Streamlit
    try:
        # Use subprocess to run streamlit
        cmd = [sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py', '--server.port=8501']
        
        # Start the process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Try to open browser
        try:
            webbrowser.open('http://localhost:8501')
            print("🌐 Browser opened automatically")
        except Exception:
            print("⚠️ Could not open browser automatically")
            print("📖 Please open http://localhost:8501 in your browser")
        
        print()
        print("🎉 Dashboard is running!")
        print("📊 You should see the Student Insights Pipeline dashboard")
        print()
        print("Features available:")
        print("  📈 Performance Analytics")
        print("  ⚠️ Risk Assessment")
        print("  📚 Subject Analysis")
        print("  📝 Data Entry")
        print("  🔍 Interactive Filters")
        print()
        
        # Wait for the process to complete or be interrupted
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ Stopping dashboard...")
            process.terminate()
            print("✅ Dashboard stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False


if __name__ == "__main__":
    try:
        success = launch_dashboard()
        if not success:
            print("❌ Failed to start dashboard")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard launcher cancelled")
        sys.exit(0)
