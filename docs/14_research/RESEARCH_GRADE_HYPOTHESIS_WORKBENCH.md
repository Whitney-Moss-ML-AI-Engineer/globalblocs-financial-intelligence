# GlobalBLOCS Research-Grade Hypothesis Workbench

## Purpose and scope
This package turns 20 proposed macro-financial and firm-level hypotheses into reproducible research specifications. The hypotheses are proposals, not established findings. A regression coefficient is not automatically causal: identification assumptions must be defended and documented before interpreting an estimate causally.

## Shared research protocol
1. **Pre-register** the primary outcome, treatment/exposure, sample, estimand, estimator, controls, exclusion rules, and primary robustness tests before inspecting results.
2. **Build a point-in-time dataset.** Preserve source release dates/vintages and avoid using revised values that were not available at the decision date when testing real-time forecasts.
3. **Define units and frequency.** Do not interpolate annual macro data into monthly observations as if those were observed values. Align periods with transparent aggregation rules.
4. **Establish a baseline.** Plot levels and changes; inspect missingness, outliers, structural breaks, stationarity, cross-sectional dependence, and serial correlation.
5. **Estimate the design appropriate to the question.** Fixed effects address time-invariant confounding, not time-varying confounding. IV requires relevance and exclusion; DiD requires a credible counterfactual and appropriate pre-trend evidence; Granger causality is predictive precedence, not causal proof.
6. **Use valid inference.** Cluster at the treatment-assignment or shock level where appropriate. With few clusters, use suitable small-sample methods or randomization inference. Correct for multiple testing across related hypotheses (e.g., Holm or Benjamini–Hochberg).
7. **Report all results.** Include sample construction, effect sizes and units, confidence intervals, standard errors, diagnostics, robustness, null results, code, source versions, and limitations.
8. **Reproduce.** Version data manifests, code, model formula, package versions, random seeds, and output artifacts.

## Twenty hypothesis specifications

Notation: (i) = country or firm; (t) = time; (s) = sector; (j) = trading partner. (X) denotes pre-specified controls. Fixed effects and time effects should be included only where supported by the design and estimand.

