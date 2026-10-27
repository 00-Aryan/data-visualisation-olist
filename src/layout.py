"""
High-density Power BI / Tableau executive dashboard layout for Olist Expansion Analytics.

Completely eliminates website/SaaS bloat:
- Compact dark-navy header (#0f172a, height 46px)
- Understated Power BI page tabs
- 4 dense 72px metric tiles (exactly 2 lines: small uppercase label + bold number)
- High-density BI chart grid (p-2, g-2, crisp 1px border #cbd5e1, 4px border-radius, zero drop-shadow)
- Fits cleanly on a standard monitor without unnecessary vertical scrolling
"""

from __future__ import annotations

from typing import List, Optional

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.data_loader import load_seller_summary, load_state_analysis
from src.figures import (
    COLOR_ALERT,
    COLOR_BORDER,
    COLOR_CANVAS,
    COLOR_CARD,
    COLOR_CORPORATE,
    COLOR_INK,
    COLOR_MUTED,
    COLOR_STRATEGIC,
    FONT_FAMILY,
    build_figure_1_monthly_revenue,
    build_figure_2_category_performance,
    build_figure_3_state_analysis,
    build_figure_4_delivery_cliff,
    build_figure_5_customer_value,
    build_figure_6_payment_rails,
    build_figure_7_seller_hub,
    build_figure_8_geo_revenue,
    build_figure_9_lead_conversion,
    build_figure_10_closed_deals,
)

# Crisp Power BI / Tableau Border and Container Styles
BORDER_COLOR = "#cbd5e1"  # Crisp Slate-300 border
DARK_NAVY = "#0f172a"     # Slate-900 Power BI Header bar

CHART_BOX_STYLE = {
    "backgroundColor": "#FFFFFF",
    "border": f"1px solid {BORDER_COLOR}",
    "borderRadius": "4px",
    "boxShadow": "none",
    "padding": "6px",
}

# Understated Power BI Page Tab Styles
TAB_STYLE = {
    "backgroundColor": "transparent",
    "border": "none",
    "borderBottom": "2px solid transparent",
    "padding": "7px 18px",
    "fontWeight": "600",
    "color": "#64748B",
    "fontSize": "12px",
    "cursor": "pointer",
}

TAB_SELECTED_STYLE = {
    "backgroundColor": "#FFFFFF",
    "border": "none",
    "borderBottom": f"2px solid {DARK_NAVY}",
    "padding": "7px 18px",
    "fontWeight": "700",
    "color": DARK_NAVY,
    "fontSize": "12px",
    "cursor": "pointer",
}



def build_metric_tile(label: str, value: str, text_color: str = COLOR_CORPORATE) -> html.Div:
    """Builds a compact border-framed metric tile (height ~72px, 2 lines only)."""
    return html.Div(
        [
            html.Div(
                label,
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "color": "#64748B",
                    "letterSpacing": "0.06em",
                    "lineHeight": "1",
                },
            ),
            html.Div(
                value,
                style={
                    "fontSize": "23px",
                    "fontWeight": "800",
                    "color": text_color,
                    "lineHeight": "1.1",
                    "marginTop": "4px",
                    "fontFamily": FONT_FAMILY,
                },
            ),
        ],
        style={
            "backgroundColor": "#FFFFFF",
            "border": f"1px solid {BORDER_COLOR}",
            "borderRadius": "4px",
            "boxShadow": "none",
            "padding": "10px 14px",
            "height": "72px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
        },
    )


def build_kpi_row() -> dbc.Row:
    """Builds the 4 compact, border-framed metric tiles row."""
    tiles = [
        ("TOTAL SALES (GMV)", "R$ 15.8M", COLOR_CORPORATE),
        ("REPEAT CUSTOMER RATE", "3.12%", COLOR_STRATEGIC),
        ("DELAYED ORDERS (>14 DAYS)", "8.5%", COLOR_ALERT),
        ("TOP SELLERS IN SÃO PAULO", "75.0%", COLOR_CORPORATE),
    ]

    cols = [
        dbc.Col(
            build_metric_tile(lbl, val, col),
            xs=6, md=3,
        )
        for lbl, val, col in tiles
    ]
    return dbc.Row(cols, className="g-2 mb-2")


