"""
Prepare and export data for Power BI dashboard.
This script processes the insurance data and creates necessary derived datasets for the dashboard.
"""

import pandas as pd
import numpy as np
from insurance_analysis import InsuranceAnalysis

def prepare_customer_metrics(df):
    """Prepare customer-related metrics for the dashboard."""
    customer_metrics = df.groupby('customer_segment').agg({
        'age': ['mean', 'min', 'max', 'count'],
        'annual_premium': ['mean', 'sum'],
        'claim_amount': ['mean', 'sum'],
        'fraud_reported': 'mean'
    }).round(2)
    
    customer_metrics.columns = [
        'avg_age', 'min_age', 'max_age', 'customer_count',
        'avg_premium', 'total_premium',
        'avg_claim', 'total_claims',
        'fraud_rate'
    ]
    
    # Calculate profitability metrics
    customer_metrics['profit'] = (
        customer_metrics['total_premium'] - customer_metrics['total_claims']
    )
    customer_metrics['loss_ratio'] = (
        customer_metrics['total_claims'] / customer_metrics['total_premium']
    ).round(4)
    
    return customer_metrics

def prepare_fraud_metrics(df):
    """Prepare fraud-related metrics for the dashboard."""
    fraud_metrics = df[df['fraud_reported'] == 1].groupby('customer_segment').agg({
        'claim_amount': ['count', 'mean', 'sum'],
        'annual_premium': ['mean', 'sum']
    }).round(2)
    
    fraud_metrics.columns = [
        'fraud_cases', 'avg_fraudulent_claim', 'total_fraudulent_claims',
        'avg_premium_fraud_cases', 'total_premium_fraud_cases'
    ]
    
    return fraud_metrics

def prepare_time_series(df):
    """Prepare time-based metrics for the dashboard."""
    # Assuming we have date columns in the dataset
    # If not, we'll create synthetic dates for demonstration
    if 'policy_date' not in df.columns:
        df['policy_date'] = pd.date_range(
            start='2022-01-01',
            periods=len(df),
            freq='D'
        )
    
    time_metrics = df.groupby(df['policy_date'].dt.to_period('M')).agg({
        'annual_premium': 'sum',
        'claim_amount': 'sum',
        'fraud_reported': 'sum',
        'customer_id': 'count'
    }).round(2)
    
    time_metrics.columns = [
        'monthly_premium',
        'monthly_claims',
        'monthly_fraud_cases',
        'new_policies'
    ]
    
    return time_metrics

def main():
    """Main function to prepare and export dashboard data."""
    # Initialize analysis
    analysis = InsuranceAnalysis('data/raw/Synthetic_Insurance_Data_Realistic_20000.csv')
    
    # Load and process data
    df = analysis.load_data()
    df_cleaned = analysis.clean_data()
    analysis.segment_customers()  # This adds customer_segment column
    
    # Prepare different metric datasets
    customer_metrics = prepare_customer_metrics(df_cleaned)
    fraud_metrics = prepare_fraud_metrics(df_cleaned)
    time_metrics = prepare_time_series(df_cleaned)
    
    # Export processed datasets
    print("Exporting processed datasets for Power BI...")
    
    # Main cleaned dataset
    df_cleaned.to_csv('data/processed/cleaned_insurance_data.csv', index=False)
    
    # Derived metrics datasets
    customer_metrics.to_csv('data/processed/customer_metrics.csv')
    fraud_metrics.to_csv('data/processed/fraud_metrics.csv')
    time_metrics.to_csv('data/processed/time_metrics.csv')
    
    print("Data export completed. Files ready for Power BI import.")
    print("\nExported files:")
    print("1. cleaned_insurance_data.csv - Main dataset")
    print("2. customer_metrics.csv - Customer segment metrics")
    print("3. fraud_metrics.csv - Fraud analysis metrics")
    print("4. time_metrics.csv - Time-based metrics")

if __name__ == "__main__":
    main() 