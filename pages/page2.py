# import packages
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from dash import dash
import plotly.graph_objs as go
import plotly.express as px
import psycopg2
import os
import pandas as pd
import numpy as np

# create database connection
DB_NAME = os.environ.get('DBNM')
DB_USER = os.environ.get('DBUS')
DB_PASS = os.environ.get('DBPS')
DB_HOST = os.environ.get('DBHS')
DB_PORT = os.environ.get('DBPT')

conn = psycopg2.connect(database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)
cur = conn.cursor()

def create_pandas_table(sql_query, database = conn):
    table = pd.read_sql_query(sql_query, database)
    return table

# pull date range from expense postgres relation and convert column headings from 'yr2001'
# string format to 2001 int format - consider local method also maybe write as function
years = ['yr' + str(yr) for yr in range(2001,2021)]
yr_string = ', '.join(i for i in years)

dates = create_pandas_table("SELECT {yrs} FROM expense limit 0".format(yrs = yr_string))
old_cols = dates.columns
new_cols = [i for i in range(2001,2021)]
col_dict = dict(zip(old_cols, new_cols))
dates.rename(mapper = col_dict, axis = 1, inplace=True)

# create dicts for pulldown menus - {psql categories: pull down display categories}
income_dict = {"World": "World", "Low income": "Low Income", "Lower middle income": "Lower Middle Income", \
    "Upper middle income": "Upper Middle Income", "High income": "High Income", "Uncategorized": "Uncategorized"}

indicator_dict ={"agricultural_raw_materials_imports": "Raw Agricultural Imports", "food_imports": "Food Imports",
                "fuel_imports": "Fuel Imports", "ores_and_metals_imports": "Ores and Metals Imports"}

# Define the page layout

layout = html.Div(children = [

    # Imports income group
    html.Div(
        children = [
            html.Div(
                children = [
                    html.Div(
                        children = "Import Type (as % of Total Merchandise)", 
                        className = "menu-title"),
                    dcc.Dropdown(
                        indicator_dict,
                        id = "indicator_dropdown",
                        value = "agricultural_raw_materials_imports"
                            ),
                ],
                style=dict(width='50%')
            ),
            html.Div(
                children = [
                    html.Div(
                        children = "Income Group", 
                        className = "menu-title"
                    ),
                    dcc.Dropdown(
                        income_dict,
                        id = "income_dropdown",
                        value = "World",
                    ),
                ],
                style=dict(width='50%')
            ),
        ],
        style=dict(display='flex')
    ),
    # Imports Year
    html.Div(
        children = [
            html.Div(
                children = "Year", 
                className = "menu-title"),    
            dcc.Slider(
                dates.columns.min(),
                dates.columns.max(),
                step=None,
                value=dates.columns.min(),
                marks={str(int(i)): str(int(i)) for i in dates.columns},
                id='year_slider',
            )
        ]
    ),
    html.Div(
        children = [
            html.H2(
                children = 'Yearly Percentage of Merchandise Value Imported',
                style = {
                    'textAlign': 'center',
                    'color': '#A3B6C7',
                    'margin': '10px'
                }
            )
        ]
    ),
    html.Div(
        children = [
            dcc.Graph(
                id='imports_choropleth2',
                config = {"displayModeBar": False},
                style = {'display': 'inline-block', 'padding': '5px'},
            ),
            dcc.Graph(
                id='imports_histogram2',
                config = {"displayModeBar": False},
                style = {'display': 'inline-block', 'padding': '5px'},
            )
        ]
    )    
])

# define callbacks - inputs include indicator, income group, and year
@callback(
    Output('imports_choropleth2', 'figure'),
    Output('imports_histogram2', 'figure'),
    Input('indicator_dropdown', 'value'),
    Input('income_dropdown', 'value'),
    Input('year_slider', 'value'))
