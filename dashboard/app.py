import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the data
df = pd.read_csv('../data/processed/time_metrics.csv')
df['policy_date'] = pd.to_datetime(df['policy_date'])

# Define the layout
app.layout = html.Div([
    html.H1('Insurance Analytics Dashboard'),
    
    # Time range selector
    dcc.DatePickerRange(
        id='date-range',
        min_date_allowed=df['policy_date'].min(),
        max_date_allowed=df['policy_date'].max(),
        start_date=df['policy_date'].min(),
        end_date=df['policy_date'].max()
    ),
    
    # KPI Cards
    html.Div([
        html.Div([
            html.H4('Total Premium'),
            html.H2(id='total-premium')
        ], className='kpi-card'),
        html.Div([
            html.H4('Total Claims'),
            html.H2(id='total-claims')
        ], className='kpi-card'),
        html.Div([
            html.H4('Fraud Cases'),
            html.H2(id='fraud-cases')
        ], className='kpi-card'),
        html.Div([
            html.H4('New Policies'),
            html.H2(id='new-policies')
        ], className='kpi-card')
    ], className='kpi-container'),
    
    # Graphs
    html.Div([
        dcc.Graph(id='premium-trend'),
        dcc.Graph(id='claims-trend'),
        dcc.Graph(id='fraud-trend'),
        dcc.Graph(id='policies-trend')
    ])
])

# Callbacks
@app.callback(
    [Output('total-premium', 'children'),
     Output('total-claims', 'children'),
     Output('fraud-cases', 'children'),
     Output('new-policies', 'children'),
     Output('premium-trend', 'figure'),
     Output('claims-trend', 'figure'),
     Output('fraud-trend', 'figure'),
     Output('policies-trend', 'figure')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_dashboard(start_date, end_date):
    # Filter data based on date range
    mask = (df['policy_date'] >= start_date) & (df['policy_date'] <= end_date)
    filtered_df = df.loc[mask]
    
    # Calculate KPIs
    total_premium = f"${filtered_df['monthly_premium'].sum():,.2f}"
    total_claims = f"${filtered_df['monthly_claims'].sum():,.2f}"
    fraud_cases = f"{filtered_df['monthly_fraud_cases'].sum():,}"
    new_policies = f"{filtered_df['new_policies'].sum():,}"
    
    # Create figures
    premium_fig = px.line(filtered_df, x='policy_date', y='monthly_premium',
                         title='Monthly Premium Trends')
    claims_fig = px.line(filtered_df, x='policy_date', y='monthly_claims',
                        title='Monthly Claims Trends')
    fraud_fig = px.line(filtered_df, x='policy_date', y='monthly_fraud_cases',
                       title='Monthly Fraud Cases')
    policies_fig = px.line(filtered_df, x='policy_date', y='new_policies',
                          title='New Policies Over Time')
    
    return (total_premium, total_claims, fraud_cases, new_policies,
            premium_fig, claims_fig, fraud_fig, policies_fig)

if __name__ == '__main__':
    app.run_server(debug=True) 