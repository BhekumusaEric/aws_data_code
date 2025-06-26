# Student Insights Pipeline

A comprehensive predictive intervention system that helps educators personalize student support through AI-powered analytics and actionable recommendations — built with **Python**, **Streamlit**, and **AWS Free Tier services**.

## 🚀 **Main System: `predictive_intervention_system.py`**

**This is your primary application** with all features built-in:
- ✅ Complete Student Insights Pipeline functionality
- ✅ **Integrated tutorial system** for first-time users
- ✅ **Contextual help** and smart hints throughout
- ✅ **Role-specific guidance** for Teachers, Parents, and Administrators
- ✅ **Interactive learning modules** accessible from the sidebar

## ⚡ **Quick Start (2 Commands)**

```bash
# 1. Install dependencies (one time only)
pip install streamlit plotly pandas numpy boto3

# 2. Launch the system
python -m streamlit run main.py
```

**Windows users:** Double-click `launchers/run_tutorial_system.bat` for automatic setup and launch!

---

## 🎯 Project Overview

### 👩‍🏫 Problem Statement
Many classrooms today rely on a "one-size-fits-all" teaching approach, which often fails to meet individual student needs. Educators are overwhelmed, and students who fall behind go unnoticed until it’s too late.

### ✅ Our Solution
This project provides an intelligent predictive intervention system with a user-friendly web interface that analyzes student data and generates personalized action plans. The system combines data engineering with predictive analytics to help educators make data-driven decisions for individual student success.

### 🌟 Key Features
- **🎯 Predictive Intervention System**: AI-powered risk assessment and personalized recommendations
- **👩‍🏫 Teacher Portal**: Dedicated interface for educators with class management and individual student insights
- **👨‍👩‍👧‍👦 Parent Portal**: Family-friendly dashboard showing student progress and home support strategies
- **📊 Interactive Analytics**: Real-time performance tracking and trend analysis
- **⚠️ Risk Assessment**: Early identification of students needing intervention
- **📝 Data Entry & Management**: Easy student data input and management
- **🔍 Advanced Filtering**: Multi-dimensional data exploration by grade, subject, and performance metrics

---

## 🚀 How to Use the System

### Quick Start (2 minutes)
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the Main System**:
   ```bash
   # Method 1: Direct command
   python -m streamlit run predictive_intervention_system.py

   # Method 2: Use the launcher (Windows)
   .\run_tutorial_system.bat

   # Method 3: Alternative port if 8501 is busy
   python -m streamlit run predictive_intervention_system.py --server.port=8502
   ```

3. **Access the Dashboard**: Open your browser to `http://localhost:8501`

### 🎯 Main User Interface

The system provides a comprehensive web-based dashboard with multiple views:

#### **🏠 Dashboard Overview**
- Real-time student performance metrics
- Risk assessment summary
- Intervention effectiveness tracking
- System-wide analytics

#### **👤 Individual Student Analysis**
- Detailed student profiles with performance history
- Personalized risk assessment
- AI-generated intervention recommendations
- Progress tracking and goal setting

#### **📊 Predictive Analytics**
- Machine learning-powered risk prediction
- Performance trend analysis
- Early warning system for at-risk students
- Comparative analytics across cohorts

#### **📋 Intervention Plans**
- Automated action plan generation
- Evidence-based intervention strategies
- Progress monitoring and adjustment
- Success rate tracking

#### **👩‍🏫 Teacher Portal**
- Class-specific dashboards
- Individual student deep-dives
- Intervention plan management
- Parent communication tools

#### **👨‍👩‍👧‍👦 Parent Portal**
- Child-specific progress reports
- Home support recommendations
- Communication with teachers
- Goal tracking and celebrations

---

## 🔧 How the System Works

### **System Architecture**
The Student Insights Pipeline operates as a **local-first Streamlit application** with optional cloud integration:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Streamlit App   │───▶│   User Roles    │
│                 │    │                  │    │                 │
│ • CSV Upload    │    │ • Data Processing│    │ • Teachers      │
│ • Manual Entry  │    │ • ML Analytics   │    │ • Parents       │
│ • API (Optional)│    │ • Risk Assessment│    │ • Administrators│
│ • Sample Data   │    │ • Visualizations │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Data Flow Process**
1. **Data Input**:
   - Load sample data automatically on startup
   - Upload CSV files through the interface
   - Manual data entry via forms
   - (Optional) Real-time API integration

