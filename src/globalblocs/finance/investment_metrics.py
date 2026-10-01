"""Global BLOC investment metrics engine.

Calculates 50 commonly used investment metrics and attaches a performance/trend
interpretation to each result. Values are research outputs, not investment advice.
"""
import numpy as np
import pandas as pd

METRICS = [
    (1, "Total Return", "Return"), (2, "Annualized Return (CAGR)", "Return"),
    (3, "Absolute Return", "Return"), (4, "Holding Period Return (HPR)", "Return"),
    (5, "Expected Return", "Return"), (6, "Excess Return", "Return"),
    (7, "Real Return", "Return"), (8, "Risk-Adjusted Return", "Return"),
    (9, "Dividend Yield", "Return"), (10, "Capital Gain Yield", "Return"),
    (11, "Standard Deviation", "Risk"), (12, "Variance", "Risk"),
    (13, "Beta", "Risk"), (14, "Alpha", "Risk"), (15, "Maximum Drawdown (MDD)", "Risk"),
    (16, "Downside Deviation", "Risk"), (17, "Value at Risk (VaR)", "Risk"),
    (18, "Conditional Value at Risk (CVaR)", "Risk"), (19, "Tracking Error", "Risk"),
    (20, "Volatility", "Risk"), (21, "Sharpe Ratio", "Risk-Adjusted"),
    (22, "Sortino Ratio", "Risk-Adjusted"), (23, "Treynor Ratio", "Risk-Adjusted"),
    (24, "Information Ratio", "Risk-Adjusted"), (25, "Calmar Ratio", "Risk-Adjusted"),
    (26, "Omega Ratio", "Risk-Adjusted"), (27, "Jensen's Alpha", "Risk-Adjusted"),
    (28, "Appraisal Ratio", "Risk-Adjusted"), (29, "M² Measure", "Risk-Adjusted"),
    (30, "R-Squared (R²)", "Risk-Adjusted"), (31, "P/E", "Valuation"),
    (32, "Forward P/E", "Valuation"), (33, "P/B", "Valuation"),
    (34, "P/S", "Valuation"), (35, "P/CF", "Valuation"), (36, "Enterprise Value", "Valuation"),
    (37, "EV/EBITDA", "Valuation"), (38, "PEG Ratio", "Valuation"),
    (39, "Dividend Payout Ratio", "Valuation"), (40, "FCF Yield", "Valuation"),
    (41, "Asset Allocation", "Portfolio"), (42, "Portfolio Turnover", "Portfolio"),
    (43, "Portfolio Concentration Ratio", "Portfolio"), (44, "Correlation Coefficient", "Portfolio"),
    (45, "Covariance", "Portfolio"), (46, "Portfolio Expected Return", "Portfolio"),
    (47, "Portfolio Variance", "Portfolio"), (48, "Portfolio Standard Deviation", "Portfolio"),
    (49, "Portfolio Beta", "Portfolio"), (50, "Portfolio Sharpe Ratio", "Portfolio"),
]

