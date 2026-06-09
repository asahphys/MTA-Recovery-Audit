# DSTW-Final-Project
Comprehensive technical implementation and source code for the DSTW (EL-5069) Final Project framework.

# Disrupted Transit, Missed Projections: A Six-Year Post-Mortem on MTA's COVID-19 Recovery

**EL5069 — Data Science dan Teknologi Web | Institut Teknologi Bandung**  
Ardiansah · 20225006

---

When COVID-19 erased 93% of MTA ridership overnight, McKinsey & Company was commissioned to model recovery across six transit modes and three scenarios — a forecast that would anchor $15B+ in budget decisions through 2026. Six years later, the data tells a different story: McKinsey overestimated urban transit recovery by 22–30 percentage points (Subway MAE: 29.6 pp; Bus: 26.2 pp) while underestimating suburban demand that drove Bridges & Tunnels 16 points beyond pre-pandemic peak — a structural behavioral shift no prior-disruption model had priced in, translating to an estimated $0.79B annual revenue gap. This dashboard benchmarks 16,529 rows of MTA actuals against McKinsey's projections across trend analysis, statistical accuracy scoring, and parametric financial simulation.

## Analytical Framework

```
Raw Data (MTA + McKinsey)
        │
        ▼
Preprocessing & Standardization
  · Date parsing → monthly periods
  · Count normalization (comma-stripped integers)
  · Mode filtering (6 valid transit modes)
        │
        ▼
Feature Engineering
  · Recovery Rate (%) vs. 2019 baseline
  · Revenue Gap (%) = 100 − Recovery Rate
  · Monthly aggregation per agency
        │
   ┌────┴────┬────────────┐
   ▼         ▼            ▼
Trend     Statistical   Financial
Analysis  Analytics     Simulation
(Tab 1)   (Tab 2)       (Tab 3)
```

---

## Key Findings

### 1. Recovery Divergence Is Structural, Not Temporary

The data reveals a consistent bifurcation between urban and commuter modes — a pattern that has persisted since 2022 and shows no sign of mean-reverting.

| Mode | Actual Recovery (avg.) | McKinsey Projection | Mean Error | Verdict |
|---|---|---|---|---|
| BT | **107.6%** | 91.8% | +12.8 pp | McKinsey too conservative |
| MNR | **78.0%** | 62.0% | +6.0 pp | McKinsey too conservative |
| Bus | 52.3% | 74.8% | −26.2 pp | McKinsey too optimistic |
| LIRR | 52.1% | 67.2% | −22.9 pp | McKinsey too optimistic |
| SIR | 48.0% | 70.3% | −30.7 pp | McKinsey too optimistic |
| Subway | 50.0% | 71.3% | −29.6 pp | McKinsey too optimistic |

*pp = percentage points. Projection scenario: Midpoint.*

### 2. McKinsey's Model Failed to Anticipate Behavioral Shifts

The model was calibrated on historical recovery patterns from prior disruptions (9/11, Hurricane Sandy) — episodes where commuting resumed because office attendance resumed. The pandemic permanently restructured work patterns. Remote and hybrid work suppressed Subway and Bus demand structurally, while personal vehicle usage (BT) and leisure/suburban rail travel (MNR) rebounded beyond 2019 norms.

### 3. The Forecast Error Is Largest Where It Matters Most

Subway alone carries ~64% of system volume. A 29.6 pp miss on the largest mode is not a rounding error — it cascades into material financial exposure.

### 4. Financial Exposure Estimate

At $8B target revenue (2019) and 50% fare contribution assumption:

> **Estimated annual revenue shortfall: $0.79 Billion**  
> Equivalent to ~$66M/month in unrealized fare revenue across the system.

The shortfall is front-loaded: monthly losses peaked in 2021–2022 and have declined as BT surplus partially offsets urban transit underperformance.

---