2. **Processing & Analysis**:
   - **Data Validation**: Ensure data quality and consistency
   - **Risk Scoring**: ML algorithms calculate student risk levels
   - **Trend Analysis**: Identify performance patterns over time
   - **Intervention Matching**: AI suggests personalized action plans

3. **User Interface**:
   - **Multi-Role Dashboard**: Different views for teachers, parents, admins
   - **Interactive Analytics**: Real-time filtering and exploration
   - **Predictive Insights**: Early warning systems and recommendations
   - **Progress Tracking**: Monitor intervention effectiveness

4. **Output & Actions**:
   - **Personalized Reports**: Individual student assessments
   - **Action Plans**: Evidence-based intervention strategies
   - **Communication Tools**: Parent-teacher collaboration features
   - **Export Capabilities**: Generate reports for meetings

### **Key Components**
- **🎯 Predictive Engine**: Machine learning models for risk assessment
- **📊 Analytics Dashboard**: Interactive data visualization and exploration
- **👥 Multi-Role Interface**: Customized views for different user types
- **🔄 Real-Time Processing**: Immediate analysis of new data
- **📈 Progress Monitoring**: Track intervention success over time

---

## 🛠 Tech Stack

| Layer           | Technology       | Purpose                                 |
|----------------|------------------|-----------------------------------------|
| Frontend        | Streamlit        | Interactive web dashboard               |
| Analytics       | Pandas, NumPy    | Data processing and analysis            |
| Visualization   | Plotly, Charts   | Interactive graphs and metrics          |
| ML/AI           | Scikit-learn     | Predictive modeling and risk assessment |
| Backend Data    | AWS Lambda       | Data ingestion API (Optional)           |
| Storage         | Amazon S3        | Raw and processed data storage (Optional)|
| Query Engine    | Athena           | SQL analytics on stored data (Optional) |
| Infrastructure  | CloudFormation   | Infrastructure as Code (Optional)       |

---

## 📁 Project Structure (Organized with Separation of Concerns)
```
student_insights_pipeline/
├── main.py                             # 🎯 MAIN ENTRY POINT - Launch this!
├── app/                                # 📱 Main application code
│   ├── core/                           # 🧠 Core business logic
│   │   └── predictive_system.py        # AI prediction and data processing
│   ├── ui/                             # 🎨 User interface components
│   │   ├── dashboard.py                # Dashboard views and charts
│   │   └── student_analysis.py         # Individual student analysis UI
│   ├── tutorials/                      # 🎓 Tutorial and learning system
│   │   └── tutorial_manager.py         # Tutorial integration and management
│   └── utils/                          # 🔧 Utility functions and helpers
├── launchers/                          # 🚀 Application launchers
│   ├── run_tutorial_system.bat         # Windows launcher (double-click)
│   └── run_system.py                   # Cross-platform Python launcher
├── docs/                               # 📖 Documentation and guides
│   ├── tutorials/                      # 🎓 Tutorial resources
│   │   └── tutorial_website.html       # Standalone tutorial website
│   └── *.md                           # Various documentation files
├── data/                               # 📊 Data files
│   └── sample_student_data.csv         # Sample data for testing
├── src/                                # 🔧 Legacy core modules (being migrated)
├── ingestion/                          # 📥 AWS data ingestion
│   └── lambda_function.py              # AWS Lambda functions
├── transformation/                     # 🔄 Data transformation
│   └── glue_job_script.py              # AWS Glue scripts
├── analytics/                          # 📊 Analytics and queries
│   └── athena_queries.sql              # SQL queries for insights
├── infrastructure/                     # ☁️ Cloud infrastructure
│   └── cloudformation.yaml             # AWS infrastructure as code
├── scripts/                            # 🛠️ Utility and management scripts
├── tests/                              # 🧪 Test suites
├── requirements.txt                    # 📦 Python dependencies
├── setup.py                           # 📦 Package installation
└── README.md                          # 📖 This documentation
```

---

## 🧪 Typical User Workflow

