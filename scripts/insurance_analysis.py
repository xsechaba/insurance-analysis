"""
Insurance Analytics Dashboard Project
===================================

This script performs comprehensive analysis of insurance data, including data cleaning,
exploratory data analysis, customer segmentation, and fraud detection.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from datetime import datetime, timedelta

# Set style for better visualizations
plt.style.use('default')
sns.set_theme(style="whitegrid")
sns.set_palette("husl")
pd.set_option('display.max_columns', None)

class InsuranceAnalysis:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.df_cleaned = None
        self.customer_segments = None
    
    def load_data(self):
        print("Loading and examining the dataset...")
        self.df = pd.read_csv(self.data_path)
        
        # Convert date columns to datetime
        if 'policy_date' in self.df.columns:
            self.df['policy_date'] = pd.to_datetime(self.df['policy_date'])
        
        # Display basic information
        print("\nDataset Info:")
        print("-" * 50)
        self.df.info()
        
        print("\nFirst few rows:")
        print("-" * 50)
        print(self.df.head())
        
        return self.df
    
    def clean_data(self):
        print("Cleaning the dataset...")
        self.df_cleaned = self.df.copy()
        
        # Clean dates if they exist
        if 'policy_date' in self.df_cleaned.columns:
            current_date = pd.Timestamp.now()
            max_future_date = current_date + pd.DateOffset(years=2)
            
            # Fix future dates
            future_mask = self.df_cleaned['policy_date'] > max_future_date
            if future_mask.any():
                print(f"Found {future_mask.sum()} unrealistic future dates")
                self.df_cleaned.loc[future_mask, 'policy_date'] = max_future_date
            
            # Fix past dates
            past_mask = self.df_cleaned['policy_date'] < pd.Timestamp('2000-01-01')
            if past_mask.any():
                print(f"Found {past_mask.sum()} unrealistic past dates")
                self.df_cleaned.loc[past_mask, 'policy_date'] = pd.Timestamp('2000-01-01')
        
        # Handle missing values
        missing_values = self.df_cleaned.isnull().sum()
        if missing_values.any():
            print("\nMissing Values:")
            print("-" * 50)
            print(missing_values[missing_values > 0])
        
        # Handle outliers for numeric columns
        numeric_columns = self.df_cleaned.select_dtypes(include=[np.number]).columns
        for column in numeric_columns:
            Q1 = self.df_cleaned[column].quantile(0.25)
            Q3 = self.df_cleaned[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Replace outliers with bounds
            self.df_cleaned[column] = self.df_cleaned[column].clip(lower_bound, upper_bound)
        
        return self.df_cleaned
    
    def perform_eda(self):
        print("Performing Exploratory Data Analysis...")
        
        # Time series analysis if date column exists
        if 'policy_date' in self.df_cleaned.columns:
            plt.figure(figsize=(12, 6))
            self.df_cleaned.set_index('policy_date')['monthly_premium'].plot()
            plt.title('Monthly Premium Trends Over Time')
            plt.xlabel('Date')
            plt.ylabel('Monthly Premium')
            plt.show()
            
            # Plot monthly claims
            plt.figure(figsize=(12, 6))
            self.df_cleaned.set_index('policy_date')['monthly_claims'].plot()
            plt.title('Monthly Claims Trends Over Time')
            plt.xlabel('Date')
            plt.ylabel('Monthly Claims')
            plt.show()
            
            # Plot fraud cases
            plt.figure(figsize=(12, 6))
            self.df_cleaned.set_index('policy_date')['monthly_fraud_cases'].plot()
            plt.title('Monthly Fraud Cases Over Time')
            plt.xlabel('Date')
            plt.ylabel('Number of Fraud Cases')
            plt.show()
            
            # Plot new policies
            plt.figure(figsize=(12, 6))
            self.df_cleaned.set_index('policy_date')['new_policies'].plot()
            plt.title('New Policies Over Time')
            plt.xlabel('Date')
            plt.ylabel('Number of New Policies')
            plt.show()
        
        # Distribution of numeric variables
        numeric_cols = self.df_cleaned.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            plt.figure(figsize=(10, 6))
            sns.histplot(data=self.df_cleaned, x=col, bins=30, kde=True)
            plt.title(f'Distribution of {col}')
            plt.show()
        
        # Correlation heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(self.df_cleaned.select_dtypes(include=[np.number]).corr(), 
                   annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Matrix of Numerical Variables')
        plt.show()
    
    def generate_report(self):
        print("Generating analysis report...")
        
        report = {
            'total_policies': len(self.df_cleaned),
            'date_range': f"{self.df_cleaned['policy_date'].min()} to {self.df_cleaned['policy_date'].max()}",
            'total_monthly_premium': self.df_cleaned['monthly_premium'].sum(),
            'average_monthly_premium': self.df_cleaned['monthly_premium'].mean(),
            'total_monthly_claims': self.df_cleaned['monthly_claims'].sum(),
            'average_monthly_claims': self.df_cleaned['monthly_claims'].mean(),
            'total_fraud_cases': self.df_cleaned['monthly_fraud_cases'].sum(),
            'total_new_policies': self.df_cleaned['new_policies'].sum()
        }
        
        return report

def main():
    # Initialize analysis
    analysis = InsuranceAnalysis('data/processed/time_metrics.csv')
    
    # Execute analysis pipeline
    analysis.load_data()
    analysis.clean_data()
    analysis.perform_eda()
    
    # Save cleaned data
    analysis.df_cleaned.to_csv('data/processed/cleaned_time_metrics.csv', index=False)
    
    # Generate and print report
    report = analysis.generate_report()
    print("\nAnalysis Report:")
    print("-" * 50)
    for key, value in report.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 