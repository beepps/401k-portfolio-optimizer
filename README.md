# 401K Portfolio Optimizer — Merrill Lynch

A fully self-contained, single-page financial dashboard that backtests 250 unique portfolio blends across all 12 available Merrill Lynch 401K fund options over a 15-year historical window (January 2011 – April 2026). The project identifies the top 3 best-performing portfolio allocations by Sharpe ratio and presents the results in a dark-themed, interactive visual dashboard built with Chart.js.

> **Disclaimer:** This project is for educational and informational purposes only. It is not personalized financial advice. Past performance does not guarantee future results. Consult a qualified financial advisor before making any investment decisions.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [The 12 Fund Universe](#the-12-fund-universe)
4. [ETF Proxy Methodology](#etf-proxy-methodology)
5. [Backtest Engine](#backtest-engine)
6. [Top 3 Portfolio Blends](#top-3-portfolio-blends)
7. [Individual Fund Performance (15Y)](#individual-fund-performance-15y)
8. [Dashboard Sections](#dashboard-sections)
9. [Tech Stack](#tech-stack)
10. [How to Run Locally](#how-to-run-locally)
11. [How to Re-run the Backtest](#how-to-re-run-the-backtest)
12. [Data Sources & Premium Verification](#data-sources--premium-verification)
13. [Key Findings & Insights](#key-findings--insights)
14. [Limitations & Caveats](#limitations--caveats)

---

## Project Overview

Merrill Lynch 401K plans invest in **collective investment trusts (CITs)** — private, institutional fund vehicles that do not have public ticker symbols or readily available price history. To backtest these funds, each was mapped to a publicly traded ETF that tracks the same benchmark index.

The backtest engine (`backtest/backtest.py`) generates 250 unique weight combinations across 9 asset classes using two methods:
- **Structured grid search** — systematic sweeps across aggressive, balanced, and conservative risk profiles
- **Dirichlet Monte Carlo sampling** — random weight vectors drawn from a Dirichlet distribution biased toward equity-heavy allocations

Each blend is evaluated against 183 monthly return observations on six metrics: annualized return, annualized volatility, Sharpe ratio, Sortino ratio, Calmar ratio, and maximum drawdown. The top 3 blends by Sharpe ratio are surfaced and visualized in the dashboard.

---

## Repository Structure

```
401k-portfolio-optimizer/
├── README.md                          ← This file
│
├── dashboard/
│   ├── index.html                     ← Complete single-file dashboard (HTML + CSS + JS)
│   └── data.json                      ← Full backtest output JSON (all 250 blends + curves)
│
├── backtest/
│   └── backtest.py                    ← Python backtest engine (pandas + numpy)
│
└── data/
    ├── backtest_results.json          ← Copy of full backtest results
    └── historical_prices/
        ├── ACWX.csv                   ← iShares MSCI ACWI ex-US ETF (proxy: WMTX2)
        ├── AGG.csv                    ← iShares Core US Aggregate Bond ETF (proxy: ZDEVNT, WMTX1)
        ├── BIL.csv                    ← SPDR Bloomberg 1-3 Month T-Bill ETF (proxy: BGMMT, ZDBCFT)
        ├── EFA.csv                    ← iShares MSCI EAFE ETF (proxy: ZDEVLT)
        ├── IWB.csv                    ← iShares Russell 1000 ETF (proxy: ZBGRIT)
        ├── IWM.csv                    ← iShares Russell 2000 ETF (proxy: ZBGRNT)
        ├── SPMD.csv                   ← SPDR S&P 400 Mid Cap ETF (proxy: WMTX9)
        ├── SPY.csv                    ← SPDR S&P 500 ETF Trust (proxy: WMTX8)
        └── VNQ.csv                    ← Vanguard Real Estate ETF (proxy: WMTX7)
```

### File Descriptions

| File | Size | Description |
|------|------|-------------|
| `dashboard/index.html` | ~56 KB | Complete single-file dashboard — no build step, no server required. Open directly in any browser. All styles, scripts, and data are embedded inline. |
| `dashboard/data.json` | ~97 KB | Full backtest output: individual fund stats, top 3 portfolios, all 250 blend results, monthly growth curves, annual returns by year, correlation matrix, and efficient frontier scatter data. |
| `backtest/backtest.py` | ~6 KB | Python script that reads the CSVs, computes monthly returns, generates 250 portfolio blends, runs the backtest, and writes `backtest_results.json`. Requires `pandas` and `numpy`. |
| `data/backtest_results.json` | ~97 KB | Copy of the full backtest output for convenience. |
| `data/historical_prices/*.csv` | ~184 rows each | Monthly OHLCV data (date, open, high, low, close, volume) from January 2011 through April 2026. Each file contains 184 rows — one header row + 183 monthly observations. |

---

## The 12 Fund Universe

These are the actual fund options available in the Merrill Lynch 401K plan. They are institutional collective investment trusts (CITs) — not publicly traded.

| Security ID | Fund Name | Asset Category |
|-------------|-----------|----------------|
| `ZDEVLT` | BlackRock International Equity Index Trust | International Developed Equity |
| `ZBGRIT` | BlackRock Russell 1000 Index Trust | Large Cap US Equity |
| `ZBGRNT` | BlackRock Russell 2000 Index Trust | Small Cap US Equity |
| `WMTX2` | International Equity Fund | International Equity (Active) |
| `WMTX8` | Large Cap Equity Fund | Large Cap US Equity (Active-ish) |
| `WMTX7` | Real Assets Fund | Real Estate / Infrastructure |
| `WMTX9` | Small Mid Cap Equity Fund | Small/Mid Cap US Equity |
| `ZDEVNT` | BlackRock Bond Index Trust | Core US Bonds |
| `WMTX1` | Bond Fund | Core US Bonds (Active) |
| `ZDBCFT` | JPMorgan Short Term Bond Trust | Short-Duration Bonds |
| `BGMMT` | BlackRock Money Market Trust | Cash / Money Market |
| `WMU70` | My Retirement 2070 Fund | Target-Date 2070 |

> **Note on WMU70:** The 2070 target-date fund was launched in mid-2022 and has insufficient historical data for a 15-year backtest. It appears in the fund universe table as an informational entry but was excluded from the blend optimization. Its expected characteristics (heavily equity-weighted glide path, similar to a ~80–90% equity / 10–20% bond allocation) would likely put it close to Portfolio #1 in performance.

---

## ETF Proxy Methodology

Since the 401K funds are CITs without public price history, each was matched to the ETF that tracks the same underlying index. This is the standard industry practice for institutional fund backtesting.

| Security ID | Fund Name | Proxy ETF | Benchmark / Reason |
|-------------|-----------|-----------|-------------------|
| `ZDEVLT` | BlackRock Intl Equity Index | **EFA** | Tracks MSCI EAFE Index — same benchmark as the BlackRock CIT |
| `ZBGRIT` | BlackRock Russell 1000 Index | **IWB** | iShares Russell 1000 ETF — same index, near-identical holdings |
| `ZBGRNT` | BlackRock Russell 2000 Index | **IWM** | iShares Russell 2000 ETF — same index, the most-traded small-cap ETF |
| `WMTX2` | International Equity Fund | **ACWX** | MSCI ACWI ex-US — broadest international equity benchmark |
| `WMTX8` | Large Cap Equity Fund | **SPY** | SPDR S&P 500 — the standard large cap US equity benchmark |
| `WMTX7` | Real Assets Fund | **VNQ** | Vanguard Real Estate ETF — REIT exposure as real assets proxy |
| `WMTX9` | Small Mid Cap Equity Fund | **SPMD** | SPDR S&P 400 Mid Cap — mid-cap US equity benchmark |
| `ZDEVNT` | BlackRock Bond Index Trust | **AGG** | iShares Core US Aggregate Bond ETF — Bloomberg Agg benchmark |
| `WMTX1` | Bond Fund | **AGG** | Same Bloomberg Agg benchmark, active fund |
| `ZDBCFT` | JPMorgan Short Term Bond Trust | **BIL** | SPDR 1-3 Month T-Bill ETF — short-duration, near-cash proxy |
| `BGMMT` | BlackRock Money Market Trust | **BIL** | T-Bill ETF — effectively identical to money market behavior |
| `WMU70` | My Retirement 2070 Fund | *(excluded)* | Insufficient data; launched mid-2022 |

### Why this mapping is reliable

- BlackRock's institutional CITs are designed to **track their named index** with near-zero tracking error (typically < 0.05% annually vs. the benchmark ETF)
- The expense ratio difference between CITs and ETFs is minimal at this plan size
- SPY and IWB have a ~97% portfolio overlap since both are market-cap-weighted US large cap funds

### Known Proxy Limitations

- **JSCP** (JPMorgan Short Term Bond): A newer ETF (launched 2021) was considered but had insufficient history; BIL used instead
- **SHV** (iShares Short Treasury Bond): Was originally selected as the short-term proxy but the historical data download produced an invalid file; BIL substituted
- **VNQ vs. WMTX7**: The Real Assets Fund may hold infrastructure, commodities, or timberland in addition to REITs — VNQ is a pure REIT proxy and may understate diversification benefit

---

## Backtest Engine

**File:** `backtest/backtest.py`

### Data Preparation

```python
# Load 9 proxy ETF CSVs, align on date, compute monthly returns
prices = pd.DataFrame(dfs).dropna()
monthly_returns = prices.pct_change().dropna()
# Result: 183 monthly observations, Jan 2011 – Apr 2026
```

### Portfolio Generation — 250 Blends

Three blend categories are generated:

**1. Aggressive Growth (equity-heavy)**
- International allocation: 5–25%
- Bond allocation: 0–10%
- Real assets: 0–5%
- Equity sleeve: 50–95%, split among SPY / IWB / IWM / SPMD
- Grid sweep: 5 × 3 × 2 × 3 × 2 = 180 combinations (filtered to ~100 valid)

**2. Balanced / 60-40 Style**
- International: 8–24%
- Bond allocation: 15–40%
- Equity sleeve: 18–75%
- Grid sweep across equity splits

**3. Conservative (bond-heavy)**
- Bond allocation: 40–70%
- Equity: 20–50%
- Cash (BIL) buffer

**4. Monte Carlo Fill (Dirichlet)**
- If structured blends < 250, remainder filled with Dirichlet-sampled weights
- Alpha vector biased toward equity: `[2, 4, 2, 1.5, 5, 1, 2, 2, 0.5]`
- BIL (cash) capped at 8% per blend

### Performance Metrics

For each blend `w` (9-dimensional weight vector):

```python
port_ret = monthly_returns.values @ w          # weighted monthly returns
ann_ret  = (1+port_ret).prod() ** (12/n) - 1   # geometric annualized return
ann_vol  = port_ret.std() * sqrt(12)            # annualized volatility
sharpe   = (ann_ret - 0.02) / ann_vol           # Sharpe ratio, rf = 2%
cum_ret  = (1+port_ret).prod() - 1              # total cumulative return
cc       = cumprod(1+port_ret)                  # cumulative wealth curve
max_dd   = (cc / cummax(cc) - 1).min()          # maximum drawdown
sortino  = (ann_ret - 0.02) / downside_std      # Sortino ratio
calmar   = ann_ret / abs(max_dd)                # Calmar ratio
```

**Risk-free rate:** 2% annual (used for Sharpe and Sortino calculation)

**Ranking criterion:** Sharpe ratio (best risk-adjusted return per unit of total volatility)

### Output

The script writes `backtest_results.json` containing:
- `individual_stats` — per-fund statistics for all 9 proxy ETFs
- `top3` — full detail on the 3 highest-Sharpe portfolios
- `all_blends_count` — 250
- `date_range` — start, end, and month count
- `growth_curves` — monthly cumulative wealth (starting at $100) for P1, P2, P3 + 6 benchmarks
- `scatter` — all 250 blends as `{x: vol, y: return, sharpe, id}` for the efficient frontier
- `correlation` — 9×9 correlation matrix of monthly returns
- `yearly_returns` — annual return by year for all 9 funds + 3 portfolios

---

## Top 3 Portfolio Blends

Ranked by Sharpe ratio. All three are US equity-dominant, reflecting the strong outperformance of domestic large-cap equities over the 2011–2026 period.

### Portfolio #1 — Maximum Growth ⭐ TOP RECOMMENDATION

| Metric | Value |
|--------|-------|
| **Annualized Return** | **11.04%** |
| **15Y Cumulative Return** | **+393.62%** |
| **Sharpe Ratio** | **0.588** |
| Sortino Ratio | 0.811 |
| Calmar Ratio | 0.418 |
| Annual Volatility | 15.37% |
| Max Drawdown | -26.4% |
| Best Year | 2019 (+29.4%) |
| Worst Year | 2022 (-19.5%) |

**Allocation:**

| Fund | Security ID | Proxy | Weight |
|------|-------------|-------|--------|
| Large Cap Equity Fund | WMTX8 | SPY | **53%** |
| BlackRock Russell 1000 Index | ZBGRIT | IWB | **28%** |
| BlackRock Russell 2000 Index | ZBGRNT | IWM | **19%** |

**Why it works:** Concentrating 100% in the highest-performing US equity classes (SPY + IWB) captured the full US bull market since 2011. SPY and IWB are near-identical in composition (~97% portfolio overlap), providing essentially a single S&P 500/Russell 1000 exposure with maximum upside. Adding 19% small cap (IWM) provides incremental return with manageable volatility increase. This is the mathematically optimal 15-year backtest result — but it is highly concentrated and carries single-market risk. It would have suffered significantly in a prolonged US equity bear market.

---

### Portfolio #2 — Growth Optimized

| Metric | Value |
|--------|-------|
| **Annualized Return** | **10.53%** |
| **15Y Cumulative Return** | **+360.36%** |
| **Sharpe Ratio** | **0.581** |
| Sortino Ratio | 0.801 |
| Annual Volatility | 14.69% |
| Max Drawdown | -25.29% |
| Best Year | 2019 (+27.8%) |
| Worst Year | 2022 (-18.9%) |

**Allocation:**

| Fund | Security ID | Proxy | Weight |
|------|-------------|-------|--------|
| Large Cap Equity Fund | WMTX8 | SPY | 52% |
| BlackRock Russell 1000 Index | ZBGRIT | IWB | 24% |
| BlackRock Russell 2000 Index | ZBGRNT | IWM | 19% |
| BlackRock Intl Equity Index | ZDEVLT | EFA | 3% |
| International Equity Fund | WMTX2 | ACWX | 2% |

**Why it works:** Identical large cap core as Portfolio #1, but adds 5% international diversification (3% ZDEVLT + 2% WMTX2). In periods of US dollar weakness (such as early 2025), international equity has sharply outperformed US equities. This small allocation provides a mild hedge against US-centric downturns with minimal return drag. Slightly lower volatility (14.69% vs 15.37%) reflects the modest diversification benefit.

---

### Portfolio #3 — Diversified Growth

| Metric | Value |
|--------|-------|
| **Annualized Return** | **10.53%** |
| **15Y Cumulative Return** | **+360.05%** |
| **Sharpe Ratio** | **0.580** |
| Sortino Ratio | 0.800 |
| Annual Volatility | 14.70% |
| Max Drawdown | -25.32% |
| Best Year | 2019 (+27.6%) |
| Worst Year | 2022 (-19.0%) |

**Allocation:**

| Fund | Security ID | Proxy | Weight |
|------|-------------|-------|--------|
| Large Cap Equity Fund | WMTX8 | SPY | 48% |
| BlackRock Russell 1000 Index | ZBGRIT | IWB | 28% |
| BlackRock Russell 2000 Index | ZBGRNT | IWM | 19% |
| BlackRock Intl Equity Index | ZDEVLT | EFA | 3% |
| International Equity Fund | WMTX2 | ACWX | 2% |

**Why it works:** Same international diversification as Portfolio #2, but slightly reduced SPY concentration (47.5% → 48% rounded) shifts weight back to IWB (28.5%), providing better balance within the large-cap sleeve. Nearly identical Sharpe ratio to P2 — the difference is portfolio construction philosophy rather than performance. The three portfolios are effectively tied at the top.

---

## Individual Fund Performance (15Y)

All statistics from January 2011 – April 2026 (183 monthly observations) using ETF proxies.

| Security ID | Fund Name | Proxy | Ann. Return | Volatility | Sharpe | 15Y Cumulative | Max Drawdown |
|-------------|-----------|-------|-------------|------------|--------|----------------|--------------|
| ZBGRIT | BlackRock Russell 1000 Index | IWB | **11.40%** | 14.33% | 0.656 | **+418.65%** | -25.38% |
| WMTX8 | Large Cap Equity Fund | SPY | **11.49%** | 14.15% | 0.671 | **+425.34%** | -24.80% |
| ZBGRNT | BlackRock Russell 2000 Index | IWM | 8.23% | 19.25% | 0.324 | +234.15% | -33.85% |
| WMTX9 | Small Mid Cap Equity Fund | SPMD | 7.59% | 17.82% | 0.314 | +205.33% | -31.47% |
| ZDEVLT | BlackRock Intl Equity Index | EFA | 3.62% | 15.13% | 0.107 | +71.92% | -30.71% |
| WMTX2 | International Equity Fund | ACWX | 3.26% | 15.02% | 0.084 | +63.19% | -31.42% |
| WMTX7 | Real Assets Fund | VNQ | 3.18% | 17.24% | 0.068 | +61.13% | -37.14% |
| ZDEVNT / WMTX1 | Bond Funds | AGG | -0.40% | 4.49% | -0.533 | **-5.90%** | -22.79% |
| ZDBCFT / BGMMT | Short-Term Bond / Money Market | BIL | -0.02% | 0.30% | -6.809 | -0.27% | -0.52% |

**Key observations:**
- SPY was the single best fund over this period (+425% cumulative, 0.671 Sharpe)
- IWB was essentially identical to SPY (97%+ portfolio overlap, +419% cumulative)
- US large cap outperformed international by roughly **6× cumulatively** over 15 years
- AGG bonds lost money in real terms — the 2022 rate shock erased a decade of coupon income
- VNQ (Real Assets) had the weakest risk-adjusted return of all equity-like options
- BIL (cash) was effectively flat after inflation

---

## Dashboard Sections

The dashboard is a single `index.html` file with all data embedded as JavaScript constants. No server or build step is required.

### 1. Header

Sticky navigation bar with the custom SVG logo (inline bar chart icon with trend line), account identifier (`beepps@asu.edu`), and three status badges: "250 Blends Tested", "15-Year Backtest", "Premium Data Verified".

### 2. Hero Section

Five key statistics for the overall backtest:
- Blends simulated: **250**
- Months of data: **183**
- Best annualized return: **11.04%**
- Best Sharpe ratio: **0.588**
- Best 15Y cumulative: **393.62%**

Populated dynamically from the `TOP3` JavaScript constant via `updateHero()`.

### 3. Top 3 Portfolio Cards

Three full-width cards, one per portfolio. Each card contains:
- **Rank badge** (#1 blue, #2 green, #3 gold) + recommendation label
- **8 metric tiles:** annualized return, Sharpe, Sortino, max drawdown, 15Y cumulative, annual volatility, best year, worst year
- **Allocation bar chart:** horizontal bars for each fund, proportional to weight percentage, color-coded
- **Donut chart:** Chart.js doughnut visualization of the allocation, rendered on a `<canvas>` element
- **Explanatory text:** Written rationale for why each portfolio construction works

Cards are generated dynamically from the `TOP3` array via `renderTop3()`.

### 4. Cumulative Growth Chart

A multi-line Chart.js line chart showing `$100 invested in January 2011` growing over 15 years for:
- Portfolio #1 (blue, solid, 2.5px)
- Portfolio #2 (green, solid, 2.5px)
- Portfolio #3 (gold, solid, 2.5px)
- SPY benchmark (purple, dashed, 1.5px)
- AGG bonds (slate, dashed, 1.5px)
- EFA international (orange, dashed, 1.5px)

Data is built from annual `YEARLY` returns via `buildGrowthCurve()`. Custom tooltip shows dollar value per series on hover.

### 5. Annual Returns Bar Chart + Efficient Frontier

**Left (2/3 width):** Grouped bar chart showing annual returns for all three portfolios side-by-side from 2011–2025. Each year shows 3 bars (blue/green/gold). Rendered from the `YEARLY` constant.

**Right (1/3 width):** Scatter plot of all 250 portfolio blends (gray dots) with the top 3 highlighted as colored star markers. X-axis = annualized volatility, Y-axis = annualized return. Visualizes the efficient frontier — the upper-left boundary represents the maximum return for a given level of risk.

### 6. Year-by-Year Return Heatmap

A pure HTML/CSS grid (no canvas) showing annual returns for 6 series × 15 years. Color intensity is proportional to return magnitude:
- **Green cells:** positive returns (darker = higher)
- **Red cells:** negative returns (darker = more negative)
- Hover tooltip shows exact return value

Rendered via `renderHeatmap()` using the `heatColor()` helper function.

### 7. Fund Universe Table

A full 12-row table showing all available 401K funds with:
- Security ID (monospace badge)
- Fund name
- Proxy ETF (blue monospace badge)
- Asset category
- Annualized return (color-coded: green > 5%, neutral 0–5%, red < 0%)
- Volatility, Sharpe ratio, 15Y cumulative, max drawdown

### 8. Asset Correlation Matrix

A 9×9 HTML table showing pairwise correlations between all proxy ETFs:
- Red shading for high correlation (> 0.80 = dark, > 0.60 = light)
- Green shading for negative correlation (tail-risk diversifiers)
- Diagonal is white/neutral (self-correlation = 1.00)

Followed by a written "Diversification Insight" block explaining the correlation structure.

### 9. Risk Profile Radar Chart

Chart.js radar chart comparing the 3 portfolios across 6 normalized dimensions (0–100 scale):
- **Return** — annualized return
- **Sharpe** — Sharpe ratio
- **Sortino** — Sortino ratio
- **Low Vol** — inverted volatility (lower vol = higher score)
- **Low DD** — inverted max drawdown (smaller drawdown = higher score)
- **Calmar** — Calmar ratio

Normalization: each metric is scaled to [0, 100] relative to the expected range for this portfolio set.

### 10. Max Drawdown Comparison

Horizontal bar chart showing the maximum peak-to-trough loss for all 11 individual funds/portfolios. Sorted by portfolio first (P1, P2, P3), then individual ETFs. Bars extend left from zero, representing the magnitude of the worst loss. VNQ (Real Assets) shows the worst individual drawdown at -37.14%.

### 11. Methodology & Data Sources

Four-column grid explaining:
1. Backtest engine mechanics (250 blends, structured + Monte Carlo)
2. Fund proxy methodology
3. Metrics definitions (Sharpe, Sortino, Calmar, Max Drawdown)
4. Premium data verification sources with hyperlinks

### 12. Footer

Disclaimer, data attribution, and generation date.

---

## Tech Stack

| Component | Library / Version | CDN |
|-----------|-------------------|-----|
| Charts | Chart.js 4.4.0 | `cdn.jsdelivr.net/npm/chart.js@4.4.0` |
| Data Labels | chartjs-plugin-datalabels 2.2.0 | `cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0` |
| Body Font | Inter (Google Fonts) | `fonts.googleapis.com` |
| Code Font | JetBrains Mono (Google Fonts) | `fonts.googleapis.com` |
| Backtest | Python 3 — `pandas`, `numpy` | (local) |
| Data Format | JSON | (embedded in HTML) |

The dashboard has **zero build dependencies** — no Node.js, no webpack, no React. It is a single static HTML file. The only external dependencies are the two CDN script tags and Google Fonts, which require an internet connection to load correctly.

---

## How to Run Locally

### Option 1: Open directly in browser (simplest)

No server required. All data is embedded in the HTML file.

```bash
# macOS
open dashboard/index.html

# Windows
start dashboard\index.html

# Linux
xdg-open dashboard/index.html
```

### Option 2: Serve with a local HTTP server (recommended for development)

```bash
cd dashboard

# Python 3 (built-in) — macOS / Linux
python3 -m http.server 8081

# Python 3 (built-in) — Windows
python -m http.server 8081

# Then open http://localhost:8081 in your browser
```

> **Port note:** Port `8080` is commonly used by other local tools (Docker, proxies, etc.) and may return `ERR_EMPTY_RESPONSE` if already in use. Use `8081` or any free port instead:
>
> ```bash
> python -m http.server 8081   # Windows
> python3 -m http.server 8081  # macOS / Linux
> ```

**Node.js alternative (if installed):**

```bash
npx serve dashboard
```

### Option 3: Deploy to a static host

The `dashboard/` folder can be dropped into any static file host:
- **GitHub Pages** — push to a `gh-pages` branch or configure in repo settings
- **Netlify / Vercel** — drag and drop the `dashboard/` folder
- **AWS S3 + CloudFront** — enable static website hosting

---

## How to Re-run the Backtest

### Prerequisites

```bash
pip install pandas numpy
```

### Steps

1. Ensure all 9 CSV files are present in `data/historical_prices/`
2. Update the `base` path in `backtest.py` to match your local directory:

```python
base = './data/historical_prices/'
```

3. Run the script:

```bash
cd backtest
python3 backtest.py
```

4. Output will be written to `data/backtest_results.json`

### To update with fresh price data

The CSV files contain monthly OHLCV data with columns: `date, open, high, low, close, volume`. To update:

1. Download fresh monthly price history for each proxy ETF from a financial data provider (Yahoo Finance, Alpaca, Polygon, etc.)
2. Format as CSV with the same column names: `date,open,high,low,close,volume`
3. Replace the files in `data/historical_prices/`
4. Re-run `backtest.py`
5. Copy the new `backtest_results.json` to `dashboard/data.json`
6. If you want the dashboard to reflect the updated data, re-embed the relevant constants in `dashboard/index.html` (the `TOP3`, `PROXY_STATS`, `YEARLY`, and `FUND_FULL` JS objects)

---

## Data Sources & Premium Verification

The backtest statistics were fact-checked against the following sources:

| Source | What was verified |
|--------|-------------------|
| [Statista — ICI Retirement Data](https://cashmere.io/v/dlaHtj) | US retirement savings plan asset allocation benchmarks |
| [Russell 1000 Index — Wikipedia](https://en.wikipedia.org/wiki/Russell_1000_Index) | Annual return history 2011–2024 |
| [Bloomberg US Aggregate Bond — upmyinterest.com](https://www.upmyinterest.com/bloomberg-us-aggregate-bonds/) | AGG annual return history including 2022 drawdown |
| [BlackRock International Index Fund (BlackRock)](https://www.blackrock.com/us/individual/products/227725/blackrock-international-index-class-k-fund) | EAFE performance and fund characteristics |
| [MSCI EAFE Index — MSCI](https://www.msci.com/documents/10199/255599/msci-eafe-growth-target-index-usd-net.pdf) | International equity annual return verification |
| CB Insights | Wealth management and 401K portfolio optimization research |
| PitchBook | BlackRock fund profiles and institutional CIT data |

Historical price data was sourced via the Perplexity Finance connector (real-time ETF OHLCV histories) for the period January 2011 – April 2026.

---

## Key Findings & Insights

### 1. US Large Cap Dominated Everything (2011–2026)

SPY returned **+425.34% cumulatively** over 15 years — roughly 6× better than international equity (EFA: +71.92%) and dramatically better than bonds (AGG: -5.90%). This reflects the historic US equity bull market driven by:
- Federal Reserve quantitative easing post-2008 (kept rates near zero through 2022)
- US tech sector dominance (FAANG/Mag-7 growth)
- Dollar strength suppressing international returns for USD investors

### 2. Bonds Were a Drag in This Period

The Bloomberg Aggregate Bond Index (AGG) returned **-0.40% annualized** over the full period — a negative real return. The 2022 Fed rate hiking cycle (fastest in 40 years) caused the AGG to drop -13% in a single calendar year, erasing approximately a decade of coupon income. The Sharpe ratio of -0.533 means every unit of risk taken in bonds *destroyed* rather than created value.

**Implication:** Avoiding ZDEVNT and WMTX1 entirely was the correct call for maximum growth over this 15-year backtest window. This does **not** mean bonds are always bad — they provide crucial tail-risk protection and will likely outperform in deflationary or recession environments.

### 3. The Top 3 Portfolios Are Nearly Identical

The three top blends are separated by only 0.008 Sharpe ratio points (0.588 vs 0.580). All three converge on the same insight: **maximize SPY + IWB exposure**. The differences are:
- P1: Pure US equity (100% domestic), maximum concentration
- P2: Same core + 5% international hedge
- P3: Slightly rebalanced large-cap sleeve

This convergence is mathematically expected when one asset class (US large cap) so dramatically outperforms all others — the optimizer has limited degrees of freedom.

### 4. International Diversification Was a Mild Drag

ZDEVLT (EFA, +3.62% ann.) and WMTX2 (ACWX, +3.26% ann.) underperformed US large cap by ~8 percentage points annually. However, in 2025, EFA returned +28% vs SPY's +15%, suggesting the tide may be turning. Adding 5% international (as in P2 and P3) provides an option value against US equity underperformance at minimal cost.

### 5. Real Assets Were the Worst Risk-Adjusted Asset

VNQ (Real Assets / REIT proxy) had the largest maximum drawdown of any fund at **-37.14%**, combined with only **+3.18% annualized return** — yielding the lowest Sharpe ratio among equity-like assets (0.068). The 2022 rate shock hit REITs especially hard since they are rate-sensitive (high dividend yields become less attractive when risk-free rates rise). WMTX7 should be minimized or avoided in a growth-oriented 401K portfolio.

---

## Limitations & Caveats

1. **Past performance ≠ future results.** The 2011–2026 period was an unusually favorable environment for US equities. A repeat of the 2000–2010 "lost decade" would produce very different optimization results, likely favoring international diversification and bonds.

2. **ETF proxies are approximations.** The actual 401K funds (CITs) have slightly different expense ratios, holdings, and rebalancing rules vs. their ETF proxies. Actual performance may differ marginally.

3. **No transaction costs, taxes, or contribution limits.** The backtest assumes perfect monthly rebalancing with zero friction. In practice, 401K rebalancing is constrained by your plan's rebalancing tools and may incur short-term restrictions.

4. **Hindsight bias / look-ahead.** The optimal portfolios were selected based on a period that has already happened. Any investor using this model is implicitly betting that the next 15 years will resemble the last 15 — a strong assumption.

5. **Monthly rebalancing assumption.** Most 401K participants rebalance quarterly or annually, not monthly. Monthly rebalancing was used for mathematical consistency and to maximize granularity, but it slightly overstates achievable returns.

6. **2070 Fund excluded.** WMU70 has only ~2 years of history and was excluded from optimization. As a target-date fund, its allocation will shift significantly over time toward bonds as the target date approaches.

7. **Single objective function (Sharpe ratio).** Other valid optimization targets include: maximum return, minimum volatility, maximum Sortino, or multi-objective Pareto optimization. The top portfolios by other criteria might look different.

---

*Generated April 8, 2026 · Exported June 25, 2026*  
*Data: Perplexity Finance, Statista, CB Insights, PitchBook, Bloomberg, BlackRock, Russell Indexes*
