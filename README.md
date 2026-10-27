# E-commerce Dataset

An analytical study and interactive executive dashboard investigating marketplace growth dynamics, logistics bottlenecks, and seller supply concentration on Brazilian e-commerce platform Olist (2016–2018).

---

## 1. Project Overview & Background

Between late 2016 and mid-2018, Olist grew from a localized marketplace integrator into a national e-commerce platform across Brazil, processing over 100,000 orders worth roughly R$ 15.8 million in gross marketplace value (GMV). However, by the second quarter of 2018, monthly order volume plateaued near 7,000 to 7,500 orders per month, and total sales growth stalled.

This project investigates why platform growth flattened despite healthy buyer demand across northern, northeastern, and central expansion states. By analyzing 11 relational tables covering orders, order items, product categories, customer locations, seller registries, payments, reviews, and marketing funnels, the data reveals several interconnected operational bottlenecks:

### Key Empirical Findings

1. **The 14-Day Delivery Threshold & Review Score Collapse**
   - Customer review scores (CSAT) remain stable between 4.1 and 4.3 stars as long as fulfillment transit times stay under 12 to 14 days.
   - Once transit duration crosses the 14-day mark, customer satisfaction collapses sharply: 1-star reviews average 20.8 delivery days, and orders with late deliveries suffer a 37.8% failure rate. Over 68% of all 1-star ratings cite delivery delays rather than product defect issues.

2. **Supply Hub Concentration in São Paulo (SP)**
   - 75% of the top 20 grossing sellers on the marketplace (and over 70% of total fulfilled volume) operate from the state of São Paulo.
   - Because national inventory is heavily concentrated in the Southeast, orders shipped to buyers in distant regions must travel overland across several thousand kilometers, making long transit durations structural rather than accidental.

3. **Freight Overhead in Frontier States**
   - Customers in peripheral states—particularly in the North and Northeast (such as Alagoas `AL`, Maranhão `MA`, Ceará `CE`, and Paraíba `PB`)—exhibit higher average order values (R$ 215–250 per order) than customers in São Paulo (R$ 137).
   - However, freight costs in these frontier states swallow between 28% and 40% of the customer's total expenditure, with transit times averaging 19 to 25 days. High shipping friction suppresses transaction frequency among the platform's highest-spending potential customers.

4. **Low Repeat Purchase Rate (3.12%)**
   - Out of nearly 96,000 unique buyers, only 3.12% placed a second order.
   - When customers do return, their average spend more than doubles compared to one-time buyers (R$ 294 vs. R$ 138). However, after enduring multi-week fulfillment delays and costly freight on their initial order, the vast majority never make a second purchase.

5. **Merchant Acquisition Mismatch in the Commercial Funnel**
   - An examination of closed sales deals vs. product category demand reveals a structural pipeline imbalance.
   - The commercial merchant team heavily onboarded sellers in categories like *Home Decor* (105 closed merchants, average 51-day sales cycle) while acquiring relatively few merchants in *Bed, Bath & Table* (22 closed merchants), despite the latter being the platform's single largest volume driver (11,115 units sold).

---

## 2. Project Deliverables

This study is structured around three primary deliverables designed for academic review and executive decision-makers:

1. **Interactive Marketplace Dashboard (`src/`, `app.py`)**
   - A multi-page Dash application providing a high-density, Tableau/Power BI style executive workspace.
   - Allows users to interactively filter regional market tiers (Southeast Core vs. Expansion Markets), inspect state-level SLA delivery transit times against CSAT scores, examine seller hub concentration, and review inbound lead-to-deal conversion performance.

2. **Executive Presentation Deck**
   - A structured slide deck summarizing the core business problem, methodology, data visualisations, operational diagnosis, and four strategic recommendations:
     - Establishing decentralized fulfillment consolidation hubs in the Northeast.
     - Subsidizing frontier freight for high-AOV orders.
     - Aligning seller acquisition incentives toward everyday, high-turnover merchandise.
     - Introducing regional SLA promises at checkout to prevent customer expectation mismatch.

3. **Technical Report & Codebase**
   - Detailed pipeline documentation explaining table joins, data cleaning, metric formulas (safe division, delivery duration calculation, probability density modeling), and the complete reproducible source code.

---

## 3. Technical Choices & Visual Design

### Tech Stack & Architecture

- **Python 3.12+**: Foundation language for data engineering, statistical aggregation, and application backend.
- **Pandas**: Used for relational table joins, handling timestamps (`order_delivered_customer_date`, `order_estimated_delivery_date`), and computing aggregated summary metrics.
- **Plotly & Dash (`dash`, `dash-bootstrap-components`)**: Chosen for high-density reactive data visualization. Plotly provides precise hover templates, custom color scales, and dual-axis time series without external frontend dependencies.
- **Two-Stage Processing (Google Colab / ETL to Pre-Aggregated CSVs)**:
  - Rather than having the interactive web server process raw 100MB+ transaction tables on every user interaction, heavy joining and aggregation were completed beforehand in data notebooks.
  - The Dash application reads small, typed CSVs from `data/` (each under 25KB), resulting in sub-50ms cold starts, instantaneous tab transitions, and stable memory usage.

