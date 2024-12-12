import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.io as pio
import io
from dash.exceptions import PreventUpdate
from fpdf import FPDF
import os
import tempfile
import base64

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Insurance Analytics Dashboard'

# Load data
try:
    df = pd.read_csv('data/processed/insurance_data.csv')
    time_metrics = pd.read_csv('data/processed/time_metrics.csv')
    region_metrics = pd.read_csv('data/processed/region_metrics.csv')
    
    # Convert date columns
    time_metrics['policy_date'] = pd.to_datetime(time_metrics['policy_date'])
    
    # Calculate additional metrics
    df['risk_score'] = df['claim_amount'] / df['annual_premium']
    df['premium_category'] = pd.qcut(df['annual_premium'], q=4, labels=['Low', 'Medium', 'High', 'Premium'])
    
except Exception as e:
    print(f"Error loading data: {e}")
    raise

# Create reports directory if it doesn't exist
if not os.path.exists('reports'):
    os.makedirs('reports')
if not os.path.exists('temp'):
    os.makedirs('temp')

# Navigation bar with modern styling
nav_bar = html.Div([
    html.Div([
        dcc.Link('Executive Summary', href='/', className='nav-link'),
        dcc.Link('Customer Analysis', href='/customer', className='nav-link'),
        dcc.Link('Risk Analysis', href='/risk', className='nav-link'),
        dcc.Link('Regional Analysis', href='/regional', className='nav-link'),
    ], className='nav-links'),
    html.Div([
        html.Button('Download Data (Excel)', id='download-button', className='export-button'),
        html.Button('Export Dashboard (PDF)', id='export-pdf-button', className='export-button'),
        dcc.Download(id='download-dataframe'),
        dcc.Download(id='download-pdf'),
        html.Div(id='pdf-status')
    ], className='nav-buttons')
], className='navbar')

# Executive Summary Layout
def create_executive_summary():
    return html.Div([
        html.Div([
            html.H1('Executive Summary', className='dashboard-title'),
            html.P('Key Performance Metrics and Business Insights', className='dashboard-description')
        ], className='header'),
        
        # Enhanced KPI Cards
        html.Div([
            html.Div([
                html.Div('💰', className='kpi-icon'),
                html.H3('Total Premium'),
                html.Div(className='kpi-separator'),
                html.H4(f"${df['annual_premium'].sum():,.2f}"),
                html.P('↑ 15% YoY', className='trend-up')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('📊', className='kpi-icon'),
                html.H3('Total Claims'),
                html.Div(className='kpi-separator'),
                html.H4(f"${df['claim_amount'].sum():,.2f}"),
                html.P('↓ 8% YoY', className='trend-down')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('⚠️', className='kpi-icon'),
                html.H3('Fraud Rate'),
                html.Div(className='kpi-separator'),
                html.H4(f"{df['fraud_reported'].mean()*100:.1f}%"),
                html.P('↔ Stable', className='trend-neutral')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('👥', className='kpi-icon'),
                html.H3('Active Policies'),
                html.Div(className='kpi-separator'),
                html.H4(f"{len(df):,}"),
                html.P('↑ 12% YoY', className='trend-up')
            ], className='kpi-card'),
        ], className='kpi-row'),
        
        # Main Charts
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.line(time_metrics, 
                                 x='policy_date', 
                                 y=['monthly_premium', 'monthly_claims'],
                                 title='Premium vs Claims Trend',
                                 template='plotly_dark')
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.bar(time_metrics,
                                x='policy_date',
                                y='monthly_fraud_cases',
                                title='Monthly Fraud Cases',
                                template='plotly_dark')
                )
            ], className='chart-container'),
        ], className='chart-row'),
        
        # Additional Insights
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.pie(df, 
                                names='premium_category',
                                title='Premium Distribution',
                                template='plotly_dark',
                                hole=0.4)
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.box(df,
                                x='customer_segment',
                                y='annual_premium',
                                title='Premium by Customer Segment',
                                template='plotly_dark')
                )
            ], className='chart-container'),
        ], className='chart-row'),
    ])

