# Athena Cost Optimization Guide
## Student Insights Pipeline

### Overview
This guide provides comprehensive strategies for optimizing Amazon Athena costs while maintaining query performance in the Student Insights Pipeline.

### Cost Structure Understanding

#### Athena Pricing Model
- **Query Cost**: $5.00 per TB of data scanned
- **No charges for**: Failed queries, DDL statements, partition management
- **Free Tier**: 10GB of data scanned per month for first 12 months

#### Cost Factors
1. **Data Scanned**: Primary cost driver
2. **Query Frequency**: Number of queries executed
3. **Data Format**: Compression and file format efficiency
4. **Partitioning**: Partition pruning effectiveness

### Optimization Strategies

#### 1. Partition Pruning (60-90% Cost Reduction)

**Implementation:**
```sql
-- ✅ GOOD: Uses partition filters
SELECT student_id, average_score 
FROM processed_student_data
WHERE year = '2024' 
  AND month = '01'
  AND subject_partition = 'Mathematics';

-- ❌ BAD: Scans all partitions
SELECT student_id, average_score 
FROM processed_student_data
WHERE average_score > 80;
```

**Best Practices:**
- Always include `year` filter for time-based queries
- Add `month` filter for recent data analysis
- Use `subject_partition` for subject-specific queries
- Combine multiple partition filters when possible

#### 2. Column Selection (30-70% Cost Reduction)

**Implementation:**
```sql
-- ✅ GOOD: Select only needed columns
SELECT student_id, name, average_score, risk_level
FROM latest_student_data
WHERE year = '2024';

-- ❌ BAD: Selects all columns
SELECT * 
FROM latest_student_data
WHERE year = '2024';
```

**Guidelines:**
- Avoid `SELECT *` in production queries
- Use specific column names
- Prioritize frequently used columns
- Consider creating views for common column sets

#### 3. Data Format Optimization (40-60% Cost Reduction)

**Current Implementation:**
- **Format**: Parquet (columnar storage)
- **Compression**: Snappy
- **Benefits**: 
  - 3-5x smaller file sizes
  - Column-level compression
  - Predicate pushdown support

**File Size Optimization:**
```yaml
Optimal File Sizes:
  - Target: 128MB - 1GB per file
  - Avoid: Files < 10MB (overhead)
  - Avoid: Files > 5GB (parallelism issues)
```

#### 4. Query Pattern Optimization

**Use Optimized Views:**
```sql
-- ✅ GOOD: Use pre-optimized view
SELECT * FROM latest_student_data
WHERE risk_level = 'High Risk';

-- ❌ BAD: Manual window function
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (...) as rn
  FROM processed_student_data
) WHERE rn = 1 AND risk_level = 'High Risk';
```

**Aggregation Optimization:**
```sql
-- ✅ GOOD: Aggregate with partition filters
SELECT grade_level, AVG(average_score)
FROM latest_student_data
WHERE year = '2024' AND month = '01'
GROUP BY grade_level;

-- ❌ BAD: Aggregate without filters
SELECT grade_level, AVG(average_score)
FROM processed_student_data
GROUP BY grade_level;
```

### Cost Monitoring

#### 1. Query Cost Tracking

**CloudWatch Metrics:**
- `DataScannedInBytes`: Primary cost metric
- `QueryExecutionTime`: Performance indicator
- `ProcessedBytes`: Data processing volume

**Cost Calculation:**
```python
def calculate_query_cost(data_scanned_bytes):
    cost_per_tb = 5.00  # USD
    bytes_per_tb = 1024 ** 4
    return (data_scanned_bytes / bytes_per_tb) * cost_per_tb
```

#### 2. Budget Alerts

**CloudWatch Alarm Setup:**
```python
# Alert when daily costs exceed $0.50
alarm_threshold_bytes = 0.50 * (1024**4) / 5.00  # ~100GB
```

**Monthly Budget Tracking:**
- **Free Tier**: 10GB/month = ~$0.05 value
- **Recommended Budget**: $2-5/month for development
- **Production Budget**: $10-20/month for full analytics

#### 3. Cost Optimization Metrics

**Key Performance Indicators:**
```yaml
Cost Efficiency Metrics:
  - Cost per query: < $0.01
  - Data scanned per query: < 100MB
  - Partition pruning rate: > 80%
  - Query success rate: > 95%
```

### Query Optimization Patterns

#### 1. Time-Based Analysis
```sql
-- Optimized for recent data analysis
SELECT student_id, average_score, risk_level
FROM latest_student_data  -- Pre-filtered view
WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
  AND month = CAST(MONTH(CURRENT_DATE) AS VARCHAR)
  AND risk_level IN ('High Risk', 'Medium Risk');
```