### Visual Design System

The visual design follows Edward Tufte’s principles of high data-to-ink ratio and clean executive dashboards:
- **Canvas & Containers**: Neutral Slate-50 background (`#F8FAFC`) with white card panels (`#FFFFFF`), subtle 1px border frames (`#cbd5e1`), and no drop shadows.
- **Restrained Semantic Palette**:
  - **Corporate Core (`#1E3A8A`, Navy-900)**: Anchors São Paulo baseline metrics and historical Southeast sales.
  - **Strategic Accent (`#0D9488`, Teal-600)**: Highlights high-value buyers, expansion market milestones, and channels exceeding performance benchmarks.
  - **Alert / Negative (`#DC2626`, Red-600)**: Strictly reserved for operational failures: 1-star reviews, SLA breaches, and delivery delays exceeding 14 days.
  - **Target / Positive (`#16A34A`, Green-600)**: Strictly reserved for on-time fulfillment and 5-star ratings.
- **Clutter Elimination**:
  - All static annotation boxes and decorative pill badges were removed in favor of clean reference lines and clean hover templates (`<b>Rating: %{y} Stars</b><br>Average Delivery: <b>%{x:.1f} Days</b>...`).
  - Dual distributions (such as customer spending) use normalized probability density (`histnorm="probability density"`) so small but crucial populations (the 3.12% repeat buyers) are not visually hidden by the 96.88% one-time cohort.

---

## 4. Repository Structure

```text
├── app.py                     # Dash application entry point and server initialization
├── data/                      # Pre-aggregated clean datasets for dashboard views
│   ├── category_summary.csv   # Top product categories by units, GMV, and ticket yield
│   ├── customer_spend_dist.csv# Spend distribution: one-time vs. repeat buyers
│   ├── delivery_review.csv    # Review score breakdown by delivery transit days
│   ├── geo_revenue.csv        # State-level revenue, customers, and market tiers
│   ├── lead_origin.csv        # Acquisition channels, qualified leads, and conversion rates
│   ├── monthly_revenue.csv    # National monthly GMV and order volume trajectory
│   ├── monthly_revenue_by_tier.csv # Monthly GMV split by Southeast Core vs Expansion
│   ├── payment_summary.csv    # Payment methods (Boleto, Credit, Voucher, Debit) & AOV
│   ├── segment_pipeline.csv   # Closed seller deals and average sales cycle length
│   ├── seller_summary.csv     # Individual seller revenue, orders, and origin states
│   └── state_analysis.csv     # State-level transit duration, CSAT, and late delivery rates
├── pyproject.toml             # Project configuration and dependency specifications
├── requirements.txt           # Pip-installable dependency manifest
├── src/                       # Application source modules
│   ├── __init__.py
│   ├── callbacks.py           # Reactive Dash callbacks (tier filters, state slicers)
│   ├── data_loader.py         # Type-annotated cached readers with LRU cache
│   ├── figures.py             # Pure builder functions generating configured Plotly figures
│   └── layout.py              # Power BI style high-density layout and metric tiles
└── README.md                  # Project documentation
```

---

## 5. Reproduction & Setup Instructions

Follow these steps to run the interactive dashboard locally:

### 1. Clone the Repository & Navigate to Directory
```bash
git clone https://github.com/00-Aryan/Data-Visualisation.git
cd Data-Visualisation
```

### 2. Set Up a Virtual Environment

Using standard Python `venv`:
```bash
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate
```

Or using `uv` (recommended for faster dependency resolution):
```bash
uv venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
*(Dependencies: `dash >= 4.4.1`, `dash-bootstrap-components >= 2.0.4`, `pandas >= 3.0.5`, `plotly >= 7.0.0`)*

### 4. Verify the Data Directory

Ensure the 11 pre-aggregated CSV files are present in `data/`. You can verify dataset integrity using:
```bash
python -c "from src.data_loader import load_state_analysis; df = load_state_analysis(); print(f'Loaded {len(df)} states successfully.')"
```

### 5. Launch the Dash Application

```bash
python app.py
```

Once started, open your web browser and navigate to:
```text
http://127.0.0.1:8050/
```

- **Overview & Growth Plateau (Tab 1)**: Inspect the monthly GMV trajectory, Black Friday 2017 volume peak, category yields, and regional market tier distributions.
- **Logistics & Delivery Cliff (Tab 2)**: Analyze state-by-state transit latency against customer review ratings, review the 14-day delivery cliff, and review payment rail breakdowns.
- **Supply Hub & Unit Economics (Tab 3)**: Examine the São Paulo supply concentration, explore customer lifetime spend density, evaluate marketing lead conversion against the 10.5% benchmark, and review commercial sales cycle velocities.
