# ML Algorithms to GlobalBLOCS Investment Research

This map describes candidate research applications. It does not imply that any model creates profitable signals without rigorous validation.

| Method | GlobalBLOCS use case | Example output | Key guardrail |
|---|---|---|---|
| Naive Bayes | Filing/news topic triage | Topic or risk class | Conditional independence is often unrealistic |
| Logistic Regression | Event or direction baseline | Calibrated event probability | Define event horizon and calibrate |
| KNN classifier | Similar historical regimes | Class from comparable feature vectors | Scale features; prevent temporal leakage |
| Random Forest classifier | Credit/event-risk classification | Risk class | Monitor imbalance and drift |
| SVM classifier | Regime/event classification | Class label | Scale features; tune only inside training folds |
| Decision Tree classifier | Explainable screening baseline | Class and decision path | Control depth and instability |
| Random Forest regressor | Volatility, earnings or macro forecast | Continuous estimate | Compare with naive/linear baselines |
| SVR | Nonlinear continuous forecast | Forecast value | Scale features and tune epsilon inside training folds |
| Decision Tree regressor | Nonlinear threshold relationships | Continuous estimate | Limit overfit and extrapolation |
| Simple linear regression | One macro variable versus return/metric | Slope and forecast | Association is not causation |
| Multiple regression | Multi-factor exposure analysis | Conditional estimate | Check multicollinearity and residuals |
| Lasso | Sparse factor selection | Shrunk coefficients | Standardize predictors and test selection stability |
| K-Means | Market/sector regime grouping | Cluster assignment | Standardize; assess stability and interpretability |
| DBSCAN | Unusual market-state density | Cluster/noise flag | Tune distance parameters; density changes by regime |
| PCA | Compress correlated macro/market variables | Principal components | Fit transforms on training data only |
| ICA | Explore latent co-movement patterns | Independent components | Test independence assumptions and stability |
| FP-Growth | Frequent combinations of events/features | Frequent itemsets | Discretization can dominate results |
| Apriori | Co-occurring risk indicators | Rules with support/confidence/lift | Association is not causation |
| Z-score | Unusual metric or return moves | Standardized deviation | Review non-normality and changing regimes |
| Isolation Forest | Multivariate anomaly triage | Anomaly score | Anomaly does not automatically mean fraud or trade |

## yfinance-to-official-source mapping
Use yfinance as a convenient market/company series adapter for ticker-based historical prices, volume, dividends, splits, selected company information, and financial-statement fields when available. Treat coverage, field definitions, historical availability, and adjustments as provider-dependent. It is not an official source of record.

| Research question | Market/company layer | Government or authoritative validation layer |
|---|---|---|
| Price, volume, return, drawdown | yfinance series; exchange/licensed feed when required | Exchange publications; national securities regulator; corporate-action notices |
| Revenue, earnings, balance sheet, cash flow | yfinance statement fields where present | SEC EDGAR/XBRL in the US; issuer filings and national regulator filings elsewhere |
| Macro regime | Ticker/sector returns as market response | National statistics offices, central banks, finance ministries; IMF/OECD/World Bank for comparison |
| Interest rates and credit | Listed bond/ETF proxies where available | Central banks, treasury/debt offices, BIS, national debt-management agencies |
| Import/export exposure | Company disclosures and sector proxies | Customs/trade ministries, national statistics offices, WTO, UN Comtrade |
| Industry/sector productivity | Listed-company peer samples | National industry statistics, labor agencies, energy/agriculture/transport regulators |
| Enforcement and policy risk | Price/volume reaction around timestamped events | Securities/banking regulators, central banks, official gazettes and enforcement releases |

Keep market series and official observations in separate source records, then join them using issuer/security identifiers, jurisdiction, currency, publication timestamp, and observation period. Do not treat a ticker symbol as a globally unique company identifier.

## Shared experiment contract
Record dataset version, source lineage, entity universe, feature definitions, target definition, event horizon, availability timestamp, train/validation/test windows, baseline, hyperparameters, random seed, code version, metrics, calibration, and limitations.

## Avoiding look-ahead bias
- Use only information available at the prediction timestamp.
- Use point-in-time fundamentals and publication dates; do not backdate revised macroeconomic releases.
- Split chronologically and use rolling or expanding evaluation.
- Fit preprocessing, feature selection, and dimensionality reduction inside each training fold.
- Include transaction costs, slippage, liquidity, turnover, delistings, and survivorship effects in backtests.
- Compare with cash, broad-market, and simple benchmark strategies.
- Report drawdown and downside risk, not only accuracy or returns.

## Investment-opportunity output
Each candidate should include thesis, supporting indicators, contrary evidence, model version, validation window, confidence/calibration, liquidity and volatility flags, downside scenarios, source citations, and an explicit human-review status. Treat output as research triage, not a guaranteed recommendation.