# ==============================================================================
# TAB 1: EXECUTIVE OVERVIEW & GROWTH PLATEAU (Figures 1, 2, and 8)
# ==============================================================================
def build_tab_1() -> html.Div:
    """Tab 1 layout with compact slicer ribbon and high-density chart grid."""
    return html.Div(
        [
            # Slim Slicer Ribbon (Height ~38px) with Power BI button strips
            html.Div(
                [
                    html.Span(
                        "MARKET TIER:",
                        style={"fontSize": "11px", "fontWeight": "700", "color": "#1E293B", "marginRight": "8px"},
                    ),
                    dbc.RadioItems(
                        id="tab1-market-tier-filter",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-secondary btn-sm py-1 px-3",
                        labelCheckedClassName="active btn-dark",
                        options=[
                            {"label": "All Markets", "value": "ALL"},
                            {"label": "Southeast Core", "value": "Southeast Core"},
                            {"label": "Expansion Markets", "value": "Expansion Markets"},
                        ],
                        value="ALL",
                    ),
                    html.Div(style={"width": "20px"}),
                    html.Span(
                        "CATEGORIES:",
                        style={"fontSize": "11px", "fontWeight": "700", "color": "#1E293B", "marginRight": "8px"},
                    ),
                    dbc.RadioItems(
                        id="tab1-category-top-n",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-secondary btn-sm py-1 px-2",
                        labelCheckedClassName="active btn-dark",
                        options=[
                            {"label": "Top 10", "value": 10},
                            {"label": "Top 15", "value": 15},
                            {"label": "Top 20", "value": 20},
                        ],
                        value=15,
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "height": "38px",
                    "backgroundColor": "#FFFFFF",
                    "border": f"1px solid {BORDER_COLOR}",
                    "borderRadius": "4px",
                    "padding": "0 12px",
                    "marginBottom": "6px",
                },
            ),

            # Row 1: Figure 1 (Monthly GMV & Order Trajectory)
            html.Div(
                dcc.Graph(
                    id="fig-1-monthly-revenue",
                    figure=build_figure_1_monthly_revenue(),
                    config={"displayModeBar": False, "responsive": True},
                    style={"height": "265px"},
                ),
                style=CHART_BOX_STYLE,
                className="mb-2",
            ),

            # Row 2: Figure 2 (Categories, 7 cols) & Figure 8 (Geo Revenue, 5 cols)
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                                id="fig-2-category-performance",
                                figure=build_figure_2_category_performance(),
                                config={"displayModeBar": False, "responsive": True},
                                style={"height": "265px"},
                            ),
                            style=CHART_BOX_STYLE,
                        ),
                        lg=7,
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                                id="fig-8-geo-revenue",
                                figure=build_figure_8_geo_revenue(),
                                config={"displayModeBar": False, "responsive": True},
                                style={"height": "265px"},
                            ),
                            style=CHART_BOX_STYLE,
                        ),
                        lg=5,
                    ),
                ],
                className="g-2",
            ),
        ]
    )


# ==============================================================================
# TAB 2: LOGISTICS FRICTION & THE DELIVERY CLIFF (Figures 3, 4, and 6)
# ==============================================================================
def build_tab_2() -> html.Div:
    """Tab 2 layout with compact slicer ribbon and high-density chart grid."""
    state_df = load_state_analysis()
    all_states = sorted(state_df["customer_state"].unique().tolist())

    return html.Div(
        [
            # Slim Slicer Ribbon (Height ~36px)
            html.Div(
                [
                    html.Span(
                        "STATE FILTER:",
                        style={"fontSize": "11px", "fontWeight": "700", "color": "#1E293B", "marginRight": "8px"},
                    ),
                    html.Div(
                        dcc.Dropdown(
                            id="tab2-state-sla-filter",
                            options=[{"label": s, "value": s} for s in all_states],
                            value=[],
                            multi=True,
                            placeholder="All States (Default)",
                            style={"fontSize": "11px"},
                        ),
                        style={"flex": "1", "maxWidth": "400px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "height": "36px",
                    "backgroundColor": "#FFFFFF",
                    "border": f"1px solid {BORDER_COLOR}",
                    "borderRadius": "4px",
                    "padding": "0 12px",
                    "marginBottom": "6px",
                },
            ),

            # Row 1: Figure 3 (State SLA vs CSAT, 7 cols) & Figure 4 (Delivery Review Cliff, 5 cols)
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                                id="fig-3-state-analysis",
                                figure=build_figure_3_state_analysis(),
                                config={"displayModeBar": False, "responsive": True},
                                style={"height": "275px"},
                            ),
                            style=CHART_BOX_STYLE,
                        ),
                        lg=7,
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                                id="fig-4-delivery-cliff",
                                figure=build_figure_4_delivery_cliff(),
                                config={"displayModeBar": False, "responsive": True},
                                style={"height": "275px"},
                            ),
                            style=CHART_BOX_STYLE,
                        ),
                        lg=5,
                    ),
                ],
                className="g-2 mb-2",
            ),

            # Row 2: Figure 6 (Payment Rails Breakdown, 12 cols)
            html.Div(
                dcc.Graph(
                    id="fig-6-payment-rails",
                    figure=build_figure_6_payment_rails(),
                    config={"displayModeBar": False, "responsive": True},
                    style={"height": "235px"},
                ),
                style=CHART_BOX_STYLE,
            ),
        ]
    )


