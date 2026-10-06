import pandas as pd
import pytest
from src.ethical_simulation import SCENARIOS,modify_inputs,run_scenario
from src.prediction import load_bundle

@pytest.mark.parametrize("scenario",SCENARIOS)
def test_actual_scenario(data,bundle,scenario):
    original = data.copy(deep=True)
    run = run_scenario(data,scenario,bundle,under_bundle=load_bundle(True))
    pd.testing.assert_frame_equal(data,original)
    assert run["predictions"].rescue_teams.sum() == 5
    assert run["predictions"].priority_score.between(0,100).all()
    assert run["predictions"].true_severity.sort_index().equals(data.true_severity.sort_index())
    if scenario == SCENARIOS[0]:
        assert run["comparison"].priority_score_change.eq(0).all()
    else:
        assert not run["inputs"].equals(data)
        assert run["comparison"].priority_score_change.abs().sum() > 0
    pd.testing.assert_frame_equal(modify_inputs(data,scenario),modify_inputs(data,scenario))

def test_bad_scenario(data):
    with pytest.raises(ValueError):
        modify_inputs(data,"invalid")
