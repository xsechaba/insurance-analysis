# Power BI Dashboard Setup Guide

## Initial Setup

### Step 1: Install Power BI Desktop
1. Download Power BI Desktop from: https://powerbi.microsoft.com/en-us/desktop/
2. Run PowerBIDesktopSetup_x64.exe
3. Follow installation wizard with default settings
4. Launch Power BI Desktop

### Step 2: Configure Workspace
1. Create a new Power BI file
2. Save it as `Insurance_Analytics_Dashboard.pbix` in the `dashboard/powerbi` folder

### Step 3: Import Data
1. Click "Get Data" → "Text/CSV"
2. Navigate to `data/processed` folder
3. Import files in this order:
   - `insurance_data.csv`
   - `time_metrics.csv`
   - `customer_metrics.csv`
   - `region_metrics.csv`

### Step 4: Configure Data Types
For each table, set these data types:

#### insurance_data
- customer_id: Text
- age: Whole Number
- policy_date: Date
- annual_premium: Decimal Number
- claim_amount: Decimal Number
- fraud_reported: Whole Number
- customer_segment: Text
- policy_type: Text
- region: Text
- payment_method: Text
- policy_status: Text

#### time_metrics
- date: Date
- monthly_premium: Decimal Number
- monthly_claims: Decimal Number
- monthly_fraud_cases: Whole Number
- new_policies: Whole Number

### Step 5: Create Relationships
1. Go to "Model" view
2. Create these relationships:
   - insurance_data[policy_date] → time_metrics[date]
   - insurance_data[customer_segment] → customer_metrics[customer_segment]
   - insurance_data[region] → region_metrics[region]

### Step 6: Apply Theme
1. Go to View → Themes
2. Click "Browse for themes"
3. Select `dashboard/theme.json`
4. Apply theme

## Creating Pages

### 1. Executive Summary
1. Create new page
2. Add KPI cards at top:
   - Total Premium
   - Total Claims
   - Loss Ratio
   - Fraud Rate
3. Add line chart for trends
4. Add donut chart for segments

### 2. Customer Analysis
1. Create new page
2. Add demographic visuals:
   - Age distribution
   - Policy types
   - Payment methods
3. Add customer metrics

### 3. Risk Analysis
1. Create new page
2. Add risk metrics
3. Create risk matrix
4. Add fraud patterns

### 4. Regional Analysis
1. Create new page
2. Add map visualization
3. Add regional metrics
4. Create performance comparisons

## Final Steps

### 1. Configure Refresh
1. Go to File → Options and settings
2. Set up automatic refresh
3. Configure credentials

### 2. Test Dashboard
1. Check all visualizations
2. Verify filters work
3. Test drill-through actions
4. Validate calculations

### 3. Optimize Performance
1. Check query dependencies
2. Verify relationship cardinality
3. Test load times

## Troubleshooting

### Common Issues
1. Data not refreshing:
   - Check file paths
   - Verify permissions
   - Review credentials

2. Slow performance:
   - Reduce visual complexity
   - Create aggregations
   - Optimize relationships

3. Incorrect calculations:
   - Verify measure logic
   - Check relationship directions
   - Validate filter context

## Next Steps
1. Review full documentation
2. Schedule regular updates
3. Plan user training
4. Set up monitoring 