### For Teachers:
1. **Launch System**: `python -m streamlit run main.py`
2. **Take the Tutorial**: Click "📚 Interactive Tutorial" in the sidebar for guided learning
3. **Navigate to Teacher Portal**: Select "👩‍🏫 Teacher Portal" from the main navigation
4. **Review Class Overview**: See all students' performance and risk levels
5. **Drill Down**: Click on individual students for detailed analysis
6. **Generate Action Plans**: Use AI-powered recommendations for interventions
7. **Track Progress**: Monitor intervention effectiveness over time
8. **Get Help**: Use the built-in hints and tips throughout the interface

### For Parents:
1. **Access Parent Portal**: Select "👨‍👩‍👧‍👦 Parent Portal" from the sidebar
2. **Enter Parent Information**: Provide name and select your child
3. **View Progress Report**: See comprehensive performance overview
4. **Get Home Support Tips**: Access personalized strategies to help at home
5. **Track Goals**: Monitor progress toward academic targets
6. **Communicate**: Send messages to teachers through the platform

### For Administrators:
1. **Dashboard Overview**: Monitor system-wide performance metrics
2. **Predictive Analytics**: Review risk assessments across all students
3. **Intervention Tracking**: Analyze effectiveness of intervention programs
4. **Resource Planning**: Use insights for staffing and resource allocation

---

## 🎯 Key System Features

### **Predictive Analytics Engine**
- **Risk Scoring**: Machine learning algorithms assess student risk levels
- **Trend Analysis**: Identifies performance patterns and trajectories
- **Early Warning System**: Flags students before they fall behind
- **Comparative Analytics**: Benchmarks individual progress against peers

### **Personalized Intervention System**
- **AI-Generated Recommendations**: Tailored action plans for each student
- **Evidence-Based Strategies**: Interventions backed by educational research
- **Progress Tracking**: Real-time monitoring of intervention effectiveness
- **Adaptive Planning**: Recommendations adjust based on student response

### **Multi-Role Dashboard**
- **Teacher View**: Class management, individual student insights, intervention tools
- **Parent View**: Child-specific progress, home support strategies, communication
- **Admin View**: System-wide analytics, resource planning, effectiveness metrics

### **Data Integration**
- **Flexible Input**: CSV upload, manual entry, or API integration
- **Real-time Processing**: Immediate analysis of new student data
- **Historical Tracking**: Long-term performance and intervention history
- **Export Capabilities**: Generate reports for meetings and documentation

---

## 🔐 Security & Privacy
- Student data privacy protection with anonymization options
- Secure local processing - no sensitive data leaves your environment
- Role-based access control for different user types
- Optional AWS integration with IAM security controls

---

## 💸 Cost Structure
- **Local Usage**: Free - runs entirely on your computer
- **AWS Integration** (Optional): Uses AWS Free Tier services
- **Scalable**: Pay-as-you-grow model for larger deployments
- **No Licensing Fees**: Open source solution

---

## 🧠 Educational Impact
- **Personalized Learning**: Move beyond one-size-fits-all approaches
- **Early Intervention**: Catch struggling students before they fall behind
- **Data-Driven Decisions**: Replace guesswork with evidence-based strategies
- **Parent Engagement**: Provide families with actionable insights and support tools
- **Teacher Efficiency**: Streamline identification and intervention processes

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.9+** installed on your system
- **Git** for cloning the repository
- **(Optional)** AWS account for cloud integration

### Step 1: Clone and Install
```bash
# Clone the repository
git clone https://github.com/your-repo/student-insights-pipeline.git
cd student-insights-pipeline

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Launch the System
```bash
# Start the main system
python -m streamlit run main.py

# Windows users can also double-click:
# launchers/run_tutorial_system.bat
```

### Step 3: Access the Dashboard
- Open your web browser
- Navigate to `http://localhost:8501`
- The system will automatically load with sample data for demonstration

### Step 4: Take the Interactive Tutorial
- Look for the **📚 Interactive Tutorial** button in the sidebar
- Choose your role (Teacher, Parent, or Administrator)
- Follow the step-by-step guided tour
- Practice with sample data in a safe environment

## 🎓 Learning & Tutorial System

We've built a comprehensive tutorial system to help first-time users master the platform:

### **📚 Interactive Tutorials**
The tutorial system is **built directly into the main application**:
```bash
# Launch the main system (tutorials included)
python -m streamlit run predictive_intervention_system.py

# Windows users can also use:
.\run_tutorial_system.bat
```

