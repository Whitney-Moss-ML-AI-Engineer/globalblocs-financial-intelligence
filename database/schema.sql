CREATE SCHEMA IF NOT EXISTS metadata;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS compliance;

CREATE TABLE IF NOT EXISTS metadata.source (
  source_id BIGSERIAL PRIMARY KEY,
  source_code VARCHAR(100) UNIQUE NOT NULL,
  provider_name VARCHAR(255) NOT NULL,
  source_name VARCHAR(255) NOT NULL,
  access_method VARCHAR(80) NOT NULL,
  source_url TEXT,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metadata.dataset (
  dataset_id BIGSERIAL PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES metadata.source(source_id),
  dataset_code VARCHAR(150) NOT NULL,
  dataset_name VARCHAR(255) NOT NULL,
  source_version VARCHAR(150),
  frequency VARCHAR(50),
  release_date DATE,
  UNIQUE(source_id, dataset_code)
);

CREATE TABLE IF NOT EXISTS metadata.variable (
  variable_id BIGSERIAL PRIMARY KEY,
  dataset_id BIGINT NOT NULL REFERENCES metadata.dataset(dataset_id),
  source_variable_name TEXT NOT NULL,
  canonical_variable_name TEXT,
  data_type VARCHAR(50),
  unit TEXT,
  description TEXT,
  UNIQUE(dataset_id, source_variable_name)
);

CREATE TABLE IF NOT EXISTS core.entity (
  entity_id BIGSERIAL PRIMARY KEY,
  entity_type VARCHAR(50) NOT NULL,
  entity_code VARCHAR(100),
  entity_name TEXT NOT NULL,
  country_code CHAR(3),
  valid_from DATE,
  valid_to DATE
);

CREATE TABLE IF NOT EXISTS core.institution (
  institution_id BIGSERIAL PRIMARY KEY,
  entity_id BIGINT REFERENCES core.entity(entity_id),
  institution_type VARCHAR(100),
  legal_name TEXT,
  regulator TEXT,
  cik VARCHAR(20),
  rssd_id VARCHAR(50),
  fdic_certificate_number VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS core.instrument (
  instrument_id BIGSERIAL PRIMARY KEY,
  instrument_type VARCHAR(100) NOT NULL,
  identifier_type VARCHAR(100),
  identifier_value VARCHAR(255),
  issuer_entity_id BIGINT REFERENCES core.entity(entity_id),
  currency CHAR(3),
  maturity_date DATE
);

CREATE TABLE IF NOT EXISTS core.period (
  period_id BIGSERIAL PRIMARY KEY,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  frequency VARCHAR(50) NOT NULL,
  year INTEGER,
  quarter INTEGER,
  month INTEGER,
  UNIQUE(period_start, period_end, frequency)
);

CREATE TABLE IF NOT EXISTS core.observation (
  observation_id BIGSERIAL PRIMARY KEY,
  dataset_id BIGINT NOT NULL REFERENCES metadata.dataset(dataset_id),
  variable_id BIGINT REFERENCES metadata.variable(variable_id),
  entity_id BIGINT REFERENCES core.entity(entity_id),
  instrument_id BIGINT REFERENCES core.instrument(instrument_id),
  period_id BIGINT REFERENCES core.period(period_id),
  observed_value NUMERIC,
  observed_text TEXT,
  unit TEXT,
  source_record_id TEXT,
  source_url TEXT,
  retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  source_payload_path TEXT,
  transformation_version VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS ix_observation_dataset_period
  ON core.observation(dataset_id, period_id);
CREATE INDEX IF NOT EXISTS ix_observation_entity_period
  ON core.observation(entity_id, period_id);
CREATE INDEX IF NOT EXISTS ix_observation_instrument_period
  ON core.observation(instrument_id, period_id);

CREATE TABLE IF NOT EXISTS compliance.regulatory_event (
  regulatory_event_id BIGSERIAL PRIMARY KEY,
  agency VARCHAR(100) NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  subject_entity_id BIGINT REFERENCES core.entity(entity_id),
  event_date DATE,
  docket_or_case_id TEXT,
  title TEXT,
  source_url TEXT,
  source_payload_path TEXT,
  retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metadata.data_quality_result (
  quality_result_id BIGSERIAL PRIMARY KEY,
  dataset_id BIGINT NOT NULL REFERENCES metadata.dataset(dataset_id),
  run_id UUID NOT NULL,
  check_name VARCHAR(150) NOT NULL,
  status VARCHAR(30) NOT NULL,
  records_checked BIGINT,
  records_failed BIGINT,
  details JSONB,
  checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
