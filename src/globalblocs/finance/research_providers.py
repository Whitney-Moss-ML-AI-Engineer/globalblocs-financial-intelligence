"""Provider, regulatory, research and financial-instrument registry for GlobalBLOCS.

This module intentionally stores provider metadata and credentialed API templates rather
than assuming that licensed endpoints are publicly callable. Exact commercial endpoints,
authentication schemes and entitlements must be confirmed against each provider's
current contract/developer documentation.
"""

RATING_RESEARCH_PROVIDERS = [
    {"name":"S&P Global Ratings","category":"Credit Rating Agency","focus":"Issuer, sovereign, corporate, structured-finance and debt ratings","priority":"Core","access":"Commercial / licensed"},
    {"name":"Moody's Ratings","category":"Credit Rating Agency","focus":"Credit ratings, default risk and structured finance","priority":"Core","access":"Commercial / licensed"},
    {"name":"Fitch Ratings","category":"Credit Rating Agency","focus":"Issuer, debt, sovereign and structured-finance ratings","priority":"Core","access":"Commercial / licensed"},
    {"name":"DBRS Morningstar","category":"Credit Rating Agency","focus":"Credit ratings and structured-finance research","priority":"Core","access":"Commercial / licensed"},
    {"name":"Kroll Bond Rating Agency (KBRA)","category":"Credit Rating Agency","focus":"Corporate, financial-institution, structured-finance and public-finance ratings","priority":"Extended","access":"Commercial / licensed"},
    {"name":"Japan Credit Rating Agency (JCR)","category":"Credit Rating Agency","focus":"Corporate, sovereign and structured-finance credit ratings","priority":"Extended","access":"Commercial / licensed"},
    {"name":"Rating and Investment Information (R&I)","category":"Credit Rating Agency","focus":"Japanese and international credit ratings","priority":"Extended","access":"Commercial / licensed"},
    {"name":"China Chengxin International Credit Rating (CCXI)","category":"Credit Rating Agency","focus":"China-focused corporate, financial and sovereign credit assessment","priority":"Extended","access":"Commercial / licensed"},
    {"name":"Dagong Global Credit Rating","category":"Credit Rating Agency","focus":"Sovereign and corporate credit assessment","priority":"Extended","access":"Commercial / licensed"},
    {"name":"AM Best","category":"Credit Rating Agency","focus":"Insurance-company financial strength and credit ratings","priority":"Extended","access":"Commercial / licensed"},

    {"name":"Morningstar","category":"Equity & Investment Research","focus":"Equity, fund, portfolio and investment research","priority":"Core","access":"Commercial / licensed"},
    {"name":"CFRA Research","category":"Equity & Investment Research","focus":"Equity and investment research","priority":"Extended","access":"Commercial / licensed"},
    {"name":"Argus Research","category":"Equity & Investment Research","focus":"Equity research, estimates and investment research","priority":"Extended","access":"Commercial / licensed"},
    {"name":"Value Line","category":"Equity & Investment Research","focus":"Equity research, rankings, forecasts and financial statistics","priority":"Core","access":"Commercial / licensed"},
    {"name":"Zacks Investment Research","category":"Equity & Investment Research","focus":"Earnings estimates, rankings and quantitative equity research","priority":"Extended","access":"Commercial / licensed"},
    {"name":"The Motley Fool","category":"Equity & Investment Research","focus":"Investment commentary and equity research content","priority":"Reference","access":"Mixed / subscription"},
    {"name":"Visible Alpha","category":"Equity & Investment Research","focus":"Consensus estimates and fundamental company models","priority":"Core","access":"Commercial / licensed"},
    {"name":"New Constructs","category":"Equity & Investment Research","focus":"Fundamental research and accounting-based valuation analytics","priority":"Extended","access":"Commercial / licensed"},
    {"name":"Independent Research Group","category":"Equity & Investment Research","focus":"Independent investment research","priority":"Extended","access":"Commercial / licensed"},
    {"name":"Melius Research","category":"Equity & Investment Research","focus":"Sector and thematic equity research","priority":"Extended","access":"Commercial / licensed"},

    {"name":"Bloomberg L.P.","category":"Market Data & Financial Intelligence","focus":"Market data, news, analytics, terminals and financial intelligence","priority":"Core","access":"Commercial / licensed"},
    {"name":"FactSet","category":"Market Data & Financial Intelligence","focus":"Market data, fundamentals, estimates, portfolio analytics and research","priority":"Core","access":"Commercial / licensed"},
    {"name":"LSEG Data & Analytics","category":"Market Data & Financial Intelligence","focus":"Market data, reference data, analytics and financial intelligence","priority":"Core","access":"Commercial / licensed"},
    {"name":"MSCI","category":"Market Data & Financial Intelligence","focus":"Indexes, factor models, risk analytics and ESG research","priority":"Core","access":"Commercial / licensed"},
    {"name":"S&P Global Market Intelligence","category":"Market Data & Financial Intelligence","focus":"Capital IQ, market data, fundamentals, estimates and intelligence","priority":"Core","access":"Commercial / licensed"},
    {"name":"Moody's Analytics","category":"Market Data & Financial Intelligence","focus":"Credit risk, economic data, models and analytics","priority":"Core","access":"Commercial / licensed"},
    {"name":"Axioma","category":"Market Data & Financial Intelligence","focus":"Portfolio construction, factor risk and quantitative analytics","priority":"Core","access":"Commercial / licensed"},
    {"name":"Morningstar Direct","category":"Market Data & Financial Intelligence","focus":"Investment research, portfolio analytics and institutional data","priority":"Core","access":"Commercial / licensed"},
    {"name":"Capital IQ","category":"Market Data & Financial Intelligence","focus":"Company, transaction, market and financial data","priority":"Core","access":"Commercial / licensed"},
    {"name":"Refinitiv","category":"Market Data & Financial Intelligence","focus":"Market data and financial intelligence platform; legacy LSEG branding","priority":"Reference","access":"Commercial / licensed"},

    {"name":"J.P. Morgan Research","category":"Bank Research","focus":"Macro, equity, rates, credit, FX and commodities research","priority":"Core","access":"Bank research / subscription"},
    {"name":"Goldman Sachs Research","category":"Bank Research","focus":"Macro, equity, rates, credit and sector research","priority":"Core","access":"Bank research / subscription"},
    {"name":"Morgan Stanley Research","category":"Bank Research","focus":"Equity, macro, rates and industry research","priority":"Core","access":"Bank research / subscription"},
    {"name":"Bank of America Global Research","category":"Bank Research","focus":"Global macro, equity, fixed income and sector research","priority":"Core","access":"Bank research / subscription"},
    {"name":"Barclays Research","category":"Bank Research","focus":"Macro, rates, credit, equity and industry research","priority":"Extended","access":"Bank research / subscription"},
    {"name":"UBS Research","category":"Bank Research","focus":"Global macro, equity, rates and sector research","priority":"Core","access":"Bank research / subscription"},
    {"name":"Citi Research","category":"Bank Research","focus":"Global macro, FX, rates, credit, equity and commodities research","priority":"Core","access":"Bank research / subscription"},
    {"name":"Wells Fargo Investment Institute","category":"Bank Research","focus":"Asset allocation, markets and investment strategy research","priority":"Core","access":"Research / subscription"},
    {"name":"Deutsche Bank Research","category":"Bank Research","focus":"Macro, rates, credit, FX and equity research","priority":"Extended","access":"Bank research / subscription"},
    {"name":"Jefferies Research","category":"Bank Research","focus":"Equity, credit, macro and industry research","priority":"Extended","access":"Bank research / subscription"},

    {"name":"MSCI ESG Research","category":"ESG & Sustainability","focus":"ESG ratings, climate, controversy and sustainability research","priority":"Core","access":"Commercial / licensed"},
    {"name":"Sustainalytics","category":"ESG & Sustainability","focus":"ESG risk, controversies and sustainability research","priority":"Core","access":"Commercial / licensed"},
    {"name":"ISS ESG","category":"ESG & Sustainability","focus":"ESG ratings, governance and responsible-investment analytics","priority":"Extended","access":"Commercial / licensed"},
    {"name":"CDP","category":"ESG & Sustainability","focus":"Corporate environmental disclosure and climate data","priority":"Core","access":"Mixed / disclosure-based"},
    {"name":"FTSE Russell ESG Ratings","category":"ESG & Sustainability","focus":"ESG ratings, indexes and sustainability analytics","priority":"Core","access":"Commercial / licensed"},

    {"name":"Verisk Analytics","category":"Risk & Quantitative Analytics","focus":"Risk analytics, insurance, catastrophe and decision intelligence","priority":"Extended","access":"Commercial / licensed"},
    {"name":"Dun & Bradstreet","category":"Risk & Quantitative Analytics","focus":"Business credit, company information and risk intelligence","priority":"Core","access":"Commercial / licensed"},
    {"name":"Experian","category":"Risk & Quantitative Analytics","focus":"Credit, identity, business and consumer risk analytics","priority":"Core","access":"Commercial / licensed"},
    {"name":"Equifax","category":"Risk & Quantitative Analytics","focus":"Credit and risk information","priority":"Core","access":"Commercial / licensed"},
    {"name":"TransUnion","category":"Risk & Quantitative Analytics","focus":"Credit and risk information","priority":"Core","access":"Commercial / licensed"},
]

