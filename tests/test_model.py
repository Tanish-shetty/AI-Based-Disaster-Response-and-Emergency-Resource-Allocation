import numpy as np
import pytest
from src.prediction import predict_areas
from src.scoring import priority_scores, score_band
from src.explainability import explain_record

def test_predictions_and_imputation(data,bundle):
    a = predict_areas(data,bundle)
    b = predict_areas(data,bundle)
    np.testing.assert_allclose(a.priority_score,b.priority_score)
    assert a.priority_score.between(0,100).all() and a.confidence.between(0,1).all()
    damaged = data.copy(); damaged["vulnerable_population"] = np.nan
    output = predict_areas(damaged,bundle)
    assert output.mandatory_review.all() and np.isfinite(output.priority_score).all()

def test_probability_scoring():
    np.testing.assert_allclose(priority_scores([[.1,.2,.3,.4]],["Low","Medium","High","Critical"]),[74.1])
    assert [score_band(x) for x in [0,39.9,40,69.9,70,84.9,85,100]] == ["Low","Low","Medium","Medium","High","High","Critical","Critical"]
    with pytest.raises(ValueError):
        priority_scores([[.4,.4]],["Low","High"])
    with pytest.raises(ValueError):
        score_band(101)

def test_shap_additivity(data,bundle):
    result = explain_record(data.iloc[:1],bundle)
    assert result["method"] == "SHAP",result["warning"]
    assert len(result["features"]) >= 16
    assert result["reconstructed_output"] == pytest.approx(result["explained_output"],abs=1e-6)
    assert (result["features"].contribution != 0).any()

def test_threshold_guard(data,bundle):
    with pytest.raises(ValueError):
        predict_areas(data,bundle,1.1)
