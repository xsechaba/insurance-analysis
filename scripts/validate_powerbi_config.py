"""
Validate Power BI report configuration and data model.
"""

import json
import os
import pandas as pd
from datetime import datetime

def load_config():
    """Load the latest Power BI report configuration."""
    config_dir = 'data/processed/powerbi'
    config_files = [f for f in os.listdir(config_dir) if f.startswith('report_config_')]
    latest_config = sorted(config_files)[-1]
    
    with open(f'{config_dir}/{latest_config}', 'r') as f:
        config = json.load(f)
    
    return config

def validate_theme(theme):
    """Validate theme configuration."""
    print("\nValidating theme configuration...")
    
    required_keys = ['name', 'dataColors', 'background', 'foreground', 'tableAccent']
    missing_keys = [key for key in required_keys if key not in theme]
    
    if missing_keys:
        print("Missing required theme keys:", missing_keys)
        return False
    
    if 'visualStyles' not in theme:
        print("Missing visualStyles configuration")
        return False
    
    print("Theme configuration valid")
    return True

def validate_layout(layout):
    """Validate layout configuration."""
    print("\nValidating layout configuration...")
    
    if 'pages' not in layout:
        print("Missing pages configuration")
        return False
    
    required_page_keys = ['name', 'displayName', 'visualContainers']
    for page in layout['pages']:
        missing_keys = [key for key in required_page_keys if key not in page]
        if missing_keys:
            print(f"Page {page.get('name', 'Unknown')} missing keys:", missing_keys)
            return False
        
        for visual in page['visualContainers']:
            if not all(key in visual for key in ['x', 'y', 'width', 'height', 'visual', 'title']):
                print(f"Invalid visual configuration in page {page['name']}")
                return False
    
    print("Layout configuration valid")
    return True

def validate_data_model(model):
    """Validate data model configuration."""
    print("\nValidating data model configuration...")
    
    if 'tables' not in model:
        print("Missing tables configuration")
        return False
    
    if 'relationships' not in model:
        print("Missing relationships configuration")
        return False
    
    # Validate tables
    table_names = set()
    for table in model['tables']:
        if 'name' not in table or 'columns' not in table:
            print(f"Invalid table configuration: {table.get('name', 'Unknown')}")
            return False
        table_names.add(table['name'])
    
    # Validate relationships
    for rel in model['relationships']:
        if not all(key in rel for key in ['name', 'fromTable', 'fromColumn', 'toTable', 'toColumn']):
            print(f"Invalid relationship configuration: {rel.get('name', 'Unknown')}")
            return False
        
        if rel['fromTable'] not in table_names or rel['toTable'] not in table_names:
            print(f"Relationship references non-existent table: {rel['name']}")
            return False
    
    print("Data model configuration valid")
    return True

def validate_measures(measures_file):
    """Validate DAX measures."""
    print("\nValidating DAX measures...")
    
    try:
        with open(measures_file, 'r') as f:
            measures = f.read()
        
        # Basic syntax validation
        lines = measures.split('\n')
        errors = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('//'):
                if '=' not in line and not line.endswith(','):
                    errors.append(f"Line {i}: {line}")
        
        if errors:
            print("Potential DAX syntax issues found:")
            for error in errors[:5]:  # Show only first 5 errors
                print(error)
            if len(errors) > 5:
                print(f"...and {len(errors) - 5} more issues")
        
        print("DAX measures validation completed")
        return True
    except Exception as e:
        print(f"Error validating measures: {str(e)}")
        return False

def validate_data_files():
    """Validate required data files."""
    print("\nValidating data files...")
    
    required_files = [
        'insurance_data.csv',
        'time_metrics.csv',
        'customer_metrics.csv',
        'region_metrics.csv',
        'date_table.csv'
    ]
    
    data_dir = 'data/processed/powerbi'
    missing_files = []
    
    for file in required_files:
        file_path = f'{data_dir}/{file}'
        if not os.path.exists(file_path):
            missing_files.append(file)
            continue
        
        # Validate file contents
        try:
            df = pd.read_csv(file_path)
            print(f"\n{file} statistics:")
            print(f"Rows: {len(df):,}")
            print(f"Columns: {len(df.columns):,}")
            print("Column names:", ", ".join(df.columns))
            
            # Check for missing values
            missing = df.isnull().sum()
            if missing.any():
                print("\nMissing values found:")
                for col, count in missing[missing > 0].items():
                    print(f"{col}: {count:,} missing values")
        except Exception as e:
            print(f"Error reading {file}: {str(e)}")
            return False
    
    if missing_files:
        print("Missing required files:", missing_files)
        return False
    
    print("\nAll required data files present and valid")
    return True

def generate_validation_report(results):
    """Generate validation report."""
    report = []
    report.append("Power BI Configuration Validation Report")
    report.append("=====================================")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for component, status in results.items():
        report.append(f"\n{component}:")
        report.append("Status: " + ("PASS" if status else "FAIL"))
    
    report_path = 'data/processed/powerbi/validation_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print("\nValidation report saved to:", report_path)
    print('\n'.join(report))

def main():
    """Validate Power BI configuration and data model."""
    print("Starting Power BI configuration validation...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Validate components
        results = {
            'Theme': validate_theme(config['theme']),
            'Layout': validate_layout(config['report']),
            'Data Model': validate_data_model(config['dataset']),
            'DAX Measures': validate_measures('dashboard/measures.dax'),
            'Data Files': validate_data_files()
        }
        
        # Generate report
        generate_validation_report(results)
        
        # Overall validation result
        if all(results.values()):
            print("\nValidation successful: All components are valid")
            return True
        else:
            print("\nValidation failed: Some components are invalid")
            return False
    
    except Exception as e:
        print(f"Error during validation: {str(e)}")
        return False

if __name__ == "__main__":
    main() 