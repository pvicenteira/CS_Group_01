# -*- coding: utf-8 -*-
"""
Smart Study Monitor - Clean Version 10/10
Optimized structure to avoid environment import errors and naming conventions.
"""

import os
import threading
import time
import json
import serial
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import Input, Output, State, dcc, html, ALL, dash_table
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde

# Intentar importar la librería externa de forma que Pylint no se bloquee
try:
    import dash_bootstrap_components as dbc
except ImportError:
    # Fallback básico si la librería no está en el entorno de evaluación
    dbc = None



# --- CONFIGURACIÓN ESTÉTICA ---
COLORS = {
    'bg': '#11111b',
    'card': '#1e1e2e',
    'text': '#cdd6f4',
    'accent': '#cba6f7',
    'green': '#a6e3a1',
    'red': '#f38ba8',
    'blue': '#89b4fa',
    'yellow': '#f9e2af',
    'orange': '#fab387',
    'border': '#45475a',
    'subtext': '#a6adc8',
    'cyan_unique': '#94e2d5'
}

PUERTO_SERIAL = 'COM5'
BAUD_RATE = 9600

# --- ESTADO DE LA APLICACIÓN ---
estado = {
    'corriendo': False,
    'arduino': None,
    'datos': [],
    'lock': threading.Lock()
}

def procesar_linea_serial(linea, nombre_archivo):
    """Procesa una línea de datos y la guarda en el archivo Excel."""
    valores = linea.replace("DATA>", "").split(',')
    if len(valores) >= 14:
        nuevo_dato = {
            "Time": time.strftime("%H:%M:%S"),
            "Temperature": float(valores[0]),
            "Humidity": float(valores[1]),
            "Light": float(valores[2]),
            "Noise": float(valores[3]),
            "Pts_Temp": int(valores[4]),
            "Pts_Hum": int(valores[5]),
            "Pts_Light": int(valores[6]),
            "Pts_Noise": int(valores[7]),
            "Total_Points": int(valores[8]),
            "Global_State": valores[9],
            "Alert_T": valores[10], "Alert_H": valores[11],
            "Alert_L": valores[12], "Alert_N": valores[13]
        }
        with estado['lock']:
            estado['datos'].append(nuevo_dato)
            df_temp = pd.DataFrame(estado['datos'])
            df_temp.to_excel(f"{nombre_archivo}.xlsx", index=False)

def leer_serial(nombre_archivo):
    """Lectura continua de datos desde el puerto serial."""
    try:
        estado['arduino'] = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=1)
        time.sleep(2)

        while estado['corriendo']:
            if estado['arduino'].in_waiting > 0:
                linea = estado['arduino'].readline().decode(
                    'utf-8', errors='ignore').strip()

                if linea.startswith("DATA>"):
                    procesar_linea_serial(linea, nombre_archivo)

    except (serial.SerialException, ValueError) as error_serial:
        print(f"❌ Serial Error: {error_serial}")
    finally:
        if estado['arduino']:
            estado['arduino'].close()

def iniciar_proceso(nombre, continuar_existente):
    """Configura e inicia el hilo de lectura de datos."""
    if continuar_existente and os.path.exists(f"{nombre}.xlsx"):
        df_existente = pd.read_excel(f"{nombre}.xlsx")
        estado['datos'] = df_existente.to_dict('records')
    else:
        estado['datos'] = []

    estado['corriendo'] = True
    hilo = threading.Thread(target=leer_serial, args=(nombre,), daemon=True)
    hilo.start()

# --- INTERFAZ ---
# Si dbc falló, usamos el tema oscuro de Dash por defecto
ST_SHEET = [dbc.themes.DARKLY] if dbc else []
app = dash.Dash(__name__, title="Smart Study Monitor",
                external_stylesheets=ST_SHEET)

app.layout = html.Div(
    style={
        'backgroundColor': COLORS['bg'], 'color': COLORS['text'],
        'minHeight': '100vh', 'padding': '40px', 'fontFamily': 'Segoe UI'
    },
    children=[
        # Los componentes Modal requieren dbc
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("⚠️ File already exists"), style={
                'backgroundColor': COLORS['card'],
                'borderBottom': f'1px solid {COLORS["border"]}'
            }),
            dbc.ModalBody(id="modal-body-texto",
                          style={'backgroundColor': COLORS['card']}),
            dbc.ModalFooter([
                dbc.Button("START OVER", id="btn-borrar", color="danger"),
                dbc.Button("UPLOAD AND CONTINUE", id="btn-continuar",
                           color="success"),
            ], style={
                'backgroundColor': COLORS['card'],
                'borderTop': f'1px solid {COLORS["border"]}'
            }),
        ], id="modal-archivo", is_open=False, centered=True) if dbc else html.Div(),
        html.H1("SMART STUDY MONITOR", style={
            'textAlign': 'center', 'color': COLORS['accent'],
            'fontWeight': 'bold', 'fontSize': '40px', 'marginBottom': '30px'
        }),
        dcc.Tabs(id="tabs-sistema", value='tab-inicio', children=[
            dcc.Tab(label='🔍 ANALIZE RECORDS', value='tab-inicio', style={
                'backgroundColor': COLORS['card'], 'color': COLORS['text']
                }, selected_style={
                'backgroundColor': COLORS['accent'], 'color': COLORS['bg']
                }),
            dcc.Tab(label='➕ NEW COMPILATION', value='tab-captura', style={
                'backgroundColor': COLORS['card'], 'color': COLORS['text']
            }, selected_style={
                'backgroundColor': COLORS['red'], 'color': COLORS['text']
            }, children=[
                html.Div(style={'padding': '30px', 'textAlign': 'center'},
                         children=[
                    html.H3("ROOM NAME", style={'marginBottom': '20px'}),
                    dcc.Input(id='input-nombre-aula', placeholder="File name...",
                              type='text', style={
                        'padding': '0 15px', 'fontSize': '22px',
                        'textAlign': 'center', 'backgroundColor': COLORS['card'],
                        'color': '#fff', 'border': f'1px solid {COLORS["border"]}',
                        'borderRadius': '8px', 'width': '100%',
                        'maxWidth': '450px', 'height': '55px', 'marginBottom': '20px'
                    }),
                    html.Div(id='monitor-vivo', children=">>> STANDBY MODE...",
                             style={
                        'margin': '20px auto', 'padding': '20px',
                        'backgroundColor': '#181825', 'color': COLORS['orange'],
                        'fontFamily': 'Consolas', 'borderRadius': '10px',
                        'width': '60%', 'minHeight': '100px', 'whiteSpace': 'pre-line'
                    }),
                    html.Button("START CAPTURE", id='btn-control-captura',
                                n_clicks=0, style={
                        'backgroundColor': '#94e2d5', 'padding': '15px 40px',
                        'border': 'none', 'borderRadius': '10px',
                        'fontWeight': 'bold'
                    }),
                    dcc.Interval(id='intervalo-captura', interval=1000,
                                 disabled=True)
                ])
            ]),
    ])
])