# ==============================================================================
# TAB 3: SUPPLY HUB & UNIT ECONOMICS (Figures 5, 7, 9, and 10)
# ==============================================================================
def build_tab_3() -> html.Div:
    """Tab 3 layout with compact slicer ribbon and high-density chart grid."""
    seller_df = load_seller_summary()
    sorted_states = sorted([str(s) for s in seller_df["seller_state"].dropna().unique() if str(s) != "nan"])

    return html.Div(
        [
            # Slim Slicer Ribbon (Height ~36px)
            html.Div(
                [
                    html.Span("SELLER STATE:", style={"fontSize": "11px", "fontWeight": "700", "color": "#1E293B", "marginRight": "8px"}),
                    dcc.Dropdown(
                        id="tab3-state-dropdown",
                        options=[{"label": "All States", "value": "ALL"}] + [{"label": s, "value": s} for s in sorted_states],
                        value="ALL",
                        clearable=False,
                        placeholder="Filter by Seller State...",
                        style={"fontSize": "11px", "width": "250px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "height": "36px",
                    "backgroundColor": "#FFFFFF",
                    "border": f"1px solid {BORDER_COLOR}",
                    "borderRadius": "4px",
                    "padding": "0 12px",
                    "marginBottom": "6px",
                },
            ),

            # Row 1: Figure 5 (Spend Density, 6 cols) & Figure 7 (Seller Hub, 6 cols)
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                                id="fig-5-customer-value",
                                figure=build_figure_5_customer_value(),
                                config={"displayModeBar": False, "responsive": True},
                                style={"height": "255px"},
                            ),
                            style=CHART_BOX_STYLE,
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                                id="fig-7-seller-hub",
                                figure=build_figure_7_seller_hub(),
                                config={"displayModeBar": False, "responsive": True},
                                style={"height": "255px"},
                            ),
                            style=CHART_BOX_STYLE,
                        ),
                        lg=6,
                    ),
                ],
                className="g-2 mb-2",
            ),

            # Row 2: Figure 9 (Lead Conversion, 6 cols) & Figure 10 (Closed Deals vs Velocity, 6 cols)
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                                id="fig-9-lead-conversion",
                                figure=build_figure_9_lead_conversion(),
                                config={"displayModeBar": False, "responsive": True},
                                style={"height": "255px"},
                            ),
                            style=CHART_BOX_STYLE,
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                                id="fig-10-closed-deals",
                                figure=build_figure_10_closed_deals(),
                                config={"displayModeBar": False, "responsive": True},
                                style={"height": "255px"},
                            ),
                            style=CHART_BOX_STYLE,
                        ),
                        lg=6,
                    ),
                ],
                className="g-2",
            ),
        ]
    )


# ==============================================================================
# MASTER LAYOUT ASSEMBLY
# ==============================================================================
def create_layout() -> html.Div:
    """Builds the complete clean, dense Power BI executive dashboard layout."""
    return html.Div(
        [
            # Hidden dummy container for clientside tab resize event
            html.Div(id="clientside-resize-dummy", style={"display": "none"}),

            # 1. Dense Top KPI Scorecard Row (4 compact tiles, height ~72px)
            build_kpi_row(),

            # 2. Understated Power BI Page Tabs
            html.Div(
                dcc.Tabs(
                    id="analytics-tabs",
                    value="tab-1",
                    children=[
                        dcc.Tab(
                            label="Overview & Growth Plateau",
                            value="tab-1",
                            children=build_tab_1(),
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                        dcc.Tab(
                            label="Logistics & Delivery Cliff",
                            value="tab-2",
                            children=build_tab_2(),
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                        dcc.Tab(
                            label="Supply Hub & Unit Economics",
                            value="tab-3",
                            children=build_tab_3(),
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                    ],
                    style={"height": "34px", "borderBottom": f"1px solid {BORDER_COLOR}"},
                ),
                style={"backgroundColor": "#FFFFFF", "padding": "0 4px", "marginBottom": "6px"},
            ),
        ],
        style={
            "backgroundColor": COLOR_CANVAS,
            "minHeight": "100vh",
            "padding": "12px",
            "maxWidth": "100%",
            "fontFamily": FONT_FAMILY,
        },
    )


layout = create_layout
