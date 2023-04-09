import dash
import dash_bootstrap_components as dbc

# reference font style and css file
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

# define app
app = dash.Dash(__name__,
                # define style of navbar
                external_stylesheets=[dbc.themes.MORPH], 
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True)
app.title = "Economics of International Food Insecurity"

server = app.server