PRIORITY_PROVIDERS = ["S&P Global Ratings","Moody's Ratings","Fitch Ratings","Morningstar","MSCI","Bloomberg L.P.","FactSet","Value Line","Capital IQ","Moody's Analytics"]

REGULATORY_REPORTS = [
    {"agency":"Financial Crimes Enforcement Network (FinCEN)","reports":"SAR, CTR, FBAR","purpose":"AML, suspicious activity, cash transactions and foreign-account reporting","public_access":"Restricted / authorized access for SARs; public reporting and guidance are available"},
    {"agency":"U.S. Securities and Exchange Commission (SEC)","reports":"10-K, 10-Q, 8-K, 13F, Form 4, Schedule 13D/13G, Form ADV","purpose":"Public-company, ownership, insider and investment-adviser disclosures","public_access":"Public filings and APIs for many datasets"},
    {"agency":"Federal Deposit Insurance Corporation (FDIC)","reports":"Call Reports, Summary of Deposits, institution financials, bank failures","purpose":"Bank financial condition, deposits and failure history","public_access":"Public data and APIs"},
    {"agency":"Federal Reserve System","reports":"FR Y-9C, H.8, H.6, Z.1, H.4.1, FRED series","purpose":"Bank holding companies, banking aggregates, financial accounts and monetary conditions","public_access":"Public data; some APIs require registration/keys"},
    {"agency":"Office of the Comptroller of the Currency (OCC)","reports":"Quarterly Banking Profile and supervisory publications","purpose":"National-bank profitability, asset quality, capital and risk information","public_access":"Public reports and datasets"},
    {"agency":"Financial Industry Regulatory Authority (FINRA)","reports":"BrokerCheck, short-interest and TRACE-related market data","purpose":"Broker-dealer oversight and securities-market transparency","public_access":"Public tools/data; some APIs require credentials or agreements"},
    {"agency":"Commodity Futures Trading Commission (CFTC)","reports":"Commitment of Traders (COT) and enforcement/publications","purpose":"Futures positioning, derivatives-market oversight and enforcement","public_access":"Public reports/data"},
    {"agency":"National Futures Association (NFA)","reports":"Registration, BASIC and disciplinary information","purpose":"Futures and derivatives-industry registration and oversight","public_access":"Public search/data"},
    {"agency":"Consumer Financial Protection Bureau (CFPB)","reports":"Consumer Complaint Database and research","purpose":"Consumer-finance trends, complaints and supervisory research","public_access":"Public data and API"},
    {"agency":"Public Company Accounting Oversight Board (PCAOB)","reports":"Audit inspection reports and standards","purpose":"Audit quality, inspection findings and accounting oversight","public_access":"Public reports and standards"},
]

