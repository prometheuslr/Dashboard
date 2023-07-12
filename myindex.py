from dash import html, dcc
import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from components import sidebar, extratos, dashboards,receitas
from app import *
from globals import *
import pdb


# =========  Layout  =========== #
#md = 2 a coluna ira ocupar 2 espaçoes de 12
content = html.Div(id="page-content")

appe.layout = dbc.Container(
    children=[
        dcc.Store(id="store-receitas", data=df_receitas.to_dict()),
        dcc.Store(id="store-despesas", data=df_despesas.to_dict()),
        dcc.Store(id="store-cat-receita", data=df_cat_receita.to_dict()),
        dcc.Store(id="store-cat-despesa", data=df_cat_despesa.to_dict()),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Location(id="url"),
                        sidebar.layout,
                    ],
                    md=2,
                    
                ),
                dbc.Col(
                    [
                        content,
                    ],
                    md=10,
                    
                ),
            ]
        )
    ],
    fluid=True,
)


@appe.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page(pathname):
    if pathname == "/" or pathname == "/dashboards":
        return dashboards.layout

    if pathname == "/extratos":
        return extratos.layout

    if pathname == "/receitas":
        return receitas.layout

if __name__ == "__main__":
    appe.run_server(debug=True)