### H01 — Policy rates and equity returns
- **Claim:** Unexpected monetary tightening lowers broad equity returns.
- **Outcome/exposure:** Broad market-index log return; monetary policy surprise, preferably high-frequency around policy announcements rather than the raw policy rate.
- **Baseline:** (R_{i,t} = \alpha_i + \delta_t + \beta Shock_{i,t} + \gamma'X_{i,t-1} + \epsilon_{i,t}).
- **Design:** Event study/local projections using identified monetary surprises; country FE only if comparable cross-country shocks exist. VAR/SVAR is a complementary dynamic model.
- **Controls/data:** Inflation, output news, exchange rates, global risk, lagged returns; FRED, central-bank releases, IMF, World Bank, CBOE/VIX via FRED.
- **Threats/checks:** Policy endogeneity, announcement information effects, anticipation. Test alternative shock series, event windows, horizons, placebo dates, and crisis exclusions.

### H02 — Inflation and real consumption
- **Claim:** Unexpected inflation reduces real household consumption, conditional on income and expectations.
- **Baseline:** \(\Delta\ln C_{i,t}=\alpha_i+\delta_t+\sum_{k=0}^{p}\beta_k\pi_{i,t-k}+\gamma'X_{i,t}+\epsilon_{i,t}\).
- **Design:** Panel FE/ARDL for associations; local projections around plausibly exogenous commodity supply shocks only if the exclusion restriction is defensible.
- **Controls/data:** Real disposable income, unemployment, rates, credit conditions, demographics; national accounts, WDI, IMF, OECD, FRED.
- **Threats/checks:** CPI/consumption measurement, expectations, heterogeneous exposure. Compare headline/core inflation, nominal versus real consumption, and country-specific estimates.

### H03 — Output growth and unemployment (Okun's law)
- **Claim:** Higher real output growth is associated with a decline in unemployment.
- **Baseline:** \(\Delta U_{i,t}=\alpha_i+\delta_t+\beta g_{i,t}+\gamma'X_{i,t}+\epsilon_{i,t}\).
- **Design:** Panel FE and country-specific estimates; dynamic panel/VAR for lag structure. Treat Granger tests as predictive evidence, not identification.
- **Controls/data:** Participation, hours worked, productivity, sector mix; ILOSTAT, WDI, OECD, IMF WEO.
- **Checks:** Alternative unemployment definitions, output gaps versus growth, lag lengths, recession subsamples, cross-sectional dependence.

### H04 — Public debt and currency value
- **Claim:** Increases in sovereign debt burdens may be associated with depreciation, conditional on fiscal credibility and external balances.
- **Baseline:** \(\Delta\ln FX_{i,t}=\alpha_i+\delta_t+\beta DebtGDP_{i,t-1}+\gamma'X_{i,t}+\epsilon_{i,t}\); define FX quotation explicitly (e.g. local currency per USD).
- **Design:** Panel FE is associational. IV is acceptable only with a credible excluded instrument; lagged debt alone is generally not a valid instrument by itself. Consider sovereign-risk event studies.
- **Controls/data:** Rate differentials, inflation, current account, reserves, fiscal balance, risk; IMF WEO/IFS, BIS, WDI, central banks.
- **Checks:** Alternative FX quotation, debt maturity/currency composition, floating-rate regimes, stress episodes, weak-instrument diagnostics.

### H05 — FDI and long-run growth
- **Claim:** FDI inflows can support long-run productivity and per-capita growth, conditional on absorptive capacity.
- **Baseline:** \(g_{i,t:t+h}=\alpha_i+\delta_t+\beta FDI_{i,t}+\gamma'X_{i,t-1}+\epsilon_{i,t}\).
- **Design:** Panel FE/local projections; causal interpretation requires exogenous FDI variation or a defensible design, not simply lagged FDI.
- **Controls/data:** Initial income, human capital, trade openness, institutions, domestic investment; WDI, OECD, IMF, Penn World Table.
- **Checks:** Greenfield vs M&A, FDI/GDP vs per-capita FDI, income groups, leave-one-country-out, alternative productivity outcomes.

### H06 — Gold and market stress
- **Claim:** Gold may hedge or act as a safe haven during selected market stress windows; the effect may vary by horizon and currency.
- **Baseline:** \(r^{gold}_t=\alpha+\beta VIX_t+\gamma'X_t+\epsilon_t\); model conditional variance separately using GARCH/EGARCH where justified.
- **Design:** Time-series regressions, quantile models, and event studies; correlation alone does not establish safe-haven status.
- **Controls/data:** Real yields, USD, oil, equity returns; FRED, World Bank commodity data, market data with license/adjustment policy.
- **Checks:** Rolling windows, crisis vs non-crisis, tail quantiles, local currency returns, alternative volatility proxies.

### H07 — Exchange rates and exports
- **Claim:** Real depreciation can improve export volumes over time, depending on price elasticities and imported-input exposure.
- **Baseline:** \(\Delta\ln X_{i,t}=\alpha_i+\delta_t+\sum_k\beta_k\Delta\ln REER_{i,t-k}+\gamma'X_{i,t}+\epsilon_{i,t}\).
- **Design:** Panel ARDL/ECM only after testing integration and cointegration; use gravity models for bilateral trade.
- **Controls/data:** Partner demand, tariffs, commodity prices, global supply chains; UN Comtrade, WDI, BIS effective exchange rates, WTO.
- **Checks:** Export quantities vs nominal values, sector-level estimates, lags/J-curve, partner-time effects, trade deflators.

### H08 — Quantum R&D and firm performance
- **Claim:** Quantum-related R&D is associated with future firm innovation or valuation; a causal premium is not assumed.
- **Baseline:** \(Y_{i,t+h}=\alpha_i+\delta_t+\beta QuantumR\&D_{i,t}+\gamma'X_{i,t-1}+\epsilon_{i,t}\).
- **Design:** Firm FE and event studies around clearly dated disclosures; DiD only with a credible comparison group and parallel-trend evidence.
- **Controls/data:** Total R&D, size, leverage, industry, patents and pre-trends; SEC EDGAR, USPTO, EPO/PATSTAT where licensed, company reports, market/financial databases.
- **Checks:** Alternative keyword/patent classifications, placebo announcement dates, matched controls, multiple outcome horizons.

### H09 — ESG and firm valuation
- **Claim:** ESG ratings may correlate with valuation; direction and size may differ by provider, sector, and pillar.
- **Baseline:** \(\ln MV_{i,t}=\alpha_i+\delta_t+\beta ESG_{i,t-1}+\gamma'X_{i,t-1}+\epsilon_{i,t}\).
- **Design:** Firm FE; regulatory disclosure changes may support DiD if treatment timing and parallel trends are defensible. Lagging ESG alone does not eliminate endogeneity.
- **Controls/data:** Profitability, leverage, size, sector-year effects; SEC filings, issuer reports, licensed ESG providers, regulatory sources.
- **Checks:** Alternative ESG providers, E/S/G pillars, valuation metrics, industry-specific estimates, reverse-causality sensitivity.

### H10 — CBDC rollout and bank deposits
- **Claim:** Retail CBDC introduction may change deposit balances; sign and magnitude are empirical questions.
- **Baseline:** \(Y_{i,t}=\alpha_i+\delta_t+\beta CBDCExposure_{i,t}+\gamma'X_{i,t}+\epsilon_{i,t}\).
- **Design:** Staggered-adoption DiD using estimators robust to heterogeneous treatment effects; synthetic control for a small number of treated jurisdictions.
- **Controls/data:** Deposit rates, output, deposit insurance, banking structure, policy changes; central banks, BIS, IMF, national statistics.
- **Checks:** Pre-trends, placebo dates/outcomes, anticipation, pilot intensity, wholesale vs retail, donor-pool sensitivity. Distinguish announced, pilot, launched, and discontinued status.

### H11 — AI adoption and investment-bank profitability
- **Claim:** Measured AI adoption may be associated with subsequent productivity or profitability, with uncertain causal direction.
- **Baseline:** \(Profit_{i,t+h}=\alpha_i+\delta_t+\beta AIAdoption_{i,t}+\gamma'X_{i,t-1}+\epsilon_{i,t}\).
- **Design:** Firm FE and announcement event studies; causal designs require credible treatment variation. Patent/product-launch counts are noisy proxies.
- **Controls/data:** Size, capital, leverage, business mix, market conditions; SEC filings, annual reports, patent records, licensed financial data.
- **Checks:** Alternative adoption measures, placebo dates, pre-trends, cost vs revenue outcomes, bank-specific trends.

### H12 — Pension size and portfolio risk
- **Claim:** Larger pension funds may have different risk profiles; size does not mechanically reduce portfolio risk.
- **Baseline:** \(Risk_{f,t}=\alpha_f+\delta_t+\beta\ln(AUM_{f,t-1})+\gamma'Allocation_{f,t-1}+\epsilon_{f,t}\).
- **Design:** Fund FE with consistent return series; lagged AUM is not automatically exogenous.
- **Controls/data:** Asset allocation, leverage, liabilities, liquidity, sponsor type, currency; audited fund reports, OECD pension statistics, public disclosures.
- **Checks:** Risk-adjusted vs raw volatility, allocation controls, private-asset smoothing, public/private fund split, survivorship bias.

### H13 — Sanctions and bilateral trade
- **Claim:** Sanctions reduce targeted bilateral trade, potentially with diversion to third countries.
- **Baseline:** PPML gravity: \(E[Trade_{ij,t}|X]=\exp(\alpha_{ij}+\delta_{it}+\eta_{jt}+\beta Sanction_{ij,t}+\gamma'Z_{ij,t})\).
- **Design:** Pair FE and exporter-time/importer-time FE; PPML accommodates zero trade and heteroskedasticity better than log-OLS. DiD interpretation requires a defensible counterfactual.
- **Controls/data:** Tariffs, agreements, GDP, sector, sanction scope; UN Comtrade, WTO, official sanctions lists, research datasets with documented definitions.
- **Checks:** Sector/product breakdown, anticipation, third-country diversion, placebo dyads, alternative sanction intensity. Document endogeneity of sanction assignment.

### H14 — Digital payments and informal economy
- **Claim:** Digital payment adoption may be associated with a smaller informal economy, but measurement is uncertain.
- **Baseline:** \(Shadow_{i,t}=\alpha_i+\delta_t+\beta DigitalPay_{i,t}+\gamma'X_{i,t}+\epsilon_{i,t}\).
- **Design:** Panel FE; rollout-based DiD only if credible comparison and pre-trends. Avoid using mobile penetration as an instrument without defending exclusion.
- **Controls/data:** Income, tax administration, enforcement, banking access, demographics; World Bank Global Findex, IMF, national statistical offices, central banks.
- **Checks:** Multiple shadow-economy measures, formal employment/tax outcomes, digital cash-transfer reforms, sensitivity to measurement error.

### H15 — De-dollarization and USD reserve share
- **Claim:** Reserve diversification and non-USD settlement may be associated with changes in the USD share, but reserve shares also reflect valuation and reporting effects.
- **Baseline:** \(USDShare_t=\alpha+\beta NonUSDUse_t+\gamma'X_t+\epsilon_t\), with cointegration/ECM only when integration properties support it.
- **Design:** Aggregate time series with low-frequency data; report limited effective sample size and avoid overfitting. Do not infer causality from a trending correlation.
- **Controls/data:** FX valuation effects, reserve composition, global trade, interest-rate differentials; IMF COFER, BIS, central-bank publications.
- **Checks:** Constant-exchange-rate valuation adjustment where feasible, alternative currencies, structural breaks, alternative sample windows.

### H16 — Infrastructure investment and productivity
- **Claim:** Infrastructure investment may increase productivity, with heterogeneous effects and implementation lags.
- **Baseline:** \(\Delta\ln TFP_{i,t+h}=\alpha_i+\delta_t+\beta Infrastructure_{i,t}+\gamma'X_{i,t-1}+\epsilon_{i,t}\).
- **Design:** Panel FE/local projections; causal identification requires a defensible allocation rule, natural experiment, or instrument.
- **Controls/data:** Capital stock, education, institutions, urbanization, fiscal capacity; IMF, WDI, Penn World Table, national budget and project records.
- **Checks:** Public vs private investment, project completion vs budget, lags, income heterogeneity, alternative TFP series.

### H17 — Cybersecurity spending and financial losses
- **Claim:** Security investment may reduce expected loss, but spending is endogenous to threat and prior incidents.
- **Baseline:** \(Loss_{i,t}=\alpha_i+\delta_t+\beta SecuritySpend_{i,t-1}+\gamma'X_{i,t}+\epsilon_{i,t}\); use Poisson/negative binomial for incident counts where appropriate.
- **Design:** Firm FE or matched/event-study designs; interpret disclosed incidents with reporting-bias caution.
- **Controls/data:** Firm size, sector, exposure, regulation, incident severity; public filings, regulator breach disclosures, VERIS and other documented datasets, insurance claims where lawfully accessible.
- **Checks:** Loss amount vs incident count, disclosure coverage, alternative lag lengths, severity-weighted outcome, regulation subgroups.

### H18 — Interlocking directorates and concentration
- **Claim:** Board interlocks may correlate with market concentration; anticompetitive interpretation requires careful causal evidence.
- **Baseline:** \(HHI_{s,t}=\alpha_s+\delta_t+\beta Interlocks_{s,t}+\gamma'X_{s,t}+\epsilon_{s,t}\).
- **Design:** Industry panel and network analysis; potential instruments such as director deaths require ethical, legal, and exclusion scrutiny and are not presumed valid.
- **Controls/data:** Industry growth, entry, regulation, merger activity, firm size; SEC proxy statements, company filings, market shares, licensed board data.
- **Checks:** Alternative concentration measures, sector definitions, lagged interlocks, network centrality, merger controls, placebo industries.

### H19 — Carbon taxes and industrial output
- **Claim:** Carbon pricing may reduce output in exposed sectors or shift production, while effects vary with exemptions and recycling.
- **Baseline:** \(\ln Output_{i,s,t}=\alpha_{i,s}+\delta_t+\beta CarbonPriceExposure_{i,s,t}+\gamma'X_{i,s,t}+\epsilon_{i,s,t}\).
- **Design:** DiD/event study with treatment intensity by pre-policy emissions exposure; use modern staggered-treatment estimators if timing varies.
- **Controls/data:** Energy prices, trade exposure, demand, subsidies, free allowances; OECD, national policy records, industrial production statistics, emissions inventories.
- **Checks:** Pre-trends, placebo sectors/dates, leakage, output vs employment/productivity, alternative carbon-price measures.

### H20 — Sovereign wealth fund activity and market stability
- **Claim:** SWF transactions may support or destabilize market liquidity depending on timing, scale, and mandate.
- **Baseline:** \(Volatility_{m,t}=\alpha_m+\delta_t+\beta SWFExposure_{m,t}+\gamma'X_{m,t}+\epsilon_{m,t}\).
- **Design:** Event study around disclosed transactions or mandate changes; transaction disclosure and selection into crises create serious endogeneity.
- **Controls/data:** Liquidity, volatility, global risk, rates, crisis state; SWF annual reports, national disclosures, market data, BIS.
- **Checks:** Crisis vs non-crisis, asset class, event-window sensitivity, placebo dates, alternative volatility measures, disclosure bias.

## Common reporting table
For each estimate report: hypothesis ID; estimand; unit of analysis; source/vintage; sample dates; N entities and observations; formula; estimator; fixed effects; standard-error method; coefficient; 95% confidence interval; p-value; effect-size interpretation; missingness; diagnostics; robustness family; multiplicity adjustment; causal-identification status; caveats.

## Methodology chapter scaffold
This project uses hypothesis-driven quantitative research across country panels, firm panels, bilateral trade panels, and financial time series. The estimand and identification strategy are defined separately for each hypothesis. Data are collected from documented official and licensed sources, retained with provenance and release dates, validated for units and coverage, and transformed using reproducible code. Country and firm identifiers are harmonized with stable keys; source-native classifications are preserved with explicit crosswalks.

Panel estimators use entity and time effects when appropriate to the research design. Time-series models are selected after examining integration, structural breaks, and dynamic dependence. IV, DiD, synthetic control, and event-study estimates are described as causal only when their assumptions are argued and tested to the extent possible. Robust inference accounts for heteroskedasticity, serial correlation, and treatment clustering. Primary outcomes and specifications are separated from exploratory analyses, and multiple testing is addressed across related claims.

Robustness analyses include alternate measures, samples, lag structures, estimators, placebo tests, pre-trend checks where applicable, and sensitivity to missing-data rules. Limitations include inconsistent international definitions, revised macroeconomic vintages, licensed-data coverage, proxy measurement error, selection into treatment, limited time-series observations, and external-validity constraints. Results are research outputs, not guaranteed forecasts or investment advice.

## Data and implementation caveats
- WDI and many official APIs have rate limits and schema/version changes; cache raw responses and log retrieval time.
- FRED requires an API key for its API; keep keys in environment variables, never in code or commits.
- IMF and BIS interfaces vary by dataset and SDMX version. Discover the actual dataflow, dimensions, and series key before requesting observations; there is no universal endpoint/key that works for every dataset.
- Commercial ESG, Compustat, BoardEx, PATSTAT, and some fund/market datasets require licenses or access permissions.
- Missing observations are not zero. Distinguish not published, not applicable, restricted, licensed, and missing.
- Do not claim empirical findings until the pipeline is run on documented data and results are reviewed.