**Tutorial features are automatically available:**
- 🎓 **First-time user welcome** with guided tour options
- 📚 **Interactive Tutorial button** in the sidebar Learning Center
- 💡 **Contextual hints** that appear based on current page
- 🎯 **Role-specific guidance** for Teachers, Parents, and Administrators

### **🌐 Tutorial Website**
Open `tutorial_website.html` in your browser for a comprehensive learning experience with:
- Step-by-step guides for each user role
- Interactive demonstrations
- Video tutorials (coming soon)
- Quick reference guides

### **💡 Built-in Help System**
The main application includes:
- **First-time user welcome**: Automatic tutorial prompts for new users
- **Contextual hints**: Smart tips based on what you're viewing
- **Interactive tooltips**: Hover help throughout the interface
- **Progress tracking**: See your learning progress across modules

### **🎯 Tutorial Modules Available**
1. **🏠 System Overview** (5 min) - Dashboard navigation and key features
2. **👩‍🏫 Teacher Portal** (8 min) - Classroom management and student analysis
3. **👨‍👩‍👧‍👦 Parent Portal** (6 min) - Supporting your child's learning at home
4. **📊 Predictive Analytics** (7 min) - Understanding AI-powered insights
5. **🎯 Intervention Plans** (5 min) - Creating and managing action plans
6. **📈 Advanced Features** (10 min) - Power user tips and tricks

### Optional: AWS Integration
For production deployment with cloud storage and processing:

```bash
# Configure AWS credentials
aws configure

# Deploy infrastructure
python deploy.py --environment dev

# Test deployment
python test_deployment.py
```

---

## 📊 Sample Data & Demo Mode

The system includes comprehensive sample data to demonstrate all features:
- **50+ synthetic student records** with realistic performance data
- **Multiple subjects**: Math, Science, English, History, Art
- **Various grade levels**: Elementary through High School
- **Risk categories**: Low, Medium, High risk students
- **Intervention history**: Sample intervention plans and outcomes

**Demo Mode Features:**
- Fully functional without AWS setup
- All analytics and predictions work with sample data
- Safe environment for testing and training
- Easy transition to real data when ready

---

## 📬 Team Info
- **Team Members**: Sibusiso Skhosana, Eric Noah Ntshwenya, Israel Mbuyu
- **Challenge**: AWS Data Engineering Challenge 2025
- **Email**: siskhoscjc025@student.wethinkcode.co.za, ismbuyucjc025@student.wethinkcode.co.za, bhntshwcjc025@student.wethinkcode.co.za

---

## ✅ AWS Free Tier Tracker
| Service       | Limits                  | Usage in Project         |
|---------------|--------------------------|---------------------------|
| S3            | 5GB/month                | ~<10MB student data       |
| Lambda        | 1M requests/month        | 1 API per student         |
| Athena        | 1TB scanned/month        | CSV queries < 100MB       |
| Glue (opt)    | 1M requests/month        | Single test script        |
| QuickSight    | Free Trial / Viewer mode | Optional dashboard        |

---

## 🎓 Educational Value
This project can be used by:
- **Schools** to personalize student interventions
- **Universities** for data-driven curriculum support
- **EdTech startups** as a backend for adaptive platforms

Want help turning this into a SaaS or pitch deck? Let’s go!



---

## 🎯 Project Overview

### 👩‍🏫 Problem Statement
Many classrooms today rely on a "one-size-fits-all" teaching approach, which often fails to meet individual student needs. Educators are overwhelmed, and students who fall behind go unnoticed until it’s too late.

### ✅ Our Solution
This project provides a lightweight, serverless data pipeline that ingests, transforms, analyzes, and visualizes student data. Educators get real-time insights into who is struggling, where, and why — enabling personalized, data-driven interventions.

### 🌟 Key Features
- Upload or receive student data through an API
- Store and process data securely in AWS
- Analyze performance trends using SQL
- Generate educator-friendly dashboards
- All using AWS Free Tier to minimize costs

---

## 🧱 Architecture Diagram
> ![architecture_diagram.png](architecture_diagram.png)

### 🔄 Pipeline Flow
1. **Ingest**: Student data collected via Lambda and API Gateway
2. **Store**: Raw data saved to S3
3. **Transform**: Cleaned with Glue or Python script
4. **Analyze**: Query with Athena
5. **Visualize**: (Optional) QuickSight dashboard or export

