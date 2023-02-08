from dash import dcc, html

layout = html.Div(
    children = [
        html.H1(
            children = [
                "The data explored in this dashboard was taken from the World" \
                "Bank development index.", html.Br(), "This dashboard is intended as an effort " \
                "to further elucidate the findings in a Brookings Institute Article. \n"  
                "Please choose a link from the drop down menu to explore the data."
            ],
        ),
        html.Div(
            children =[
                "Please Choose a link from the drop down menu"
            ],
        ),
    ]    
)