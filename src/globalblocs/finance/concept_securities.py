"""U.S. listed security universe used to connect economic concepts to market instruments.

This is a research universe, not a claim that every U.S. security is causally driven by a
concept. It combines liquid U.S.-listed equities and ETFs that can serve as observable
market proxies. Direct Treasury/CUSIP coverage should be added through an authorized
reference-data source because yfinance does not provide a complete U.S. security master.
"""

US_SECURITY_UNIVERSE = {
    "Broad Market": [
        "SPY","VOO","IVV","DIA","QQQ","IWM","RSP","VTI"
    ],
    "Growth / Technology": [
        "AAPL","MSFT","NVDA","AMZN","GOOGL","META","AVGO","ORCL","CRM","ADBE","AMD","CSCO","INTC","QCOM","IBM","NOW","PLTR","XLK","QQQ"
    ],
    "Consumer": [
        "AMZN","WMT","COST","HD","LOW","MCD","NKE","SBUX","TGT","TJX","PG","KO","PEP","XLY","XLP"
    ],
    "Financials / Banking": [
        "JPM","BAC","C","WFC","GS","MS","BLK","SCHW","USB","PNC","TFC","COF","AXP","SPY","XLF","KRE"
    ],
    "Industrial / Infrastructure": [
        "CAT","DE","GE","HON","RTX","LMT","BA","UPS","FDX","UNP","CSX","WM","EMR","ETN","XLI"
    ],
    "Energy / Commodities": [
        "XOM","CVX","COP","EOG","SLB","OXY","MPC","VLO","PSX","HAL","XLE","GLD","SLV","DBC","USO"
    ],
    "Healthcare": [
        "UNH","LLY","JNJ","PFE","MRK","ABBV","ABT","TMO","DHR","ISRG","CVS","XLV"
    ],
    "Housing / Real Estate": [
        "DHI","LEN","PHM","TOL","NVR","ITB","XHB","HD","LOW","AMT","PLD","O","VNQ","XLRE"
    ],
    "Rates / Fixed Income": [
        "SGOV","SHY","IEI","IEF","TLT","TIP","LQD","HYG","BND","AGG","MUB","VCIT"
    ],
    "Inflation / Inflation Protection": [
        "TIP","SCHP","VTIP","LTPZ","GLD","DBC","XLE","XLP"
    ],
    "Labor / Employment Cycle": [
        "IWM","XLI","XLY","XLF","JPM","HD","WMT","UPS","FDX","MAN","RHI","ADP"
    ],
    "Trade / Global Exposure": [
        "CAT","DE","UPS","FDX","UNP","CSX","XOM","CVX","AAPL","MSFT","AMZN","KO","PEP","MMM","GE","SPY"
    ],
    "Money / Liquidity": [
        "SGOV","BIL","SHY","IEF","TLT","LQD","HYG","JPM","BAC","GS","MS","XLF"
    ],
    "Fiscal / Government Finance": [
        "TLT","IEF","SHY","SGOV","MUB","PIMCO?","SPY","XLI","CAT","HON"
    ],
    "Productivity / Innovation": [
        "MSFT","NVDA","AAPL","GOOGL","AMZN","META","AVGO","ORCL","CRM","ADBE","AMD","IBM","NOW","QQQ","XLK"
    ],
    "Market Structure / Risk": [
        "SPY","QQQ","IWM","DIA","TLT","HYG","LQD","GLD","USO","VNQ","XLF","XLK"
    ],
}

# Remove any placeholder/non-tradable entries before use.
for _k, _v in list(US_SECURITY_UNIVERSE.items()):
    US_SECURITY_UNIVERSE[_k] = [x for x in _v if "?" not in x]

CONCEPT_SECURITY_RULES = [
    (["inflation","consumer price","price level","demand-pull","cost-push","expected inflation"], "Inflation / Inflation Protection"),
    (["interest rate","loanable funds","time value of money","real interest","nominal interest","monetary policy"], "Rates / Fixed Income"),
    (["money supply","money demand","money multiplier","quantity theory","liquidity"], "Money / Liquidity"),
    (["bank","financial","credit","lending"], "Financials / Banking"),
    (["housing","real estate","rent","mortgage"], "Housing / Real Estate"),
    (["labor","employment","unemployment","human capital","wage","productivity"], "Labor / Employment Cycle"),
    (["trade","export","import","comparative advantage","absolute advantage","specialization","current account","balance of trade","open economy"], "Trade / Global Exposure"),
    (["energy","oil","commodity","production","supply","resource"], "Energy / Commodities"),
    (["technology","innovation","research and development","research & development","productivity"], "Productivity / Innovation"),
    (["government","fiscal","public debt","deficit","budget","crowding out"], "Fiscal / Government Finance"),
    (["market","demand","supply","equilibrium","scarcity","opportunity cost","business cycle","growth","gdp","consumption","investment"], "Broad Market"),
]

def concept_security_categories(concept_name: str):
    """Return relevant U.S.-listed security categories for an economic concept."""
    name = (concept_name or "").lower()
    categories = []
    for terms, category in CONCEPT_SECURITY_RULES:
        if any(term in name for term in terms):
            categories.append(category)
    if not categories:
        categories = ["Broad Market"]
    # Add a broad-market benchmark to every concept for comparison.
    if "Broad Market" not in categories:
        categories.append("Broad Market")
    return categories

def securities_for_concept(concept_name: str):
    categories = concept_security_categories(concept_name)
    seen = set()
    rows = []
    for category in categories:
        for ticker in US_SECURITY_UNIVERSE.get(category, []):
            if ticker not in seen:
                seen.add(ticker)
                rows.append({"ticker": ticker, "security_group": category, "concept": concept_name})
    return rows
