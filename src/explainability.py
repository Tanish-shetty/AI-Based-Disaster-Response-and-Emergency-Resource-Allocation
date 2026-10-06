import numpy as np
import pandas as pd
from .preprocessing import validate_features

def explain_record(record, bundle) -> dict:
    """Signed local SHAP values for the predicted class, in explicitly stated units."""
    import shap
    from sklearn.ensemble import RandomForestClassifier
    pipeline = bundle["pipeline"]
    x = validate_features(record.iloc[:1])
    pre = pipeline.named_steps["preprocess"]
    estimator = pipeline.named_steps["model"]
    transformed = pre.transform(x)
    predicted = pipeline.predict(x)[0]
    class_index = list(estimator.classes_).index(predicted)
    try:
        if isinstance(estimator, RandomForestClassifier):
            explainer = shap.TreeExplainer(estimator)
            explanation = explainer(transformed)
            values = np.asarray(explanation.values)[0, :, class_index]
            base = float(np.asarray(explanation.base_values)[0, class_index])
            units = "predicted-class probability"
            target = float(pipeline.predict_proba(x)[0, class_index])
        else:
            explainer = shap.LinearExplainer(estimator, pre.transform(bundle["background"]))
            explanation = explainer(transformed)
            values = np.asarray(explanation.values)[0, :, class_index]
            base = float(np.asarray(explanation.base_values)[0, class_index])
            units = "predicted-class logit (before softmax)"
            target = float(estimator.decision_function(transformed)[0, class_index])
        table = pd.DataFrame({"feature": pre.get_feature_names_out(), "contribution": values})
        table = table.iloc[np.argsort(-np.abs(values))].reset_index(drop=True)
        return {"method": "SHAP", "prediction": str(predicted), "units": units,
                "base_value": base, "explained_output": target, "reconstructed_output": base+float(values.sum()),
                "features": table, "warning": "Attribution explains model behavior; it does not establish causality or correctness."}
    except (ImportError, ValueError, TypeError, AttributeError) as error:
        # Honest global fallback: never relabel unsigned global values as signed local explanations.
        importance = getattr(estimator, "feature_importances_", None)
        if importance is None:
            importance = np.abs(estimator.coef_[class_index])
        table = pd.DataFrame({"feature": pre.get_feature_names_out(), "contribution": importance}).sort_values("contribution", ascending=False)
        return {"method": "Global model importance fallback", "prediction": str(predicted),
                "units": "unsigned global importance", "features": table,
                "warning": f"SHAP unavailable: {type(error).__name__}: {error}. Global importance is not a local signed explanation."}
