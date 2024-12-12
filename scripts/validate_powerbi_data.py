"""
Validate the generated data for Power BI dashboard.
This script checks data quality, relationships, and completeness.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def validate_file_existence():
    """Check if all required files exist."""
    required_files = [
        'data/processed/insurance_data.csv',
        'data/processed/time_metrics.csv',
        'data/processed/customer_metrics.csv',
        'data/processed/region_metrics.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def validate_insurance_data(df):
    """Validate main insurance dataset."""
    checks = {
        'null_check': df.isnull().sum().sum() == 0,
        'customer_id_unique': df['customer_id'].nunique() == len(df),
        'premium_positive': (df['annual_premium'] >= 0).all(),
        'claim_amount_valid': (df['claim_amount'] >= 0).all(),
        'age_valid': df['age'].between(18, 85).all(),
        'fraud_binary': df['fraud_reported'].isin([0, 1]).all(),
        'segments_valid': df['customer_segment'].isin(['Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk']).all(),
        'policy_types_valid': df['policy_type'].isin(['Basic', 'Standard', 'Premium', 'Elite']).all(),
        'regions_valid': df['region'].isin(['North', 'South', 'East', 'West', 'Central']).all()
    }
    return checks

def validate_time_metrics(df):
    """Validate time-based metrics."""
    checks = {
        'null_check': df.isnull().sum().sum() == 0,
        'premium_positive': (df['monthly_premium'] >= 0).all(),
        'claims_positive': (df['monthly_claims'] >= 0).all(),
        'fraud_cases_positive': (df['monthly_fraud_cases'] >= 0).all(),
        'new_policies_positive': (df['new_policies'] >= 0).all()
    }
    return checks

def validate_customer_metrics(df):
    """Validate customer segment metrics."""
    checks = {
        'null_check': df.isnull().sum().sum() == 0,
        'segments_present': len(df.index) == 4,  # Should have 4 segments
        'metrics_positive': all(
            df[['avg_premium', 'total_premium', 'avg_claim', 'total_claims']].ge(0).all()
        ),
        'customer_counts_match': df['customer_count'].sum() == 20000  # Total customers
    }
    return checks

def validate_region_metrics(df):
    """Validate region-based metrics."""
    checks = {
        'null_check': df.isnull().sum().sum() == 0,
        'regions_present': len(df.index) == 5,  # Should have 5 regions
        'metrics_positive': all(
            df[['total_premium', 'total_claims', 'customer_count']].ge(0).all()
        ),
        'customer_counts_match': df['customer_count'].sum() == 20000  # Total customers
    }
    return checks

def validate_relationships():
    """Validate relationships between datasets."""
    try:
        # Load all datasets
        insurance_data = pd.read_csv('data/processed/insurance_data.csv')
        customer_metrics = pd.read_csv('data/processed/customer_metrics.csv')
        region_metrics = pd.read_csv('data/processed/region_metrics.csv')
        
        # Check relationships
        checks = {
            'customer_segments_match': set(insurance_data['customer_segment'].unique()) == \
                                     set(customer_metrics.index),
            'regions_match': set(insurance_data['region'].unique()) == \
                           set(region_metrics.index),
            'customer_totals_match': len(insurance_data) == 20000,
            'segment_totals_match': customer_metrics['customer_count'].sum() == 20000,
            'region_totals_match': region_metrics['customer_count'].sum() == 20000
        }
        return checks
    except Exception as e:
        return {'error': str(e)}

def print_validation_results(results, section):
    """Print validation results in a formatted way."""
    print(f"\n{section} Validation Results:")
    print("-" * 50)
    for check, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {check.replace('_', ' ').title()}")

def main():
    """Run all validations."""
    print("Starting Power BI Data Validation...")
    
    # Check file existence
    files_exist, missing_files = validate_file_existence()
    if not files_exist:
        print("\nError: Missing required files:")
        for file in missing_files:
            print(f"- {file}")
        return
    
    try:
        # Load and validate main dataset
        insurance_data = pd.read_csv('data/processed/insurance_data.csv')
        print_validation_results(
            validate_insurance_data(insurance_data),
            "Insurance Data"
        )
        
        # Load and validate time metrics
        time_metrics = pd.read_csv('data/processed/time_metrics.csv')
        print_validation_results(
            validate_time_metrics(time_metrics),
            "Time Metrics"
        )
        
        # Load and validate customer metrics
        customer_metrics = pd.read_csv('data/processed/customer_metrics.csv')
        print_validation_results(
            validate_customer_metrics(customer_metrics),
            "Customer Metrics"
        )
        
        # Load and validate region metrics
        region_metrics = pd.read_csv('data/processed/region_metrics.csv')
        print_validation_results(
            validate_region_metrics(region_metrics),
            "Region Metrics"
        )
        
        # Validate relationships
        print_validation_results(
            validate_relationships(),
            "Data Relationships"
        )
        
        # Print summary statistics
        print("\nSummary Statistics:")
        print("-" * 50)
        print(f"Total Customers: {len(insurance_data):,}")
        print(f"Total Premium: ${insurance_data['annual_premium'].sum():,.2f}")
        print(f"Total Claims: ${insurance_data['claim_amount'].sum():,.2f}")
        print(f"Overall Fraud Rate: {(insurance_data['fraud_reported'].mean() * 100):.2f}%")
        print("\nCustomer Segments Distribution:")
        print(insurance_data['customer_segment'].value_counts(normalize=True).round(3) * 100)
        
    except Exception as e:
        print(f"\nError during validation: {str(e)}")

if __name__ == "__main__":
    main() 