import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, classification_report
from .config import LABELS

def evaluate(model, x, y) -> dict:
    predicted = model.predict(x)
    probabilities = model.predict_proba(x)
    metrics = {"accuracy": float(accuracy_score(y, predicted)),
        "precision_macro": float(precision_score(y, predicted, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y, predicted, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y, predicted, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(y, predicted, labels=LABELS).tolist(),
        "classification_report": classification_report(y, predicted, labels=LABELS, output_dict=True, zero_division=0)}
    try:
        metrics["roc_auc_ovr_macro"] = float(roc_auc_score(y, probabilities, labels=model.classes_, multi_class="ovr", average="macro"))
    except ValueError:
        metrics["roc_auc_ovr_macro"] = None
    metrics["multiclass_brier"] = float(np.mean(np.sum((probabilities - (np.asarray(y)[:,None] == model.classes_[None,:]))**2, axis=1)))
    return metrics

def disparity_table(data, predictions) -> pd.DataFrame:
    """Descriptive synthetic area groups; small denominators explicit, no demographic claims."""
    rows = []
    for category, subset in data.groupby("area_category"):
        pred = predictions.loc[subset.index]
        truth_high = subset.priority_label.isin(["High", "Critical"])
        predicted_high = pred.prediction.isin(["High", "Critical"])
        count = int(truth_high.sum())
        rows.append({"area_category": category, "n": len(subset), "high_severity_n": count,
                     "miss_rate_high": float((truth_high & ~predicted_high).sum()/count) if count else None,
                     "mean_score": float(pred.priority_score.mean()),
                     "mean_rescue_teams": float(pred.rescue_teams.mean()) if "rescue_teams" in pred else None,
                     "interpretation": "Descriptive only; small group" if count < 30 else "Synthetic group diagnostic"})
    return pd.DataFrame(rows)
