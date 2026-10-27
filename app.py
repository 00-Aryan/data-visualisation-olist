"""
Production Dash Application entrypoint for Olist Expansion Analytics.

Initializes the Dash instance with Bootstrap stylesheet, attaches executive layout,
registers interactive callbacks and tab-resize event dispatchers, and runs on
http://127.0.0.1:8050.
"""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc

from src.callbacks import register_callbacks
from src.layout import create_layout

# Initialize Dash application with clean Bootstrap theme
app = dash.Dash(
    __name__,
    title="Dash",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "Dash"

server = app.server

# Attach executive layout
app.layout = create_layout()

# Register interactive server-side and clientside callbacks
register_callbacks(app)

if __name__ == "__main__":
    # Bind server to run locally on http://127.0.0.1:8050 in clean executive mode (debug=False removes purple toolbar)
    app.run(host="127.0.0.1", port=8050, debug=False)
