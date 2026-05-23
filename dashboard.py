import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Load datasets
df_india = pd.read_csv('data/ev_market_data_500.csv')
df_global = pd.read_csv('data/global_ev_market_data_500.csv')

app = dash.Dash(__name__)

# IMPORTANT: This line is required for Render.com
server = app.server

app.layout = html.Div([
    html.H1("Global & India EV Market Analysis", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # 1. Market Selection (Tabs)
    dcc.Tabs(id='market-tabs', value='india', children=[
        dcc.Tab(label='India Market', value='india'),
        dcc.Tab(label='Global Market', value='global'),
    ]),
    
    # 2. Filters
    html.Div([
        html.Div([
            html.Label("Select Category:"),
            dcc.Dropdown(id='category-dropdown')
        ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Select Vehicle Model:"),
            dcc.Dropdown(id='model-dropdown')
        ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'})
    ]),
    
    # 3. KPI Cards Area
    html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}),
    
    # 4. Main Chart
    dcc.Graph(id='main-graph')
])

# --- Callbacks ---

@app.callback(
    [Output('category-dropdown', 'options'), Output('model-dropdown', 'options')],
    [Input('market-tabs', 'value')]
)
def update_filters(market):
    df = df_india if market == 'india' else df_global
    cat_opts = [{'label': i, 'value': i} for i in df['Category'].unique()]
    model_opts = [{'label': i, 'value': i} for i in df['Model'].unique()]
    return cat_opts, model_opts

@app.callback(
    [Output('main-graph', 'figure'), Output('kpi-cards', 'children')],
    [Input('market-tabs', 'value'), Input('category-dropdown', 'value'), Input('model-dropdown', 'value')]
)
def update_dashboard(market, category, model):
    df = df_india if market == 'india' else df_global
    
    # Default filter logic
    if not category: category = df['Category'].unique()[0]
    if not model: model = df[df['Category'] == category]['Model'].unique()[0]
    
    filtered_df = df[(df['Category'] == category) & (df['Model'] == model)]
    price_col = 'Price_Lakhs' if market == 'india' else 'Price_USD_k'
    
    # Chart
    fig = px.line(filtered_df, x='Year', y=price_col, title=f"Trend: {model} ({market.upper()})", markers=True)
    
    # KPI Cards
    kpi = [
        html.Div([html.H4("Category"), html.P(category)], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '10px'}),
        html.Div([html.H4("Avg Price"), html.P(f"{filtered_df[price_col].mean():.2f}")], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '10px'}),
        html.Div([html.H4("Max Speed"), html.P(f"{filtered_df['Max_Speed_kmh'].max()} km/h")], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '10px'})
    ]
    return fig, kpi

if __name__ == '__main__':
    app.run(debug=True)