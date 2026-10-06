import joblib
from .config import ROOT, FEATURES
from .preprocessing import validate_features
from .scoring import priority_scores, score_band

def load_bundle(underrepresented: bool = False):
    name = "underrepresented_model.joblib" if underrepresented else "priority_model.joblib"
    path = ROOT/"models"/name
    if not path.exists():
        raise FileNotFoundError("Run python -m src.train first.")
    return joblib.load(path)  # Load only project-created local artifacts, never untrusted uploads.

def predict_areas(data, bundle, threshold: float = .7):
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between zero and one.")
    x = validate_features(data)
    model = bundle["pipeline"]
    probabilities = model.predict_proba(x)
    result = data.copy()
    result["prediction"] = model.predict(x)
    result["priority_score"] = priority_scores(probabilities, model.classes_)
    result["score_band"] = result.priority_score.map(score_band)
    result["confidence"] = probabilities.max(axis=1)
    result["missing_feature_count"] = x.isna().sum(axis=1)
    result["mandatory_review"] = (result.confidence < threshold) | (result.missing_feature_count > 0) | (result.sensor_reliability < .7)
    result["review_status"] = result.mandatory_review.map({True: "MANDATORY HUMAN REVIEW", False: "Human sign-off required"})
    # Stable ordering and deterministic ties.
    result = result.sort_values(["priority_score", "area_id"], ascending=[False, True])
    result["rank"] = range(1, len(result)+1)
    return result