REGULATORY_SOURCE_CONFIG = {
    "SEC EDGAR": {"base_url":"https://data.sec.gov","auth":"User-Agent header","status":"Public API","notes":"Submissions and XBRL datasets; identify the registrant and filing before point-in-time analysis."},
    "FDIC BankFind": {"base_url":"https://banks.data.fdic.gov","auth":"Public API","status":"Public API","notes":"Institution, financial, deposit and failure datasets."},
    "Federal Reserve / FRED": {"base_url":"https://fred.stlouisfed.org","auth":"FRED API key for API endpoint; fredgraph CSV can be used for many public series","status":"Public data","notes":"Preserve series ID, observation date, frequency and retrieval timestamp."},
    "CFTC": {"base_url":"https://www.cftc.gov","auth":"Public files / reports","status":"Public data","notes":"COT data are periodic positioning reports; normalize report date and market."},
    "FINRA": {"base_url":"https://api.finra.org","auth":"Depends on dataset / entitlement","status":"Public or credentialed by dataset","notes":"Do not assume every FINRA dataset is anonymously callable."},
    "CFPB": {"base_url":"https://www.consumerfinance.gov","auth":"Public API/data","status":"Public data","notes":"Complaint records should be handled with privacy and aggregation controls."},
}

RATING_API_TEMPLATES = [
    {"provider":"S&P Global Ratings / Capital IQ","auth":"Commercial credentials; verify current OAuth/API-key scheme","endpoint":"Configure from licensed S&P developer documentation","example_query":"issuer/ticker lookup, ratings, fundamentals","safe_default":True},
    {"provider":"Moody's Ratings / Moody's Analytics","auth":"Commercial credentials; verify product-specific authentication","endpoint":"Configure from licensed Moody's developer documentation","example_query":"economic series, credit risk, ratings","safe_default":True},
    {"provider":"Fitch Ratings","auth":"Commercial credentials/token; verify current portal documentation","endpoint":"Configure from licensed Fitch developer documentation","example_query":"issuer/debt/rating lookup","safe_default":True},
    {"provider":"Morningstar","auth":"Commercial client credentials; verify current product entitlement","endpoint":"Configure from licensed Morningstar developer documentation","example_query":"equity/fund/portfolio research","safe_default":True},
    {"provider":"DBRS Morningstar","auth":"Commercial credentials/JWT or current licensed scheme","endpoint":"Configure from licensed DBRS Morningstar documentation","example_query":"issuer/debt/rating/document lookup","safe_default":True},
    {"provider":"KBRA","auth":"Commercial API key/credential; verify current portal documentation","endpoint":"Configure from licensed KBRA documentation","example_query":"ratings and issuer research","safe_default":True},
    {"provider":"AM Best","auth":"Commercial credentials; verify current product entitlement","endpoint":"Configure from licensed AM Best documentation","example_query":"insurance financial-strength ratings","safe_default":True},
    {"provider":"JCR","auth":"Commercial credentials; verify current product entitlement","endpoint":"Configure from licensed JCR documentation","example_query":"issuer/rating lookup","safe_default":True},
    {"provider":"R&I","auth":"Commercial credentials; verify current product entitlement","endpoint":"Configure from licensed R&I documentation","example_query":"issuer/rating lookup","safe_default":True},
    {"provider":"CCXI","auth":"Commercial credentials; verify current product entitlement","endpoint":"Configure from licensed CCXI documentation","example_query":"issuer/rating lookup","safe_default":True},
]

