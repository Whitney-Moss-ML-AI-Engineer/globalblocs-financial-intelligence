-- GlobalBLOCS Energy Intelligence domain
CREATE SCHEMA IF NOT EXISTS energy;
CREATE TABLE IF NOT EXISTS energy.company (
 company_id BIGSERIAL PRIMARY KEY, ticker VARCHAR(20) UNIQUE NOT NULL, company_name TEXT NOT NULL,
 segment VARCHAR(40) NOT NULL, subsector VARCHAR(100) NOT NULL, business_model TEXT, cik VARCHAR(20),
 exchange VARCHAR(40), active BOOLEAN NOT NULL DEFAULT TRUE,
 source_code VARCHAR(100) NOT NULL DEFAULT 'globalblocs_curated_universe', retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS energy.commodity (
 commodity_id BIGSERIAL PRIMARY KEY, commodity_code VARCHAR(40) UNIQUE NOT NULL,
 commodity_name TEXT NOT NULL, benchmark_symbol VARCHAR(30), unit VARCHAR(40) NOT NULL,
 source_code VARCHAR(100), active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS energy.market_observation (
 observation_id BIGSERIAL PRIMARY KEY, instrument_code VARCHAR(40) NOT NULL, observed_at TIMESTAMPTZ NOT NULL,
 price NUMERIC(24,8), currency CHAR(3) NOT NULL DEFAULT 'USD', unit VARCHAR(40),
 adjusted BOOLEAN NOT NULL DEFAULT FALSE, source_code VARCHAR(100) NOT NULL, source_url TEXT,
 retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(instrument_code, observed_at, source_code)
);
CREATE TABLE IF NOT EXISTS energy.operating_observation (
 operating_observation_id BIGSERIAL PRIMARY KEY, company_id BIGINT REFERENCES energy.company(company_id),
 asset_code VARCHAR(100), metric_code VARCHAR(100) NOT NULL, period_start DATE NOT NULL, period_end DATE NOT NULL,
 value NUMERIC(28,8), unit VARCHAR(60), source_code VARCHAR(100) NOT NULL, source_record_id TEXT,
 source_url TEXT, retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS energy.infrastructure_asset (
 asset_id BIGSERIAL PRIMARY KEY, asset_type VARCHAR(60) NOT NULL, asset_name TEXT NOT NULL,
 operator_company_id BIGINT REFERENCES energy.company(company_id), jurisdiction VARCHAR(100),
 latitude NUMERIC(10,7), longitude NUMERIC(10,7), capacity_value NUMERIC(24,8),
 capacity_unit VARCHAR(60), source_code VARCHAR(100) NOT NULL, source_record_id TEXT,
 source_url TEXT, retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS energy.regulatory_event (
 energy_event_id BIGSERIAL PRIMARY KEY, agency VARCHAR(100) NOT NULL, event_type VARCHAR(100) NOT NULL,
 company_id BIGINT REFERENCES energy.company(company_id), asset_id BIGINT REFERENCES energy.infrastructure_asset(asset_id),
 event_date DATE, severity VARCHAR(40), title TEXT, source_url TEXT, source_record_id TEXT,
 retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_energy_market_observation_instrument_date ON energy.market_observation(instrument_code, observed_at DESC);
CREATE INDEX IF NOT EXISTS ix_energy_operating_observation_company_period ON energy.operating_observation(company_id, period_end DESC);
CREATE INDEX IF NOT EXISTS ix_energy_infrastructure_operator ON energy.infrastructure_asset(operator_company_id);
CREATE INDEX IF NOT EXISTS ix_energy_regulatory_event_company_date ON energy.regulatory_event(company_id, event_date DESC);