DEFINITIONS = {
    1:"Overall gain/loss including price appreciation and dividends.",
    2:"Compound annual growth rate over the selected holding period.",
    3:"Raw change in investment value over the selected period.",
    4:"Return earned during the ownership period.",
    5:"Historical expected return estimate based on the selected return series.",
    6:"Return above the selected benchmark.",
    7:"Return adjusted for an inflation assumption.",
    8:"Return relative to measured risk, represented here by Sharpe ratio.",
    9:"Annual dividend divided by current price.",
    10:"Price appreciation excluding dividends.",
    11:"Standard deviation of periodic returns.",
    12:"Variance of periodic returns.",
    13:"Sensitivity of the security to benchmark returns.",
    14:"Return unexplained by the benchmark beta relationship.",
    15:"Largest peak-to-trough decline.",
    16:"Standard deviation of returns below the target threshold.",
    17:"Return quantile used as an estimated loss threshold.",
    18:"Average return in the tail beyond the VaR threshold.",
    19:"Standard deviation of active returns versus benchmark.",
    20:"Annualized standard deviation of periodic returns.",
    21:"Excess return per unit of total volatility.",
    22:"Excess return per unit of downside deviation.",
    23:"Excess return per unit of systematic risk.",
    24:"Active return per unit of tracking error.",
    25:"Annualized return relative to maximum drawdown.",
    26:"Ratio of gains above a threshold to losses below it.",
    27:"Benchmark-adjusted alpha from a CAPM-style regression.",
    28:"Alpha divided by residual volatility.",
    29:"Risk-adjusted return expressed at the benchmark volatility.",
    30:"Variance share explained by benchmark returns.",
    31:"Price divided by trailing earnings per share.",
    32:"Price divided by forward earnings per share.",
    33:"Market price relative to book value per share.",
    34:"Market capitalization relative to revenue.",
    35:"Market capitalization relative to operating cash flow.",
    36:"Enterprise value: equity value plus debt and minority interest less cash.",
    37:"Enterprise value relative to EBITDA.",
    38:"P/E relative to an earnings-growth rate.",
    39:"Dividends relative to earnings.",
    40:"Free cash flow relative to market value.",
    41:"Weight of each security in the selected portfolio.",
    42:"Trading activity relative to portfolio value; estimated from available history.",
    43:"Largest portfolio weight, a simple concentration measure.",
    44:"Correlation of the selected securities' returns.",
    45:"Covariance of selected securities' returns.",
    46:"Weighted expected return of the selected portfolio.",
    47:"Variance of portfolio returns using the covariance matrix.",
    48:"Standard deviation of portfolio returns.",
    49:"Weighted beta relative to the benchmark.",
    50:"Portfolio excess return per unit of portfolio volatility.",
}

def _safe(x):
    try:
        if x is None or not np.isfinite(float(x)): return np.nan
        return float(x)
    except (TypeError, ValueError):
        return np.nan

def _info_num(info, *keys):
    for k in keys:
        v = info.get(k)
        if v is not None:
            try: return float(v)
            except (TypeError, ValueError): pass
    return np.nan

def _annual_return(r):
    if len(r) == 0: return np.nan
    return float((1 + r).prod() ** (252 / len(r)) - 1)

def _beta_alpha(r, b):
    x = pd.concat([r, b], axis=1).dropna()
    if len(x) < 2 or x.iloc[:,1].var() == 0: return np.nan, np.nan, np.nan
    cov = x.iloc[:,0].cov(x.iloc[:,1]); bv = x.iloc[:,1].var()
    beta = cov / bv
    alpha_daily = x.iloc[:,0].mean() - beta * x.iloc[:,1].mean()
    return beta, alpha_daily * 252, x.corr().iloc[0,1] ** 2

def _trend(series, lookback=20):
    s = pd.Series(series).dropna()
    if len(s) < max(lookback, 5): return "Insufficient history", np.nan
    a = s.iloc[-lookback:]
    slope = np.polyfit(np.arange(len(a)), a.values, 1)[0]
    scale = a.mean() if a.mean() else 1
    normalized = slope / abs(scale)
    if normalized > 0.001: return "Trending Up", normalized
    if normalized < -0.001: return "Trending Down", normalized
    return "Sideways", normalized

def _performance(metric_name, value, history):
    h = pd.Series(history).dropna()
    if len(h) < 10 or not np.isfinite(value):
        return "N/A", "Insufficient history"
    # For risk/valuation metrics, upward movement is not universally better.
    # The label describes direction, while the text avoids a value judgment.
    recent = h.tail(min(20, len(h))).mean()
    prior = h.iloc[:-min(20, len(h))].tail(min(60, len(h))).mean()
    if not np.isfinite(prior) or prior == 0:
        direction = "Stable"
    else:
        change = (recent - prior) / abs(prior)
        direction = "Improving" if change > .02 else "Deteriorating" if change < -.02 else "Stable"
    return direction, f"Recent metric level {direction.lower()} versus its prior comparison window."

