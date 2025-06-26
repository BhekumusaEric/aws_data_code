# Student Insights Pipeline

A smart data engineering solution designed to help educators personalize student support by identifying individual learning challenges and strengths using real-time insights — built entirely using **Python** and **AWS Free Tier services**.

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
- **Email**: siskhoscjc025@student.wethinkcode.co.za, ismbuyucjc025@student.wethinkcode.co.za, bhntshwcjc025@student.wethinkcode.co.za

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
