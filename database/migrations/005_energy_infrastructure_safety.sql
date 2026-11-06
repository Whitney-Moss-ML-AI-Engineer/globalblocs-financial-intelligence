-- Energy infrastructure safety and operator-performance facts.
-- PHMSA public incident source files are versioned downloads; preserve the
-- original source record and the source-specific field dictionary.
CREATE TABLE IF NOT EXISTS energy.infrastructure_incident (
 incident_id BIGSERIAL PRIMARY KEY,
 source_code VARCHAR(80) NOT NULL DEFAULT 'PHMSA',
 source_dataset VARCHAR(120) NOT NULL,
 source_record_id TEXT NOT NULL,
 report_type VARCHAR(80),
 incident_date DATE,
 report_date DATE,
 operator_name TEXT,
 operator_id VARCHAR(80),
 asset_type VARCHAR(80),
 state_code CHAR(2),
 county_name TEXT,
 city_name TEXT,
 commodity TEXT,
 cause_category TEXT,
 fatalities INTEGER,
 injuries INTEGER,
 evacuation_count INTEGER,
 estimated_property_damage_usd NUMERIC(24,2),
 released_quantity NUMERIC(28,8),
 released_quantity_unit VARCHAR(40),
 source_file_name TEXT,
 source_file_version TEXT,
 source_url TEXT,
 raw_record JSONB NOT NULL,
 retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 UNIQUE(source_dataset,source_record_id)
);
CREATE INDEX IF NOT EXISTS ix_energy_incident_date ON energy.infrastructure_incident(incident_date DESC);
CREATE INDEX IF NOT EXISTS ix_energy_incident_operator ON energy.infrastructure_incident(operator_id,incident_date DESC);
CREATE INDEX IF NOT EXISTS ix_energy_incident_state ON energy.infrastructure_incident(state_code,incident_date DESC);
CREATE INDEX IF NOT EXISTS ix_energy_incident_cause ON energy.infrastructure_incident(cause_category,incident_date DESC);

CREATE TABLE IF NOT EXISTS energy.operator_performance (
 operator_performance_id BIGSERIAL PRIMARY KEY,
 source_code VARCHAR(80) NOT NULL DEFAULT 'PHMSA',
 source_dataset VARCHAR(120) NOT NULL,
 operator_id VARCHAR(80) NOT NULL,
 operator_name TEXT,
 period_start DATE NOT NULL,
 period_end DATE NOT NULL,
 system_type VARCHAR(100),
 metric_code VARCHAR(100) NOT NULL,
 metric_value NUMERIC(28,8),
 metric_unit VARCHAR(60),
 source_file_name TEXT,
 source_url TEXT,
 source_record_id TEXT,
 retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 UNIQUE(source_dataset,operator_id,period_end,system_type,metric_code)
);
CREATE INDEX IF NOT EXISTS ix_energy_operator_performance ON energy.operator_performance(operator_id,period_end DESC);
