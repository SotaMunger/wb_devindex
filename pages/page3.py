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

# define connection variable
conn = psycopg2.connect(database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)

# define cursor variable
cur = conn.cursor()

# define function to create pandas table from sql query
def create_pandas_table(sql_query, database = conn):
    table = pd.read_sql_query(sql_query, database)
    return table

# pull date range from expense postgres relation and convert column headings from 'yr2020'
# string format to 2020 int format
years = ['yr' + str(yr) for yr in range(2020,2025)]
yr_string = ', '.join(i for i in years)

dates = create_pandas_table("SELECT {yrs} FROM gdp_growth_constant limit 0".format(yrs = yr_string))
old_cols = dates.columns
new_cols = [i for i in range(2020,2025)]
col_dict = dict(zip(old_cols, new_cols))
dates.rename(mapper = col_dict, axis = 1, inplace=True)

# create dicts for pulldown menus - "label": text displayed in menu, "value": table name, "title": hover text
income_dict = [
    {
        "label": "World",
        "value": "World",
        "title": "World"
    },
    {
        "label": "Low Income",
        "value": "Low income",
        "title": "GNI per capita below $1,086"
    },
    {
        "label": "Lower Middle Income",
        "value": "Lower middle income",
        "title": "GNI per capita between $1,086 and $4,255"
    },
    {
        "label": "Upper Middle Income",
        "value": "Upper middle income",
        "title": "GNI per capita between $4,256 and $13,025"
    },
    {
        "label": "High Income",
        "value": "High income",
        "title": "GNI per capita above $13,025"
    },
    {
        "label": "Uncategorized",
        "value": "Uncategorized",
        "title": "Venezuela"
    }
]

indicator_dict = [
    {
        "label": "GDP Projections",
        "value": "gdp_growth_constant",
        "title": "GDP Projections (% Shift in GDP over Previous Year)"
    }
]

# Define the page layout
layout = html.Div(
    [
        dbc.Row(
            [
                # side bar
                dbc.Col(
                    [
                        # header
                        html.H2(
                            children = 'Projected GDP Growth',
                            style = {'textAlign': 'center', 'color': '#FFFFFF', 'margin': '10px'}
                        ),
                        html.Br(),
                        # globe image
                        html.Img(
                            src = "assets/globe1.png",
                            width = 240,
                            className = "globe",
                        ),
                        html.Br(),
                        # indicator dropdown text description
                        html.Label(
                            children = "Import Type", 
                            className = "menu-title"
                        ),
                        # indicator dropdown
                        dcc.Dropdown(
                            indicator_dict,
                            id = "indicator_dropdown",
                            value = "gdp_growth_constant",
                            className = 'dropdown',
                            clearable=False
                        ),
                        html.Br(),
                        # income dropdown text description
                        html.Label(
                            children = "Income Group", 
                            className = "menu-title"
                        ),
                        # indicator dropdown
                        dcc.Dropdown(
                            income_dict,
                            id = "income_dropdown",
                            value = "World",
                            className = 'dropdown',
                            clearable=False
                        ),
                        html.Br(),
                        # year slider bar text description
                        html.Div(
                            children = "Year", 
                            className = "menu-title"
                        ),    
                        # year slider
                        dcc.Slider(
                            min = dates.columns.min(),
                            max = dates.columns.max(),
                            step = 1,
                            value=dates.columns.min(),
                            marks = {2020: '2020', 
                                    2021: '2021',
                                    2022: '2022',
                                    2023: '2023', 
                                    2024: '2024'
                            },
                            #tooltip property shows value on hover
                            tooltip={"placement": "bottom"},
                            id='year_slider',
                        )     
                    ], id='left-container',
                ),
                # main body
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                html.Div(
                                    children = [
                                        # line graph
                                        dcc.Graph(
                                            id='gdp_line',
                                            config = {'displayModeBar': False},
                                        )
                                    ], id = 'line-graph',
                                )
                            ], id = 'line'
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Row([
                                        html.Div(
                                            # choropleth container
                                            [
                                                # choropleth
                                                dcc.Graph(
                                                    id='gdp_choropleth',
                                                    className = 'choropleth',
                                                    config = {"displayModeBar": False},
                                                )
                                            ], id = 'choro',
                                        ), 
                                        html.Div(
                                            # violin plot container
                                            [
                                                # violin plot
                                                dcc.Graph(
                                                    id='gdp_histogram',
                                                    className = 'violin',
                                                    config = {"displayModeBar": False},
                                                )
                                            ], id = "vio",
                                        ),
                                    ])
                                )
                            ], id = 'non-temporal_graphs'
                        ),
                    ], id = 'right-container'
                )
            ], 
        )
    ]
)

# define callbacks - inputs include indicator, income group, and year
@callback(
    Output('gdp_choropleth', 'figure'),
    Output('gdp_histogram', 'figure'),
    Output('gdp_line', 'figure'),
    Input('indicator_dropdown', 'value'),
    Input('income_dropdown', 'value'),
    Input('year_slider', 'value'))
