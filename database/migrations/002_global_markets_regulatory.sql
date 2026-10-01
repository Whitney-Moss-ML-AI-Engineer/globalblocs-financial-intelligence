-- Global market/regulatory extension
CREATE TABLE IF NOT EXISTS core.jurisdiction (
    jurisdiction_id BIGSERIAL PRIMARY KEY,
    iso2 CHAR(2),
    iso3 CHAR(3),
    name TEXT NOT NULL,
    region TEXT,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS core.market_venue (
    market_venue_id BIGSERIAL PRIMARY KEY,
    jurisdiction_id BIGINT REFERENCES core.jurisdiction(jurisdiction_id),
    venue_name TEXT NOT NULL,
    venue_type TEXT NOT NULL,
    mic_code TEXT,
    website TEXT,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS core.regulator (
    regulator_id BIGSERIAL PRIMARY KEY,
    jurisdiction_id BIGINT REFERENCES core.jurisdiction(jurisdiction_id),
    regulator_name TEXT NOT NULL,
    regulator_role TEXT NOT NULL,
    website TEXT,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS core.classification (
    classification_id BIGSERIAL PRIMARY KEY,
    code_system TEXT NOT NULL,
    code TEXT NOT NULL,
    label TEXT,
    parent_code TEXT,
    UNIQUE (code_system, code)
);

CREATE TABLE IF NOT EXISTS core.sector (
    sector_id BIGSERIAL PRIMARY KEY,
    classification_id BIGINT REFERENCES core.classification(classification_id),
    sector_code TEXT NOT NULL,
    sector_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS core.trade_observation (
    trade_observation_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT REFERENCES metadata.dataset(dataset_id),
    reporter_jurisdiction_id BIGINT REFERENCES core.jurisdiction(jurisdiction_id),
    partner_jurisdiction_id BIGINT REFERENCES core.jurisdiction(jurisdiction_id),
    classification_system TEXT,
    product_code TEXT,
    flow TEXT NOT NULL,
    period_id BIGINT REFERENCES core.period(period_id),
    quantity NUMERIC,
    quantity_unit TEXT,
    trade_value NUMERIC,
    currency TEXT,
    tariff_rate NUMERIC,
    source_record_id TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.market_observation (
    market_observation_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT REFERENCES metadata.dataset(dataset_id),
    market_venue_id BIGINT REFERENCES core.market_venue(market_venue_id),
    instrument_id BIGINT REFERENCES core.instrument(instrument_id),
    period_id BIGINT REFERENCES core.period(period_id),
    price NUMERIC,
    volume NUMERIC,
    turnover NUMERIC,
    market_cap NUMERIC,
    volatility NUMERIC,
    open_interest NUMERIC,
    source_record_id TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.sector_observation (
    sector_observation_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT REFERENCES metadata.dataset(dataset_id),
    jurisdiction_id BIGINT REFERENCES core.jurisdiction(jurisdiction_id),
    sector_id BIGINT REFERENCES core.sector(sector_id),
    period_id BIGINT REFERENCES core.period(period_id),
    output_value NUMERIC,
    value_added NUMERIC,
    employment NUMERIC,
    wages NUMERIC,
    productivity NUMERIC,
    imports NUMERIC,
    exports NUMERIC,
    investment NUMERIC,
    capacity_utilization NUMERIC,
    energy_use NUMERIC,
    business_count NUMERIC,
    insolvencies NUMERIC,
    source_record_id TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_trade_reporter_partner_period
ON core.trade_observation(reporter_jurisdiction_id, partner_jurisdiction_id, period_id);

CREATE INDEX IF NOT EXISTS ix_market_venue_period
ON core.market_observation(market_venue_id, period_id);

CREATE INDEX IF NOT EXISTS ix_sector_jurisdiction_sector_period
ON core.sector_observation(jurisdiction_id, sector_id, period_id);