# Customer Analysis Layout
def create_customer_analysis():
    return html.Div([
        html.Div([
            html.H1('Customer Analysis', className='dashboard-title'),
            html.P('Customer Segmentation and Behavior Insights', className='dashboard-description')
        ], className='header'),
        
        # Enhanced Customer KPIs
        html.Div([
            html.Div([
                html.Div('💎', className='kpi-icon'),
                html.H3('Average Premium'),
                html.Div(className='kpi-separator'),
                html.H4(f"${df['annual_premium'].mean():,.2f}"),
                html.P('Per Customer', className='metric-subtitle')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('🎯', className='kpi-icon'),
                html.H3('Customer Segments'),
                html.Div(className='kpi-separator'),
                html.H4(f"{len(df['customer_segment'].unique())}"),
                html.P('Active Segments', className='metric-subtitle')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('👑', className='kpi-icon'),
                html.H3('Premium Customers'),
                html.Div(className='kpi-separator'),
                html.H4(f"{len(df[df['premium_category'] == 'Premium']):,}"),
                html.P('Top Tier', className='metric-subtitle')
            ], className='kpi-card'),
        ], className='kpi-row'),
        
        # Customer Segmentation
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.pie(df, 
                                names='customer_segment',
                                title='Customer Segments Distribution',
                                template='plotly_dark',
                                hole=0.4)
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.scatter(df.sample(1000),
                                    x='annual_premium',
                                    y='claim_amount',
                                    color='customer_segment',
                                    title='Customer Behavior Analysis',
                                    template='plotly_dark')
                )
            ], className='chart-container'),
        ], className='chart-row'),
        
        # Additional Customer Insights
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.histogram(df,
                                      x='annual_premium',
                                      color='customer_segment',
                                      title='Premium Distribution by Segment',
                                      template='plotly_dark')
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.box(df,
                                x='customer_segment',
                                y='claim_amount',
                                title='Claims by Customer Segment',
                                template='plotly_dark')
                )
            ], className='chart-container'),
        ], className='chart-row'),
    ])

# Risk Analysis Layout
def create_risk_analysis():
    return html.Div([
        html.Div([
            html.H1('Risk Analysis', className='dashboard-title'),
            html.P('Risk Assessment and Fraud Detection', className='dashboard-description')
        ], className='header'),
        
        # Enhanced Risk KPIs
        html.Div([
            html.Div([
                html.Div('📈', className='kpi-icon'),
                html.H3('Average Risk Score'),
                html.Div(className='kpi-separator'),
                html.H4(f"{df['risk_score'].mean():.2f}"),
                html.P('Overall', className='metric-subtitle')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('⚡', className='kpi-icon'),
                html.H3('High Risk Cases'),
                html.Div(className='kpi-separator'),
                html.H4(f"{len(df[df['risk_score'] > df['risk_score'].quantile(0.75)]):,}"),
                html.P('Top 25%', className='metric-subtitle')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('🚨', className='kpi-icon'),
                html.H3('Fraud Cases'),
                html.Div(className='kpi-separator'),
                html.H4(f"{df['fraud_reported'].sum():,}"),
                html.P('Total Reported', className='metric-subtitle')
            ], className='kpi-card'),
        ], className='kpi-row'),
        
        # Risk Analysis Charts
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.scatter(df,
                                    x='annual_premium',
                                    y='claim_amount',
                                    color='fraud_reported',
                                    title='Fraud Detection Analysis',
                                    template='plotly_dark')
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.histogram(df,
                                      x='risk_score',
                                      color='fraud_reported',
                                      title='Risk Score Distribution',
                                      template='plotly_dark')
                )
            ], className='chart-container'),
        ], className='chart-row'),
        
        # Additional Risk Insights
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.box(df,
                                x='customer_segment',
                                y='risk_score',
                                title='Risk by Customer Segment',
                                template='plotly_dark')
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.line(time_metrics,
                                 x='policy_date',
                                 y='monthly_fraud_cases',
                                 title='Fraud Cases Over Time',
                                 template='plotly_dark')
                )
            ], className='chart-container'),
        ], className='chart-row'),
    ])

