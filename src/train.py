import hashlib
import json
import platform
import joblib
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupShuffleSplit
from .config import ROOT, SEED, FEATURES, DATASET_VERSION
from .data_generation import generate_dataset, demo_incident
from .preprocessing import make_preprocessor, validate_features
from .evaluation import evaluate

def train_project() -> dict:
    for folder in ["data/raw", "data/processed", "models", "reports/figures", "logs"]:
        (ROOT/folder).mkdir(parents=True, exist_ok=True)
    data = generate_dataset()
    raw_path = ROOT/"data/raw/synthetic_flood.csv"
    data.to_csv(raw_path, index=False)
    demo_incident().to_csv(ROOT/"data/raw/demo_incident.csv", index=False)
    x = validate_features(data)
    y = data.priority_label
    tv, test = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=SEED).split(x, y, data.incident_id))
    train_rel, val_rel = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=SEED+1).split(x.iloc[tv], y.iloc[tv], data.iloc[tv].incident_id))
    train, val = tv[train_rel], tv[val_rel]
    splits = {"train": train, "validation": val, "test": test}
    manifest = data[["input_record_identifier", "incident_id"]].copy()
    for name, indices in splits.items():
        manifest.loc[indices, "split"] = name
    manifest.to_csv(ROOT/"data/processed/split_manifest.csv", index=False)
    candidates = {"Logistic Regression": LogisticRegression(C=1, max_iter=1500, random_state=SEED),
                  "Random Forest": RandomForestClassifier(n_estimators=180, min_samples_leaf=3, max_features=.8, random_state=SEED, n_jobs=-1)}
    fitted, validation = {}, {}
    for name, estimator in candidates.items():
        model = Pipeline([("preprocess", make_preprocessor()), ("model", estimator)])
        model.fit(x.iloc[train], y.iloc[train])
        fitted[name] = model
        validation[name] = evaluate(model, x.iloc[val], y.iloc[val])
    selected = max(validation, key=lambda name: validation[name]["f1_macro"])
    # Test metrics are collected only after selection and do not tune the winner.
    test_metrics = {name: evaluate(model, x.iloc[test], y.iloc[test]) for name, model in fitted.items()}
    digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    metadata = {"dataset_version": DATASET_VERSION, "dataset_sha256": digest,
                "model_name": selected, "model_version": f"v1-{digest[:8]}",
                "seed": SEED, "records": len(data), "features": FEATURES,
                "split_counts": {k: len(v) for k, v in splits.items()},
                "class_counts": data.priority_label.value_counts().to_dict(),
                "selection_rule": "Highest validation macro F1; test never used for selection",
                "validation": validation, "test": test_metrics,
                "python_version": platform.python_version(), "sklearn_version": sklearn.__version__}
    bundle = {"pipeline": fitted[selected], "metadata": metadata,
              "background": x.iloc[train[:100]], "test_indices": test.tolist()}
    joblib.dump(bundle, ROOT/"models/priority_model.joblib")
    # Deliberately reduce peripheral TRAINING observations; not validation/test data.
    peripheral = train[data.iloc[train].area_category.to_numpy() == "Peripheral"]
    retained = np.concatenate([train[data.iloc[train].area_category.to_numpy() != "Peripheral"], peripheral[:max(1,len(peripheral)//10)]])
    from sklearn.base import clone
    under = clone(fitted[selected]).fit(x.iloc[retained], y.iloc[retained])
    joblib.dump({"pipeline": under, "metadata": {**metadata, "model_name": selected+" (underrepresented training)",
                "model_version": metadata["model_version"]+"-under", "training_records": len(retained),
                "peripheral_training_records": int(sum(data.iloc[retained].area_category == "Peripheral"))},
                "background": x.iloc[retained[:100]]}, ROOT/"models/underrepresented_model.joblib")
    (ROOT/"reports/metrics.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"selected": selected, "validation_f1": validation[selected]["f1_macro"], "test": test_metrics[selected], "splits": metadata["split_counts"]}, indent=2))
    return metadata

if __name__ == "__main__":
    train_project()
