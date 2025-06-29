#!/usr/bin/env python3
"""
AWS Health Dashboard UI Components
Real-time AWS service health monitoring for the Student Insights Pipeline
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any
import json

from app.utils.aws_health_checker import AWSHealthChecker


def render_aws_health_dashboard():
    """Render the AWS health monitoring dashboard"""
    st.title("☁️ AWS Services Health Dashboard")
    st.markdown("### Real-time monitoring of your Student Insights Pipeline infrastructure")
    
    # Health check controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("**Monitor the health and connectivity of all AWS services**")
    
    with col2:
        if st.button("🔄 Refresh Status", type="primary"):
            st.rerun()
    
    with col3:
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    
    # Auto-refresh functionality
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()
    
    # Initialize health checker
    health_checker = AWSHealthChecker()
    
    # Run comprehensive health check
    with st.spinner("🔍 Checking AWS services health..."):
        health_results = health_checker.run_comprehensive_health_check()
    
    # Display overall status
    render_overall_status(health_results)
    
    # Display detailed service status
    render_service_details(health_results)
    
    # Display metrics and charts
    render_health_metrics(health_results)
    
    # Display troubleshooting guide
    render_troubleshooting_guide(health_results)


def render_overall_status(health_results: Dict[str, Any]):
    """Render overall system health status"""
    st.markdown("---")
    st.markdown("### 🎯 Overall System Status")
    
    overall_status = health_results.get('overall_status', 'unknown')
    healthy_services = health_results.get('healthy_services', 0)
    total_services = health_results.get('total_services', 0)
    
    # Status indicator
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if overall_status == 'healthy':
            st.success("✅ **ALL SYSTEMS OPERATIONAL**")
        elif overall_status == 'partial':
            st.warning("⚠️ **PARTIAL OUTAGE**")
        else:
            st.error("🚨 **SYSTEM DOWN**")
    
    with col2:
        st.metric(
            "Services Online", 
            f"{healthy_services}/{total_services}",
            delta=f"{(healthy_services/total_services)*100:.0f}%" if total_services > 0 else "0%"
        )
    
    with col3:
        st.metric(
            "Region", 
            health_results.get('region', 'Unknown'),
            help="AWS region where services are deployed"
        )
    
    with col4:
        timestamp = health_results.get('timestamp', '')
        if timestamp:
            check_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            st.metric(
                "Last Check", 
                check_time.strftime("%H:%M:%S"),
                help=f"Full timestamp: {check_time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )


def render_service_details(health_results: Dict[str, Any]):
    """Render detailed service status information"""
    st.markdown("---")
    st.markdown("### 🔧 Service Details")
    
    services = health_results.get('services', {})
    
    # Create tabs for each service
    service_tabs = st.tabs([
        "🔐 Credentials", 
        "🪣 S3 Storage", 
        "⚡ Lambda Functions", 
        "🌐 API Gateway", 
        "📊 Athena", 
        "🗄️ Glue Catalog"
    ])
    
    # Credentials tab
    with service_tabs[0]:
        render_credentials_status(services.get('credentials', {}))
    
    # S3 tab
    with service_tabs[1]:
        render_s3_status(services.get('s3', {}))
    
    # Lambda tab
    with service_tabs[2]:
        render_lambda_status(services.get('lambda', {}))
    
    # API Gateway tab
    with service_tabs[3]:
        render_api_gateway_status(services.get('api_gateway', {}))
    
    # Athena tab
    with service_tabs[4]:
        render_athena_status(services.get('athena', {}))
    
    # Glue tab
    with service_tabs[5]:
        render_glue_status(services.get('glue', {}))


def render_credentials_status(creds_status: Dict[str, Any]):
    """Render AWS credentials status"""
    status = creds_status.get('status', 'unknown')
    
    if status == 'healthy':
        st.success("✅ AWS credentials configured successfully")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Account ID:** {creds_status.get('account_id', 'Unknown')}")
            st.info(f"**Region:** {creds_status.get('region', 'Unknown')}")
        
        with col2:
            user_arn = creds_status.get('user_arn', 'Unknown')
            if 'user/' in user_arn:
                user_name = user_arn.split('user/')[-1]
                st.info(f"**User:** {user_name}")
            elif 'role/' in user_arn:
                role_name = user_arn.split('role/')[-1]
                st.info(f"**Role:** {role_name}")
            else:
                st.info(f"**Identity:** {user_arn}")
    else:
        st.error(f"❌ {creds_status.get('message', 'AWS credentials not configured')}")
        if 'suggestion' in creds_status:
            st.code(creds_status['suggestion'])


def render_s3_status(s3_status: Dict[str, Any]):
    """Render S3 buckets status"""
    status = s3_status.get('status', 'unknown')
    buckets = s3_status.get('buckets', {})
    
    if status == 'healthy':
        st.success(f"✅ All {len(buckets)} S3 buckets are accessible")
    else:
        st.error(f"❌ S3 bucket issues detected")
    
    # Display bucket details
    for bucket_name, bucket_info in buckets.items():
        with st.expander(f"🪣 {bucket_name}"):
            if bucket_info['status'] == 'healthy':
                col1, col2 = st.columns(2)
                with col1:
                    st.success("✅ Accessible")
                    st.info(f"**Location:** {bucket_info.get('location', 'us-east-1')}")
                with col2:
                    st.info(f"**Versioning:** {bucket_info.get('versioning', 'Disabled')}")
                    notifications = "✅ Configured" if bucket_info.get('notifications_configured') else "❌ Not configured"
                    st.info(f"**Notifications:** {notifications}")
            else:
                st.error(f"❌ {bucket_info.get('message', 'Unknown error')}")


def render_lambda_status(lambda_status: Dict[str, Any]):
    """Render Lambda functions status"""
    status = lambda_status.get('status', 'unknown')
    functions = lambda_status.get('functions', {})
    
    if status == 'healthy':
        st.success(f"✅ All {len(functions)} Lambda functions are operational")
    else:
        st.error(f"❌ Lambda function issues detected")
    
    # Display function details
    for func_name, func_info in functions.items():
        with st.expander(f"⚡ {func_name}"):
            if func_info['status'] == 'healthy':
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.success("✅ Operational")
                    st.info(f"**Runtime:** {func_info.get('runtime', 'Unknown')}")
                    st.info(f"**Memory:** {func_info.get('memory_size', 'Unknown')} MB")
                
                with col2:
                    st.info(f"**Timeout:** {func_info.get('timeout', 'Unknown')}s")
                    st.info(f"**24h Invocations:** {func_info.get('invocations_24h', 0)}")
                
                with col3:
                    errors = func_info.get('errors_24h', 0)
                    if errors > 0:
                        st.warning(f"**24h Errors:** {errors}")
                    else:
                        st.success(f"**24h Errors:** {errors}")
                    
                    last_modified = func_info.get('last_modified', 'Unknown')
                    st.info(f"**Last Modified:** {last_modified}")
            else:
                st.error(f"❌ {func_info.get('message', 'Unknown error')}")


def render_api_gateway_status(api_status: Dict[str, Any]):
    """Render API Gateway status"""
    status = api_status.get('status', 'unknown')
    
    if status == 'healthy':
        st.success("✅ API Gateway is operational")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**API Name:** {api_status.get('api_name', 'Unknown')}")
            st.info(f"**API ID:** {api_status.get('api_id', 'Unknown')}")
            st.info(f"**24h Requests:** {api_status.get('requests_24h', 0)}")
        
        with col2:
            stages = api_status.get('stages', [])
            st.info(f"**Stages:** {', '.join(stages) if stages else 'None'}")
            
            endpoint_url = api_status.get('endpoint_url', '')
            if endpoint_url:
                st.info(f"**Endpoint:** {endpoint_url}")
                if st.button("🧪 Test API Endpoint"):
                    st.code(f"curl -X GET {endpoint_url}")
    else:
        st.error(f"❌ {api_status.get('message', 'API Gateway not accessible')}")


def render_athena_status(athena_status: Dict[str, Any]):
    """Render Athena workgroup status"""
    status = athena_status.get('status', 'unknown')
    
    if status == 'healthy':
        st.success("✅ Athena workgroup is operational")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Workgroup:** {athena_status.get('workgroup_name', 'Unknown')}")
            st.info(f"**State:** {athena_status.get('state', 'Unknown')}")
            st.info(f"**24h Queries:** {athena_status.get('queries_24h', 0)}")
        
        with col2:
            st.info(f"**Successful:** {athena_status.get('successful_queries_24h', 0)}")
            st.info(f"**Failed:** {athena_status.get('failed_queries_24h', 0)}")
            
            result_location = athena_status.get('result_location', 'Not configured')
            st.info(f"**Results:** {result_location}")
    else:
        st.error(f"❌ {athena_status.get('message', 'Athena workgroup not accessible')}")


def render_glue_status(glue_status: Dict[str, Any]):
    """Render Glue Data Catalog status"""
    status = glue_status.get('status', 'unknown')
    
    if status == 'healthy':
        st.success("✅ Glue Data Catalog is operational")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Database:** {glue_status.get('database_name', 'Unknown')}")
            st.info(f"**Tables:** {glue_status.get('table_count', 0)}")
        
        with col2:
            description = glue_status.get('description', 'No description')
            st.info(f"**Description:** {description}")
        
        # Display table details
        tables = glue_status.get('tables', {})
        if tables:
            st.markdown("**Tables:**")
            for table_name, table_info in tables.items():
                with st.expander(f"📊 {table_name}"):
                    st.info(f"**Location:** {table_info.get('location', 'Unknown')}")
                    st.info(f"**Columns:** {table_info.get('columns', 0)}")
                    st.info(f"**Partitions:** {table_info.get('partitions', 0)}")
    else:
        st.error(f"❌ {glue_status.get('message', 'Glue Data Catalog not accessible')}")


def render_health_metrics(health_results: Dict[str, Any]):
    """Render health metrics and charts"""
    st.markdown("---")
    st.markdown("### 📈 Health Metrics")
    
    services = health_results.get('services', {})
    
    # Create service status summary chart
    service_names = []
    service_statuses = []
    
    for service_name, service_data in services.items():
        service_names.append(service_name.replace('_', ' ').title())
        status = service_data.get('status', 'unknown')
        service_statuses.append(1 if status == 'healthy' else 0)
    
    if service_names:
        fig = px.bar(
            x=service_names,
            y=service_statuses,
            title="Service Health Status",
            labels={'x': 'AWS Services', 'y': 'Status (1=Healthy, 0=Error)'},
            color=service_statuses,
            color_continuous_scale=['red', 'green']
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def render_troubleshooting_guide(health_results: Dict[str, Any]):
    """Render troubleshooting guide based on health status"""
    st.markdown("---")
    st.markdown("### 🔧 Troubleshooting Guide")
    
    overall_status = health_results.get('overall_status', 'unknown')
    services = health_results.get('services', {})
    
    if overall_status == 'healthy':
        st.success("🎉 All systems are operational! No action required.")
        
        with st.expander("💡 Optimization Tips"):
            st.markdown("""
            **Your AWS infrastructure is healthy! Here are some optimization tips:**
            
            - 📊 Monitor Lambda function execution times and memory usage
            - 🪣 Review S3 storage costs and lifecycle policies
            - 📈 Set up CloudWatch alarms for proactive monitoring
            - 🔐 Regularly rotate AWS access keys
            - 💰 Use AWS Cost Explorer to optimize spending
            """)
    else:
        st.warning("⚠️ Some services need attention. Follow the troubleshooting steps below:")
        
        # Provide specific troubleshooting for each failed service
        for service_name, service_data in services.items():
            if service_data.get('status') != 'healthy':
                with st.expander(f"🔧 Fix {service_name.replace('_', ' ').title()} Issues"):
                    render_service_troubleshooting(service_name, service_data)


def render_service_troubleshooting(service_name: str, service_data: Dict[str, Any]):
    """Render specific troubleshooting steps for a service"""
    error_message = service_data.get('message', 'Unknown error')
    
    troubleshooting_guides = {
        'credentials': {
            'steps': [
                "1. Run `aws configure` to set up credentials",
                "2. Verify your AWS Access Key ID and Secret Access Key",
                "3. Ensure your region is set to 'af-south-1'",
                "4. Check if your AWS account has necessary permissions"
            ],
            'commands': [
                "aws configure",
                "aws sts get-caller-identity"
            ]
        },
        's3': {
            'steps': [
                "1. Verify S3 bucket names in CloudFormation outputs",
                "2. Check if buckets exist in the correct region (af-south-1)",
                "3. Verify IAM permissions for S3 access",
                "4. Ensure bucket policies allow your user/role access"
            ],
            'commands': [
                "aws s3 ls",
                "aws s3 ls s3://your-bucket-name"
            ]
        },
        'lambda': {
            'steps': [
                "1. Check if Lambda functions are deployed",
                "2. Verify function names match CloudFormation outputs",
                "3. Check Lambda execution role permissions",
                "4. Review CloudWatch logs for errors"
            ],
            'commands': [
                "aws lambda list-functions --region af-south-1",
                "aws logs describe-log-groups --region af-south-1"
            ]
        },
        'api_gateway': {
            'steps': [
                "1. Verify API Gateway deployment",
                "2. Check API Gateway stage configuration",
                "3. Test API endpoints manually",
                "4. Verify Lambda integration permissions"
            ],
            'commands': [
                "aws apigateway get-rest-apis --region af-south-1"
            ]
        },
        'athena': {
            'steps': [
                "1. Verify Athena workgroup exists",
                "2. Check S3 result location permissions",
                "3. Ensure Glue Data Catalog is accessible",
                "4. Test a simple query"
            ],
            'commands': [
                "aws athena list-work-groups --region af-south-1"
            ]
        },
        'glue': {
            'steps': [
                "1. Verify Glue database exists",
                "2. Check table definitions",
                "3. Run Glue crawler if needed",
                "4. Verify S3 data location permissions"
            ],
            'commands': [
                "aws glue get-databases --region af-south-1",
                "python scripts/athena-table-manager.py --action health-check"
            ]
        }
    }
    
    guide = troubleshooting_guides.get(service_name, {})
    
    st.error(f"**Error:** {error_message}")
    
    if guide:
        st.markdown("**Troubleshooting Steps:**")
        for step in guide.get('steps', []):
            st.markdown(f"- {step}")
        
        if guide.get('commands'):
            st.markdown("**Useful Commands:**")
            for cmd in guide['commands']:
                st.code(cmd)
    
    st.markdown("**Need Help?** Check the deployment guide or AWS documentation for more details.")
