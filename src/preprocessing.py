import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .config import NUMERIC, CATEGORICAL, FEATURES, BOUNDS

def validate_features(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty or not set(FEATURES).issubset(data.columns):
        raise ValueError("Nonempty input with every required feature is necessary.")
    result = data[FEATURES].copy()
    for feature in NUMERIC:
        result[feature] = pd.to_numeric(result[feature], errors="raise")
        values = result[feature].dropna()
        low, high = BOUNDS[feature]
        if not np.isfinite(values).all() or ((values < low) | (values > high)).any():
            raise ValueError(f"{feature} must be finite and within [{low}, {high}].")
    categories = result["area_category"].dropna()
    if not categories.isin(["Central", "Residential", "Peripheral"]).all():
        raise ValueError("Unknown area_category.")
    return result

def make_preprocessor() -> ColumnTransformer:
    return ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),
                              ("scale", StandardScaler())]), NUMERIC),
        ("category", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                               ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), CATEGORICAL)
    ], verbose_feature_names_out=False)
