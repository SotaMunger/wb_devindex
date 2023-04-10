from dash import dcc, html
import dash_bootstrap_components as dbc

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Row([
                                        html.Div(
                                            # map image container
                                            [
                                                html.Img(
                                                    src = "assets/income-map.png",
                                                    height = 650,
                                                    className = "main_img",
                                                ),
                                                html.Br(),
                                                html.P("Reference: https://datatopics.worldbank.org/sdgatlas/archive/2017/the-world-by-income.html")
                                            ], id = 'main_map',
                                        ), 
                                        html.Div(
                                            # text container
                                            [
                                                # text box
                                                html.Div(
                                                    children =[
                                                        html.P(
                                                        "The data avaiable for exploration in this dashboard was taken from the World \
                                                        Bank World Development Index and Global Economic Prospects data sets (https://databank.worldbank.org/home).\
                                                        It consists of international inflation, imports, and wealth indicators that contrast the often precarious\
                                                        economic conditions of low income countries against the more stable conditions of \
                                                        wealthier countries in the years 2001 - 2020. The dashboard is loosely inspired by the Brookings Institute article \
                                                        'Food insecurity and economic misery in low-income countries' \
                                                        (https://www.brookings.edu/blog/future-development/2022/07/01/food-insecurity-and-economic-misery-in-low-income-countries/).\
                                                        However, since the raw data used in that study was unavailable, the data from the World Bank databank \
                                                        was used as a substitute (although the time spans studied are different, the indicators are similar). \
                                                        Please choose a link from the drop down menu to explore the data."
                                                        ),
                                                        html.Br()
                                                    ], id = "text_box",
                                                ),
                                            ], id = "main_text",
                                        ),
                                    ])
                                )
                            ], id = 'main_body'
                        ),
                    ], id = 'main_box'
                )
            ]
        )
    ]
)