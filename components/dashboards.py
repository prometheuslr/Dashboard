from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import calendar
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
from globals import *
from app import appe
from dash_bootstrap_templates import template_from_url, ThemeChangerAIO

card_icon = {
    "colo": "white",
    "textAling": "center",
    "fontSize": 30,
    "margin": "auto",
}

graph_margin = dict(l=50, r=50, t=50, b=0)


# Obter data atual
today = datetime.today().date()

# Obter o primeiro dia do mês atual
first_day_current_month = datetime(today.year, today.month, 1).date()

# Calcular o primeiro dia do próximo mês
next_month = today.month + 1 if today.month < 12 else 1
next_month_year = today.year if today.month < 12 else today.year + 1
first_day_next_month = datetime(next_month_year, next_month, 1).date()

# ========= Layout =========== #

layout = dbc.Col([
    dbc.Row([
        # Saldo total
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Saldo'),
                    html.H5('R$ 5400', id='p-saldo-dashboards', style={})
                ], style={"padding-left": "20px", "padding-top": "10px"}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon),
                    color="warning",
                    style={"maxWidth": 75, "height": 97, "margin-left": "-10px"}
                )
            ])
        ], width=4),

        # Receita
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Receita'),
                    html.H5('R$ 10000', id='p-receita-dashboards', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-smile-o', style=card_icon),
                    color="success",
                    style={'maxWidth': 75, 'height': 97, 'margin-left': '-10px'}
                )
            ])
        ], width=4),

        # Despesa
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Despesa'),
                    html.H5('R$ 4600', id='p-despesa-dashboards', style={})
                ], style={"padding-left": "20px", "padding-top": "10px"}),
                dbc.Card(
                    html.Div(className='fa fa-meh-o', style=card_icon),
                    color="danger",
                    style={'maxWidth': 75, 'height': 97, 'margin-left': '-10px'}
                )
            ])
        ], width=4)
    ], style={'margin': '10px'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Legend("Filtra lançamentos", className="card-title"),
                html.Label("Categoria das receitas"),
                html.Div(
                    dcc.Dropdown(
                        id="dropdown-receitas",
                        clearable=False,
                        style={"width": "100%"},
                        persistence=True,
                        persistence_type="session",
                        multi=True
                    )
                ),

                html.Label("Categorias das despesas", style={"margin-top": "10px"}),
                dcc.Dropdown(
                    id="dropdown-despesa",
                    clearable=False,
                    style={"width": "100%"},
                    persistence=True,
                    persistence_type="session",
                    multi=True
                ),

                html.Legend("Período de Análise", style={"margin-top": "10px"}),
                dcc.DatePickerRange(
                month_format='Do MMM, YY',
                end_date_placeholder_text="Data....",
                start_date=first_day_current_month,
                end_date=first_day_next_month,
                updatemode='singledate',
                id="date-picker-config",
                style={'z-index': '100'}
            )
            ], style={'height': '100%', 'padding': '25px'})
        ], width=4, style={'padding-left': '-10px'}),

        dbc.Col(
            dbc.Card(dcc.Graph(id='graph1'), style={'padding': '10px', 'height': '100%'}), width=8
        )
    ], style={'margin': '10px', 'height': '100%'}),

    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='graph2'), style={'padding': '10px'}), width=6),
        dbc.Col(dbc.Card(dcc.Graph(id='graph3'), style={'padding': '10px'}), width=3),
        dbc.Col(dbc.Card(dcc.Graph(id='graph4'), style={'padding': '10px'}), width=3),
    ])
])

# ========= Callbacks =========== #