def calculate_metrics(price_df, info=None, benchmark_df=None, inflation=0.0, portfolio_prices=None):
    info = info or {}
    d = price_df.copy()
    close = pd.to_numeric(d["Close"], errors="coerce").dropna()
    if close.empty: return pd.DataFrame()
    ret = close.pct_change().dropna()
    if benchmark_df is None:
        bclose = close.copy()
    else:
        bclose = pd.to_numeric(benchmark_df["Close"], errors="coerce").reindex(close.index).ffill()
    bret = bclose.pct_change().reindex(ret.index).dropna()
    aligned = pd.concat([ret, bret], axis=1).dropna()
    r, br = aligned.iloc[:,0], aligned.iloc[:,1]
    beta, alpha, r2 = _beta_alpha(r, br)
    rf_daily = (1 + 0.0) ** (1/252) - 1
    excess = r - rf_daily
    downside = r[r < rf_daily]
    dd = close / close.cummax() - 1
    mdd = dd.min()
    var95 = r.quantile(.05)
    cvar95 = r[r <= var95].mean()
    te = (r - br).std() * np.sqrt(252)
    ann_ret = _annual_return(r)
    ann_vol = r.std() * np.sqrt(252)
    sharpe = ((r.mean()-rf_daily)/r.std()*np.sqrt(252)) if r.std() else np.nan
    sortino = ((r.mean()-rf_daily)/downside.std()*np.sqrt(252)) if downside.std() else np.nan
    treynor = ((ann_ret-rf_daily*252)/beta) if beta and np.isfinite(beta) else np.nan
    info_ratio = ((ann_ret-_annual_return(br))/te) if te else np.nan
    calmar = ann_ret/abs(mdd) if mdd < 0 else np.nan
    threshold = rf_daily
    gains = (r[r > threshold]-threshold).sum()
    losses = (threshold-r[r < threshold]).sum()
    omega = gains/losses if losses else np.nan
    residual = r - (rf_daily + beta*(br-rf_daily)) if np.isfinite(beta) else pd.Series(dtype=float)
    appraisal = alpha/(residual.std()*np.sqrt(252)) if len(residual)>1 and residual.std() else np.nan
    m2 = rf_daily*252 + sharpe*br.std()*np.sqrt(252) if np.isfinite(sharpe) else np.nan
    current = close.iloc[-1]; start = close.iloc[0]
    years = max((close.index[-1]-close.index[0]).days/365.25, 1/365.25)
    total_return = current/start-1
    cagr = (current/start)**(1/years)-1
    dividend_yield = _info_num(info, "dividendYield")
    if dividend_yield > 1: dividend_yield /= 100
    market_cap = _info_num(info, "marketCap")
    trailing_eps = _info_num(info, "trailingEps")
    forward_eps = _info_num(info, "forwardEps")
    book = _info_num(info, "bookValue")
    revenue = _info_num(info, "totalRevenue", "revenue")
    ocf = _info_num(info, "operatingCashflow")
    ebitda = _info_num(info, "ebitda")
    ev = _info_num(info, "enterpriseValue")
    growth = _info_num(info, "earningsGrowth")
    payout = _info_num(info, "payoutRatio")
    fcf = _info_num(info, "freeCashflow")
    peg = _info_num(info, "pegRatio")
    real_return = (1+total_return)/(1+inflation)-1 if inflation > -1 else np.nan
    values = {
        "Total Return": total_return, "Annualized Return (CAGR)": cagr,
        "Absolute Return": current-start, "Holding Period Return (HPR)": total_return,
        "Expected Return": ann_ret, "Excess Return": ann_ret-_annual_return(br),
        "Real Return": real_return, "Risk-Adjusted Return": sharpe,
        "Dividend Yield": dividend_yield, "Capital Gain Yield": total_return-dividend_yield,
        "Standard Deviation": r.std(), "Variance": r.var(), "Beta": beta, "Alpha": alpha,
        "Maximum Drawdown (MDD)": mdd, "Downside Deviation": downside.std(),
        "Value at Risk (VaR)": var95, "Conditional Value at Risk (CVaR)": cvar95,
        "Tracking Error": te, "Volatility": ann_vol, "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino, "Treynor Ratio": treynor, "Information Ratio": info_ratio,
        "Calmar Ratio": calmar, "Omega Ratio": omega, "Jensen's Alpha": alpha,
        "Appraisal Ratio": appraisal, "M² Measure": m2, "R-Squared (R²)": r2,
        "P/E": current/trailing_eps if trailing_eps else np.nan,
        "Forward P/E": current/forward_eps if forward_eps else np.nan,
        "P/B": current/book if book else np.nan,
        "P/S": market_cap/revenue if market_cap and revenue else np.nan,
        "P/CF": market_cap/ocf if market_cap and ocf else np.nan,
        "Enterprise Value": ev, "EV/EBITDA": ev/ebitda if ev and ebitda else np.nan,
        "PEG Ratio": peg, "Dividend Payout Ratio": payout,
        "FCF Yield": fcf/market_cap if fcf and market_cap else np.nan,
    }
    if portfolio_prices is None:
        portfolio_prices = pd.DataFrame({str(getattr(price_df, "name", "Asset")): close})
    pp = portfolio_prices.apply(pd.to_numeric, errors="coerce").dropna(how="all")
    weights = pd.Series(1/len(pp.columns), index=pp.columns)
    pr = pp.pct_change().dropna()
    common = pr.index.intersection(bret.index)
    port_ret = pr.loc[common].dot(weights) if len(common) else pd.Series(dtype=float)
    if len(port_ret):
        cov = pr.cov()
        port_var = float(weights.T @ cov.values @ weights)
        port_vol = np.sqrt(port_var) * np.sqrt(252)
        port_ann = _annual_return(port_ret)
        port_beta = float(weights.dot(pd.Series({c:_beta_alpha(pr[c], bret.reindex(pr.index))[0] for c in pr.columns})))
        port_sharpe = (port_ann-rf_daily*252)/port_vol if port_vol else np.nan
        concentration = float(weights.max())
    else:
        port_ann=port_var=port_vol=port_beta=port_sharpe=concentration=np.nan
    values.update({
        "Asset Allocation": 1.0/len(pp.columns), "Portfolio Turnover": np.nan,
        "Portfolio Concentration Ratio": concentration, "Correlation Coefficient": pr.iloc[:,0].corr(pr.iloc[:,1]) if pr.shape[1] >= 2 else 1.0,
        "Covariance": pr.iloc[:,0].cov(pr.iloc[:,1]) if pr.shape[1] >= 2 else 0.0,
        "Portfolio Expected Return": port_ann, "Portfolio Variance": port_var,
        "Portfolio Standard Deviation": port_vol, "Portfolio Beta": port_beta,
        "Portfolio Sharpe Ratio": port_sharpe,
    })
    rows=[]
    for mid,name,cat in METRICS:
        v=_safe(values.get(name))
        # Direction is based on the metric's own time series where available;
        # for scalar fundamentals it compares the current value to a proxy history.
        if name in ["Total Return","Annualized Return (CAGR)","Absolute Return","Holding Period Return (HPR)","Expected Return","Excess Return","Real Return","Capital Gain Yield","Standard Deviation","Variance","Maximum Drawdown (MDD)","Downside Deviation","Value at Risk (VaR)","Conditional Value at Risk (CVaR)","Tracking Error","Volatility","Sharpe Ratio","Sortino Ratio","Treynor Ratio","Information Ratio","Calmar Ratio","Omega Ratio","Jensen's Alpha","Appraisal Ratio","M² Measure","R-Squared (R²)"]:
            hist = ret.rolling(20).mean().dropna() if name in ["Total Return","Annualized Return (CAGR)","Absolute Return","Holding Period Return (HPR)"] else ret.rolling(20).std().dropna()
        else:
            hist = pd.Series([v]) if np.isfinite(v) else pd.Series(dtype=float)
        direction, note = _performance(name, v, hist)
        trend, slope = _trend(hist) if len(hist) >= 10 else ("N/A", np.nan)
        rows.append({"ID":mid,"Metric":name,"Category":cat,"Value":v,"Direction":direction,"Trend":trend,"Performance Note":note,"Definition":DEFINITIONS[name]})
    return pd.DataFrame(rows)

def metric_catalog():
    return pd.DataFrame([{"ID":i,"Metric":n,"Category":c,"Definition":DEFINITIONS[n]} for i,n,c in METRICS])