---

## 🛠 Tech Stack (Free Tier Friendly)

| Layer           | Service         | Purpose                                 |
|----------------|------------------|-----------------------------------------|
| Ingestion       | AWS Lambda       | Handle incoming student JSON data       |
| API             | API Gateway      | Trigger Lambda with HTTP POST requests  |
| Storage         | Amazon S3        | Store raw and cleaned student data      |
| Transformation  | Python or Glue   | Clean and enrich student records        |
| Query Engine    | Athena           | Analyze structured data in S3           |
| IAM             | IAM Roles/Policy | Grant secure access between services    |
| Visualization   | QuickSight (opt) | Dashboards for educators                |

---

## 📁 Project Structure
```
student_insights_pipeline/
├── data/
│   └── sample_student_data.csv
├── ingestion/
│   └── lambda_function.py
├── transformation/
│   └── glue_job_script.py
├── analytics/
│   └── athena_queries.sql
├── dashboard/
│   └── quicksight_mockup.png
├── infrastructure/
│   └── cloudformation.yaml
├── README.md
└── architecture_diagram.png
```

---

## 🧪 Sample Use Case
1. Teacher uploads CSV or sends student JSON to an API
2. The data is saved to S3 and optionally transformed
3. Educators run predefined Athena queries (or see visual dashboard)
4. Results show which students are at risk, by subject

---

## 🔐 Security
- IAM roles restrict access between Lambda, S3, and Athena
- No personally identifiable data (PII) is stored
- Secrets Manager can be added for future API key protection

---

## 💸 Cost Optimization
- **All services run on AWS Free Tier**
- No EC2 or provisioned resources
- Query volume and dashboard usage kept minimal

---

## 🧠 Lessons Learned
- Simple data formats (like CSV/JSON) speed up prototyping
- Monitoring data quality early prevents garbage-in, garbage-out
- Even synthetic student data can model real-world problems

---

## 🗣️ Demo Pitch Summary
> This project empowers educators with real-time, data-driven insights about student performance using an AWS-powered pipeline — enabling tailored interventions that boost learning success.

---

## 📬 Team Info
- **Team Members**: Sibusiso Skhosana, Eric Noah Ntshwenya, Israel Mbuyu
- **Challenge**: AWS Data Engineering Challenge 2025
- **Email**: siskhoscjc025@student.wethinkcode.co.za, ismbuyucjc025@student.wethinkcode.co.za , bhntshwcjc025@student.wethinkcode.co.za , 

---

## 📦 Submission Deliverables
| Item                        | Location                      |
|-----------------------------|-------------------------------|
| Source Code (Python)        | `repo/`                       |
| Architecture Diagram        | `architecture_diagram.png`   |
| Infrastructure as Code      | `infrastructure/cloudformation.yaml` |
| Sample Data                 | `data/sample_student_data.csv` |
| Deployment Guide (This Doc) | `README.md`                  |

---

## 🚀 How to Deploy
1. Create an S3 bucket manually or via CloudFormation
2. Deploy the `lambda_function.py` and attach proper IAM role
3. (Optional) Use API Gateway to trigger Lambda via POST
4. Upload sample data to S3 or call API
5. Query S3 with Athena using `analytics/athena_queries.sql`
6. (Optional) Connect QuickSight to S3/Athena for dashboards

---

## ✅ AWS Free Tier Tracker
| Service       | Limits                  | Usage in Project         |
|---------------|--------------------------|---------------------------|
| S3            | 5GB/month                | ~<10MB student data       |
| Lambda        | 1M requests/month        | 1 API per student         |
| Athena        | 1TB scanned/month        | CSV queries < 100MB       |
| Glue (opt)    | 1M requests/month        | Single test script        |
| QuickSight    | Free Trial / Viewer mode | Optional dashboard        |

---

## 🎓 Educational Value
This project can be used by:
- **Schools** to personalize student interventions
- **Universities** for data-driven curriculum support
- **EdTech startups** as a backend for adaptive platforms

Want help turning this into a SaaS or pitch deck? Let’s go!


# Student Insights Pipeline

A lightweight, scalable data engineering solution to help educators personalize learning by identifying each student's strengths and weaknesses. Built using **Python** and **AWS Free Tier services** only.

