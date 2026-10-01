-- GlobalBLOCS canonical financial warehouse contract
CREATE SCHEMA IF NOT EXISTS globalblocs;
CREATE TABLE IF NOT EXISTS globalblocs.metric_observation (
  metric_id INTEGER NOT NULL,
  entity_id VARCHAR(128) NOT NULL,
  period_start DATE,
  period_end DATE,
  available_to_market_date TIMESTAMP,
  value NUMERIC,
  source_provider VARCHAR(128),
  source_record_id VARCHAR(256),
  quality_grade VARCHAR(16),
  retrieved_at TIMESTAMP,
  PRIMARY KEY(metric_id, entity_id, period_end, source_provider)
);
CREATE INDEX IF NOT EXISTS idx_metric_observation_available ON globalblocs.metric_observation(available_to_market_date);
CREATE INDEX IF NOT EXISTS idx_metric_observation_metric ON globalblocs.metric_observation(metric_id);
