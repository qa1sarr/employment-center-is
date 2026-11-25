"""Модельдерді үйрету логикасы (Streamlit интерфейсі осыны шақырады)."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, mean_absolute_error,
                             mean_squared_error, precision_score, r2_score, recall_score)
from sklearn.model_selection import train_test_split


def train_regression(data: pd.DataFrame, test_size=0.2, random_state=42) -> dict:
    X = data[["experience_years", "skills_count"]].values
    y = data["salary"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    model = LinearRegression().fit(X_train, y_train)          # y = w1*өтіл + w2*дағдылар + b
    y_pred = model.predict(X_test)
    return {
        "model": model, "X": X, "y": y,
        "X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test, "y_pred": y_pred,
        "w_exp": float(model.coef_[0]), "w_skills": float(model.coef_[1]), "bias": float(model.intercept_),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "mse": float(mean_squared_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)) if len(y_test) > 1 else float("nan"),
    }


def train_classification(data: pd.DataFrame, test_size=0.2, random_state=42) -> dict:
    X = data[["experience_years", "match_score"]].values
    y = data["hired"].values
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y)
    model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return {
        "model": model, "X": X, "y": y,
        "X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test, "y_pred": y_pred,
        "w_exp": float(model.coef_[0][0]), "w_score": float(model.coef_[0][1]), "bias": float(model.intercept_[0]),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "confusion": confusion_matrix(y_test, y_pred, labels=[0, 1]),
    }
