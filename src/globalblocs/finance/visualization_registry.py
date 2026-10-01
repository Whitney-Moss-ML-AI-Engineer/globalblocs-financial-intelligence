"""Global BLOC visualization registry.

Metric-agnostic visualization metadata for the 350-metric financial intelligence
dashboard. Recommended visualizations are highlighted, but every registered
visualization remains selectable.
"""

VISUALIZATIONS = [
    {"id":"line","name":"Line Chart","category":"Trend","recommended_for":["returns","growth","ratios","financial_statements"],"reason":"Shows a metric through time."},
    {"id":"bar","name":"Bar Chart","category":"Comparison","recommended_for":["period_comparison","peer_comparison"],"reason":"Compares discrete periods, companies, or categories."},
    {"id":"area","name":"Area Chart","category":"Trend","recommended_for":["cumulative","drawdown"],"reason":"Emphasizes magnitude and cumulative change."},
    {"id":"histogram","name":"Histogram","category":"Distribution","recommended_for":["returns","risk","ratios"],"reason":"Shows the distribution of observations."},
    {"id":"box","name":"Box Plot","category":"Distribution","recommended_for":["returns","risk","ratios"],"reason":"Shows median, quartiles, spread, and outliers."},
    {"id":"violin","name":"Violin Plot","category":"Distribution","recommended_for":["returns","risk","ratios"],"reason":"Shows distribution shape and density."},
    {"id":"density","name":"Density Plot","category":"Distribution","recommended_for":["returns","risk","ratios"],"reason":"Shows a smoothed probability distribution."},
    {"id":"ecdf","name":"ECDF","category":"Distribution","recommended_for":["probability","returns"],"reason":"Shows the cumulative distribution."},
    {"id":"qq","name":"Q-Q Plot","category":"Statistical","recommended_for":["normality","residuals"],"reason":"Compares an observed distribution with a theoretical distribution."},
    {"id":"scatter","name":"Scatter Plot","category":"Relationship","recommended_for":["correlation","regression","factor_analysis"],"reason":"Shows the relationship between two numeric variables."},
    {"id":"heatmap","name":"Heatmap","category":"Relationship","recommended_for":["correlation_matrix","covariance_matrix"],"reason":"Encodes relationships across two dimensions."},
    {"id":"waterfall","name":"Waterfall","category":"Financial Statement","recommended_for":["income_statement","cash_flow","value_bridge"],"reason":"Shows sequential contributions to a total."},
    {"id":"radar","name":"Radar Chart","category":"Comparison","recommended_for":["multi_factor","portfolio"],"reason":"Compares multiple normalized dimensions."},
    {"id":"candlestick","name":"Candlestick","category":"Market","recommended_for":["price","ohlc"],"reason":"Displays OHLC price movement."},
    {"id":"ohlc","name":"OHLC Bar","category":"Market","recommended_for":["price","ohlc"],"reason":"Displays open, high, low, and close."},
    {"id":"volume","name":"Volume Chart","category":"Market","recommended_for":["volume"],"reason":"Shows trading volume through time."},
    {"id":"drawdown","name":"Drawdown","category":"Risk","recommended_for":["drawdown","portfolio_risk"],"reason":"Shows losses from prior peaks."},
    {"id":"var_cvar","name":"VaR / CVaR Distribution","category":"Risk","recommended_for":["var","cvar","expected_shortfall"],"reason":"Shows tail-loss thresholds and expected tail loss."},
    {"id":"volatility_cone","name":"Volatility Cone","category":"Risk","recommended_for":["volatility"],"reason":"Compares volatility across horizons and historical percentiles."},
    {"id":"risk_contribution","name":"Risk Contribution","category":"Risk","recommended_for":["portfolio_risk"],"reason":"Shows marginal and component contributions to portfolio risk."},
    {"id":"acf","name":"ACF","category":"Time Series","recommended_for":["autocorrelation"],"reason":"Shows autocorrelation by lag."},
    {"id":"pacf","name":"PACF","category":"Time Series","recommended_for":["partial_autocorrelation"],"reason":"Shows partial autocorrelation by lag."},
    {"id":"stationarity","name":"Stationarity Plot","category":"Time Series","recommended_for":["stationarity","unit_root"],"reason":"Combines the series with rolling statistics for stationarity analysis."},
    {"id":"residual","name":"Residual Plot","category":"Model Diagnostics","recommended_for":["regression","forecasting"],"reason":"Examines prediction errors and model assumptions."},
    {"id":"residual_qq","name":"Residual Q-Q Plot","category":"Model Diagnostics","recommended_for":["regression","forecasting"],"reason":"Checks residual distribution against a theoretical distribution."},
    {"id":"actual_predicted","name":"Actual vs Predicted","category":"Model Evaluation","recommended_for":["regression","forecasting"],"reason":"Compares model predictions with observed values."},
    {"id":"forecast_interval","name":"Forecast + Prediction Interval","category":"Forecasting","recommended_for":["arima","lstm","forecasting"],"reason":"Shows forecasts together with uncertainty intervals."},
    {"id":"forecast_error","name":"Forecast Error Distribution","category":"Forecasting","recommended_for":["forecasting"],"reason":"Shows the distribution of forecast errors."},
    {"id":"roc","name":"ROC Curve","category":"Classification","recommended_for":["classification"],"reason":"Shows classification discrimination across thresholds."},
    {"id":"precision_recall","name":"Precision-Recall Curve","category":"Classification","recommended_for":["classification","imbalanced_data"],"reason":"Shows the precision/recall tradeoff."},
    {"id":"confusion_matrix","name":"Confusion Matrix","category":"Classification","recommended_for":["classification"],"reason":"Shows actual versus predicted classes."},
    {"id":"learning_curve","name":"Learning Curve","category":"Model Diagnostics","recommended_for":["ml_training"],"reason":"Shows training and validation performance as data increases."},
    {"id":"loss_curve","name":"Training / Validation Loss","category":"Deep Learning","recommended_for":["ann","lstm"],"reason":"Shows optimization and generalization behavior."},
    {"id":"feature_importance","name":"Feature Importance","category":"Explainability","recommended_for":["random_forest","xgboost","decision_tree"],"reason":"Ranks features by model importance."},
    {"id":"shap","name":"SHAP Importance","category":"Explainability","recommended_for":["ml","xgboost","ann"],"reason":"Shows feature contribution and direction."},
    {"id":"pca_projection","name":"PCA Projection","category":"Dimensionality Reduction","recommended_for":["pca"],"reason":"Shows observations in principal-component space."},
    {"id":"pca_scree","name":"PCA Scree Plot","category":"Dimensionality Reduction","recommended_for":["pca"],"reason":"Shows variance explained by each component."},
    {"id":"cluster","name":"Cluster Plot","category":"Clustering","recommended_for":["kmeans"],"reason":"Shows observations grouped by cluster."},
    {"id":"elbow","name":"Elbow Curve","category":"Clustering","recommended_for":["kmeans"],"reason":"Helps inspect within-cluster sum of squares across k."},
    {"id":"silhouette","name":"Silhouette Plot","category":"Clustering","recommended_for":["kmeans"],"reason":"Shows cluster cohesion and separation."},
    {"id":"isolation_anomaly","name":"Isolation Forest Anomaly Plot","category":"Anomaly Detection","recommended_for":["isolation_forest"],"reason":"Highlights observations with high anomaly scores."},
    {"id":"anomaly_time_series","name":"Anomaly Score Time Series","category":"Anomaly Detection","recommended_for":["isolation_forest"],"reason":"Shows anomaly scores through time."},
    {"id":"filing_timeline","name":"SEC Filing Timeline","category":"SEC / Provenance","recommended_for":["sec_filings"],"reason":"Shows filing events and reporting periods."},
    {"id":"source_comparison","name":"Source Comparison","category":"SEC / Provenance","recommended_for":["validation"],"reason":"Compares values from independent sources."},
    {"id":"source_difference","name":"Source Difference","category":"SEC / Provenance","recommended_for":["validation"],"reason":"Shows absolute or percentage differences between sources."},
    {"id":"data_quality","name":"Data Quality Scorecard","category":"SEC / Provenance","recommended_for":["validation"],"reason":"Summarizes completeness, agreement, timeliness, and provenance."},
]

