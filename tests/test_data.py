import numpy as np
import pandas as pd
import pytest
from src.data_generation import generate_dataset
from src.preprocessing import validate_features
from src.config import ROOT, FEATURES

def test_reproducibility_and_physical_ranges():
    a,b = generate_dataset(), generate_dataset()
    pd.testing.assert_frame_equal(a,b)
    assert len(a) == 3000 and a.input_record_identifier.is_unique
    validate_features(a)
    assert a.true_severity.between(0,100).all()
    assert a.vulnerable_population.isna().any()
    assert not {"true_severity", "priority_label", "response_time_minutes", "incident_id"}.intersection(FEATURES)

def test_incident_disjoint_splits():
    manifest = pd.read_csv(ROOT/"data/processed/split_manifest.csv")
    assert manifest.groupby("incident_id").split.nunique().eq(1).all()
    assert manifest.input_record_identifier.is_unique
    assert set(manifest.split) == {"train", "test", "validation"}

@pytest.mark.parametrize("feature,value", [("flood_level",-1),("road_accessibility",2),("population",np.inf),("flood_level","oops"),("area_category","Unknown")])
def test_invalid_features(data, feature, value):
    damaged = data.copy()
    damaged[feature] = value
    with pytest.raises((ValueError,TypeError)):
        validate_features(damaged)

def test_missing_schema(data):
    with pytest.raises(ValueError):
        validate_features(data.drop(columns="flood_level"))
