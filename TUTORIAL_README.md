# Tutorial System Files

This document explains the tutorial-related files in the Student Insights Pipeline project.

## 🎯 Main System (Primary Entry Point)

### `predictive_intervention_system.py`
**This is your main application file** - it contains:
- Complete Student Insights Pipeline functionality
- **Built-in tutorial system** integrated seamlessly
- First-time user welcome experience
- Contextual hints and help throughout the interface
- Role-specific guidance for Teachers, Parents, and Administrators

**To run:** `python -m streamlit run predictive_intervention_system.py`

## 🚀 Launcher Files

### `run_tutorial_system.bat` (Windows)
- **Double-click to run** on Windows systems
- Automatically installs dependencies
- Launches the main system with helpful output
- **Recommended for Windows users**

### `run_system.py`
- Cross-platform Python launcher
- Checks and installs requirements automatically
- Opens browser automatically
- Provides detailed status information

### `launch_tutorial.py`
- Menu-driven launcher with multiple options
- Includes troubleshooting guide
- Access to tutorial website and documentation
- **Good for exploring all available resources**

## 📚 Tutorial Components

### `tutorial_system.py`
- Contains the tutorial classes and interactive lessons
- **Integrated into the main system** - no need to run separately
- Provides step-by-step learning modules
- Sample data and practice exercises

### `tutorial_integration.py`
- Helper functions for integrating tutorials into main app
- First-time user detection
- Contextual hint system
- Progress tracking functionality

### `tutorial_website.html`
- **Standalone tutorial website** you can open in any browser
- Comprehensive guides and documentation
- Visual learning materials
- **Open directly in browser** - no server needed

## 🎓 How the Tutorial System Works

### Built-in Integration
The tutorial system is **seamlessly integrated** into `predictive_intervention_system.py`:

1. **First Visit Detection**: Automatically detects new users
2. **Welcome Experience**: Shows guided tour options
3. **Sidebar Learning Center**: Always available tutorial access
4. **Contextual Hints**: Smart help based on current page
5. **Progress Tracking**: Remembers completed tutorials

### Tutorial Modules Available
1. **🏠 System Overview** - Dashboard navigation and basic features
2. **👩‍🏫 Teacher Portal** - Classroom management and student analysis
3. **👨‍👩‍👧‍👦 Parent Portal** - Supporting your child's learning
4. **📊 Predictive Analytics** - Understanding AI-powered insights
5. **🎯 Intervention Plans** - Creating and managing action plans

## 🚀 Quick Start

### Option 1: Windows (Easiest)
```cmd
# Double-click this file:
run_tutorial_system.bat
```

### Option 2: Command Line
```bash
# Run the main system directly:
python -m streamlit run predictive_intervention_system.py
```

### Option 3: Menu Launcher
```bash
# Use the interactive menu:
python launch_tutorial.py
```

## 💡 Key Points

- **Main System is Complete**: `predictive_intervention_system.py` has everything built-in
- **No Separate Tutorial App**: Tutorials are integrated, not standalone
- **Multiple Launch Options**: Choose what works best for your setup
- **Tutorial Website**: `tutorial_website.html` works independently
- **Windows Friendly**: `.bat` file for easy double-click launching

## 🔧 Troubleshooting

### "streamlit not recognized"
Use: `python -m streamlit` instead of just `streamlit`

### "Port already in use"
Use: `python -m streamlit run predictive_intervention_system.py --server.port=8502`

### Missing packages
Run: `pip install streamlit plotly pandas numpy boto3`

### Need help?
1. Run `python launch_tutorial.py` and choose option 5 (Troubleshooting)
2. Check the main README.md file
3. Open tutorial_website.html for comprehensive guides

---

**Remember: `predictive_intervention_system.py` is your main application with all tutorial features built-in!** 🎯📊
