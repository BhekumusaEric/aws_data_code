#!/usr/bin/env python3
"""
Student Insights Pipeline - Quick Launcher
Organized system with proper separation of concerns
"""

import subprocess
import sys
import os
import webbrowser
import time

def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🎓 STUDENT INSIGHTS PIPELINE - ORGANIZED SYSTEM")
    print("=" * 70)
    print()
    print("✨ New Organized Structure with Separation of Concerns!")
    print("📁 Clean folder organization for better maintainability")
    print("🎯 Main entry point: main.py")
    print()

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'plotly', 'pandas', 'numpy', 'boto3']
    missing = []
    
    print("🔍 Checking requirements...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - Missing")
    
    if missing:
        print(f"\n📦 Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("✅ All packages installed!")
        except subprocess.CalledProcessError:
            print("❌ Installation failed. Please install manually:")
            print(f"pip install {' '.join(missing)}")
            return False
    
    return True

def launch_system():
    """Launch the main system"""
    print("\n🚀 Starting Student Insights Pipeline...")
    print("📊 Features included:")
    print("  • 🎯 Predictive intervention system")
    print("  • 📚 Built-in interactive tutorials")
    print("  • 💡 Contextual help and hints")
    print("  • 🎨 Clean, organized UI components")
    print("  • 🧠 Separated business logic")
    print()
    
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found!")
        print("Please make sure you're in the project root directory.")
        return False
    
    print("🌐 Opening browser in 3 seconds...")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  To stop: Press Ctrl+C")
    print()
    
    # Open browser after delay
    def open_browser():
        time.sleep(3)
        try:
            webbrowser.open('http://localhost:8501')
        except:
            pass
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'main.py',
            '--server.port=8501'
        ])
    except KeyboardInterrupt:
        print("\n⏹️ System stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def show_structure():
    """Show the new project structure"""
    print("📁 NEW ORGANIZED PROJECT STRUCTURE:")
    print("=" * 50)
    print("""
📂 student_insights_pipeline/
├── 🎯 main.py                    # Main entry point
├── 📱 app/                       # Application code
│   ├── 🧠 core/                  # Business logic
│   ├── 🎨 ui/                    # User interface
│   ├── 🎓 tutorials/             # Tutorial system
│   └── 🔧 utils/                 # Utilities
├── 🚀 launchers/                 # Launch scripts
├── 📖 docs/                      # Documentation
├── 📊 data/                      # Data files
└── ☁️ infrastructure/            # AWS resources
    """)
    print("✨ Benefits of this structure:")
    print("  • 🎯 Clear separation of concerns")
    print("  • 📁 Easy to navigate and maintain")
    print("  • 🔧 Modular and extensible")
    print("  • 🧪 Better for testing")
    print("  • 👥 Team-friendly development")
    print()

def main():
    """Main function"""
    print_banner()
    
    while True:
        print("Choose an option:")
        print("1. 🚀 Launch the system")
        print("2. 📁 Show project structure")
        print("3. 🌐 Open tutorial website")
        print("4. ❌ Exit")
        print()
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            if check_requirements():
                launch_system()
            break
        elif choice == '2':
            show_structure()
            input("\nPress Enter to continue...")
        elif choice == '3':
            tutorial_path = os.path.join('docs', 'tutorials', 'tutorial_website.html')
            if os.path.exists(tutorial_path):
                webbrowser.open(f'file://{os.path.abspath(tutorial_path)}')
                print("🌐 Tutorial website opened!")
            else:
                print("❌ Tutorial website not found")
            input("\nPress Enter to continue...")
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
