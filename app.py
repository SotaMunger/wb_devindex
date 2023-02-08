from dash import Dash, dcc, html, Input, Output, callback
# from pages import page1, page2

import dash
import dash_bootstrap_components as dbc

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, 
                # external_stylesheets = external_stylesheets,
                external_stylesheets=[dbc.themes.MORPH], 
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True)
app.title = "Economics of International Food Insecurity"

server = app.server