VISUALIZATION_IDS = [v["id"] for v in VISUALIZATIONS]
RECOMMENDED_DEFAULT = {
    "return":"line", "growth":"line", "ratio":"line", "volatility":"line",
    "drawdown":"drawdown", "correlation":"heatmap", "covariance":"heatmap",
    "probability":"histogram", "time_series":"line", "regression":"actual_predicted",
    "classification":"confusion_matrix", "forecasting":"forecast_interval",
    "pca":"pca_scree", "clustering":"cluster", "anomaly":"isolation_anomaly",
    "sec":"filing_timeline", "validation":"source_comparison"
}

def get_visualizations(metric=None):
    """Return the complete visualization library; never restrict by recommendation."""
    return VISUALIZATIONS

def get_recommended_visualizations(metric):
    """Return recommendations for a metric while preserving universal availability."""
    category = str(metric.get("category", "")).lower()
    name = str(metric.get("name", "")).lower()
    matches = []
    for item in VISUALIZATIONS:
        haystack = " ".join(item.get("recommended_for", []))
        if category in haystack or any(token in name for token in item.get("recommended_for", [])):
            matches.append(item)
    return matches[:8] if matches else VISUALIZATIONS[:5]

def visualization_options(metric):
    """Return UI options with recommendation flags and explanatory text."""
    recommended = {x["id"] for x in get_recommended_visualizations(metric)}
    return [
        {**v, "recommended": v["id"] in recommended}
        for v in VISUALIZATIONS
    ]