DERIVATIVE_PRODUCTS = [
    ("Total Return Swap (TRS)","Derivatives"),("Interest Rate Swap","Derivatives"),("Currency Swap","Derivatives"),("Cross-Currency Swap","Derivatives"),("Credit Default Swap (CDS)","Derivatives"),("Equity Swap","Derivatives"),("Variance Swap","Derivatives"),("Volatility Swap","Derivatives"),("Inflation Swap","Derivatives"),("Commodity Swap","Derivatives"),
    ("Bond Option","Options"),("Interest Rate Option","Options"),("Swaption","Options"),("Equity Option","Options"),("Index Option","Options"),("Currency Option","Options"),("Commodity Option","Options"),("Barrier Option","Options"),("Asian Option","Options"),("Bermudan Option","Options"),
    ("Interest Rate Forward","Futures & Forwards"),("Forward Rate Agreement (FRA)","Futures & Forwards"),("Treasury Future","Futures & Forwards"),("Bond Future","Futures & Forwards"),("Equity Index Future","Futures & Forwards"),("Commodity Future","Futures & Forwards"),("Currency Future","Futures & Forwards"),("Overnight Index Swap (OIS)","Futures & Forwards"),("SOFR Future","Futures & Forwards"),("Eurodollar Future (historical/legacy)","Futures & Forwards"),
    ("Tender Option Bond (TOB) Trust","Structured Finance"),("Collateralized Debt Obligation (CDO)","Structured Finance"),("Collateralized Loan Obligation (CLO)","Structured Finance"),("Mortgage-Backed Security (MBS)","Structured Finance"),("Commercial Mortgage-Backed Security (CMBS)","Structured Finance"),("Asset-Backed Security (ABS)","Structured Finance"),("Residential Mortgage-Backed Security (RMBS)","Structured Finance"),("Covered Bond","Structured Finance"),("Structured Note","Structured Finance"),("Principal-Protected Note","Structured Finance"),
    ("Corporate Bond","Fixed Income & Credit"),("Municipal Bond","Fixed Income & Credit"),("Treasury Bill","Fixed Income & Credit"),("Treasury Note","Fixed Income & Credit"),("Treasury Bond","Fixed Income & Credit"),("Floating Rate Note (FRN)","Fixed Income & Credit"),("Convertible Bond","Fixed Income & Credit"),("Preferred Stock","Fixed Income & Credit"),("Commercial Paper","Fixed Income & Credit"),("Repurchase Agreement (Repo)","Fixed Income & Credit"),
]

def provider_dataframe():
    return RATING_RESEARCH_PROVIDERS

def priority_provider_dataframe():
    return [x for x in RATING_RESEARCH_PROVIDERS if x["name"] in PRIORITY_PROVIDERS]

def regulatory_dataframe():
    return REGULATORY_REPORTS

def product_dataframe():
    return [{"id":i+1,"product":name,"category":category} for i,(name,category) in enumerate(DERIVATIVE_PRODUCTS)]

def credentialed_request_template(provider, endpoint, method="GET", params=None):
    """Return a safe request template. Secrets are intentionally never stored in source."""
    return {
        "provider": provider,
        "method": method,
        "endpoint": endpoint,
        "params": params or {},
        "headers": {
            "Authorization": "Bearer <TOKEN>",
            "Accept": "application/json",
        },
        "note": "Replace placeholders with credentials and endpoint details from the provider's licensed documentation. Never commit secrets."
    }