---

## 🚀 Project Overview

**Goal:** Help educators make data-driven decisions by analyzing student performance data, and surfacing tailored learning insights.

**How it works:**
- Collects student data via API (AWS Lambda)
- Stores raw data in Amazon S3
- Transforms data with Python or AWS Glue
- Queries insights using Athena
- Visualizes results with QuickSight (or placeholder if QuickSight isn't available)

---

## 🛠 Tech Stack (AWS Free Tier Compatible)

| Component         | Service            | Free Tier? | Purpose                              |
|------------------|--------------------|------------|--------------------------------------|
| Ingestion        | AWS Lambda         | ✅         | Collect and store data               |
| Storage          | Amazon S3          | ✅         | Store raw and transformed CSV files  |
| Transformation   | Python (or AWS Glue) | ✅       | Clean and structure data             |
| Query            | Athena             | ✅         | Analyze structured data              |
| Dashboard        | QuickSight (optional) | ⚠️     | Visual reports (or use mockups)      |
| IAM              | IAM Roles/Policies | ✅         | Secure access between services       |

---

## 📁 Project Structure

```
repo/
├── data/
│   └── sample_student_data.csv         # Example data
├── ingestion/
│   └── lambda_function.py              # Lambda function to receive + push to S3
├── transformation/
│   └── glue_job_script.py              # Glue (or local) transformation logic
├── analytics/
│   └── athena_queries.sql              # SQL to surface insights
├── dashboard/
│   └── quicksight_mockup.png           # (Optional) dashboard visual
├── infrastructure/
│   └── cloudformation.yaml             # Infrastructure-as-Code
├── README.md
└── architecture_diagram.png            # Visual system diagram
```

---

## 📌 Features
- Upload and ingest student CSVs via HTTP (API Gateway → Lambda → S3)
- Validate and transform student performance data
- Query top struggling students, topic-specific issues
- Visualize with Athena and (optionally) QuickSight

---

## 🔐 Security
- IAM role limits for Lambda and S3
- No sensitive student PII stored
- (Optional) Secrets Manager for API keys / credentials

---

## 🧠 How to Run
1. Deploy infrastructure using `cloudformation.yaml`
2. Upload `sample_student_data.csv` manually or through API
3. Use Athena queries to explore insights
4. (Optional) Connect QuickSight to Athena for dashboards

---

## 💸 Cost Optimization
- All components use AWS Free Tier
- Small file sizes, no provisioned compute
- No paid QuickSight unless enabled

---

## 📚 Lessons Learned
- Data pipelines need thoughtful error handling
- Even synthetic data can reveal real-world challenges
- Visualization brings clarity to raw numbers

---

## 📣 Credits & Acknowledgments
- AWS User Groups
- UCI Student Dataset
- Open University Analytics dataset

---

Main Goal of the Solution

The primary goal of this data engineering solution is:

    To help educators identify individual student challenges and strengths using structured data pipelines — enabling personalized, data-driven learning interventions instead of a one-size-fits-all approach.

✅ What This Means Practically

Instead of teachers manually guessing which students are struggling and why, the system:

    Ingests student performance data (e.g. quiz scores, attendance)

    Cleans and structures that data for analysis

    Surfaces insights like:

        Which students are underperforming in math?

        Who has irregular attendance linked to lower scores?

        Which learners are improving over time?

    Visualizes trends with dashboards so teachers can act fast

🧠 Why It Matters

    Personalization = better learning outcomes 🧑‍🏫📈

    Helps educators target support where it's needed

    Saves time analyzing performance manually

    Builds a future-ready education system powered by data

    Demo Pitch Script: Project Summary

    “In today’s classrooms, educators are overwhelmed by large class sizes, diverse learning needs, and limited visibility into individual student struggles. Our solution empowers teachers with real-time, data-driven insights — built on a scalable AWS data pipeline — to identify which students are falling behind, in what areas, and why.

    Instead of a one-size-fits-all approach, we offer tailored, actionable feedback so teachers can give the right help to the right student at the right time. It’s not just a dashboard — it’s a tool for transforming student outcomes.”

## 📬 Contact
**Team**: Kagiso, Mesh, and Kgothatso  
**Challenge**: Data Engineering Challenge 2025  
**Email**: yourname@example.com
