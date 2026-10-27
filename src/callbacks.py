"""
Interactive callbacks registration for Olist Expansion Analytics Dashboard.

Provides clientside tab resize dispatching and server-side filtering callbacks
with empty-filter fallbacks and zero-division protections.
"""

from __future__ import annotations

from typing import List, Optional

import dash
from dash import Input, Output

from src.data_loader import (
    load_geo_revenue,
    load_monthly_revenue_by_tier,
    load_state_analysis,
)
from src.figures import (
    build_figure_1_monthly_revenue,
    build_figure_2_category_performance,
    build_figure_3_state_analysis,
    build_figure_7_seller_hub,
    build_figure_8_geo_revenue,
)


def register_callbacks(app: dash.Dash) -> None:
    """Registers all clientside and server-side interactive callbacks on the Dash application."""

    # 1. Clientside Tab-Resize Fix Callback
    # Triggers window.dispatchEvent(new Event('resize')) when active tab changes
    # so hidden figures never render with 0px width.
    app.clientside_callback(
        """
        function(activeTab) {
            setTimeout(function() {
                window.dispatchEvent(new Event('resize'));
            }, 60);
            return "";
        }
        """,
        Output("clientside-resize-dummy", "children"),
        Input("analytics-tabs", "value"),
    )

    # 2. Tab 1: Monthly Sales & Orders Tier Filter Callback
    @app.callback(
        Output("fig-1-monthly-revenue", "figure"),
        Input("tab1-market-tier-filter", "value"),
    )
    def update_monthly_sales(tier: Optional[str]):
        df_tier = load_monthly_revenue_by_tier()
        if not tier or tier == "ALL":
            return build_figure_1_monthly_revenue()
        filtered_df = df_tier[df_tier["market_tier"] == tier].sort_values("month").reset_index(drop=True)
        return build_figure_1_monthly_revenue(filtered_df, tier=tier)

    # 3. Tab 1: Geographic Revenue Tier Filter Callback
    @app.callback(
        Output("fig-8-geo-revenue", "figure"),
        Input("tab1-market-tier-filter", "value"),
    )
    def update_geo_revenue(tier: Optional[str]):
        df = load_geo_revenue()
        if not tier or tier == "ALL":
            return build_figure_8_geo_revenue(df)
        filtered_df = df[df["market_tier"] == tier]
        return build_figure_8_geo_revenue(filtered_df)

    # 3. Tab 1: Top Categories Volume Callback
    @app.callback(
        Output("fig-2-category-performance", "figure"),
        Input("tab1-category-top-n", "value"),
    )
    def update_top_categories(top_n: Optional[int]):
        if not top_n or not isinstance(top_n, int) or top_n <= 0:
            top_n = 15
        return build_figure_2_category_performance(top_n=top_n)

    # 4. Tab 2: State SLA Filter Callback
    @app.callback(
        Output("fig-3-state-analysis", "figure"),
        Input("tab2-state-sla-filter", "value"),
    )
    def update_state_analysis(selected_states: Optional[List[str]]):
        df = load_state_analysis()
        if not selected_states or len(selected_states) == 0:
            return build_figure_3_state_analysis(df)
        filtered_df = df[df["customer_state"].isin(selected_states)]
        return build_figure_3_state_analysis(filtered_df)

    # 5. Tab 3: Seller Supply Hub State Filter Callback
    @app.callback(
        Output("fig-7-seller-hub", "figure"),
        Input("tab3-state-dropdown", "value"),
    )
    def update_seller_hub(selected_state: Optional[str]):
        return build_figure_7_seller_hub(state=selected_state)

