"""Production inventory of GlobalBLOCS analytical scripts exposed to the UI."""
SCRIPT_REGISTRY = [
    {"id":"source_connectors","area":"Ingestion","path":"globalblocs.ingestion.source_connectors","status":"ready"},
    {"id":"data_quality","area":"Validation","path":"globalblocs.validation.data_quality","status":"ready"},
    {"id":"financial_features","area":"Feature Engineering","path":"globalblocs.features.financial_features","status":"ready"},
    {"id":"economic_cycle","area":"Economics","path":"globalblocs.analytics.economic_cycle","status":"ready"},
    {"id":"risk_analytics","area":"Risk","path":"globalblocs.analytics.risk","status":"ready"},
    {"id":"model_registry","area":"ML / Deep Learning","path":"globalblocs.models.model_registry","status":"ready"},
    {"id":"api_ingestion","area":"API ETL / EDA","path":"globalblocs.finance.api_ingestion","status":"ready"},
    {"id":"api_etl_eda","area":"API ETL / EDA","path":"globalblocs.finance.api_etl_eda","status":"ready"},
    {"id":"investment_metrics","area":"Financial Metrics","path":"globalblocs.finance.investment_metrics","status":"ready"},
    {"id":"recession_intelligence","area":"Global Economics","path":"globalblocs.finance.recession_intelligence","status":"ready"},
    {"id":"global_intelligence","area":"Global Intelligence","path":"globalblocs.finance.global_intelligence","status":"ready"},
    {"id":"concept_securities","area":"Markets","path":"globalblocs.finance.concept_securities","status":"ready"},
    {"id":"research_providers","area":"Research / Regulation","path":"globalblocs.finance.research_providers","status":"ready"},
]
def list_scripts():
    return SCRIPT_REGISTRY
