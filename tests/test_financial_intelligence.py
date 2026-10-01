import pandas as pd
from globalblocs.finance.api_etl_eda import api_etl_eda_pipeline

def test_api_etl_eda_pipeline_builds_dictionary_silver_and_features():
    frame=pd.DataFrame({"date":["2026-01-01","2026-01-02","2026-01-03"],"price":["100","102","105"],"rate":["2.0","2.5","3.0"]})
    out=api_etl_eda_pipeline(frame,"Test API","inline",[
        {"column":"date","operation":"to_datetime"},
        {"column":"price","operation":"to_numeric"},
        {"column":"rate","operation":"to_numeric"},
    ],[
        {"feature_name":"price_return","source_column":"price","operation":"pct_change"},
        {"feature_name":"rate_change","source_column":"rate","operation":"diff"},
    ])
    assert len(out["data_dictionary"])==3
    assert "silver" in out and "feature_table" in out and "feature_matrix" in out
    assert "price_return" in out["feature_matrix"].columns

