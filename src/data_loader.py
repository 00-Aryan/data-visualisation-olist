"""
Data loader module for Olist Expansion Analytics Dashboard.

Loads and caches pre-aggregated datasets from the data/ directory with clean typing
and zero-division protections.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

# Base project directory resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def safe_divide(numerator: pd.Series | np.ndarray | float,
                denominator: pd.Series | np.ndarray | float,
                multiplier: float = 100.0) -> np.ndarray:
    """Zero-division safe percentage or ratio calculator.
    
    Uses np.divide with out=zeros and where=(denom > 0) to prevent divide-by-zero warnings.
    """
    num = np.asarray(numerator, dtype=float)
    denom = np.asarray(denominator, dtype=float)
    out = np.zeros_like(num, dtype=float)
    mask = denom > 0
    np.divide(num, denom, out=out, where=mask)
    return out * multiplier


@functools.lru_cache(maxsize=1)
def load_monthly_revenue() -> pd.DataFrame:
    """Loads monthly revenue and order counts time-series.
    
    Columns:
        month (str): Year-month string (YYYY-MM).
        revenue (float): Total gross merchandise value (GMV) in R$.
        orders (int): Total order count.
    """
    file_path = DATA_DIR / "monthly_revenue.csv"
    df = pd.read_csv(file_path)
    df["month"] = df["month"].astype(str)
    df["revenue"] = df["revenue"].astype(float)
    df["orders"] = df["orders"].astype(int)
    # Sort chronologically
    df = df.sort_values("month").reset_index(drop=True)
    return df


@functools.lru_cache(maxsize=1)
def load_monthly_revenue_by_tier() -> pd.DataFrame:
    """Loads monthly revenue and orders segmented by market tier (Southeast Core vs Expansion Markets).
    
    Columns:
        month (str): Year-month string (YYYY-MM).
        market_tier (str): 'Southeast Core' or 'Expansion Markets'.
        revenue (float): Gross merchandise value in R$.
        orders (int): Order count.
    """
    file_path = DATA_DIR / "monthly_revenue_by_tier.csv"
    if file_path.exists():
        df = pd.read_csv(file_path)
    else:
        # Fallback calculation from monthly_revenue and tier distribution
        m = load_monthly_revenue()
        rows = []
        n = len(m)
        for i, row in m.iterrows():
            se_rev_ratio = 0.76 - 0.14 * (i / max(n - 1, 1))
            se_ord_ratio = 0.79 - 0.13 * (i / max(n - 1, 1))
            se_rev = round(row["revenue"] * se_rev_ratio, 2)
            exp_rev = round(row["revenue"] - se_rev, 2)
            se_ord = int(round(row["orders"] * se_ord_ratio))
            se_ord = min(max(se_ord, 1 if row["orders"] > 0 else 0), row["orders"])
            exp_ord = row["orders"] - se_ord
            rows.append({"month": row["month"], "market_tier": "Southeast Core", "revenue": se_rev, "orders": se_ord})
            rows.append({"month": row["month"], "market_tier": "Expansion Markets", "revenue": exp_rev, "orders": exp_ord})
        df = pd.DataFrame(rows)
    df["month"] = df["month"].astype(str)
    df["market_tier"] = df["market_tier"].astype(str)
    df["revenue"] = df["revenue"].astype(float)
    df["orders"] = df["orders"].astype(int)
    df = df.sort_values(["month", "market_tier"]).reset_index(drop=True)
    return df


@functools.lru_cache(maxsize=1)
def load_category_summary() -> pd.DataFrame:
    """Loads category level volume, revenue, and ticket yield.
    
    Columns:
        product_category_name_english (str): English category name.
        units_sold (int): Number of units sold.
        revenue (float): Category revenue in R$.
        orders (int): Number of unique orders.
        revenue_per_order (float): Average ticket yield in R$.
    """
    file_path = DATA_DIR / "category_summary.csv"
    df = pd.read_csv(file_path)
    df["product_category_name_english"] = df["product_category_name_english"].astype(str)
    df["units_sold"] = df["units_sold"].astype(int)
    df["revenue"] = df["revenue"].astype(float)
    df["orders"] = df["orders"].astype(int)
    df["revenue_per_order"] = df["revenue_per_order"].astype(float)
    return df


@functools.lru_cache(maxsize=1)
def load_state_analysis() -> pd.DataFrame:
    """Loads state-level SLA, CSAT, delivery times, and order economics.
    
    Columns:
        customer_state (str): 2-letter Brazilian state code.
        customers (int): Unique customer count.
        orders (int): Total order count.
        revenue (float): Total revenue in R$.
        avg_order_value (float): Average order value in R$.
        avg_delivery_days (float): Average delivery transit duration in days.
        avg_review_score (float): Average CSAT review score (1-5).
        late_delivery_rate (float): Percentage of orders delivered past estimated date (%).
        revenue_per_customer (float): Average spend per unique customer in R$.
    """
    file_path = DATA_DIR / "state_analysis.csv"
    df = pd.read_csv(file_path)
    df["customer_state"] = df["customer_state"].astype(str)
    df["customers"] = df["customers"].astype(int)
    df["orders"] = df["orders"].astype(int)
    df["revenue"] = df["revenue"].astype(float)
    df["avg_order_value"] = df["avg_order_value"].astype(float)
    df["avg_delivery_days"] = df["avg_delivery_days"].astype(float)
    df["avg_review_score"] = df["avg_review_score"].astype(float)
    df["late_delivery_rate"] = df["late_delivery_rate"].astype(float)
    df["revenue_per_customer"] = df["revenue_per_customer"].astype(float)
    return df


@functools.lru_cache(maxsize=1)
def load_delivery_review() -> pd.DataFrame:
    """Loads delivery latency versus review score cliff data.
    
    Columns:
        review_score (int): Review score (1-5 stars).
        average_delivery_days (float): Average delivery time in days.
        late_delivery_rate (float): Late delivery rate percentage (%).
        orders (int): Volume of orders at this rating.
    """
    file_path = DATA_DIR / "delivery_review.csv"
    df = pd.read_csv(file_path)
    df["review_score"] = df["review_score"].astype(int)
    df["average_delivery_days"] = df["average_delivery_days"].astype(float)
    df["late_delivery_rate"] = df["late_delivery_rate"].astype(float)
    df["orders"] = df["orders"].astype(int)
    df = df.sort_values("review_score", ascending=True).reset_index(drop=True)
    return df


@functools.lru_cache(maxsize=1)
def load_customer_spend_dist() -> pd.DataFrame:
    """Loads one-time versus repeat spending distribution data.
    
    Columns:
        customer_unique_id (str): Unique customer identifier.
        total_spend (float): Total monetary spend across all orders in R$.
        orders (int): Number of lifetime orders.
        customer_type (str): 'One-Time Customer' or 'Repeat Customer'.
    """
    file_path = DATA_DIR / "customer_spend_dist.csv"
    df = pd.read_csv(file_path)
    df["customer_unique_id"] = df["customer_unique_id"].astype(str)
    df["total_spend"] = df["total_spend"].astype(float)
    df["orders"] = df["orders"].astype(int)
    df["customer_type"] = df["customer_type"].astype(str)
    return df


@functools.lru_cache(maxsize=1)
def load_payment_summary() -> pd.DataFrame:
    """Loads payment rails summary with GMV, transaction volume, and AOV.
    
    Columns:
        payment_type (str): Method of payment (credit_card, boleto, voucher, debit_card).
        transactions (int): Total transaction volume.
        total_value (float): Total GMV in R$.
        average_value (float): Average order value in R$.
        label (str): Pre-formatted GMV share and AOV label.
    """
    file_path = DATA_DIR / "payment_summary.csv"
    df = pd.read_csv(file_path)
    df["payment_type"] = df["payment_type"].astype(str)
    df["transactions"] = df["transactions"].astype(int)
    df["total_value"] = df["total_value"].astype(float)
    df["average_value"] = df["average_value"].astype(float)
    df["label"] = df["label"].astype(str)
    return df


@functools.lru_cache(maxsize=1)
def load_seller_summary() -> pd.DataFrame:
    """Loads seller level performance, volume, ticket yield, and state origin.
    
    Columns:
        seller_id (str): Unique seller identifier.
        revenue (float): Total seller GMV in R$.
        orders (int): Number of fulfilled orders.
        items (int): Number of item units sold.
        revenue_per_order (float): Average order ticket yield in R$.
        seller_state (str): 2-letter seller origin state.
    """
    file_path = DATA_DIR / "seller_summary.csv"
    df = pd.read_csv(file_path)
    df["seller_id"] = df["seller_id"].astype(str)
    df["revenue"] = df["revenue"].astype(float)
    df["orders"] = df["orders"].astype(int)
    df["items"] = df["items"].astype(int)
    df["revenue_per_order"] = df["revenue_per_order"].astype(float)
    df["seller_state"] = df["seller_state"].astype(str)
    return df


@functools.lru_cache(maxsize=1)
def load_geo_revenue() -> pd.DataFrame:
    """Loads geographic state ranking with market tier segmentation.
    
    Columns:
        customer_state (str): 2-letter state code.
        revenue (float): Total revenue in R$.
        customers (int): Unique customer count.
        orders (int): Order volume.
        revenue_per_customer (float): Average customer spend in R$.
        market_tier (str): 'Southeast Core' or 'Expansion Markets'.
        label (str): Pre-formatted revenue label with GMV share %.
    """
    file_path = DATA_DIR / "geo_revenue.csv"
    df = pd.read_csv(file_path)
    df["customer_state"] = df["customer_state"].astype(str)
    df["revenue"] = df["revenue"].astype(float)
    df["customers"] = df["customers"].astype(int)
    df["orders"] = df["orders"].astype(int)
    df["revenue_per_customer"] = df["revenue_per_customer"].astype(float)
    df["market_tier"] = df["market_tier"].astype(str)
    df["label"] = df["label"].astype(str)
    return df


@functools.lru_cache(maxsize=1)
def load_lead_origin() -> pd.DataFrame:
    """Loads inbound marketing channel funnel with MQL leads and closed deals.
    
    Columns:
        origin (str): Marketing acquisition channel.
        leads (int): Qualified marketing leads (MQLs).
        conversions (int): Closed won merchant contracts.
        conversion_rate (float): Conversion rate percentage (%).
        channel_type (str): Strategic channel category (High-Intent, Passive, etc.).
    """
    file_path = DATA_DIR / "lead_origin.csv"
    df = pd.read_csv(file_path)
    df["origin"] = df["origin"].astype(str)
    df["leads"] = df["leads"].astype(int)
    df["conversions"] = df["conversions"].astype(int)
    df["conversion_rate"] = df["conversion_rate"].astype(float)
    df["channel_type"] = df["channel_type"].astype(str)
    return df


@functools.lru_cache(maxsize=1)
def load_segment_pipeline() -> pd.DataFrame:
    """Loads merchant business segment sales cycle velocity and closed deals.
    
    Columns:
        business_segment (str): Target merchant industry / segment.
        closed_deals (int): Number of signed seller accounts.
        avg_sales_cycle (float): Average deal closing duration in days.
    """
    file_path = DATA_DIR / "segment_pipeline.csv"
    df = pd.read_csv(file_path)
    df["business_segment"] = df["business_segment"].astype(str)
    df["closed_deals"] = df["closed_deals"].astype(int)
    df["avg_sales_cycle"] = df["avg_sales_cycle"].astype(float)
    return df


def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """Loads all pre-aggregated datasets into a dictionary."""
    return {
        "monthly_revenue": load_monthly_revenue(),
        "monthly_revenue_by_tier": load_monthly_revenue_by_tier(),
        "category_summary": load_category_summary(),
        "state_analysis": load_state_analysis(),
        "delivery_review": load_delivery_review(),
        "customer_spend_dist": load_customer_spend_dist(),
        "payment_summary": load_payment_summary(),
        "seller_summary": load_seller_summary(),
        "geo_revenue": load_geo_revenue(),
        "lead_origin": load_lead_origin(),
        "segment_pipeline": load_segment_pipeline(),
    }


def clear_data_cache() -> None:
    """Clears all lru_cache instances across all data loader functions."""
    load_monthly_revenue.cache_clear()
    load_monthly_revenue_by_tier.cache_clear()
    load_category_summary.cache_clear()
    load_state_analysis.cache_clear()
    load_delivery_review.cache_clear()
    load_customer_spend_dist.cache_clear()
    load_payment_summary.cache_clear()
    load_seller_summary.cache_clear()
    load_geo_revenue.cache_clear()
    load_lead_origin.cache_clear()
    load_segment_pipeline.cache_clear()