#### 2. Subject-Specific Analysis
```sql
-- Optimized for subject analysis
SELECT grade_level, COUNT(*) as student_count, AVG(average_score) as avg_score
FROM processed_student_data
WHERE year = '2024'
  AND month >= '01'
  AND subject_partition = 'Mathematics'  -- Partition filter
GROUP BY grade_level;
```

#### 3. Trend Analysis
```sql
-- Optimized for trend analysis
SELECT year, month, AVG(average_score) as monthly_avg
FROM processed_student_data
WHERE year IN ('2023', '2024')  -- Specific years only
  AND subject_partition = 'Mathematics'
GROUP BY year, month
ORDER BY year, month;
```

### Cost Control Implementation

#### 1. Query Limits
```sql
-- Add LIMIT for exploratory queries
SELECT * FROM latest_student_data
WHERE year = '2024'
LIMIT 100;  -- Prevent large result sets
```

#### 2. Workgroup Configuration
```yaml
Workgroup Settings:
  - Query timeout: 30 minutes
  - Data scanned limit: 1GB per query
  - Result retention: 7 days
  - Encryption: Enabled
```

#### 3. Access Controls
```yaml
IAM Policies:
  - Restrict to specific databases
  - Limit query execution permissions
  - Monitor usage with CloudTrail
  - Implement resource-based policies
```

### Performance vs Cost Trade-offs

#### 1. Query Frequency
```yaml
High Frequency Queries (>10/day):
  - Use materialized views
  - Implement caching
  - Optimize for minimal data scanning

Low Frequency Queries (<1/day):
  - Accept higher latency
  - Focus on cost optimization
  - Use broader partition scans if needed
```

#### 2. Data Freshness
```yaml
Real-time Requirements:
  - Query latest partitions only
  - Use incremental processing
  - Implement change data capture

Historical Analysis:
  - Batch process older data
  - Use archived storage classes
  - Implement data lifecycle policies
```

### Monitoring and Alerting

#### 1. Daily Cost Monitoring
```python
# Daily cost check script
def check_daily_costs():
    # Query CloudWatch metrics
    # Calculate costs
    # Send alerts if threshold exceeded
    pass
```

#### 2. Query Performance Monitoring
```sql
-- Query performance analysis
SELECT 
    query_execution_id,
    data_scanned_in_bytes / (1024*1024) as data_scanned_mb,
    execution_time_in_millis / 1000 as execution_time_seconds
FROM athena_query_logs
WHERE execution_date = CURRENT_DATE
ORDER BY data_scanned_in_bytes DESC;
```

#### 3. Automated Optimization
```yaml
Automation Opportunities:
  - Partition maintenance
  - Query pattern analysis
  - Cost anomaly detection
  - Performance regression alerts
```

### Best Practices Summary

#### Query Writing
1. ✅ Always use partition filters
2. ✅ Select specific columns only
3. ✅ Use optimized views when available
4. ✅ Add LIMIT for exploratory queries
5. ✅ Use appropriate data types

#### Data Management
1. ✅ Maintain optimal file sizes (128MB-1GB)
2. ✅ Use Parquet with compression
3. ✅ Implement proper partitioning
4. ✅ Regular partition maintenance
5. ✅ Archive old data appropriately

#### Cost Control
1. ✅ Set up cost alerts
2. ✅ Monitor query patterns
3. ✅ Regular cost reviews
4. ✅ Optimize high-cost queries
5. ✅ Implement query limits

### Emergency Cost Control

#### If Costs Spike Unexpectedly:
1. **Immediate Actions:**
   - Check recent query history
   - Identify expensive queries
   - Pause non-essential analytics
   - Review partition filters

2. **Investigation Steps:**
   - Analyze CloudWatch metrics
   - Review query execution logs
   - Check for runaway queries
   - Validate partition pruning

3. **Prevention Measures:**
   - Implement stricter limits
   - Add more granular alerts
   - Review query patterns
   - Update optimization guidelines

### Cost Optimization Checklist

- [ ] Partition filters in all queries
- [ ] Column selection optimization
- [ ] File size optimization
- [ ] Query pattern analysis
- [ ] Cost monitoring setup
- [ ] Performance benchmarking
- [ ] Alert configuration
- [ ] Regular cost reviews
- [ ] Query optimization training
- [ ] Automated monitoring setup

### Expected Cost Ranges

```yaml
Development Environment:
  - Daily: $0.10 - $0.50
  - Monthly: $3 - $15
  - Per Query: $0.001 - $0.01

Production Environment:
  - Daily: $0.50 - $2.00
  - Monthly: $15 - $60
  - Per Query: $0.005 - $0.05

Cost Optimization Target:
  - 60-80% reduction through partitioning
  - 30-50% reduction through column selection
  - 40-60% reduction through format optimization
  - Overall: 70-90% cost reduction vs unoptimized queries
```
