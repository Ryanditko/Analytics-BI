import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime, timedelta
import pandas as pd
import requests

# Removendo a importação direta do GenesysService, pois agora o Dash consome a API FastAPI
# from app.services.genesys.client import GenesysService

app = dash.Dash(__name__)

# URL da API FastAPI
API_URL = "http://127.0.0.1:8000"

def fetch_dashboard_data(start_date, end_date, queues, channels):
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "queue_ids": queues if queues else [],
        "channel_types": channels if channels else []
    }
    response = requests.get(f"{API_URL}/dashboard/overview", params=params)
    response.raise_for_status() # Lança exceção para erros HTTP
    return response.json()

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard Genesys Cloud - Tela Inicial"),
    
    # Filtros
    html.Div([
        html.Div([
            html.Label("Período"),
            dcc.DatePickerRange(
                id='date-range',
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now()
            )
        ], style={'marginRight': '20px'}),
        html.Div([
            html.Label("Fila"),
            dcc.Dropdown(
                id='queue-filter',
                options=[
                    {'label': 'WhatsApp Gestão da Entrega', 'value': 'whatsapp_entrega'},
                    {'label': 'WhatsApp Marketplace', 'value': 'whatsapp_marketplace'},
                    {'label': 'CALM WhatsApp', 'value': 'calm_whatsapp'},
                    {'label': 'FILA_CALM', 'value': 'FILA_CALM'},
                    {'label': 'FILA_CALM_RECHAMADA', 'value': 'FILA_CALM_RECHAMADA'},
                    # Adicionar todas as filas do seu script
                ],
                multi=True,
                value=['FILA_CALM'] # Valor inicial
            )
        ], style={'marginRight': '20px', 'width': '20%'}),
        html.Div([
            html.Label("Canal"),
            dcc.Dropdown(
                id='channel-filter',
                options=[
                    {'label': 'Voz', 'value': 'voice'},
                    {'label': 'Texto', 'value': 'text'}
                ],
                multi=True,
                value=['voice', 'text'] # Valor inicial
            )
        ], style={'marginRight': '20px', 'width': '20%'}),
        html.Div([
            html.Label("Agregação de Gráficos"),
            dcc.Dropdown(
                id='period-agg-filter',
                options=[
                    {'label': 'Por Hora', 'value': 'H'},
                    {'label': 'Por Dia', 'value': 'D'}
                ],
                value='H', # Valor inicial
                clearable=False
            )
        ], style={'width': '20%'})
    ], style={'display': 'flex', 'justifyContent': 'flex-start', 'marginBottom': '20px', 'alignItems': 'flex-end'}),
    
    # Cards de métricas principais
    html.Div([
        html.Div([
            html.H3("Total de Clientes"),
            html.H2(id='total-customers')
        ], className='metric-card'),
        html.Div([
            html.H3("Chamadas Recebidas"),
            html.H2(id='total-received-calls')
        ], className='metric-card'),
        html.Div([
            html.H3("Chamadas Atendidas"),
            html.H2(id='total-answered-calls')
        ], className='metric-card'),
        html.Div([
            html.H3("Nível de Serviço"),
            html.H2(id='service-level')
        ], className='metric-card'),
        html.Div([
            html.H3("TMA"),
            html.H2(id='average-handle-time')
        ], className='metric-card'),
        html.Div([
            html.H3("TME"),
            html.H2(id='average-wait-time')
        ], className='metric-card'),
        html.Div([
            html.H3("Tempo Conversação Média"),
            html.H2(id='average-talk-time')
        ], className='metric-card'),
        html.Div([
            html.H3("HCs Logados"),
            html.H2(id='logged-in-agents')
        ], className='metric-card'),
        html.Div([
            html.H3("Interações Auto Serviço"),
            html.H2(id='auto-service-interactions')
        ], className='metric-card'),
        html.Div([
            html.H3("Rechamadas"),
            html.H2(id='total-callbacks')
        ], className='metric-card'),
        html.Div([
            html.H3("Interações Duplicadas"),
            html.H2(id='duplicate-channel-interactions')
        ], className='metric-card')
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 'gap': '20px', 'marginBottom': '20px'}),
    
    # Gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='volume-chart')
        ], style={'width': '100%', 'marginBottom': '20px'}),
        html.Div([
            dcc.Graph(id='tma-tme-chart')
        ], style={'width': '100%', 'marginBottom': '20px'})
    ]),
    
    html.Div([
        html.H3("Top Motivos de Contato"),
        dcc.Graph(id='top-reasons-chart')
    ], style={'width': '100%', 'marginBottom': '20px'}),

    # Atualização automática
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 1 minuto
        n_intervals=0
    )
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'})

# CSS para os cards (adicione ao seu arquivo assets/style.css, por exemplo)
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

