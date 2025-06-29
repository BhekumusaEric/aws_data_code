# AWS Health Monitoring System

## 🎯 **Overview**

The AWS Health Monitoring System provides real-time visibility into the health and connectivity of all AWS services used in your Student Insights Pipeline. This ensures you can quickly identify and resolve any infrastructure issues.

## 🔍 **What It Monitors**

### **Core AWS Services**
- **🔐 AWS Credentials** - Authentication and permissions
- **🪣 S3 Storage** - Data buckets and configurations
- **⚡ Lambda Functions** - Serverless compute functions
- **🌐 API Gateway** - RESTful API endpoints
- **📊 Athena** - Query workgroups and execution
- **🗄️ Glue Data Catalog** - Database and table schemas

### **Key Metrics Tracked**
- ✅ **Service Availability** - Is the service accessible?
- 📊 **Performance Metrics** - 24-hour activity statistics
- ⚙️ **Configuration Status** - Proper setup verification
- 🚨 **Error Rates** - Recent failures and issues
- 📈 **Usage Statistics** - Invocations, queries, requests

## 🚀 **How to Access**

### **Option 1: Main Dashboard Indicator**
- Look for the AWS status indicator at the top of the main dashboard
- **Green**: ☁️ **AWS Services Connected** - All systems operational
- **Red**: ☁️ **AWS Connection Issue** - Problems detected
- **Yellow**: ☁️ **AWS Status Unknown** - Unable to check

### **Option 2: Dedicated Health Dashboard**
1. Navigate to **"☁️ AWS Health Monitor"** from the main menu
2. View comprehensive health status for all services
3. Access detailed troubleshooting guides
4. Monitor real-time metrics and performance

## 📊 **Health Dashboard Features**

### **Overall Status Panel**
- **System Status**: Overall health indicator (Healthy/Partial/Down)
- **Services Online**: Count of operational vs total services
- **Region**: Current AWS region (af-south-1)
- **Last Check**: Timestamp of most recent health check

### **Service Detail Tabs**
Each AWS service has its own detailed tab showing:

#### **🔐 Credentials Tab**
- AWS account ID and user/role information
- Region configuration
- Authentication status

#### **🪣 S3 Storage Tab**
- Bucket accessibility and permissions
- Versioning and lifecycle policies
- Notification configurations
- Regional location verification

#### **⚡ Lambda Functions Tab**
- Function operational status
- Runtime and memory configuration
- 24-hour invocation and error counts
- Last modification timestamps

#### **🌐 API Gateway Tab**
- API availability and configuration
- Deployment stages
- 24-hour request statistics
- Endpoint URLs for testing

#### **📊 Athena Tab**
- Workgroup status and configuration
- Query execution statistics
- Result storage location
- Success/failure rates

#### **🗄️ Glue Catalog Tab**
- Database and table availability
- Schema information
- Data location verification
- Partition details

### **Health Metrics Charts**
- Visual representation of service health
- Historical trends (when available)
- Performance indicators

### **Troubleshooting Guide**
- Service-specific error resolution steps
- AWS CLI commands for diagnosis
- Common issue solutions
- Optimization recommendations

## 🔧 **Troubleshooting Common Issues**

### **AWS Credentials Not Configured**
```bash
# Configure AWS credentials
aws configure

# Verify configuration
aws sts get-caller-identity
```

### **S3 Buckets Not Accessible**
```bash
# List all buckets
aws s3 ls

# Check specific bucket
aws s3 ls s3://your-bucket-name

# Verify region
aws s3api get-bucket-location --bucket your-bucket-name
```

### **Lambda Functions Not Found**
```bash
# List Lambda functions
aws lambda list-functions --region af-south-1

# Check function details
aws lambda get-function --function-name your-function-name
```

### **API Gateway Issues**
```bash
# List REST APIs
aws apigateway get-rest-apis --region af-south-1

# Test API endpoint
curl -X GET https://your-api-id.execute-api.af-south-1.amazonaws.com/dev/students
```

### **Athena Workgroup Problems**
```bash
# List workgroups
aws athena list-work-groups --region af-south-1

# Check workgroup details
aws athena get-work-group --work-group your-workgroup-name
```

### **Glue Catalog Issues**
```bash
# List databases
aws glue get-databases --region af-south-1

# List tables in database
aws glue get-tables --database-name your-database-name
```

## 🎯 **Best Practices**

### **Regular Monitoring**
- Check health status before running data pipelines
- Monitor after deployments or configuration changes
- Set up automated alerts for critical issues

### **Performance Optimization**
- Review Lambda execution times and memory usage
- Monitor S3 storage costs and access patterns
- Optimize Athena queries for better performance
- Use appropriate instance types and configurations

### **Security Considerations**
- Regularly rotate AWS access keys
- Review IAM permissions and policies
- Monitor for unusual access patterns
- Keep services updated and patched

### **Cost Management**
- Monitor service usage and costs
- Implement lifecycle policies for S3 storage
- Use appropriate Lambda memory allocations
- Optimize Athena query patterns

## 🚨 **Alert Conditions**

The health monitoring system will alert you when:

### **Critical Issues**
- AWS credentials are invalid or expired
- S3 buckets are inaccessible
- Lambda functions are failing consistently
- API Gateway is returning errors
- Athena queries are failing

### **Warning Conditions**
- High error rates in Lambda functions
- S3 bucket notifications not configured
- Athena result location not accessible
- Glue tables missing or misconfigured

### **Performance Issues**
- Lambda functions timing out
- High API Gateway latency
- Athena queries taking too long
- S3 access patterns indicating problems

## 📈 **Metrics and KPIs**

### **Availability Metrics**
- Service uptime percentage
- Error rate thresholds
- Response time benchmarks

### **Performance Metrics**
- Lambda execution duration
- API Gateway response times
- Athena query execution times
- S3 operation latencies

### **Usage Metrics**
- Daily/weekly service invocations
- Data processing volumes
- Query execution frequency
- Storage utilization trends

## 🔄 **Auto-Refresh and Real-Time Monitoring**

### **Manual Refresh**
- Click the "🔄 Refresh Status" button for immediate updates
- Useful when troubleshooting active issues

### **Auto-Refresh Mode**
- Enable "Auto-refresh (30s)" checkbox for continuous monitoring
- Ideal for monitoring during deployments or maintenance
- Automatically updates every 30 seconds

### **Real-Time Alerts**
- Immediate notification of status changes
- Color-coded indicators for quick visual assessment
- Detailed error messages and resolution steps

## 📚 **Integration with Other Systems**

### **CloudWatch Integration**
- Leverages AWS CloudWatch metrics
- Historical performance data
- Custom metric creation capabilities

### **AWS CLI Integration**
- Provides CLI commands for manual verification
- Scriptable health checks
- Automation-friendly diagnostics

### **Streamlit Integration**
- Seamless integration with main application
- Real-time updates without page refresh
- Interactive troubleshooting guides

**Your AWS infrastructure health is now fully monitored and transparent!** 🎯☁️