@appe.callback(
    [
        Output("dropdown-receitas", "options"),
        Output("dropdown-receitas", "value"),
        Output("p-receita-dashboards", "children")
    ],
    Input("store-receitas", "data")
)
def populate_dropdownvalues(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()
    return ([{"label": x, "value": x} for x in val], val, f"R$ {valor}")


@appe.callback(
    [
        Output("dropdown-despesa", "options"),
        Output("dropdown-despesa", "value"),
        Output("p-despesa-dashboards", "children")
    ],
    Input("store-despesas", "data")
)
def populate_dropdownvalues_despesa(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()
    return ([{"label": x, "value": x} for x in val], val, f"R$ {valor}")


@appe.callback(
    Output("p-saldo-dashboards", "children"),
    [Input("store-despesas", "data"),
     Input("store-receitas", "data")]
)
def saldo_total(despesas, receitas):
    df_despesas = pd.DataFrame(despesas)
    df_receitas = pd.DataFrame(receitas)
    valor = df_receitas['Valor'].sum() - df_despesas['Valor'].sum()
    return f"R$ {valor}"


@appe.callback(
    Output('graph1', 'figure'),
    [Input('store-despesas', 'data'),
    Input('store-receitas', 'data'),
    Input("dropdown-despesa", "value"),
    Input("dropdown-receitas", "value"),
   ])
def update_output(data_despesa, data_receita, despesa, receita):
    df_ds = pd.DataFrame(data_despesa).sort_values(by='Data', ascending=True)
    df_rc = pd.DataFrame(data_receita).sort_values(by='Data', ascending=True)

    dfs = [df_ds, df_rc]
    for df in dfs:
        df['Acumulo'] = df['Valor'].cumsum()
        df["Data"] = pd.to_datetime(df["Data"])
        df["Mes"] = df["Data"].apply(lambda x: x.month)

    df_receitas_mes = df_rc.groupby("Mes")["Valor"].sum()
    df_despesas_mes = df_ds.groupby("Mes")["Valor"].sum()
    df_saldo_mes = df_receitas_mes - df_despesas_mes
    df_saldo_mes.to_frame()
    df_saldo_mes = df_saldo_mes.reset_index()
    df_saldo_mes['Acumulado'] = df_saldo_mes['Valor'].cumsum()
    df_saldo_mes['Mes'] = df['Mes'].apply(lambda x: calendar.month_abbr[x])

    df_ds = df_ds[df_ds['Categoria'].isin(despesa)]
    df_rc = df_rc[df_rc['Categoria'].isin(receita)]

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(name='Despesas', x=df_ds['Data'], y=df_ds['Acumulo'], fill='tonexty', mode='lines'))
    fig.add_trace(go.Scatter(name='Receitas', x=df_rc['Data'], y=df_rc['Acumulo'], fill='tonextx', mode='lines'))
    fig.add_trace(go.Scatter(name='Saldo Mensal', x=df_saldo_mes['Mes'], y=df_saldo_mes['Acumulado'], mode='lines'))

    fig.update_layout(margin=graph_margin)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig


@appe.callback(
    Output('graph2', 'figure'),
    [Input('store-receitas', 'data'),
     Input('store-despesas', 'data'),
     Input('dropdown-receitas', 'value'),
     Input('dropdown-despesa', 'value'),
     Input('date-picker-config', 'start_date'),
     Input('date-picker-config', 'end_date')]
)
def graph2_show(data_receita, data_despesa, receita, despesa, start_date, end_date):
    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)
    df_ds["Output"] = "Despesas"
    df_rc["Output"] = "Receitas"
    df_final = pd.concat([df_ds, df_rc])
    df_final["Data"] = pd.to_datetime(df_final["Data"])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_final = df_final[(df_final["Data"] >= start_date) & (df_final["Data"] <= end_date)]
    df_final = df_final[(df_final["Categoria"].isin(receita)) | (df_final["Categoria"].isin(despesa))]
    fig = px.bar(df_final, x="Data", y="Valor", color='Output', barmode='group')
    fig.update_traces(
        hovertemplate='Data: %{x}<br>Valor: R$ %{y:.2f}',
        marker=dict(line=dict(color='#ffffff', width=1))
    )
    fig.update_layout(
        margin=graph_margin,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='top', y=1.12, xanchor='center', x=0.5),
        xaxis=dict(tickformat="%b %Y")
    )
    return fig


@appe.callback(
    Output('graph3', "figure"),
    [Input('store-receitas', 'data'),
     Input('dropdown-receitas', 'value')]
)
def pie_receita(data_receita, receita):
    df = pd.DataFrame(data_receita)
    df = df[df['Categoria'].isin(receita)]
    fig = px.pie(df, values='Valor', names='Categoria', hole=0.2)
    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    fig.update_layout(
        title="Receitas",
        margin=graph_margin,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=-0.3)
    )
    return fig


@appe.callback(
    Output('graph4', "figure"),
    [Input('store-despesas', 'data'),
     Input('dropdown-despesa', 'value')]
)
def pie_despesa(data_despesa, despesa):
    df = pd.DataFrame(data_despesa)
    df = df[df['Categoria'].isin(despesa)]
    fig = px.pie(df, values='Valor', names='Categoria', hole=0.2)
    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    fig.update_layout(
        title="Despesas",
        margin=graph_margin,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=-0.3)
    )
    return fig