app.css.append_css({
    "external_url": "/assets/style.css"
})

# Callbacks
@app.callback(
    [Output('total-customers', 'children'),
     Output('total-received-calls', 'children'),
     Output('total-answered-calls', 'children'),
     Output('service-level', 'children'),
     Output('average-handle-time', 'children'),
     Output('average-wait-time', 'children'),
     Output('average-talk-time', 'children'),
     Output('logged-in-agents', 'children'),
     Output('auto-service-interactions', 'children'),
     Output('total-callbacks', 'children'),
     Output('duplicate-channel-interactions', 'children'),
     Output('volume-chart', 'figure'),
     Output('tma-tme-chart', 'figure'),
     Output('top-reasons-chart', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('queue-filter', 'value'),
     Input('channel-filter', 'value'),
     Input('period-agg-filter', 'value')]
)
def update_dashboard(
    n_intervals,
    start_date,
    end_date,
    queues,
    channels,
    period_agg
):
    start_date_obj = datetime.fromisoformat(start_date)
    end_date_obj = datetime.fromisoformat(end_date)

    try:
        data = fetch_dashboard_data(start_date_obj, end_date_obj, queues, channels)

        # Geração dos gráficos de volume
        volume_data = requests.get(
            f"{API_URL}/dashboard/overview/volume_by_period",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "queue_ids": queues if queues else [],
                "channel_types": channels if channels else [],
                "period": period_agg
            }
        ).json()

        volume_figure = go.Figure()
        volume_figure.add_trace(go.Scatter(
            x=volume_data['timestamps'],
            y=volume_data['total_customers'],
            mode='lines+markers',
            name='Clientes Acionados'
        ))
        volume_figure.add_trace(go.Scatter(
            x=volume_data['timestamps'],
            y=volume_data['total_received_calls'],
            mode='lines+markers',
            name='Chamadas Recebidas'
        ))
        volume_figure.add_trace(go.Scatter(
            x=volume_data['timestamps'],
            y=volume_data['total_answered_calls'],
            mode='lines+markers',
            name='Chamadas Atendidas'
        ))
        volume_figure.update_layout(
            title='Volume de Clientes e Chamadas por Período',
            xaxis_title='Período',
            yaxis_title='Quantidade',
            template='plotly_white',
            hovermode='x unified'
        )

        # Geração dos gráficos de TMA e TME
        tma_tme_data = requests.get(
            f"{API_URL}/dashboard/overview/tma_tme_by_period",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "queue_ids": queues if queues else [],
                "channel_types": channels if channels else [],
                "period": period_agg
            }
        ).json()

        tma_tme_figure = go.Figure()
        tma_tme_figure.add_trace(go.Scatter(
            x=tma_tme_data['timestamps'],
            y=[t/60 for t in tma_tme_data['tma']], # Converter segundos para minutos
            mode='lines+markers',
            name='TMA (min)'
        ))
        tma_tme_figure.add_trace(go.Scatter(
            x=tma_tme_data['timestamps'],
            y=[t/60 for t in tma_tme_data['tme']], # Converter segundos para minutos
            mode='lines+markers',
            name='TME (min)'
        ))
        tma_tme_figure.update_layout(
            title='TMA e TME por Período',
            xaxis_title='Período',
            yaxis_title='Tempo (minutos)',
            template='plotly_white',
            hovermode='x unified'
        )

        # Gráfico de Top Motivos
        top_reasons_figure = go.Figure(go.Bar(
            x=list(data['top_reasons'].keys()),
            y=list(data['top_reasons'].values())
        ))
        top_reasons_figure.update_layout(
            title='Top 10 Motivos de Contato',
            xaxis_title='Motivo',
            yaxis_title='Quantidade',
            template='plotly_white'
        )

        return (
            f"{data['total_customers']:,}",
            f"{data['total_received_calls']:,}",
            f"{data['total_answered_calls']:,}",
            f"{data['service_level']:.2f}%",
            f"{data['average_handle_time']/60:.2f} min",
            f"{data['average_wait_time']/60:.2f} min",
            f"{data['average_talk_time']/60:.2f} min",
            f"{data['logged_in_agents']}",
            f"{data['auto_service_interactions']:,}",
            f"{data['total_callbacks']:,}",
            f"{data['duplicate_channel_interactions']:,}",
            volume_figure,
            tma_tme_figure,
            top_reasons_figure
        )
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar à API: {e}")
        return [f"Erro: {e}"] * 11 + [go.Figure()] * 3 # Retorna figuras vazias em caso de erro
    except Exception as e:
        print(f"Ocorreu um erro no callback: {e}")
        return [f"Erro: {e}"] * 11 + [go.Figure()] * 3

if __name__ == '__main__':
    app.run_server(debug=True) 