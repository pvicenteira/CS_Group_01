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
                })
    ])
])

if __name__ == '__main__':
    app.run(debug=False, port=8050)
