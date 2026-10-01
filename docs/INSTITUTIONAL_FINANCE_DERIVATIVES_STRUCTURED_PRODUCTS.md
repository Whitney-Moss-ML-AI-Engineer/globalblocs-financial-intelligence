# GlobalBLOCS Institutional Finance, Derivatives & Structured Products Manual

## Scope

The GlobalBLOCS institutional-finance catalog contains 50 products spanning derivatives, options, futures/forwards, structured finance, and fixed-income/credit instruments.

Each product is standardized around:

1. Definition
2. Purpose
3. How it works
4. Parties involved
5. Cash flows
6. Pricing methodology
7. Risk characteristics
8. Return characteristics
9. Typical buyers and sellers
10. Regulatory oversight
11. Real-world applications
12. Python pricing/analytics
13. Market-data identifiers
14. Related regulatory filings
15. Advantages
16. Disadvantages
17. Historical examples

## Product taxonomy

### Derivatives
TRS, interest-rate swaps, currency swaps, cross-currency swaps, CDS, equity swaps, variance swaps, volatility swaps, inflation swaps, commodity swaps.

### Options
Bond options, interest-rate options, swaptions, equity options, index options, currency options, commodity options, barrier options, Asian options, Bermudan options.

### Futures & Forwards
Interest-rate forwards, FRAs, Treasury futures, bond futures, equity-index futures, commodity futures, currency futures, OIS, SOFR futures, Eurodollar futures (historical/legacy).

### Structured Finance
TOB trusts, CDOs, CLOs, MBS, CMBS, ABS, RMBS, covered bonds, structured notes, principal-protected notes.

### Fixed Income & Credit
Corporate bonds, municipal bonds, Treasury bills, Treasury notes, Treasury bonds, FRNs, convertible bonds, preferred stock, commercial paper, repos.

## Analytical architecture

Instrument
→ Contract/reference data
→ Market data
→ Cash-flow engine
→ Pricing/valuation
→ Greeks/sensitivities where applicable
→ Credit/counterparty risk
→ Liquidity analysis
→ Stress/scenario analysis
→ Portfolio exposure
→ Macro/business-cycle context
→ Regulatory/provenance layer
→ ML/deep-learning features

## Research and ML controls

Every time-sensitive observation should retain point-in-time availability. The system should prevent later filings, amended statements, restatements, ratings actions or market observations from entering an earlier research window.

## Identifiers

Bloomberg and LSEG/Refinitiv identifiers are provider-specific and often licensed. GlobalBLOCS should resolve identifiers from authorized reference-data sources instead of guessing or hard-coding identifiers.

## Regulatory mapping

Product records should connect to applicable SEC, CFTC, FINRA, Federal Reserve, OCC, FDIC, banking-regulator, clearing and jurisdiction-specific requirements. The mapping should preserve source, effective date and jurisdiction.

## Historical case-study framework

Where evidence supports the relationship, product profiles can include documented case studies involving:

- Long-Term Capital Management (LTCM)
- 2008 financial crisis
- Archegos Capital Management
- Silicon Valley Bank

Historical cases should explain the actual instrument/exposure, mechanism of transmission, liquidity or collateral dynamics, and regulatory lessons without implying that one event represents every use of the product.