def update_figure(indicator, income, year):

    # pull data from postgres database into pandas df according to pulldown selections
    df = create_pandas_table("SELECT country_code, income_group, country_name, {yrs} FROM {table}".format(yrs = yr_string, table = indicator))
    # convert year columns from format 'yr2020' string format to 2020 int format
    old_cols = df.columns[3:]
    new_cols = [i for i in range(2020,2025)]
    col_dict = dict(zip(old_cols, new_cols))
    df.rename(mapper = col_dict, axis = 1, inplace=True)
    # df_no_uc leaves out countries not categorized into an income group (improves violin plot visualization)
    df_no_uc = df.loc[df['income_group'] != "Uncategorized"]

    # declare income group lists
    li = df['country_code'].loc[df['income_group'] == "Low income"]
    lmi = df['country_code'].loc[df['income_group'] == "Lower middle income"]
    umi = df['country_code'].loc[df['income_group'] == "Upper middle income"]
    hi = df['country_code'].loc[df['income_group'] == "High income"]
    uc = df['country_code'].loc[df['income_group'] == "Uncategorized"]

    # filter df by income group list if that income group is selected in the income pulldown menu
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

    # declare variable representing the full country name
    percent = filtered_df['country_name']

    # calculate the yearly median for each income group
    df_med_per_year = df_no_uc.groupby('income_group').median('numeric_only').transpose()

    # define graph structures
    # fig1 = choropleth
    fig1 = go.Figure(
        data = [
            go.Choropleth(
                # locations represent countries in selected income group
                locations = locations,
                # z is the indicator value for each country in the selected year
                z = filtered_df[year],
            )
        ]    
    )        
    # update_layout sets graph size, font size, background color, etc.
    fig1.update_layout(
        # paper_bgcolor is the color of the background behind the plots
        paper_bgcolor = '#BAD0E3', 
        font_size = 14,
        # plot bg_color is the color of the background behind the text, legend, etc.
        plot_bgcolor = '#E8EFF6',
        legend_title = "<b>Income Groups</b>",
        height = 400,
        title_text = "Percentage GDP Growth by Country"
    )
    # update_traces sets plot element colors, colorbar title, hover text template
    fig1.update_traces(
        colorscale = 'sunsetdark',
        colorbar_title_text = "<b>% GDP<br>Growth</b>",
        hovertemplate = ('%{z:.2f}% <extra>%{text}</extra>'), text = percent,
    )

    # fig2 = violin plot
    fig2 = px.violin(
        filtered_df_no_uc,
        # x-axis is value of indicator
        x = year,
        # y-axis is the income group
        y = 'income_group',
        color = 'income_group',
        # define colors for each income group
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
        # create variable to hold country name
        custom_data = ['country_name'],
    )
    # update_layout sets graph size, font size, background color, etc.
    fig2.update_layout(
        paper_bgcolor = '#BAD0E3', 
        font_size = 14,
        plot_bgcolor='#E8EFF6',
        legend_title = "<b>Income Groups</b>",
        height = 400,
        title_text = "Percentage GDP Growth Distributions"
    )
    # update_xaxes removes the vertical gridlines and sets the title
    fig2.update_xaxes(
        showgrid = False, 
        zeroline = False,
        title = "Percentage GDP Growth"
    )
    # update_yaxes removes the y-axis ticks
    fig2.update_yaxes(
        showticklabels = False,
        title = None,
    )
    # update_traces sets plots to show all country points, creates custom
    # hovertext appearance, and sets jitter (vertical dispersion of points)
    fig2.update_traces(
        points = "all",
        hovertemplate = "%{x:.2f}%<extra>%{customdata[0]}</extra>",
        hoveron = "points + kde",
        box_visible = True,
        jitter = 0.5
    )
    # fig3 = line graph
    fig3 = px.line(
        df_med_per_year,
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
    )
    # update_layout sets graph size, font size, background color, etc.
    fig3.update_layout(
        paper_bgcolor = '#BAD0E3', 
        font_size = 14,
        plot_bgcolor='#E8EFF6',
        legend_title = "<b>Income Groups</b>",
        title_text = "Projected Year Over Year GDP Percentage Growth"
    )
    # update_xaxes removes the vertical gridlines and sets the title
    fig3.update_xaxes(
        showgrid = False, 
        zeroline = False,
        title = "Year",
        tickvals = ["2020", "2021", "2022", "2023", "2024"]
    )
    # update_xaxes removes the horizontal gridlines and sets the title
    fig3.update_yaxes(
        showgrid = False,
        zeroline = False,
        title = "Median Percentage GDP Growth",
    )
    # update-traces sets custom hovertext
    fig3.update_traces(
        hovertemplate = ('GDP Growth: %{y}%'),
    )

    return fig1, fig2, fig3

    