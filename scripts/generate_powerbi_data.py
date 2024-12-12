"""
Generate structured data for Power BI dashboard with realistic insurance metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Define constants for consistent values across datasets
CUSTOMER_SEGMENTS = ['Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk']
REGIONS = ['North', 'South', 'East', 'West', 'Central']
POLICY_TYPES = ['Basic', 'Standard', 'Premium', 'Elite']
PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'Bank Transfer']
POLICY_STATUS = ['Active', 'Lapsed', 'Renewed', 'Cancelled']

def generate_dates(n_records, start_date='2022-01-01'):
    """Generate a sequence of dates."""
    start = pd.to_datetime(start_date)
    dates = [start + timedelta(days=x) for x in range(n_records)]
    return pd.Series(dates)

def generate_customer_data(n_customers=20000):
    """Generate customer demographic data."""
    np.random.seed(42)
    
    # Generate basic customer info
    df = pd.DataFrame()
    df['customer_id'] = [f'CUS{str(i).zfill(6)}' for i in range(n_customers)]
    df['age'] = np.random.normal(45, 15, n_customers).astype(int)
    df['age'] = df['age'].clip(18, 85)
    
    # Generate policy dates
    df['policy_date'] = generate_dates(n_customers)
    
    # Generate premiums based on age
    base_premium = 1000
    age_factor = (df['age'] - 18) / 67  # Normalize age
    df['annual_premium'] = (base_premium * (1 + age_factor) * 
                          np.random.uniform(0.8, 1.2, n_customers)).round(2)
    
    # Generate claims
    df['has_claim'] = np.random.binomial(1, 0.3, n_customers)
    claim_amounts = np.random.exponential(2000, n_customers) * df['has_claim']
    df['claim_amount'] = claim_amounts.round(2)
    
    # Generate fraud indicators
    high_risk = ((df['claim_amount'] > df['annual_premium'] * 1.5) & 
                (df['has_claim'] == 1))
    df['fraud_reported'] = np.where(high_risk, 
                                  np.random.binomial(1, 0.6, n_customers),
                                  np.random.binomial(1, 0.05, n_customers))
    
    # Calculate risk score with more variation
    df['risk_score'] = (
        (df['claim_amount'] / df['annual_premium'].clip(lower=1)).fillna(0) * 0.4 +
        (df['fraud_reported'] * 0.6) +
        np.random.uniform(0, 0.2, n_customers)  # Add random noise
    )
    
    # Ensure risk score is properly scaled
    df['risk_score'] = (df['risk_score'] - df['risk_score'].min()) / (
        df['risk_score'].max() - df['risk_score'].min()
    )
    
    # Create segments ensuring even distribution
    df['customer_segment'] = pd.qcut(
        df['risk_score'], 
        q=4, 
        labels=CUSTOMER_SEGMENTS
    )
    
    # Additional features using predefined constants
    df['policy_type'] = np.random.choice(
        POLICY_TYPES,
        n_customers, 
        p=[0.3, 0.4, 0.2, 0.1]
    )
    
    df['region'] = np.random.choice(
        REGIONS,
        n_customers
    )
    
    df['payment_method'] = np.random.choice(
        PAYMENT_METHODS,
        n_customers, 
        p=[0.5, 0.3, 0.2]
    )
    
    df['policy_status'] = np.random.choice(
        POLICY_STATUS,
        n_customers, 
        p=[0.7, 0.1, 0.15, 0.05]
    )
    
    # Add customer tenure (in years)
    df['customer_tenure'] = np.random.exponential(3, n_customers).round(1)
    
    # Add number of previous claims
    df['previous_claims'] = np.random.poisson(1, n_customers)
    
    return df

def generate_time_metrics(df):
    """Generate time-based metrics."""
    time_metrics = df.groupby(df['policy_date'].dt.to_period('M')).agg({
        'annual_premium': 'sum',
        'claim_amount': 'sum',
        'fraud_reported': 'sum',
        'customer_id': 'count'
    }).round(2)
    
    time_metrics.columns = ['monthly_premium', 'monthly_claims',
                          'monthly_fraud_cases', 'new_policies']
    return time_metrics

def generate_customer_metrics(df):
    """Generate customer segment metrics."""
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
    
    # Calculate additional metrics
    customer_metrics['loss_ratio'] = (customer_metrics['total_claims'] / 
                                    customer_metrics['total_premium']).round(4)
    customer_metrics['profit'] = (customer_metrics['total_premium'] - 
                                customer_metrics['total_claims']).round(2)
    
    # Reset index to ensure customer_segment is a column
    customer_metrics = customer_metrics.reset_index()
    return customer_metrics

def generate_region_metrics(df):
    """Generate region-based metrics."""
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
    
    # Calculate additional metrics
    region_metrics['loss_ratio'] = (region_metrics['total_claims'] / 
                                  region_metrics['total_premium']).round(4)
    region_metrics['profit'] = (region_metrics['total_premium'] - 
                              region_metrics['total_claims']).round(2)
    
    # Reset index to ensure region is a column
    region_metrics = region_metrics.reset_index()
    return region_metrics

def main():
    """Generate and save all datasets for Power BI."""
    print("Generating insurance data for Power BI...")
    
    # Generate main dataset
    df = generate_customer_data()
    
    # Generate derived datasets
    time_metrics = generate_time_metrics(df)
    customer_metrics = generate_customer_metrics(df)
    region_metrics = generate_region_metrics(df)
    
    # Create directories if they don't exist
    import os
    os.makedirs('data/processed', exist_ok=True)
    
    # Save datasets
    print("\nSaving datasets...")
    df.to_csv('data/processed/insurance_data.csv', index=False)
    time_metrics.to_csv('data/processed/time_metrics.csv')
    customer_metrics.to_csv('data/processed/customer_metrics.csv', index=False)
    region_metrics.to_csv('data/processed/region_metrics.csv', index=False)
    
    print("\nDatasets generated and saved:")
    print("1. insurance_data.csv - Main dataset")
    print("2. time_metrics.csv - Time-based metrics")
    print("3. customer_metrics.csv - Customer segment metrics")
    print("4. region_metrics.csv - Regional metrics")
    
    # Print some basic statistics
    print("\nBasic Statistics:")
    print(f"Total Customers: {len(df):,}")
    print(f"Total Premium: ${df['annual_premium'].sum():,.2f}")
    print(f"Total Claims: ${df['claim_amount'].sum():,.2f}")
    print(f"Overall Fraud Rate: {(df['fraud_reported'].mean() * 100):.2f}%")
    print(f"Customer Segment Distribution:\n{df['customer_segment'].value_counts(normalize=True).round(3) * 100}%")

if __name__ == "__main__":
    main() 