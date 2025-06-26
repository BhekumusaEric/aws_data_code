# 🎓 Student Insights Pipeline

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![AWS](https://img.shields.io/badge/AWS-Free%20Tier-orange.svg)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **AI-powered predictive intervention system that helps educators personalize student support through data-driven insights and actionable recommendations.**

## ✨ **What's New - Major Refactor!**

🎯 **Completely reorganized with proper separation of concerns**  
📱 **Clean, modular architecture for better maintainability**  
🎓 **Integrated tutorial system for first-time users**  
🚀 **Multiple launch options for easy startup**

---

## 🚀 **Quick Start**

### **Option 1: Direct Launch**
```bash
# Install dependencies
pip install streamlit plotly pandas numpy boto3

# Launch the system
python -m streamlit run main.py
```

### **Option 2: Interactive Launcher**
```bash
python run.py
```

### **Option 3: Windows Users**
```cmd
# Double-click this file:
launchers\run_tutorial_system.bat
```

**🌐 Open your browser to `http://localhost:8501` and start exploring!**

---

## 📁 **Project Architecture**

```
📂 student_insights_pipeline/
├── 🎯 main.py                    # Main entry point
├── 📱 app/                       # Application code
│   ├── 🧠 core/                  # Business logic & AI
│   ├── 🎨 ui/                    # User interface components
│   ├── 🎓 tutorials/             # Tutorial & help system
│   └── 🔧 utils/                 # Shared utilities
├── 🚀 launchers/                 # Cross-platform launchers
├── 📖 docs/                      # Documentation & guides
├── 📊 data/                      # Sample data & datasets
└── ☁️ infrastructure/            # AWS deployment resources
```

### **🧠 Separation of Concerns**
- **Core Logic** (`app/core/`): Pure business logic, AI models, data processing
- **User Interface** (`app/ui/`): Streamlit components, visualizations, interactions
- **Tutorial System** (`app/tutorials/`): Integrated learning and help system
- **Utilities** (`app/utils/`): Shared functions and helpers

---

## 🎯 **Key Features**

### **🤖 AI-Powered Analytics**
- **Risk Assessment**: Machine learning algorithms identify at-risk students
- **Predictive Modeling**: Forecast future performance trends
- **Early Warning System**: Proactive alerts before problems escalate
- **Intervention Recommendations**: Evidence-based action plans

### **🎓 Comprehensive Tutorial System**
- **First-time User Onboarding**: Guided tours and welcome experience
- **Interactive Learning Modules**: Step-by-step tutorials for each feature
- **Contextual Help**: Smart hints based on current page
- **Role-specific Guidance**: Tailored for Teachers, Parents, and Administrators

### **📊 Multi-Role Dashboard**
- **Teacher Portal**: Classroom management and student analysis
- **Parent Portal**: Child-specific insights and home support strategies
- **Admin Dashboard**: System-wide analytics and resource planning
- **Individual Analysis**: Deep-dive into student performance patterns

### **🎨 Professional UI/UX**
- **Interactive Charts**: Plotly-powered visualizations
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Intuitive Navigation**: Easy-to-use interface for all skill levels
- **Real-time Updates**: Live data refresh and dynamic filtering

---

## 🎓 **For Educators**

### **Teachers**
- 📊 **Class Overview**: Monitor all students' performance and risk levels
- 🎯 **Individual Analysis**: Detailed insights for each student
- 📋 **Intervention Planning**: AI-generated action plans and strategies
- 📞 **Parent Communication**: Built-in tools for family engagement

### **Parents**
- 📈 **Progress Tracking**: Real-time updates on your child's performance
- 🏠 **Home Support**: Personalized strategies for supporting learning at home
- 🎯 **Goal Setting**: Collaborative goal-setting with teachers
- 💬 **Communication**: Direct messaging with educators

### **Administrators**
- 📊 **System Analytics**: School-wide performance metrics and trends
- 📈 **Resource Planning**: Data-driven insights for staffing and support
- 🎯 **Intervention Tracking**: Monitor effectiveness of support programs
- 📋 **Reporting**: Generate comprehensive reports for stakeholders

---

## 🛠 **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit | Interactive web dashboard |
| **Analytics** | Pandas, NumPy | Data processing and analysis |
| **Visualization** | Plotly | Interactive charts and graphs |
| **AI/ML** | Scikit-learn | Predictive modeling and risk assessment |
| **Cloud** | AWS (Lambda, S3, Athena) | Scalable data processing |
| **Infrastructure** | CloudFormation | Infrastructure as Code |

---

## 📚 **Documentation**

- 📖 **[Organization Guide](ORGANIZATION_GUIDE.md)**: Detailed explanation of the new structure
- 🎓 **[Tutorial Guide](TUTORIAL_README.md)**: How to use the tutorial system
- 🚀 **[Quick Start](README.md)**: Getting started guide
- 🌐 **[Tutorial Website](docs/tutorials/tutorial_website.html)**: Interactive learning portal

---

## 🤝 **Contributing**

We welcome contributions! The new organized structure makes it easy to contribute:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** in the appropriate `app/` subdirectory
4. **Add tests** for new functionality
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### **Development Guidelines**
- **UI components** go in `app/ui/`
- **Business logic** goes in `app/core/`
- **Shared utilities** go in `app/utils/`
- **Tutorial features** go in `app/tutorials/`

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 **Team**

- **Sibusiso Skhosana** - [GitHub](https://github.com/BhekumusaEric)
- **Eric Noah Ntshwenya** 
- **Israel Mbuyu**

**Built for the AWS Data Engineering Challenge 2025** 🏆

---

## 🌟 **Star this repo if you find it helpful!**

**Transform student outcomes with data-driven insights. Get started in 2 minutes!** 🎯📊

---

*Made with ❤️ for educators, students, and families worldwide.*
