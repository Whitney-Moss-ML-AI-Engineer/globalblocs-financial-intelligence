# GlobalBLOCS Ingestion Matrix

| Domain | Priority sources | Main ingestion | Storage | Primary output |
|---|---|---|---|---|
| Economic Cycle | BEA, BLS, FRED, Census, Fed | API/export | Bronze/Silver/PostgreSQL | cycle indicators |
| Corporate | SEC EDGAR/XBRL | API/filings | Bronze/PostgreSQL | fundamentals |
| Banking | FDIC/FFIEC, Fed Y-9C, OCC | API/export | Bronze/PostgreSQL | bank health |
| Institutional | SEC | EDGAR | Bronze/PostgreSQL | holdings/ownership |
| Credit | Fed Z.1, OCC, FDIC, FRED | API/export | Bronze/PostgreSQL | credit risk |
| Derivatives | CFTC, SEC | API/export | Bronze/PostgreSQL | positioning |
| Structured Finance | SEC, Fed | filings/reports | Bronze/PostgreSQL | securitized credit |
| Consumer | CFPB, Fed G.19, Census | API/export | Bronze/PostgreSQL | consumer health |
| Sentiment | FINRA, CFTC, SEC | API/export | Bronze/PostgreSQL | positioning proxies |
| International | Treasury TIC, BEA, Fed H.10 | API/export | Bronze/PostgreSQL | capital flows |
| Monetary Policy | Fed/FOMC/FRED | releases/API | Bronze/PostgreSQL | policy indicators |
| Risk & Compliance | FinCEN, SEC, FINRA, PCAOB, OCC, FDIC, CFTC, CFPB | public release/API | Bronze/PostgreSQL | regulatory risk |

Every ingestion run should record run ID, source/dataset ID, request parameters, retrieval timestamp, release/version, record count, checksum where practical, schema fingerprint, validation status, destination, and errors.

Quality gates: schema conformity, required fields, duplicates, null rates, numeric/date coercion, units, range changes, freshness, referential integrity, and source-to-target reconciliation.
