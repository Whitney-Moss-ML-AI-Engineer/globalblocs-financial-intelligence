# Global Markets, Regulatory, Trade & Sector Data

## Objective

GlobalBLOCS now treats each jurisdiction as a coordinated **financial-data ecosystem**, rather than treating a country as a single macroeconomic source.

For each country, the source registry seeks these institutional roles:

1. Stock exchange / market operator
2. Central bank
3. Banking/prudential supervisor
4. Securities/markets regulator
5. Trade/customs authority
6. National statistical office
7. Finance ministry / public-finance authority
8. Sector regulators and industry statistical agencies

This mirrors the U.S. model in which financial intelligence is distributed across institutions such as the Federal Reserve, OCC, FDIC, SEC, Treasury, Census, BLS, BEA, CFTC and sector agencies.

## International benchmark layer

The repository uses international institutions as a cross-country normalization and validation layer. The World Federation of Exchanges publishes hundreds of exchange-market indicators covering equities, derivatives, ETFs, IPOs and liquidity. The BIS provides international banking, debt, credit, derivatives, property, payments, exchange-rate and central-bank statistics. WTO and UN Comtrade provide global trade/product/partner data. 

These sources do **not** replace national authorities. They provide comparable aggregates, definitions, and validation checks.

## Country-level financial coverage

The registry currently establishes institutional mappings for major markets across:

- North America
- Latin America
- Europe
- Middle East
- Africa
- South Asia
- East Asia
- Southeast Asia
- Oceania

Examples include NYSE/Nasdaq, TMX, B3, LSE, Deutsche Börse, Euronext markets, SIX, JSE, Tadawul, NSE/BSE India, JPX, Shanghai/Shenzhen, HKEX, KRX, SGX, ASX, NZX and other major exchanges.

The WFE membership directory provides a current cross-check for the exchange universe. 

## Banking data model

The global banking layer should capture U.S.-analogous information where the local authority publishes it:

- bank balance sheets
- deposits
- loans
- securities portfolios
- nonperforming loans
- capital ratios
- liquidity ratios
- leverage
- net interest margins
- profitability
- provisioning
- asset quality
- bank failures/resolutions
- supervisory actions
- stress tests
- concentration/risk exposures
- cross-border claims

Country-specific terminology must be preserved in Bronze. Standardized fields belong in Silver/Gold.

## Trade/import/export model

Trade ingestion should preserve both country and product dimensions:

`country × partner × product × period × flow`

where flow is:

- import
- export
- re-export where available

Required dimensions:

- reporter
- partner
- HS/SITC code
- product description
- quantity
- quantity unit
- customs value
- trade value
- currency
- tariff
- duty
- trade agreement/preference
- transport mode where available

WTO merchandise statistics provide global imports/exports and product/country dimensions, while UN Comtrade provides detailed reporter/partner/product data. 

## Industry-sector model

GlobalBLOCS should support multiple classification systems rather than forcing every country into NAICS:

- ISIC — international baseline
- NAICS — North American
- NACE — European
- GICS — capital-markets sector classification
- HS — traded goods
- SITC — international trade classification
- CPC — products

The canonical sector layer should preserve the original classification and provide crosswalks.

### Core sector variables

For each country/sector/period:

- gross output
- value added
- revenue
- production
- employment
- wages
- productivity
- business count
- investment
- capacity utilization
- imports
- exports
- prices
- energy consumption
- credit exposure
- insolvencies
- foreign investment

Priority sectors include banking, insurance, energy, oil & gas, mining, manufacturing, semiconductors, technology, telecom, transportation, logistics, agriculture, pharmaceuticals, healthcare, construction, real estate, automotive, aerospace/defense, chemicals, utilities, retail and tourism.

## Exchange layer

The exchange layer should not be limited to daily stock prices.

It should support:

### Equities
- listings
- market capitalization
- trading value
- trading volume
- free float
- sector
- index membership
- corporate actions

### Fixed income
- government bonds
- corporate bonds
- municipal/subnational bonds where available
- yields
- spreads
- maturities

### Derivatives
- futures
- options
- swaps where accessible
- open interest
- volume
- settlement
- implied volatility
- contract specifications
- clearing information

### Market structure
- bid/ask
- spreads
- turnover
- volatility
- halts
- circuit breakers
- clearing activity

## Regulatory intelligence

Every regulatory document becomes a lineage-aware event:

`jurisdiction → regulator → entity → event → date → legal reference → source document`

Supported event types include:

- enforcement
- supervisory action
- bank failure
- license action
- issuer filing
- market halt
- disclosure
- capital action
- sanctions
- tariff/customs action
- merger/acquisition

## Data architecture

```
National exchanges
Central banks
Banking supervisors
Securities regulators
Trade/customs agencies
Statistics offices
Sector agencies
        ↓
Official source adapters
        ↓
Raw / Bronze
        ↓
Source-variable preservation
        ↓
Validation + lineage
        ↓
Silver standardized data
        ↓
Cross-country classification mapping
        ↓
Gold analytical layer
        ↓
PostgreSQL + Parquet
        ↓
FastAPI
        ↓
GlobalBLOCS Dashboard
```

## Source hierarchy

1. Official national authority
2. Official exchange
3. Official international organization
4. Licensed market-data source
5. Academic/research source
6. Secondary source only for validation/discovery

The system should never silently replace an official source with a commercial aggregator.

## Important implementation rule

Not every country publishes the same level of bank, securities, derivatives or sector detail. The registry therefore distinguishes:

- `available`
- `partial`
- `not_published`
- `licensed_required`
- `restricted`
- `discontinued`

This prevents missing data from being mistaken for zero activity.