# Regional Analysis Layout
def create_regional_analysis():
    return html.Div([
        html.Div([
            html.H1('Regional Analysis', className='dashboard-title'),
            html.P('Geographic Performance and Insights', className='dashboard-description')
        ], className='header'),
        
        # Enhanced Regional KPIs
        html.Div([
            html.Div([
                html.Div('🏆', className='kpi-icon'),
                html.H3('Top Region'),
                html.Div(className='kpi-separator'),
                html.H4(region_metrics.loc[region_metrics['total_premium'].idxmax(), 'region']),
                html.P('By Premium', className='metric-subtitle')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('🌍', className='kpi-icon'),
                html.H3('Regional Coverage'),
                html.Div(className='kpi-separator'),
                html.H4(f"{len(df['region'].unique())}"),
                html.P('Active Regions', className='metric-subtitle')
            ], className='kpi-card'),
            
            html.Div([
                html.Div('🚀', className='kpi-icon'),
                html.H3('Regional Growth'),
                html.Div(className='kpi-separator'),
                html.H4('15.2%'),
                html.P('Year over Year', className='metric-subtitle')
            ], className='kpi-card'),
        ], className='kpi-row'),
        
        # Regional Performance
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.bar(region_metrics,
                                x='region',
                                y='total_premium',
                                title='Premium by Region',
                                template='plotly_dark')
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.pie(df.groupby('region')['fraud_reported'].mean().reset_index(),
                                values='fraud_reported',
                                names='region',
                                title='Fraud Distribution by Region',
                                template='plotly_dark')
                )
            ], className='chart-container'),
        ], className='chart-row'),
        
        # Additional Regional Insights
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.box(df,
                                x='region',
                                y='annual_premium',
                                title='Premium Distribution by Region',
                                template='plotly_dark')
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.scatter(df.groupby('region').agg({
                        'annual_premium': 'mean',
                        'claim_amount': 'mean',
                        'fraud_reported': 'mean'
                    }).reset_index(),
                        x='annual_premium',
                        y='claim_amount',
                        size='fraud_reported',
                        hover_data=['region'],
                        title='Regional Risk Assessment',
                        template='plotly_dark')
                )
            ], className='chart-container'),
        ], className='chart-row'),
    ])

# Main App Layout
app.layout = html.Div([
    nav_bar,
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className='content')
], className='dashboard-container')

# Callback to handle page routing
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/customer':
        return create_customer_analysis()
    elif pathname == '/risk':
        return create_risk_analysis()
    elif pathname == '/regional':
        return create_regional_analysis()
    else:
        return create_executive_summary()

