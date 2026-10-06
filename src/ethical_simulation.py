import numpy as np
import pandas as pd
from .config import SEED
from .prediction import predict_areas
from .resource_allocation import allocate_resources, DEFAULT_BUDGET

SCENARIOS = ["Complete Data", "Missing Vulnerable Population Data", "Delayed Emergency Call Data",
             "Noisy Sensor Data", "Underrepresented Area Data"]

def modify_inputs(data, scenario: str):
    if scenario not in SCENARIOS:
        raise ValueError("Unknown scenario.")
    result = data.copy(deep=True)
    peripheral = result.area_category.eq("Peripheral")
    if scenario == SCENARIOS[1]:
        result.loc[peripheral, "vulnerable_population"] = np.nan
    elif scenario == SCENARIOS[2]:
        result.loc[peripheral, "emergency_calls"] = np.floor(result.loc[peripheral, "emergency_calls"]*.2)
        result.loc[peripheral, "medical_emergencies"] = np.floor(result.loc[peripheral, "medical_emergencies"]*.35)
    elif scenario == SCENARIOS[3]:
        rng = np.random.default_rng(SEED)
        result["flood_level"] = np.clip(result.flood_level + rng.normal(0, .9, len(result)), 0, 6)
        result["rainfall_mm"] = np.clip(result.rainfall_mm + rng.normal(0, 65, len(result)), 0, 600)
        result["sensor_reliability"] = .4
    elif scenario == SCENARIOS[4]:
        result.loc[peripheral, "vulnerable_population"] = np.nan
        result.loc[peripheral, "emergency_calls"] = np.floor(result.loc[peripheral, "emergency_calls"]*.5)
    return result

def run_scenario(data, scenario, bundle, budget=None, threshold=.7, under_bundle=None):
    baseline = allocate_resources(predict_areas(data, bundle, threshold), budget)
    modified = modify_inputs(data, scenario)
    active = under_bundle if scenario == SCENARIOS[4] and under_bundle is not None else bundle
    changed = allocate_resources(predict_areas(modified, active, threshold), budget)
    columns = ["priority_score", "rank", *DEFAULT_BUDGET]
    compare = changed[["area_id", "area_name", "area_category", "prediction", "confidence", *columns]].merge(
        baseline[["area_id", *columns]], on="area_id", suffixes=("", "_baseline"))
    for column in columns:
        compare[column+"_change"] = compare[column]-compare[column+"_baseline"]
    # Ground truth stays fixed: corrupted observations cannot rewrite the simulated need.
    truth_high = changed.priority_label.isin(["High", "Critical"])
    pred_high = changed.prediction.isin(["High", "Critical"])
    indicators = {"scenario": scenario, "mean_absolute_score_change": float(compare.priority_score_change.abs().mean()),
                  "changed_ranks": int((compare.rank_change != 0).sum()),
                  "rescue_units_reassigned": int(compare.rescue_teams_change.abs().sum()//2),
                  "missed_high_severity_areas": int((truth_high & ~pred_high).sum()),
                  "false_high_prioritizations": int((~truth_high & pred_high).sum()),
                  "high_severity_without_rescue": int((truth_high & changed.rescue_teams.eq(0)).sum()),
                  "mean_confidence": float(changed.confidence.mean()),
                  "missing_feature_cells": int(modified[bundle["metadata"]["features"]].isna().sum().sum())}
    return {"inputs": modified, "baseline": baseline, "predictions": changed, "comparison": compare,
            "indicators": indicators, "bundle": active}
