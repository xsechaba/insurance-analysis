"""
Generate test data for Power BI dashboard validation.
Creates a smaller dataset with known patterns for testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_test_customers(n_customers=100):
    """Generate a small set of test customers."""
    np.random.seed(42)
    
    # Customer IDs
    customer_ids = [f'TEST{str(i).zfill(3)}' for i in range(n_customers)]
    
    # Age distribution (4 clear age groups)
    age_groups = [
        np.random.normal(25, 2, n_customers//4),  # Young
        np.random.normal(35, 2, n_customers//4),  # Adult
        np.random.normal(45, 2, n_customers//4),  # Middle-aged
        np.random.normal(65, 2, n_customers//4)   # Senior
    ]
    ages = np.concatenate(age_groups).clip(18, 85).astype(int)
    
    # Policy dates (last 12 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, periods=n_customers)
    
    # Premium amounts (correlated with age)
    base_premium = 1000
    age_factor = (ages - 18) / 67
    premiums = (base_premium * (1 + age_factor) * 
               np.random.uniform(0.8, 1.2, n_customers)).round(2)
    
    # Claims (with known patterns)
    has_claim = np.random.binomial(1, 0.3, n_customers)
    claim_amounts = np.zeros(n_customers)
    
    # Young drivers: high claim frequency, medium amounts
    young_mask = ages < 30
    claim_amounts[young_mask] = np.random.exponential(1500, sum(young_mask))
    
    # Senior drivers: low frequency, high amounts
    senior_mask = ages > 60
    claim_amounts[senior_mask] = np.random.exponential(3000, sum(senior_mask))
    
    # Middle-aged: medium frequency, medium amounts
    middle_mask = (ages >= 30) & (ages <= 60)
    claim_amounts[middle_mask] = np.random.exponential(2000, sum(middle_mask))
    
    claim_amounts = claim_amounts * has_claim
    
    # Fraud patterns
    high_risk = (claim_amounts > premiums * 1.5) & (has_claim == 1)
    fraud_reported = np.where(high_risk,
                            np.random.binomial(1, 0.8, n_customers),
                            np.random.binomial(1, 0.05, n_customers))
    
    # Customer segments (based on risk score)
    risk_score = ((claim_amounts / premiums.clip(min=1)) * 0.4 +
                 (fraud_reported * 0.6))
    
    # Add random noise to ensure unique values
    risk_score = risk_score + np.random.uniform(0, 0.0001, n_customers)
    
    segments = pd.qcut(risk_score, q=4,
                      labels=['Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk'],
                      duplicates='drop')
    
    # Create DataFrame
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'age': ages,
        'policy_date': dates,
        'annual_premium': premiums,
        'claim_amount': claim_amounts.round(2),
        'fraud_reported': fraud_reported,
        'customer_segment': segments,
        'policy_type': np.random.choice(
            ['Basic', 'Standard', 'Premium', 'Elite'],
            n_customers,
            p=[0.3, 0.4, 0.2, 0.1]
        ),
        'region': np.random.choice(
            ['North', 'South', 'East', 'West', 'Central'],
            n_customers
        ),
        'payment_method': np.random.choice(
            ['Credit Card', 'Debit Card', 'Bank Transfer'],
            n_customers,
            p=[0.5, 0.3, 0.2]
        ),
        'policy_status': np.random.choice(
            ['Active', 'Lapsed', 'Renewed', 'Cancelled'],
            n_customers,
            p=[0.7, 0.1, 0.15, 0.05]
        ),
        'customer_tenure': np.random.exponential(3, n_customers).round(1),
        'previous_claims': np.random.poisson(1, n_customers)
    })
    
    return df

def generate_test_metrics(df):
    """Generate test metrics from the test customer data."""
    
    # Time metrics
    time_metrics = df.groupby(df['policy_date'].dt.to_period('M')).agg({
        'annual_premium': 'sum',
        'claim_amount': 'sum',
        'fraud_reported': 'sum',
        'customer_id': 'count'
    }).round(2)
    
    time_metrics.columns = ['monthly_premium', 'monthly_claims',
                          'monthly_fraud_cases', 'new_policies']
    
    # Customer metrics
    customer_metrics = df.groupby('customer_segment').agg({
        'age': ['mean', 'min', 'max', 'count'],
        'annual_premium': ['mean', 'sum'],
        'claim_amount': ['mean', 'sum'],
        'fraud_reported': 'mean',
        'customer_tenure': 'mean',
        'previous_claims': 'sum'
    }).round(2)
    
    # Flatten column names
    customer_metrics.columns = ['avg_age', 'min_age', 'max_age', 'customer_count',
                              'avg_premium', 'total_premium',
                              'avg_claim', 'total_claims', 'fraud_rate',
                              'avg_tenure', 'total_previous_claims']
    
    # Add derived metrics
    customer_metrics['loss_ratio'] = (customer_metrics['total_claims'] / 
                                    customer_metrics['total_premium']).round(4)
    customer_metrics['profit'] = (customer_metrics['total_premium'] - 
                                customer_metrics['total_claims']).round(2)
    
    # Region metrics
    region_metrics = df.groupby('region').agg({
        'annual_premium': ['sum', 'mean'],
        'claim_amount': ['sum', 'mean'],
        'fraud_reported': ['sum', 'mean'],
        'customer_id': 'count',
        'previous_claims': 'sum'
    }).round(2)
    
    # Flatten column names
    region_metrics.columns = ['total_premium', 'avg_premium',
                            'total_claims', 'avg_claim',
                            'fraud_cases', 'fraud_rate',
                            'customer_count', 'total_previous_claims']
    
    # Add derived metrics
    region_metrics['loss_ratio'] = (region_metrics['total_claims'] / 
                                  region_metrics['total_premium']).round(4)
    region_metrics['profit'] = (region_metrics['total_premium'] - 
                              region_metrics['total_claims']).round(2)
    
    return time_metrics, customer_metrics, region_metrics

def save_test_data(df, time_metrics, customer_metrics, region_metrics):
    """Save test datasets."""
    output_dir = 'data/processed/test'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save datasets
    df.to_csv(f'{output_dir}/test_insurance_data.csv', index=False)
    time_metrics.to_csv(f'{output_dir}/test_time_metrics.csv')
    customer_metrics.to_csv(f'{output_dir}/test_customer_metrics.csv')
    region_metrics.to_csv(f'{output_dir}/test_region_metrics.csv')
    
    # Generate test data report
    report = []
    report.append("Test Data Summary")
    report.append("================")
    report.append(f"\nTotal Customers: {len(df)}")
    report.append(f"Date Range: {df['policy_date'].min()} to {df['policy_date'].max()}")
    
    report.append("\nAge Distribution:")
    age_stats = df['age'].describe()
    for stat, value in age_stats.items():
        report.append(f"{stat:>8}: {value:>8.1f}")
    
    report.append("\nPremium Distribution:")
    premium_stats = df['annual_premium'].describe()
    for stat, value in premium_stats.items():
        report.append(f"{stat:>8}: ${value:>8.2f}")
    
    report.append("\nClaim Distribution:")
    claim_stats = df['claim_amount'].describe()
    for stat, value in claim_stats.items():
        report.append(f"{stat:>8}: ${value:>8.2f}")
    
    report.append(f"\nFraud Rate: {df['fraud_reported'].mean():.2%}")
    
    report.append("\nSegment Distribution:")
    segment_dist = df['customer_segment'].value_counts(normalize=True)
    for segment, pct in segment_dist.items():
        report.append(f"{segment:>12}: {pct:>8.1%}")
    
    report.append("\nRegion Distribution:")
    region_dist = df['region'].value_counts(normalize=True)
    for region, pct in region_dist.items():
        report.append(f"{region:>8}: {pct:>8.1%}")
    
    report.append("\nPolicy Type Distribution:")
    policy_dist = df['policy_type'].value_counts(normalize=True)
    for policy, pct in policy_dist.items():
        report.append(f"{policy:>8}: {pct:>8.1%}")
    
    with open(f'{output_dir}/test_data_report.txt', 'w') as f:
        f.write('\n'.join(report))
    
    print(f"\nTest data saved to: {output_dir}")
    print('\n'.join(report))

def main():
    """Generate and save test data."""
    print("Generating test data...")
    
    # Generate test data
    df = generate_test_customers()
    time_metrics, customer_metrics, region_metrics = generate_test_metrics(df)
    
    # Save test data
    save_test_data(df, time_metrics, customer_metrics, region_metrics)
    
    print("\nTest data generation completed.")

if __name__ == "__main__":
    main() 