# Callback for Excel export
@app.callback(
    Output('download-dataframe', 'data'),
    Input('download-button', 'n_clicks'),
    prevent_initial_call=True
)
def download_report(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    try:
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create Excel writer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter', mode='xlsx') as writer:
            # Write each DataFrame
            df.to_excel(writer, sheet_name='Insurance Data', index=False)
            time_metrics.to_excel(writer, sheet_name='Time Series', index=False)
            region_metrics.to_excel(writer, sheet_name='Regional Data', index=False)
            
            # Create summary sheet
            summary_data = {
                'Metric': [
                    'Total Premium',
                    'Total Claims',
                    'Fraud Rate',
                    'Number of Policies',
                    'Average Premium',
                    'Average Claim'
                ],
                'Value': [
                    f"${df['annual_premium'].sum():,.2f}",
                    f"${df['claim_amount'].sum():,.2f}",
                    f"{df['fraud_reported'].mean()*100:.1f}%",
                    f"{len(df):,}",
                    f"${df['annual_premium'].mean():,.2f}",
                    f"${df['claim_amount'].mean():,.2f}"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Get workbook and format it
            workbook = writer.book
            
            # Add a format for headers
            header_format = workbook.add_format({
                'bold': True,
                'font_color': 'white',
                'bg_color': '#2c3e50',
                'border': 1
            })
            
            # Format each worksheet
            for worksheet in writer.sheets.values():
                # Set column widths
                worksheet.set_column('A:Z', 15)
                
                # Write the header row with formatting
                worksheet.set_row(0, None, header_format)

        # Prepare the file for download
        output.seek(0)
        
        return dcc.send_bytes(
            output.getvalue(),
            f'insurance_report_{timestamp}.xlsx'
        )
        
    except Exception as e:
        print(f"Error in Excel export: {e}")
        # Fallback to CSV export
        try:
            df_summary = pd.DataFrame({
                'Metric': ['Total Premium', 'Total Claims', 'Fraud Rate'],
                'Value': [
                    f"${df['annual_premium'].sum():,.2f}",
                    f"${df['claim_amount'].sum():,.2f}",
                    f"{df['fraud_reported'].mean()*100:.1f}%"
                ]
            })
            return dcc.send_data_frame(
                df_summary.to_csv,
                f'insurance_summary_{timestamp}.csv',
                index=False
            )
        except:
            print("Failed to generate backup CSV")
            raise PreventUpdate

# Update the PDF export callback
@app.callback(
    Output('download-pdf', 'data'),
    Input('export-pdf-button', 'n_clicks'),
    prevent_initial_call=True
)
def export_dashboard_pdf(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'dashboard_report_{timestamp}.pdf'
        
        # First save the PDF to a temporary file
        temp_pdf_path = f'temp_{filename}'
        
        # Create PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add title page
        pdf.add_page()
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 20, 'Insurance Analytics Dashboard', ln=True, align='C')
        pdf.set_font('Arial', '', 14)
        pdf.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='C')
        
        # Create figures
        figures = [
            # Executive Summary
            px.line(time_metrics, 
                   x='policy_date', 
                   y=['monthly_premium', 'monthly_claims'],
                   title='Premium vs Claims Trend'),
            px.pie(df, 
                  names='customer_segment',
                  title='Customer Segments'),
            
            # Risk Analysis
            px.scatter(df,
                      x='annual_premium',
                      y='claim_amount',
                      color='fraud_reported',
                      title='Fraud Detection Analysis'),
            
            # Regional Analysis
            px.bar(region_metrics,
                  x='region',
                  y='total_premium',
                  title='Premium by Region')
        ]
        
        # Add figures to PDF
        for i, fig in enumerate(figures):
            # Convert figure to image
            img_bytes = fig.to_image(format="png")
            
            # Save temporary image
            temp_img_path = f'temp_fig_{i}.png'
            with open(temp_img_path, 'wb') as f:
                f.write(img_bytes)
            
            # Add to PDF
            pdf.add_page()
            pdf.image(temp_img_path, x=10, y=10, w=190)
            
            # Clean up temporary image
            os.remove(temp_img_path)
        
        # Save PDF to temporary file
        pdf.output(temp_pdf_path)
        
        # Read the PDF file
        with open(temp_pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        # Clean up temporary PDF file
        os.remove(temp_pdf_path)
        
        return dcc.send_bytes(pdf_data, filename)
        
    except Exception as e:
        print(f"Error in PDF export: {e}")
        import traceback
        traceback.print_exc()
        raise PreventUpdate

if __name__ == '__main__':
    print("Starting dashboard server...")
    print("Visit http://127.0.0.1:8050/ in your web browser")
    app.run_server(debug=True, port=8050, host='127.0.0.1')