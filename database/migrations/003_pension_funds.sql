-- GlobalBLOCS: traceable global pension fund universe.
-- Apply after reviewing the repository's database/schema.sql conventions.
CREATE TABLE IF NOT EXISTS pension_fund (
    pension_fund_id BIGSERIAL PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    country_code CHAR(2),
    country_name_source TEXT,
    fund_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (canonical_name, country_code)
);

CREATE TABLE IF NOT EXISTS pension_fund_source (
    pension_fund_source_id BIGSERIAL PRIMARY KEY,
    pension_fund_id BIGINT REFERENCES pension_fund(pension_fund_id),
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    document_url TEXT,
    publication_year INTEGER,
    retrieved_at TIMESTAMPTZ NOT NULL,
    content_sha256 CHAR(64),
    license_notes TEXT,
    verification_status TEXT NOT NULL DEFAULT 'needs_source_review',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS pension_fund_snapshot (
    pension_fund_snapshot_id BIGSERIAL PRIMARY KEY,
    pension_fund_id BIGINT NOT NULL REFERENCES pension_fund(pension_fund_id),
    ranking_provider TEXT,
    ranking_edition_year INTEGER,
    published_rank INTEGER,
    aum_value NUMERIC(24, 4),
    aum_currency CHAR(3),
    aum_usd NUMERIC(24, 4),
    aum_as_of_date DATE,
    aum_usd_fx_rate NUMERIC(24, 10),
    fx_source TEXT,
    fx_rate_date DATE,
    source_id BIGINT REFERENCES pension_fund_source(pension_fund_source_id),
    source_row_hash CHAR(64),
    verification_status TEXT NOT NULL DEFAULT 'needs_source_review',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (ranking_provider, ranking_edition_year, published_rank, source_row_hash)
);

CREATE INDEX IF NOT EXISTS idx_pension_fund_snapshot_rank
    ON pension_fund_snapshot (ranking_provider, ranking_edition_year, published_rank);
CREATE INDEX IF NOT EXISTS idx_pension_fund_snapshot_asof
    ON pension_fund_snapshot (aum_as_of_date);
CREATE INDEX IF NOT EXISTS idx_pension_fund_source_retrieved
    ON pension_fund_source (retrieved_at);
