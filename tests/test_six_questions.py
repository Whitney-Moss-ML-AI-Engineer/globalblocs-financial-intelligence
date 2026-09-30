import pandas as pd
from globalblocs.analytics.six_questions import run_six_questions

def test_six_question_report_runs():
    df = pd.DataFrame({"entity_name":["A"]*6+["B"]*6,
                       "period":list(range(2015,2021))*2,
                       "value":range(12)})
    report = run_six_questions(df, "value", "entity_name", "period")
    assert "mean" in report.descriptive.columns
    assert report.inferential["p_value"] is not None
    assert report.causal["status"] == "design template only"
