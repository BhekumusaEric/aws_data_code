# S3 Data Organization Strategy
## Student Insights Pipeline

### Overview
This document outlines the comprehensive S3 data organization strategy for the Student Insights Pipeline, designed to optimize for performance, cost, and maintainability.

### Bucket Structure

#### Raw Data Bucket: `student-insights-pipeline-raw-data-{env}-{account-id}`

```
raw/
├── date=2024/01/15/
│   ├── hour=09/
│   │   ├── student_12345_20240115_093045.json
│   │   ├── student_12346_20240115_093102.json
│   │   └── ...
│   ├── hour=10/
│   └── hour=11/
├── date=2024/01/16/
└── ...
```

**Partitioning Strategy:**
- **Date Partitioning**: `date=YYYY/MM/DD` for time-based queries
- **Hour Partitioning**: `hour=HH` for granular time analysis
- **File Naming**: `student_{ID}_{timestamp}.json` for uniqueness

**Benefits:**
- Efficient time-range queries in Athena
- Automatic lifecycle management by date
- Parallel processing optimization
- Cost optimization through intelligent tiering

#### Processed Data Bucket: `student-insights-pipeline-processed-data-{env}-{account-id}`

```
processed/
├── year=2024/
│   ├── month=01/
│   │   ├── day=15/
│   │   │   ├── subject=Mathematics/
│   │   │   │   ├── part-00000-*.snappy.parquet
│   │   │   │   └── part-00001-*.snappy.parquet
│   │   │   ├── subject=English/
│   │   │   └── subject=Science/
│   │   └── day=16/
│   └── month=02/
├── year=2025/
└── ...

quality-reports/
├── data_quality_report_20240115_093045.json
├── data_quality_report_20240115_103045.json
└── ...

athena-results/
├── query-results/
│   ├── 2024/01/15/
│   └── ...
└── temp/

aggregations/
├── daily/
│   ├── year=2024/month=01/day=15/
│   │   ├── student_daily_summary.parquet
│   │   └── class_daily_summary.parquet
├── weekly/
└── monthly/
```

### Partitioning Strategy Details

#### 1. Raw Data Partitioning
- **Primary**: Date (YYYY/MM/DD) - Most common query pattern
- **Secondary**: Hour (HH) - For real-time analysis
- **File Level**: Student ID in filename for debugging

#### 2. Processed Data Partitioning
- **Level 1**: Year - Long-term analysis
- **Level 2**: Month - Semester/term analysis  
- **Level 3**: Day - Daily performance tracking
- **Level 4**: Subject - Subject-specific analysis

#### 3. Partition Pruning Benefits
```sql
-- Efficient query - only scans relevant partitions
SELECT * FROM student_data 
WHERE year = 2024 
  AND month = 1 
  AND subject = 'Mathematics'
  AND average_score < 70;
```

### File Formats and Compression

#### Raw Data
- **Format**: JSON (for flexibility and schema evolution)
- **Compression**: None (for real-time processing)
- **Size**: Small files (1-10KB per student record)

#### Processed Data
- **Format**: Parquet (columnar, optimized for analytics)
- **Compression**: Snappy (balance of speed and compression)
- **Size**: Larger files (1-10MB per partition)

### Lifecycle Management

#### Raw Data Retention
```yaml
Lifecycle Rules:
  - Transition to IA: 30 days
  - Transition to Glacier: 90 days  
  - Delete: 2 years (compliance dependent)
```

#### Processed Data Retention
```yaml
Lifecycle Rules:
  - Keep in Standard: 1 year
  - Transition to IA: 1 year
  - Transition to Glacier: 3 years
  - Long-term archive: 7 years
```

### Query Optimization Patterns

#### 1. Time-based Queries
```sql
-- Optimized: Uses partition pruning
SELECT student_id, average_score 
FROM processed_student_data
WHERE year = 2024 AND month = 1;
```

#### 2. Subject-based Analysis
```sql
-- Optimized: Subject partition pruning
SELECT AVG(average_score) as class_average
FROM processed_student_data  
WHERE subject = 'Mathematics'
  AND year = 2024;
```

#### 3. Risk Analysis
```sql
-- Cross-partition query with projection pushdown
SELECT risk_level, COUNT(*) as student_count
FROM processed_student_data
WHERE year = 2024 
GROUP BY risk_level;
```

### Performance Considerations

#### File Size Optimization
- **Target**: 128MB - 1GB per file for optimal Spark/Athena performance
- **Avoid**: Small files (<10MB) that cause overhead
- **Combine**: Use Glue job to combine small files during processing

#### Compression Benefits
- **Snappy**: 2-4x compression ratio
- **Query Speed**: Faster than GZIP for analytics
- **CPU Usage**: Lower decompression overhead

### Cost Optimization

#### Storage Classes
- **Standard**: Active data (last 30 days)
- **IA**: Historical data (30 days - 1 year)  
- **Glacier**: Archive data (1+ years)

#### Query Cost Reduction
- **Partition Pruning**: Reduces data scanned by 90%+
- **Columnar Format**: Only read required columns
- **Compression**: Reduces storage and transfer costs

### Monitoring and Maintenance

#### CloudWatch Metrics
- Bucket size by partition
- Query performance by partition
- Cost per query by time range

#### Automated Maintenance
- Daily partition validation
- Weekly small file compaction
- Monthly lifecycle policy review

### Security and Access Control

#### Bucket Policies
- Environment-specific access
- Role-based permissions
- Cross-account access controls

#### Encryption
- **At Rest**: S3-SSE (AES-256)
- **In Transit**: TLS 1.2+
- **Key Management**: AWS KMS integration

### Implementation Checklist

- [x] Raw data partitioning by date/hour
- [x] Processed data partitioning by year/month/day/subject
- [x] Parquet format with Snappy compression
- [x] Quality reports in separate folder
- [ ] Lifecycle policies implementation
- [ ] CloudWatch monitoring setup
- [ ] Cost optimization review
- [ ] Performance benchmarking

### Next Steps

1. Implement lifecycle policies in CloudFormation
2. Set up CloudWatch dashboards for monitoring
3. Create automated compaction jobs
4. Establish performance benchmarks
5. Document query best practices
