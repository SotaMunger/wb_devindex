# Import necessary libraries 
from dash import html, dcc
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app, server

# Connect to your app pages
from pages import home, page1, page2

# Connect the navbar to the index
from components import navbar

import dash_bootstrap_components as dbc

# define the navbar
# nav = navbar.Navbar()

nav = dbc.NavbarSimple(
    children = [
        dbc.DropdownMenu(
            children = [
                dbc.DropdownMenuItem("Home", href = "http://wb-devindex.onrender.com"),
                dbc.DropdownMenuItem("Inflation", href = "http://wb-devindex.onrender.com/inflation"),
                dbc.DropdownMenuItem("Imports", href = "http://wb-devindex.onrender.com/imports")
            ],
            nav=True,
            in_navbar = True,
            label = "Page",
        ),
    ],
    brand="Economics of International Food Insecurity",
    brand_href = "#",
    color = "#A3B6C7",
    dark = True,
)

# Define the index page layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav, 
    html.Div(id='page-content', children=[]), 
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/inflation':
        return page1.layout
    if pathname == '/imports':
        return page2.layout
    else:
        return home.layout

# Run the app on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=True)