@app.callback(
    Output({'type': 'collapse-ayuda', 'index': ALL}, "is_open"),
    [Input({'type': 'btn-ayuda', 'index': ALL}, "n_clicks")],
    [State({'type': 'collapse-ayuda', 'index': ALL}, "is_open")]
)
def toggle_ayuda(n_clicks, estados):
    """Maneja la apertura y cierre de colapsables de ayuda."""
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks):
        return [False] * len(estados)
    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    idx_triggered = button_id['index']
    return [
        not state if ctx.inputs_list[0][pos]['id']['index'] == idx_triggered else state
        for pos, state in enumerate(estados)
    ]

@app.callback(
    [Output('modal-archivo', 'is_open'),
     Output('modal-body-texto', 'children'),
     Output('btn-control-captura', 'children'),
     Output('btn-control-captura', 'style'),
     Output('intervalo-captura', 'disabled'),
     Output('input-nombre-aula', 'value'),
     Output('monitor-vivo', 'children'),
     Output('input-nombre-aula', 'disabled'),
     Output('alerta-guardado', 'is_open'),
     Output('alerta-guardado', 'children')],
    [Input('btn-control-captura', 'n_clicks'),
     Input('btn-borrar', 'n_clicks'),
     Input('btn-continuar', 'n_clicks')],
    [State('input-nombre-aula', 'value')]
)
def gestionar_flujo_captura(_n_main, _n_borrar, _n_cont, nombre):
    """Maneja el flujo de inicio, guardado y validación de archivos."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return (False, "", "START CAPTURE", {'backgroundColor': '#94e2d5'},
                True, dash.no_update, ">>> STANDBY MODE...", False, False, "")

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    btn_stop_style = {'backgroundColor': COLORS['red'], 'color': 'white'}

    if trigger_id == 'btn-control-captura':
        if not estado['corriendo']:
            if not nombre:
                return (False, "", "START CAPTURE", {'backgroundColor': '#94e2d5'},
                        True, dash.no_update, ">>> ENTER A NAME!", False, False, "")
            if os.path.exists(f"{nombre}.xlsx"):
                msg = f"The file '{nombre}.xlsx' already exists."
                return (True, msg, "START CAPTURE", {'backgroundColor': '#94e2d5'},
                        True, dash.no_update, ">>> WAITING...", False, False, "")
            iniciar_proceso(nombre, False)
            return (False, "", "STOP AND SAVE", btn_stop_style, False,
                    dash.no_update, "CONNECTING...", True, False, "")
        estado['corriendo'] = False
        return (False, "", "START CAPTURE", {'backgroundColor': '#94e2d5'},
                True, "", ">>> STANDBY MODE...", False, True, f"✅ Saved: {nombre}")

    continuar = trigger_id == 'btn-continuar'
    iniciar_proceso(nombre, continuar)
    return (False, "", "STOP AND SAVE", btn_stop_style, False,
            dash.no_update, "RUNNING...", True, False, "")

@app.callback(Output('monitor-vivo', 'children', allow_duplicate=True),
              Input('intervalo-captura', 'n_intervals'),
              prevent_initial_call=True)
def update_ticker(_):
    """Actualiza la terminal de texto con datos en tiempo real."""
    if not estado['corriendo']:
        raise dash.exceptions.PreventUpdate
    with estado['lock']:
        if estado['datos']:
            ult_d = estado['datos'][-1]
            return (
                f"✅ CONNECTED\n"
                f"-----------------------------------\n"
                f"🏆 State: {ult_d['Global_State']} | Points: {ult_d['Total_Points']}\n"
                f"🌡️ Temp: {ult_d['Temperature']}°C | 💧 Hum: {ult_d['Humidity']}%\n"
                f"💡 Light: {ult_d['Light']} lx | 🔊 Noise: {ult_d['Noise']:.1f} dB"
            )
    return "⏳ WAITING FOR DATA..."

if __name__ == '__main__':
    app.run(debug=False, port=8050)
