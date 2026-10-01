"""Evaluation metrics selected by visualization/model family."""
EVALUATION_BY_VISUALIZATION={
 "actual_predicted":["MAE","MSE","RMSE","MAPE","R²","Adjusted R²","Directional Accuracy"],
 "forecast_interval":["MAE","RMSE","MAPE","Pinball Loss","Quantile Coverage","Prediction Interval Width"],
 "roc":["Accuracy","Precision","Recall","F1","ROC-AUC"],
 "precision_recall":["Precision","Recall","F1","PR-AUC","Average Precision"],
 "confusion_matrix":["Accuracy","Balanced Accuracy","Precision","Recall","F1","MCC","Cohen Kappa"],
 "cluster":["Silhouette","Davies-Bouldin","Calinski-Harabasz"],
 "pca_projection":["Explained Variance","Cumulative Explained Variance"],
 "feature_importance":["Feature Importance","Permutation Importance"],
 "shap":["Mean Absolute SHAP","SHAP Interaction"],
 "residual":["MAE","RMSE","Residual Mean","Residual Variance","Normality Test"],
 "line":["Mean","Median","Standard Deviation","Trend Slope"],
 "histogram":["Mean","Median","Skewness","Kurtosis","Normality Test"],
 "box":["Median","IQR","Outlier Count"],
 "scatter":["Correlation","R²","Regression Slope"],
 "heatmap":["Correlation","Covariance"],
}
def evaluations_for_visualization(chart_type):
    return EVALUATION_BY_VISUALIZATION.get(chart_type,["Descriptive statistics","Data quality"])
