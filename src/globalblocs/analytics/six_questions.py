"""Reusable implementation of the six data-analysis question types."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

@dataclass
class SixQuestionReport:
    descriptive: pd.DataFrame
    exploratory: pd.DataFrame
    inferential: dict
    predictive: dict
    causal: dict
    mechanistic: dict

def run_six_questions(df: pd.DataFrame, value_col: str, group_col: str | None = None,
                      time_col: str | None = None, target_col: str | None = None,
                      predictors: Sequence[str] | None = None) -> SixQuestionReport:
    work = df.copy()
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[value_col])
    descriptive = work[value_col].describe().to_frame("value")
    if group_col and group_col in work:
        descriptive = work.groupby(group_col)[value_col].agg(
            ["count", "mean", "median", "std", "min", "max"]
        ).sort_values("count", ascending=False)
    numeric = work.select_dtypes(include=np.number)
    exploratory = numeric.corr(numeric_only=True) if len(numeric.columns) > 1 else pd.DataFrame()
    inferential = {"method": "one-sample t-test", "statistic": None, "p_value": None}
    x = work[value_col].dropna()
    if len(x) >= 2:
        from scipy import stats
        stat, p_value = stats.ttest_1samp(x, x.mean())
        inferential.update(statistic=float(stat), p_value=float(p_value))
    predictive = {"status": "not run"}
    if target_col and predictors and all(c in work for c in [target_col, *predictors]):
        model_df = work[[target_col, *predictors]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(model_df) >= 10:
            split = int(len(model_df) * 0.8)
            train, test = model_df.iloc[:split], model_df.iloc[split:]
            model = LinearRegression().fit(train[list(predictors)], train[target_col])
            pred = model.predict(test[list(predictors)])
            predictive = {"method": "time-ordered linear regression",
                          "mae": float(mean_absolute_error(test[target_col], pred)),
                          "r2": float(r2_score(test[target_col], pred))}
    causal = {"status": "design template only"}
    if time_col and group_col and target_col and predictors and all(
        c in work for c in [time_col, group_col, target_col, *predictors]
    ):
        formula = f"{target_col} ~ " + " + ".join(predictors) + f" + C({group_col}) + C({time_col})"
        causal = {"method": "two-way fixed-effects regression template",
                  "formula": formula,
                  "warning": "Association is not causation; consider lags, endogeneity controls, IV/DiD where justified."}
    mechanistic = {"status": "requires domain mechanism specification",
                   "recommended": ["map inputs -> mechanisms -> outcomes",
                                   "test temporal ordering and feedback loops",
                                   "use structural equations or decomposition when theory supports them"]}
    return SixQuestionReport(descriptive, exploratory, inferential, predictive, causal, mechanistic)