def update_figure(indicator, income, year):

    # pull data from postgres database according to pulldown selections into pandas df
    df = create_pandas_table("SELECT country_code, income_group, country_name, {yrs} FROM {table}".format(yrs = yr_string, table = indicator))
    # convert year columns from format 'yr2001' string format to 2001 int format
    old_cols = df.columns[3:]
    new_cols = [i for i in range(2001,2021)]
    col_dict = dict(zip(old_cols, new_cols))
    df.rename(mapper = col_dict, axis = 1, inplace=True)
    df_no_uc = df.loc[df['income_group'] != "Uncategorized"]

    # declare income group lists
    li = df['country_code'].loc[df['income_group'] == "Low income"]
    lmi = df['country_code'].loc[df['income_group'] == "Lower middle income"]
    umi = df['country_code'].loc[df['income_group'] == "Upper middle income"]
    hi = df['country_code'].loc[df['income_group'] == "High income"]
    uc = df['country_code'].loc[df['income_group'] == "Uncategorized"]

    # filter df by income groups
    if income == "World":
        filtered_df = df.loc[:,['country_name', 'country_code', 'income_group', year]]
        filtered_df_no_uc = df_no_uc.loc[:,['country_name', 'country_code', 'income_group', year]]
        locations = filtered_df['country_code']
    elif income == 'Low income':
        filtered_df = df.loc[df['country_code'].isin(li), ['country_name', 'country_code', 'income_group', year]]
        filtered_df_no_uc = df_no_uc.loc[df['country_code'].isin(li), ['country_name', 'country_code', 'income_group', year]]
        locations = filtered_df['country_code']
    elif income == 'Lower middle income':
        filtered_df = df.loc[df['country_code'].isin(lmi), ['country_name', 'country_code', 'income_group', year]]
        filtered_df_no_uc = df_no_uc.loc[df['country_code'].isin(lmi), ['country_name', 'country_code', 'income_group', year]]
        locations = filtered_df['country_code']
    elif income == 'Upper middle income':
        filtered_df = df.loc[df['country_code'].isin(umi), ['country_name', 'country_code', 'income_group', year]]
        filtered_df_no_uc = df_no_uc.loc[df['country_code'].isin(umi), ['country_name', 'country_code', 'income_group', year]]
        locations = filtered_df['country_code']
    elif income == 'High income':
        filtered_df = df.loc[df['country_code'].isin(hi), ['country_name', 'country_code', 'income_group', year]]
        filtered_df_no_uc = df_no_uc.loc[df['country_code'].isin(hi), ['country_name', 'country_code', 'income_group', year]]
        locations = filtered_df['country_code']
    else:
        filtered_df = df.loc[df['country_code'].isin(uc), ['country_name', 'country_code', 'income_group', year]]
        filtered_df_no_uc = df.loc[df['country_code'].isin(uc), ['country_name', 'country_code', 'income_group', year]]
        locations = filtered_df['country_code']

    filtered_median = np.median(filtered_df[year].loc[filtered_df[year].notna()])
    filtered_mean = np.mean(filtered_df[year].loc[filtered_df[year].notna()])
    percent = filtered_df['country_name']
    # define graph structures

    fig1 = go.Figure(
        data = [
            go.Choropleth(
                locations = locations,
                z = filtered_df[year],
            )
        ]    
    )        
    fig1.update_layout(
        paper_bgcolor = '#BAD0E3', 
        font_size = 14,
        plot_bgcolor='#E8EFF6',
        legend_title = "<b>Income Groups</b>", 
        width = 910,
        height = 500,
    )
    fig1.update_traces(
        colorscale = 'sunsetdark',
        hovertemplate = ('%{z:.2f}% <extra>%{text}</extra>'), text = percent,
    )
    fig2 = px.violin(
        filtered_df_no_uc,
        x = year,
        y = 'income_group',
        color = 'income_group',
        color_discrete_map = {
            'Low income': '#001D9B',
            'Lower middle income': '#31009B',
            'Upper middle income': '#7E009B',
            'High income': '#9B006B',
        },
        category_orders = {
            "income_group": [
                "Low income", "Lower middle income",
                "Upper middle income", "High income",
            ],
        },
        custom_data = ['country_name'],
    )
    fig2.update_layout(
        paper_bgcolor = '#BAD0E3', 
        font_size = 14,
        plot_bgcolor='#E8EFF6',
        legend_title = "<b>Income Groups</b>",
        width = 910,
        height = 500
    )
    fig2.update_xaxes(
        showgrid = False, 
        zeroline = False,
        title = "Percentage of Total Cost of Imports"
    )
    fig2.update_yaxes(
        showticklabels = False,
        title = None,
    )
    fig2.update_traces(
        points = "all",
        hovertext = "x",
        hovertemplate = "%{x:.2f}%<extra>%{customdata[0]}</extra>",
        marker_outliercolor = 'black',
        hoveron = "points + kde",
        box_visible = True,   
    )

    return fig1, fig2
