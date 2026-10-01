"""Model registry for GlobalBLOCS ML/deep-learning workflows.

The registry is framework-neutral: it describes model families and validation
requirements without training models during API startup.
"""
MODEL_REGISTRY = {
    "regression": ["Linear Regression", "Ridge", "LASSO", "Random Forest", "SVR", "XGBoost"],
    "classification": ["Logistic Regression", "Decision Tree", "Random Forest", "SVM", "KNN", "Naive Bayes", "XGBoost"],
    "clustering": ["K-Means", "Hierarchical Clustering", "DBSCAN"],
    "dimensionality_reduction": ["PCA"],
    "anomaly_detection": ["Isolation Forest"],
    "time_series": ["ARIMA", "LSTM", "GRU", "Transformer"],
    "deep_learning": ["MLP", "CNN", "RNN", "LSTM", "GRU", "Autoencoder", "VAE", "Transformer"],
    "reinforcement_learning": ["Q-Learning", "Policy Gradient"],
}

VALIDATION_POLICY = {
    "time_series": ["chronological split", "walk-forward validation", "no future leakage"],
    "tabular": ["train/validation/test split", "cross-validation"],
    "feature_transforms": ["fit transformations on training data only"],
}

def list_models() -> dict[str, list[str]]:
    return MODEL_REGISTRY

def model_requirements(family: str) -> dict[str, object]:
    return {
        "family": family,
        "models": MODEL_REGISTRY.get(family, []),
        "validation": VALIDATION_POLICY["time_series" if family == "time_series" else "tabular"],
    }
