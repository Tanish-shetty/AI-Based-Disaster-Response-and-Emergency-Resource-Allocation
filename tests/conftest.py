import pandas as pd
import pytest
from src.config import ROOT
from src.prediction import load_bundle

@pytest.fixture(scope="session")
def bundle():
    return load_bundle()

@pytest.fixture(scope="session")
def data():
    return pd.read_csv(ROOT/"data/raw/demo_incident.csv")
