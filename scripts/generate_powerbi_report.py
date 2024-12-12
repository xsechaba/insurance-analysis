"""
Generate Power BI report pages using the Power BI REST API.
This script creates a template report with all required pages and visualizations.
"""

import json
import os
from datetime import datetime

def create_report_template():
    """Create the basic report template structure."""
    template = {
        "version": "1.0",
        "type": "Report",
        "pages": []
    }
    
    # Load layout configuration
    with open('dashboard/layout.json', 'r') as f:
        layout = json.load(f)
    
    # Add pages from layout
    template["pages"] = layout["pages"]
    
    return template

def create_dataset_schema():
    """Create the dataset schema for Power BI."""
    schema = {
        "name": "InsuranceAnalytics",
        "tables": [
            {
                "name": "insurance_data",
                "columns": [
                    {"name": "customer_id", "dataType": "string"},
                    {"name": "age", "dataType": "int64"},
                    {"name": "annual_premium", "dataType": "double"},
                    {"name": "claim_amount", "dataType": "double"},
                    {"name": "fraud_reported", "dataType": "bool"},
                    {"name": "customer_segment", "dataType": "string"},
                    {"name": "policy_date", "dataType": "datetime"},
                    {"name": "policy_type", "dataType": "string"},
                    {"name": "region", "dataType": "string"},
                    {"name": "payment_method", "dataType": "string"},
                    {"name": "policy_status", "dataType": "string"},
                    {"name": "customer_tenure", "dataType": "double"},
                    {"name": "previous_claims", "dataType": "int64"}
                ]
            },
            {
                "name": "time_metrics",
                "columns": [
                    {"name": "period", "dataType": "datetime"},
                    {"name": "monthly_premium", "dataType": "double"},
                    {"name": "monthly_claims", "dataType": "double"},
                    {"name": "monthly_fraud_cases", "dataType": "int64"},
                    {"name": "new_policies", "dataType": "int64"}
                ]
            },
            {
                "name": "customer_metrics",
                "columns": [
                    {"name": "customer_segment", "dataType": "string"},
                    {"name": "avg_age", "dataType": "double"},
                    {"name": "min_age", "dataType": "int64"},
                    {"name": "max_age", "dataType": "int64"},
                    {"name": "customer_count", "dataType": "int64"},
                    {"name": "avg_premium", "dataType": "double"},
                    {"name": "total_premium", "dataType": "double"},
                    {"name": "avg_claim", "dataType": "double"},
                    {"name": "total_claims", "dataType": "double"},
                    {"name": "fraud_rate", "dataType": "double"},
                    {"name": "profit", "dataType": "double"},
                    {"name": "loss_ratio", "dataType": "double"}
                ]
            },
            {
                "name": "region_metrics",
                "columns": [
                    {"name": "region", "dataType": "string"},
                    {"name": "total_premium", "dataType": "double"},
                    {"name": "avg_premium", "dataType": "double"},
                    {"name": "total_claims", "dataType": "double"},
                    {"name": "avg_claim", "dataType": "double"},
                    {"name": "fraud_cases", "dataType": "int64"},
                    {"name": "fraud_rate", "dataType": "double"},
                    {"name": "customer_count", "dataType": "int64"},
                    {"name": "total_previous_claims", "dataType": "int64"},
                    {"name": "loss_ratio", "dataType": "double"},
                    {"name": "profit", "dataType": "double"}
                ]
            },
            {
                "name": "date_table",
                "columns": [
                    {"name": "Date", "dataType": "datetime"},
                    {"name": "Year", "dataType": "int64"},
                    {"name": "Month", "dataType": "int64"},
                    {"name": "MonthName", "dataType": "string"},
                    {"name": "Quarter", "dataType": "int64"},
                    {"name": "YearMonth", "dataType": "string"},
                    {"name": "WeekDay", "dataType": "string"},
                    {"name": "WeekDayNo", "dataType": "int64"},
                    {"name": "WeekNo", "dataType": "int64"},
                    {"name": "DayOfYear", "dataType": "int64"}
                ]
            }
        ],
        "relationships": [
            {
                "name": "insurance_to_customer",
                "fromTable": "insurance_data",
                "fromColumn": "customer_segment",
                "toTable": "customer_metrics",
                "toColumn": "customer_segment",
                "crossFilteringBehavior": "bothDirections"
            },
            {
                "name": "insurance_to_region",
                "fromTable": "insurance_data",
                "fromColumn": "region",
                "toTable": "region_metrics",
                "toColumn": "region",
                "crossFilteringBehavior": "bothDirections"
            },
            {
                "name": "insurance_to_date",
                "fromTable": "insurance_data",
                "fromColumn": "policy_date",
                "toTable": "date_table",
                "toColumn": "Date",
                "crossFilteringBehavior": "bothDirections"
            },
            {
                "name": "time_to_date",
                "fromTable": "time_metrics",
                "fromColumn": "period",
                "toTable": "date_table",
                "toColumn": "Date",
                "crossFilteringBehavior": "bothDirections"
            }
        ]
    }
    
    return schema

def create_report_config():
    """Create the complete report configuration."""
    config = {
        "report": create_report_template(),
        "dataset": create_dataset_schema(),
        "theme": None
    }
    
    # Load theme configuration
    with open('dashboard/theme.json', 'r') as f:
        config["theme"] = json.load(f)
    
    return config

def save_report_config():
    """Save the complete report configuration."""
    config = create_report_config()
    
    # Create output directory
    output_dir = 'data/processed/powerbi'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save configurations
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with open(f'{output_dir}/report_config_{timestamp}.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nReport configuration saved to: report_config_{timestamp}.json")
    print("\nConfiguration includes:")
    print(f"- {len(config['report']['pages'])} pages")
    print(f"- {len(config['dataset']['tables'])} tables")
    print(f"- {len(config['dataset']['relationships'])} relationships")
    print("\nReady for Power BI import.")

def main():
    """Main function to generate report configuration."""
    print("Generating Power BI report configuration...")
    save_report_config()

if __name__ == "__main__":
    main() 