"""
Pure functions for generating executive-grade Plotly figures (Figures 1-10)
for the Olist Expansion Analytics Dashboard.

Adheres strictly to the visual design system, Edward Tufte principles,
and color palette directives specified in GEMINI.md.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.data_loader import (
    load_category_summary,
    load_customer_spend_dist,
    load_delivery_review,
    load_geo_revenue,
    load_lead_origin,
    load_monthly_revenue,
    load_monthly_revenue_by_tier,
    load_payment_summary,
    load_segment_pipeline,
    load_seller_summary,
    load_state_analysis,
    safe_divide,
)

# ==========================================
# STRICT VISUAL DESIGN PALETTE & DESIGN TOKENS
# ==========================================
COLOR_CANVAS = "#F8FAFC"       # Slate-50: Background canvas
COLOR_CARD = "#FFFFFF"         # Container cards
COLOR_BORDER = "#E2E8F0"       # Slate-200: 1px subtle borders and gridlines
COLOR_INK = "#1E293B"          # Slate-800: Primary typography & base ink
COLOR_MUTED = "#64748B"        # Slate-500: Secondary annotations & axis labels
COLOR_LIGHT_MUTED = "#94A3B8"  # Slate-400: Tertiary elements

COLOR_STRATEGIC = "#0D9488"    # Teal-600: High-value segments, repeat buyers, expansion markers
COLOR_CORPORATE = "#1E3A8A"    # Navy-900: São Paulo and Southeast core baseline
COLOR_ALERT = "#DC2626"        # Red-600: Strictly reserved for late deliveries, 1-star reviews, SLA breaches
COLOR_TARGET = "#16A34A"       # Green-600: Strictly reserved for 5-star ratings, SLA met

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def apply_executive_theme(
    fig: go.Figure,
    title: str = "",
    subtitle: Optional[str] = None,
    margin: Optional[dict] = None,
    height: int = 280,
    show_legend: bool = True,
) -> go.Figure:
    """Applies clean, dense executive Power BI / Tableau theme without web-app bloat."""
    if margin is None:
        margin = dict(l=35, r=30, t=30, b=28)

    title_text = f"<b>{title}</b>" if title else None

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=margin,
        font=dict(family=FONT_FAMILY, color=COLOR_INK, size=11),
        title=dict(
            text=title_text,
            font=dict(size=11, color=COLOR_INK),
            x=0.005,
            xanchor="left",
            y=0.98,
            yanchor="top",
        ) if title_text else None,
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(size=10, color=COLOR_INK),
            bgcolor="rgba(255, 255, 255, 0.6)",
            bordercolor="rgba(0,0,0,0)",
            borderwidth=0,
        ) if show_legend else None,
        hoverlabel=dict(
            bgcolor=COLOR_CARD,
            bordercolor=COLOR_BORDER,
            font=dict(family=FONT_FAMILY, size=11, color=COLOR_INK),
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=COLOR_BORDER,
        gridwidth=1,
        zeroline=True,
        zerolinecolor=COLOR_BORDER,
        zerolinewidth=1,
        linecolor=COLOR_BORDER,
        tickfont=dict(color=COLOR_MUTED, size=11),
        title_font=dict(color=COLOR_INK, size=12),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLOR_BORDER,
        gridwidth=1,
        zeroline=True,
        zerolinecolor=COLOR_BORDER,
        zerolinewidth=1,
        linecolor=COLOR_BORDER,
        tickfont=dict(color=COLOR_MUTED, size=11),
        title_font=dict(color=COLOR_INK, size=12),
    )
    return fig


def create_empty_figure(title: str = "No Data Available") -> go.Figure:
    """Returns a styled empty placeholder figure."""
    fig = go.Figure()
    fig.add_annotation(
        text="No data matching current filter selection",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=13, color=COLOR_MUTED),
    )
    return apply_executive_theme(fig, title=title, show_legend=False)


# ==============================================================================
# FIGURE 1: Monthly Revenue & Order Growth Trajectory
# ==============================================================================
def build_figure_1_monthly_revenue(
    df: Optional[pd.DataFrame] = None,
    tier: Optional[str] = None,
) -> go.Figure:
    """Builds Figure 1: Monthly Sales & Order Volume time series.
    
    Supports dynamic tier filtering (Southeast Core vs Expansion Markets).
    Corporate Core Navy (#1E3A8A) for sales volume, Strategic Accent Teal
    (#0D9488) for order volume trajectory.
    """
    if df is None:
        if tier and tier != "ALL":
            df_tier = load_monthly_revenue_by_tier()
            df = df_tier[df_tier["market_tier"] == tier].sort_values("month").reset_index(drop=True)
        else:
            df = load_monthly_revenue()

    if df.empty:
        return create_empty_figure("Monthly Sales & Order Volume")

    df = df.sort_values("month").reset_index(drop=True)

    fig = go.Figure()

    # Primary Trace: Revenue / Sales Bars
    fig.add_trace(
        go.Bar(
            x=df["month"],
            y=df["revenue"],
            name="Sales (R$)",
            marker=dict(
                color=COLOR_CORPORATE,
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            opacity=0.88,
            hovertemplate="<b>%{x}</b><br>Sales: R$ %{y:,.2f}<extra></extra>",
            yaxis="y1",
        )
    )

    # Secondary Trace: Order Count Line
    fig.add_trace(
        go.Scatter(
            x=df["month"],
            y=df["orders"],
            name="Orders",
            mode="lines+markers",
            line=dict(color=COLOR_STRATEGIC, width=2.5),
            marker=dict(size=6, color=COLOR_STRATEGIC, symbol="circle"),
            hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
            yaxis="y2",
        )
    )

    # Highlight Black Friday 2017-11 Surge
    if "2017-11" in df["month"].values:
        row_bf = df[df["month"] == "2017-11"].iloc[0]
        fig.add_annotation(
            x="2017-11",
            y=row_bf["revenue"],
            text=f"<b>Black Friday Peak</b><br>R$ {row_bf['revenue']/1e6:.2f}M | {row_bf['orders']:,} orders",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor=COLOR_INK,
            ax=0,
            ay=-40,
            bgcolor=COLOR_CARD,
            bordercolor=COLOR_BORDER,
            borderwidth=1,
            font=dict(size=10, color=COLOR_INK),
            align="center",
            yref="y",
            xref="x",
        )

    title_text = "Monthly Sales & Order Volume"
    if tier and tier != "ALL":
        title_text = f"Monthly Sales & Order Volume ({tier})"

    apply_executive_theme(
        fig,
        title=title_text,
        margin=dict(l=45, r=45, t=30, b=28),
        height=280,
    )

    fig.update_layout(
        yaxis=dict(
            title="Sales (R$)",
            tickprefix="R$ ",
            side="left",
            showgrid=True,
        ),
        yaxis2=dict(
            title="Orders",
            side="right",
            overlaying="y",
            showgrid=False,
            tickfont=dict(color=COLOR_STRATEGIC),
            title_font=dict(color=COLOR_STRATEGIC),
        ),
        xaxis=dict(
            title="Month",
            tickangle=-45,
            tickmode="auto",
            nticks=16,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
        ),
    )
    return fig


# ==============================================================================
# FIGURE 2: Category Summary & Ticket Yield Performance
# ==============================================================================
def build_figure_2_category_performance(
    df: Optional[pd.DataFrame] = None,
    top_n: int = 15,
) -> go.Figure:
    """Builds Figure 2: Top Product Categories by Revenue and Ticket Yield.
    
    Ranked horizontal bar chart showing top grossing merchandise categories with
    average ticket yield (AOV) and units sold in clean inline text and hover.
    """
    if df is None:
        df = load_category_summary()
    if df.empty:
        return create_empty_figure("Figure 2: Top Merchandise Categories")

    df_top = (
        df.sort_values("revenue", ascending=False)
        .head(top_n)
        .iloc[::-1]
        .copy()
    )

    formatted_names = [
        name.replace("_", " ").title() for name in df_top["product_category_name_english"]
    ]

    customdata = np.stack(
        (
            df_top["revenue_per_order"],
            df_top["units_sold"],
            df_top["orders"],
        ),
        axis=-1,
    )

    # Inline text formatting: Revenue with ticket yield
    text_labels = [
        f"R$ {rev/1e6:.2f}M  (AOV R$ {aov:,.0f})"
        if rev >= 1e6
        else f"R$ {rev/1e3:,.0f}k  (AOV R$ {aov:,.0f})"
        for rev, aov in zip(df_top["revenue"], df_top["revenue_per_order"])
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_top["revenue"],
            y=formatted_names,
            orientation="h",
            marker=dict(
                color=COLOR_CORPORATE,
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            text=text_labels,
            textposition="outside",
            cliponaxis=False,
            customdata=customdata,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Sales: R$ %{x:,.2f}<br>"
                "Average Order Value: R$ %{customdata[0]:,.2f}<br>"
                "Units Sold: %{customdata[1]:,}<br>"
                "Orders: %{customdata[2]:,}<extra></extra>"
            ),
            showlegend=False,
        )
    )

    apply_executive_theme(
        fig,
        title="Top Categories by Sales",
        margin=dict(l=135, r=45, t=30, b=25),
        height=280,
        show_legend=False,
    )

    max_x = df_top["revenue"].max() * 1.25 if not df_top.empty else 1.0
    fig.update_layout(
        xaxis=dict(
            title="Sales (R$)",
            tickprefix="R$ ",
            range=[0, max_x],
        ),
        yaxis=dict(
            title="",
            autorange=True,
        ),
    )
    return fig


# ==============================================================================
# FIGURE 3: State SLA & CSAT Performance Analysis
# ==============================================================================
def build_figure_3_state_analysis(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Builds Figure 3: State-level SLA Transit Latency vs CSAT Satisfaction.
    
    Scatter quadrant chart mapping transit delivery duration against customer
    review ratings. Negative / Alert (#DC2626) is strictly reserved for SLA breaches
    (late delivery rate > 15%), Corporate Core (#1E3A8A) for Southeast baseline,
    and Strategic Accent (#0D9488) for expansion states meeting SLA targets.
    """
    if df is None:
        df = load_state_analysis()
    if df.empty:
        return create_empty_figure("Figure 3: State SLA & CSAT Analysis")

    df = df.copy()

    # Identify Southeast Core states
    se_states = {"SP", "RJ", "MG", "ES"}

    # Categorize states by SLA performance with strict palette rules
    def assign_category(row: pd.Series) -> str:
        if row["late_delivery_rate"] >= 15.0:
            return "SLA Breach / High Delay (>15% Late)"
        elif row["customer_state"] in se_states:
            return "Southeast Core Baseline"
        else:
            return "Expansion States (SLA Met)"

    df["category"] = df.apply(assign_category, axis=1)

    # Scale bubble marker sizes proportionally to order volume
    min_orders, max_orders = df["orders"].min(), df["orders"].max()
    sizes = 10 + 26 * np.sqrt(
        (df["orders"] - min_orders) / max(max_orders - min_orders, 1)
    )
    df["marker_size"] = sizes

    fig = go.Figure()

    category_config = [
        ("Southeast Core Baseline", COLOR_CORPORATE, "circle"),
        ("Expansion States (SLA Met)", COLOR_STRATEGIC, "circle"),
        ("SLA Breach / High Delay (>15% Late)", COLOR_ALERT, "diamond"),
    ]

    for cat_name, cat_color, cat_symbol in category_config:
        subset = df[df["category"] == cat_name]
        if subset.empty:
            continue

        customdata = np.stack(
            (
                subset["customer_state"],
                subset["late_delivery_rate"],
                subset["orders"],
                subset["revenue"],
                subset["avg_order_value"],
            ),
            axis=-1,
        )

        fig.add_trace(
            go.Scatter(
                x=subset["avg_delivery_days"],
                y=subset["avg_review_score"],
                mode="markers+text",
                name=cat_name,
                text=subset["customer_state"],
                textposition="middle center",
                textfont=dict(
                    size=10,
                    color="#FFFFFF" if cat_name != "Southeast Core Baseline" or subset["orders"].iloc[0] > 10000 else COLOR_INK,
                    family=FONT_FAMILY,
                ),
                marker=dict(
                    size=subset["marker_size"],
                    color=cat_color,
                    symbol=cat_symbol,
                    line=dict(color=COLOR_CARD, width=1.5),
                    opacity=0.88,
                ),
                customdata=customdata,
                hovertemplate=(
                    "<b>State of %{customdata[0]}</b><br>"
                    "Avg Delivery Latency: %{x:.1f} days<br>"
                    "CSAT Review Score: %{y:.2f} / 5.00<br>"
                    "Late Delivery Rate: %{customdata[1]:.1f}%<br>"
                    "Total Order Volume: %{customdata[2]:,}<br>"
                    "Gross Revenue: R$ %{customdata[3]:,.2f}<br>"
                    "AOV: R$ %{customdata[4]:,.2f}<extra></extra>"
                ),
            )
        )

    # Benchmark 14-Day Delivery Threshold Line
    fig.add_vline(
        x=14.0,
        line_dash="dash",
        line_color=COLOR_MUTED,
        line_width=1.5,
    )
    fig.add_annotation(
        x=14.0,
        y=df["avg_review_score"].max() + 0.03,
        text="14-Day SLA Target",
        showarrow=False,
        font=dict(size=10, color=COLOR_MUTED),
        xanchor="center",
        bgcolor="rgba(248, 250, 252, 0.9)",
        bordercolor=COLOR_BORDER,
        borderwidth=1,
    )

    # Benchmark CSAT 4.0 Reference Line
    fig.add_hline(
        y=4.0,
        line_dash="dot",
        line_color=COLOR_LIGHT_MUTED,
        line_width=1.0,
    )

    apply_executive_theme(
        fig,
        title="State Delivery Days vs CSAT Score",
        margin=dict(l=60, r=20, t=50, b=40),
        height=290,
        show_legend=True,
    )

    fig.update_layout(
        xaxis=dict(
            title="Average Delivery Transit Duration (Days)",
            range=[min(df["avg_delivery_days"].min() - 1.5, 7.0), df["avg_delivery_days"].max() + 2.0],
        ),
        yaxis=dict(
            title="Average Customer Review Score (CSAT 1-5)",
            range=[df["avg_review_score"].min() - 0.08, df["avg_review_score"].max() + 0.08],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
        ),
    )
    return fig


# ==============================================================================
# FIGURE 4: Delivery Review Score Cliff
# ==============================================================================
def build_figure_4_delivery_cliff(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Builds Figure 4: Delivery Latency vs Review Score Cliff bubble scatter.
    
    Bubble scatter: X = Delivery Days, Y = Review Score 1-5, Size = Orders, Color = Late Delivery Rate.
    Single subtle 14-day SLA benchmark line, zero static callouts.
    """
    if df is None:
        df = load_delivery_review()
    if df.empty:
        return create_empty_figure("Delivery Latency vs Review Score Cliff")

    df = df.sort_values("review_score", ascending=True).reset_index(drop=True)

    # Bubble size scaled proportionally by order volume
    min_orders, max_orders = df["orders"].min(), df["orders"].max()
    sizes = 14 + 32 * np.sqrt(
        (df["orders"] - min_orders) / max(max_orders - min_orders, 1)
    )

    customdata = np.stack((df["orders"],), axis=-1)

    fig = go.Figure()

    # Subtle connecting trendline
    fig.add_trace(
        go.Scatter(
            x=df["average_delivery_days"],
            y=df["review_score"],
            mode="lines",
            line=dict(color=COLOR_BORDER, width=2, dash="solid"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Bubble scatter points: X = Delivery Days, Y = Review Score 1-5, Size = Orders, Color = Late Rate
    fig.add_trace(
        go.Scatter(
            x=df["average_delivery_days"],
            y=df["review_score"],
            mode="markers",
            marker=dict(
                size=sizes,
                color=df["late_delivery_rate"],
                colorscale=[
                    [0.0, COLOR_TARGET],     # Green #16A34A at lowest late rate
                    [0.35, COLOR_STRATEGIC], # Teal #0D9488
                    [0.6, "#F59E0B"],        # Amber
                    [1.0, COLOR_ALERT],      # Red #DC2626 at 37.8% late
                ],
                showscale=False,
                line=dict(color=COLOR_CARD, width=1.5),
                opacity=0.92,
            ),
            customdata=customdata,
            hovertemplate=(
                "<b>Rating: %{y} Stars</b><br>"
                "Average Delivery: <b>%{x:.1f} Days</b><br>"
                "Late Delivery Rate: <b>%{marker.color:.1f}%</b><br>"
                "Order Volume: <b>%{customdata[0]:,.0f} orders</b><extra></extra>"
            ),
            showlegend=False,
        )
    )

    # ONLY ONE subtle vertical reference line at x=14: dashed red (#DC2626) with annotation "14-Day SLA Target"
    fig.add_vline(
        x=14.0,
        line_dash="dash",
        line_color=COLOR_ALERT,
        line_width=1.5,
        annotation_text="14-Day SLA Target",
        annotation_position="top right",
        annotation_font=dict(size=10, color=COLOR_ALERT, family=FONT_FAMILY),
    )

    apply_executive_theme(
        fig,
        title="Delivery Latency vs Review Score Cliff",
        margin=dict(l=60, r=25, t=30, b=28),
        height=290,
        show_legend=False,
    )

    fig.update_layout(
        xaxis=dict(
            title="Average Delivery Duration (Days)",
            range=[9.0, 23.5],
        ),
        yaxis=dict(
            title="Review Score",
            tickmode="array",
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"],
            range=[0.5, 5.5],
        ),
    )
    return fig


# ==============================================================================
# FIGURE 5: Customer Spend Distribution & Lifetime Value
# ==============================================================================
def build_figure_5_customer_value(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Builds Figure 5: Customer Spend Distribution (One-Time vs Repeat).
    
    MUST use normalized probability density (histnorm="probability density") to prevent
    the ~3% repeat volume from being visually crushed by 97% one-time buyers.
    Strategic Accent Teal (#0D9488) for Repeat Buyers, Corporate Core Navy (#1E3A8A)
    for One-Time Customers.
    """
    if df is None:
        df = load_customer_spend_dist()
    if df.empty:
        return create_empty_figure("Figure 5: Customer Lifetime Spend Distribution")

    # Clip distribution at 99th percentile (R$ 800) for clean density visualization
    spend_cap = 800.0
    df_filtered = df[df["total_spend"] <= spend_cap].copy()

    df_repeat = df_filtered[df_filtered["customer_type"] == "Repeat Customer"]
    df_onetime = df_filtered[df_filtered["customer_type"] == "One-Time Customer"]

    # Calculate medians for annotations (full dataset medians)
    median_repeat = df[df["customer_type"] == "Repeat Customer"]["total_spend"].median()
    median_onetime = df[df["customer_type"] == "One-Time Customer"]["total_spend"].median()

    fig = go.Figure()

    # One-Time Buyers Trace
    fig.add_trace(
        go.Histogram(
            x=df_onetime["total_spend"],
            histnorm="probability density",
            name="One-Time Customer (97.0%)",
            marker=dict(color=COLOR_CORPORATE),
            opacity=0.55,
            xbins=dict(start=0, end=spend_cap, size=20),
            hovertemplate=(
                "<b>One-Time Customer</b><br>"
                "Spend Range: R$ %{x:,.0f} - R$ %{x+20:,.0f}<br>"
                "Probability Density: %{y:.5f}<extra></extra>"
            ),
        )
    )

    # Repeat Buyers Trace
    fig.add_trace(
        go.Histogram(
            x=df_repeat["total_spend"],
            histnorm="probability density",
            name="Repeat Customer (3.0%)",
            marker=dict(color=COLOR_STRATEGIC),
            opacity=0.75,
            xbins=dict(start=0, end=spend_cap, size=20),
            hovertemplate=(
                "<b>Repeat Customer</b><br>"
                "Spend Range: R$ %{x:,.0f} - R$ %{x+20:,.0f}<br>"
                "Probability Density: %{y:.5f}<extra></extra>"
            ),
        )
    )

    # Median Line for Repeat Customers
    fig.add_vline(
        x=median_repeat,
        line_dash="dash",
        line_color=COLOR_STRATEGIC,
        line_width=2,
    )
    fig.add_annotation(
        x=median_repeat,
        y=0.0075,
        text=f"Repeat Median: R$ {median_repeat:,.0f}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor=COLOR_STRATEGIC,
        ax=55,
        ay=-35,
        bgcolor=COLOR_CARD,
        bordercolor=COLOR_STRATEGIC,
        borderwidth=1,
        font=dict(size=10, color=COLOR_STRATEGIC),
    )

    # Median Line for One-Time Customers
    fig.add_vline(
        x=median_onetime,
        line_dash="dot",
        line_color=COLOR_CORPORATE,
        line_width=1.5,
    )
    fig.add_annotation(
        x=median_onetime,
        y=0.0090,
        text=f"One-Time Median: R$ {median_onetime:,.0f}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor=COLOR_CORPORATE,
        ax=-55,
        ay=-35,
        bgcolor=COLOR_CARD,
        bordercolor=COLOR_CORPORATE,
        borderwidth=1,
        font=dict(size=10, color=COLOR_CORPORATE),
    )

    apply_executive_theme(
        fig,
        title="Customer Spend Density: One-Time vs Repeat",
        margin=dict(l=35, r=25, t=30, b=28),
        height=280,
        show_legend=True,
    )

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            title="Total Customer Spend (R$) [Clipped at R$ 800 for clarity]",
            tickprefix="R$ ",
            range=[0, spend_cap],
        ),
        yaxis=dict(
            title="Probability Density",
            showgrid=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
        ),
    )
    return fig


# ==============================================================================
# FIGURE 6: Payment Rails Breakdown
# ==============================================================================
def build_figure_6_payment_rails(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Builds Figure 6: Payment Rails Ranked Horizontal Bar.
    
    NEVER a 5-point scatter plot. Displays ranked payment methods with inline GMV %
    and AOV annotations using Corporate Core Navy (#1E3A8A) and Strategic Accent (#0D9488).
    """
    if df is None:
        df = load_payment_summary()
    if df.empty:
        return create_empty_figure("Figure 6: Payment Rails Breakdown")

    # Sort ascending so highest GMV appears at the top
    df_sorted = df.sort_values("total_value", ascending=True).reset_index(drop=True)

    name_mapping = {
        "credit_card": "Credit Card",
        "boleto": "Boleto Bancário",
        "voucher": "Voucher",
        "debit_card": "Debit Card",
    }
    formatted_rails = [name_mapping.get(p, p.replace("_", " ").title()) for p in df_sorted["payment_type"]]

    # Total GMV sum for calculating share safely
    total_gmv = df_sorted["total_value"].sum()
    shares = safe_divide(df_sorted["total_value"], total_gmv, 100.0)

    # Color allocation: Credit Card is dominant corporate rail, others differentiated
    colors = [
        COLOR_LIGHT_MUTED if p == "debit_card"
        else COLOR_MUTED if p == "voucher"
        else COLOR_STRATEGIC if p == "boleto"
        else COLOR_CORPORATE
        for p in df_sorted["payment_type"]
    ]

    customdata = np.stack(
        (
            df_sorted["transactions"],
            df_sorted["average_value"],
            shares,
            df_sorted["label"],
        ),
        axis=-1,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_sorted["total_value"],
            y=formatted_rails,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            text=df_sorted["label"],
            textposition="outside",
            cliponaxis=False,
            customdata=customdata,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Total GMV: R$ %{x:,.2f}<br>"
                "Transaction Volume: %{customdata[0]:,}<br>"
                "Average Ticket (AOV): R$ %{customdata[1]:,.2f}<br>"
                "GMV Share: %{customdata[2]:.1f}%<extra></extra>"
            ),
            showlegend=False,
        )
    )

    apply_executive_theme(
        fig,
        title="Payment Rails GMV Breakdown & AOV",
        margin=dict(l=95, r=120, t=30, b=25),
        height=240,
        show_legend=False,
    )

    max_val = df_sorted["total_value"].max() * 1.30
    fig.update_layout(
        xaxis=dict(
            title="Total Processed GMV (R$)",
            tickprefix="R$ ",
            range=[0, max_val],
        ),
        yaxis=dict(title=""),
    )
    return fig


# ==============================================================================
# FIGURE 7: Seller Supply Hub (Top 20 Sellers)
# ==============================================================================
def build_figure_7_seller_hub(
    df: Optional[pd.DataFrame] = None,
    state: Optional[str] = "ALL",
    top_n: int = 20,
) -> go.Figure:
    """Builds Figure 7: Top Marketplace Sellers ranked descending by gross revenue.
    
    Strictly ranked horizontal bar chart.
    Dynamic title:
      - 'Top 20 Marketplace Sellers (National)' if state is 'ALL'
      - 'Top Sellers: {state}' if a state is selected
    Bar text: 'R$ {rev}k | {orders} ord'
    """
    if df is None:
        df = load_seller_summary()
    if df.empty:
        return create_empty_figure("Figure 7: Top Sellers Supply Hub")

    df_filtered = df.copy()
    if state and state != "ALL":
        df_filtered = df_filtered[df_filtered["seller_state"] == state]

    if df_filtered.empty:
        title_text = f"Top Sellers: {state}" if state and state != "ALL" else "Top 20 Marketplace Sellers (National)"
        return create_empty_figure(title_text)

    # Strictly rank sellers descending by gross revenue, take top_n, then reverse for horizontal bar
    df_top = (
        df_filtered.sort_values("revenue", ascending=False)
        .head(top_n)
        .iloc[::-1]
        .copy()
        .reset_index(drop=True)
    )

    seller_labels = [
        f"Seller #{s[:8]} ({st})" for s, st in zip(df_top["seller_id"], df_top["seller_state"])
    ]

    # Bar colors: Navy for SP, Teal for other/expansion states
    colors = [
        COLOR_CORPORATE if st == "SP" else COLOR_STRATEGIC
        for st in df_top["seller_state"]
    ]

    customdata = np.stack(
        (
            df_top["seller_id"],
            df_top["seller_state"],
            df_top["orders"],
            df_top["items"],
            df_top["revenue_per_order"],
        ),
        axis=-1,
    )

    # Clean text formatting: "R$ {rev}k | {orders} ord"
    text_labels = [
        f"R$ {r/1e3:,.0f}k | {o:,} ord"
        for r, o in zip(df_top["revenue"], df_top["orders"])
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_top["revenue"],
            y=seller_labels,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            text=text_labels,
            textposition="outside",
            cliponaxis=False,
            customdata=customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Origin State: %{customdata[1]}<br>"
                "Gross Revenue: R$ %{x:,.2f}<br>"
                "Orders Fulfilled: %{customdata[2]:,}<br>"
                "Items Dispatched: %{customdata[3]:,}<br>"
                "Revenue / Order (AOV): R$ %{customdata[4]:,.2f}<extra></extra>"
            ),
            showlegend=False,
        )
    )

    title_text = "Top 20 Marketplace Sellers (National)" if not state or state == "ALL" else f"Top Sellers: {state}"

    apply_executive_theme(
        fig,
        title=title_text,
        margin=dict(l=135, r=85, t=30, b=25),
        height=280,
        show_legend=False,
    )

    max_rev = df_top["revenue"].max() * 1.32 if not df_top.empty else 1.0
    fig.update_layout(
        xaxis=dict(
            title="Seller Gross Revenue (R$)",
            tickprefix="R$ ",
            range=[0, max_rev],
        ),
        yaxis=dict(
            title="",
            categoryorder="array",
            categoryarray=seller_labels,
        ),
    )
    return fig


# ==============================================================================
# FIGURE 8: Geographic Revenue: Southeast Core vs Expansion States
# ==============================================================================
def build_figure_8_geo_revenue(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Builds Figure 8: Geographic Revenue Ranked Horizontal Bar.
    
    Compares Southeast Core states (Navy-900: #1E3A8A) with Peripheral Expansion
    markets (Teal-600: #0D9488) along with inline GMV % labels.
    """
    if df is None:
        df = load_geo_revenue()
    if df.empty:
        return create_empty_figure("Figure 8: Geographic Revenue Ranking")

    df_sorted = df.sort_values("revenue", ascending=True).reset_index(drop=True)

    fig = go.Figure()

    # Southeast Core Trace
    df_core = df_sorted[df_sorted["market_tier"] == "Southeast Core"]
    if not df_core.empty:
        customdata_core = np.stack(
            (
                df_core["market_tier"],
                df_core["customers"],
                df_core["orders"],
                df_core["revenue_per_customer"],
            ),
            axis=-1,
        )
        fig.add_trace(
            go.Bar(
                x=df_core["revenue"],
                y=df_core["customer_state"],
                orientation="h",
                name="Southeast Core",
                marker=dict(
                    color=COLOR_CORPORATE,
                    line=dict(color="rgba(255,255,255,0.2)", width=1),
                ),
                text=df_core["label"],
                textposition="outside",
                cliponaxis=False,
                customdata=customdata_core,
                hovertemplate=(
                    "<b>State of %{y}</b> (Southeast Core)<br>"
                    "Total Revenue: R$ %{x:,.2f}<br>"
                    "Unique Customers: %{customdata[1]:,}<br>"
                    "Order Volume: %{customdata[2]:,}<br>"
                    "Revenue / Customer: R$ %{customdata[3]:,.2f}<extra></extra>"
                ),
            )
        )

    # Expansion Markets Trace
    df_exp = df_sorted[df_sorted["market_tier"] == "Expansion Markets"]
    if not df_exp.empty:
        customdata_exp = np.stack(
            (
                df_exp["market_tier"],
                df_exp["customers"],
                df_exp["orders"],
                df_exp["revenue_per_customer"],
            ),
            axis=-1,
        )
        fig.add_trace(
            go.Bar(
                x=df_exp["revenue"],
                y=df_exp["customer_state"],
                orientation="h",
                name="Expansion Markets",
                marker=dict(
                    color=COLOR_STRATEGIC,
                    line=dict(color="rgba(255,255,255,0.2)", width=1),
                ),
                text=df_exp["label"],
                textposition="outside",
                cliponaxis=False,
                customdata=customdata_exp,
                hovertemplate=(
                    "<b>State of %{y}</b> (Expansion Market)<br>"
                    "Total Revenue: R$ %{x:,.2f}<br>"
                    "Unique Customers: %{customdata[1]:,}<br>"
                    "Order Volume: %{customdata[2]:,}<br>"
                    "Revenue / Customer: R$ %{customdata[3]:,.2f}<extra></extra>"
                ),
            )
        )

    apply_executive_theme(
        fig,
        title="Sales by Region: Southeast vs Expansion",
        margin=dict(l=35, r=85, t=30, b=25),
        height=280,
        show_legend=True,
    )

    max_rev = df_sorted["revenue"].max() * 1.25
    fig.update_layout(
        xaxis=dict(
            title="Sales (R$)",
            tickprefix="R$ ",
            range=[0, max_rev],
        ),
        yaxis=dict(title=""),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
        ),
    )
    return fig


# ==============================================================================
# FIGURE 9: Inbound Lead Conversion Funnel
# ==============================================================================
def build_figure_9_lead_conversion(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Builds Figure 9: Marketing Lead Channels & Conversion Rates.
    
    Ranked horizontal bar showing conversion efficiency across acquisition channels.
    Benchmark dashed red line at x=10.5% labeled 'Platform Avg (10.5%)'.
    Uniform Teal fill (#0D9488) for channels beating benchmark, and Muted Slate (#94A3B8)
    for channels below benchmark, with explicit legend explaining Above vs Below Benchmark.
    """
    if df is None:
        df = load_lead_origin()
    if df.empty:
        return create_empty_figure("Figure 9: Lead Conversion by Marketing Channel")

    # Safe conversion rate check
    rates = safe_divide(df["conversions"], df["leads"], 100.0)
    df_sorted = df.copy()
    df_sorted["rate"] = rates
    df_sorted = df_sorted.sort_values("rate", ascending=True).reset_index(drop=True)
    df_sorted["origin_fmt"] = [o.replace("_", " ").title() for o in df_sorted["origin"]]

    BENCHMARK_RATE = 10.5

    sub_above = df_sorted[df_sorted["rate"] >= BENCHMARK_RATE]
    sub_below = df_sorted[df_sorted["rate"] < BENCHMARK_RATE]

    fig = go.Figure()

    # Above Benchmark Trace (Teal #0D9488)
    if not sub_above.empty:
        customdata_above = np.stack(
            (
                sub_above["conversions"],
                sub_above["leads"],
                sub_above["channel_type"],
            ),
            axis=-1,
        )
        text_above = [
            f"{r:.1f}% ({c:,}/{l:,})"
            for r, c, l in zip(sub_above["rate"], sub_above["conversions"], sub_above["leads"])
        ]
        fig.add_trace(
            go.Bar(
                x=sub_above["rate"],
                y=sub_above["origin_fmt"],
                orientation="h",
                name="Above Benchmark",
                marker=dict(
                    color=COLOR_STRATEGIC,  # Teal #0D9488
                    line=dict(color="rgba(255,255,255,0.2)", width=1),
                ),
                text=text_above,
                textposition="outside",
                cliponaxis=False,
                customdata=customdata_above,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Status: Above Benchmark (≥ 10.5%)<br>"
                    "Conversion Rate: %{x:.2f}%<br>"
                    "Closed Won Deals: %{customdata[0]:,}<br>"
                    "Qualified Leads (MQLs): %{customdata[1]:,}<extra></extra>"
                ),
            )
        )

    # Below Benchmark Trace (Muted Slate #94A3B8)
    if not sub_below.empty:
        customdata_below = np.stack(
            (
                sub_below["conversions"],
                sub_below["leads"],
                sub_below["channel_type"],
            ),
            axis=-1,
        )
        text_below = [
            f"{r:.1f}% ({c:,}/{l:,})"
            for r, c, l in zip(sub_below["rate"], sub_below["conversions"], sub_below["leads"])
        ]
        fig.add_trace(
            go.Bar(
                x=sub_below["rate"],
                y=sub_below["origin_fmt"],
                orientation="h",
                name="Below Benchmark",
                marker=dict(
                    color="#94A3B8",  # Muted Slate
                    line=dict(color="rgba(255,255,255,0.2)", width=1),
                ),
                text=text_below,
                textposition="outside",
                cliponaxis=False,
                customdata=customdata_below,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Status: Below Benchmark (< 10.5%)<br>"
                    "Conversion Rate: %{x:.2f}%<br>"
                    "Closed Won Deals: %{customdata[0]:,}<br>"
                    "Qualified Leads (MQLs): %{customdata[1]:,}<extra></extra>"
                ),
            )
        )

    # Benchmark 10.5% Reference Line
    fig.add_vline(
        x=BENCHMARK_RATE,
        line_dash="dash",
        line_color=COLOR_ALERT,  # Red #DC2626
        line_width=1.5,
        annotation_text="Platform Avg (10.5%)",
        annotation_position="top left",
        annotation_font=dict(size=10, color=COLOR_ALERT, family=FONT_FAMILY),
    )

    apply_executive_theme(
        fig,
        title="Lead-to-Deal Conversion by Channel",
        margin=dict(l=110, r=95, t=30, b=25),
        height=280,
        show_legend=True,
    )

    max_rate = max(df_sorted["rate"].max() * 1.35, 24.0)
    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            title="Lead Conversion Rate (%)",
            ticksuffix="%",
            range=[0, max_rate],
        ),
        yaxis=dict(
            title="",
            categoryorder="array",
            categoryarray=df_sorted["origin_fmt"].tolist(),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
        ),
    )
    return fig


# ==============================================================================
# FIGURE 10: Business Segment Pipeline (Closed Deals vs Sales Velocity)
# ==============================================================================
def build_figure_10_closed_deals(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Builds Figure 10: Closed Deals by Business Segment vs Sales Velocity.
    
    Ranked horizontal bar chart comparing closed merchant deals with sales cycle velocity.
    Bars colored by avg_sales_cycle using continuous color scale Blues_r (Darker = Faster onboarding).
    Colorbar legend on the right titled 'Avg Days<br>to Close' with clean tick marks (30d, 50d, 70d).
    Bar text displays: '{deals} deals ({cycle:.0f}d cycle)'.
    """
    if df is None:
        df = load_segment_pipeline()
    if df.empty:
        return create_empty_figure("Figure 10: Closed Deals vs Sales Velocity")

    # Sort ascending by closed_deals so largest segment is at the top
    df_sorted = df.sort_values("closed_deals", ascending=True).reset_index(drop=True)

    formatted_segments = [
        s.replace("_", " ").title() for s in df_sorted["business_segment"]
    ]

    customdata = np.stack(
        (
            df_sorted["avg_sales_cycle"],
            df_sorted["closed_deals"],
        ),
        axis=-1,
    )

    # Inline text: "{deals} deals ({cycle:.0f}d cycle)"
    text_labels = [
        f"{deals:,} deals ({cycle:.0f}d cycle)"
        for deals, cycle in zip(df_sorted["closed_deals"], df_sorted["avg_sales_cycle"])
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_sorted["closed_deals"],
            y=formatted_segments,
            orientation="h",
            marker=dict(
                color=df_sorted["avg_sales_cycle"],
                colorscale="Blues_r",
                showscale=True,
                cmin=20,
                cmax=70,
                colorbar=dict(
                    title=dict(text="Avg Days<br>to Close", font=dict(size=10, family=FONT_FAMILY)),
                    tickvals=[30, 50, 70],
                    ticktext=["30d", "50d", "70d"],
                    tickfont=dict(size=9, family=FONT_FAMILY),
                    len=0.9,
                    thickness=12,
                    x=1.02,
                    xpad=8,
                ),
                line=dict(color="#cbd5e1", width=1),
            ),
            text=text_labels,
            textposition="outside",
            cliponaxis=False,
            customdata=customdata,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Closed Won Deals: %{x:,} merchants<br>"
                "Average Sales Cycle: %{customdata[0]:.1f} days<extra></extra>"
            ),
            showlegend=False,
        )
    )

    apply_executive_theme(
        fig,
        title="Merchant Deals vs Sales Velocity",
        margin=dict(l=145, r=70, t=30, b=25),
        height=280,
        show_legend=False,
    )

    max_deals = df_sorted["closed_deals"].max() * 1.38
    fig.update_layout(
        xaxis=dict(
            title="Closed Merchant Deals (Count)",
            range=[0, max_deals],
        ),
        yaxis=dict(title=""),
    )
    return fig


# ==============================================================================
# ALIASES AND MASTER FIGURE BUILDER
# ==============================================================================
create_figure_1 = build_figure_1_monthly_revenue
create_figure_2 = build_figure_2_category_performance
create_figure_3 = build_figure_3_state_analysis
create_figure_4 = build_figure_4_delivery_cliff
create_figure_5 = build_figure_5_customer_value
create_figure_6 = build_figure_6_payment_rails
create_figure_7 = build_figure_7_seller_hub
create_figure_8 = build_figure_8_geo_revenue
create_figure_9 = build_figure_9_lead_conversion
create_figure_10 = build_figure_10_closed_deals


def build_all_figures(data_dict: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, go.Figure]:
    """Pure master function returning Figures 1 through 10 as a dictionary of Plotly figures."""
    if data_dict is None:
        data_dict = {}

    return {
        "fig1": build_figure_1_monthly_revenue(data_dict.get("monthly_revenue")),
        "fig2": build_figure_2_category_performance(data_dict.get("category_summary")),
        "fig3": build_figure_3_state_analysis(data_dict.get("state_analysis")),
        "fig4": build_figure_4_delivery_cliff(data_dict.get("delivery_review")),
        "fig5": build_figure_5_customer_value(data_dict.get("customer_spend_dist")),
        "fig6": build_figure_6_payment_rails(data_dict.get("payment_summary")),
        "fig7": build_figure_7_seller_hub(data_dict.get("seller_summary")),
        "fig8": build_figure_8_geo_revenue(data_dict.get("geo_revenue")),
        "fig9": build_figure_9_lead_conversion(data_dict.get("lead_origin")),
        "fig10": build_figure_10_closed_deals(data_dict.get("segment_pipeline")),
    }
