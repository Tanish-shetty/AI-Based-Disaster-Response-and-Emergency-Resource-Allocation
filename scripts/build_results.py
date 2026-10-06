import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
from src.config import ROOT, LABELS
from src.prediction import load_bundle, predict_areas
from src.ethical_simulation import SCENARIOS, run_scenario
from src.evaluation import disparity_table
from src.explainability import explain_record
from src.resource_allocation import allocate_resources

def build_results():
    bundle, under = load_bundle(), load_bundle(True)
    data = pd.read_csv(ROOT/"data/raw/demo_incident.csv")
    rows = []
    plt.rcParams.update({"figure.dpi":150,"axes.spines.top":False,"axes.spines.right":False})
    for scenario in SCENARIOS:
        run = run_scenario(data, scenario, bundle, under_bundle=under)
        name = scenario.lower().replace(" ", "_")
        run["comparison"].to_csv(ROOT/f"reports/{name}_comparison.csv", index=False)
        run["predictions"].to_csv(ROOT/f"reports/{name}_allocation.csv", index=False)
        rows.append(run["indicators"])
        fig, ax = plt.subplots(figsize=(11,5))
        comparison = run["comparison"]
        positions = np.arange(len(comparison))
        ax.bar(positions-.18, comparison.priority_score_baseline, .36, label="Baseline", color="#167d9a")
        ax.bar(positions+.18, comparison.priority_score, .36, label="Scenario", color="#df9851")
        ax.set_xticks(positions, comparison.area_name, rotation=35, ha="right")
        ax.set_ylim(0,100); ax.set_ylabel("Priority score"); ax.set_title(scenario); ax.legend()
        fig.tight_layout(); fig.savefig(ROOT/f"reports/figures/{name}.png"); plt.close(fig)
        px.bar(comparison, x="area_name", y="priority_score_change", title=scenario+" — score change").write_html(ROOT/f"reports/figures/{name}.html", include_plotlyjs=True)
    summary = pd.DataFrame(rows)
    summary.to_csv(ROOT/"reports/scenario_summary.csv", index=False)
    raw = pd.read_csv(ROOT/"data/raw/synthetic_flood.csv")
    test = raw.loc[bundle["test_indices"]]
    predictions = pd.concat([allocate_resources(predict_areas(incident, bundle)) for _,incident in test.groupby("incident_id")])
    groups = disparity_table(test, predictions)
    groups.to_csv(ROOT/"reports/test_group_diagnostics.csv", index=False)
    meta = bundle["metadata"]
    metric_rows = [{"Model":name, "Validation macro F1":meta["validation"][name]["f1_macro"],
                   "Test accuracy":m["accuracy"],"Test precision (macro)":m["precision_macro"],
                   "Test recall (macro)":m["recall_macro"],"Test macro F1":m["f1_macro"],
                   "Test ROC-AUC (OvR macro)":m["roc_auc_ovr_macro"]} for name,m in meta["test"].items()]
    pd.DataFrame(metric_rows).to_csv(ROOT/"reports/model_comparison.csv",index=False)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar([r["Model"] for r in metric_rows], [r["Test macro F1"] for r in metric_rows], color=["#167d9a","#df9851"])
    ax.set_ylim(0,1); ax.set_ylabel("Test macro F1"); fig.tight_layout()
    fig.savefig(ROOT/"reports/figures/model_comparison.png"); plt.close(fig)
    matrix = np.array(meta["test"][meta["model_name"]]["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(6,5)); ax.imshow(matrix, cmap="Blues")
    for (i,j),v in np.ndenumerate(matrix):
        ax.text(j,i,str(v),ha="center",va="center",color="white" if v > matrix.max()/2 else "black")
    ax.set_xticks(range(4),LABELS); ax.set_yticks(range(4),LABELS); ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    fig.tight_layout(); fig.savefig(ROOT/"reports/figures/confusion_matrix.png"); plt.close(fig)
    riverside = data.loc[data.area_name.eq("Riverside")]
    explanation = explain_record(riverside, bundle)
    explanation["features"].to_csv(ROOT/"reports/riverside_shap.csv",index=False)
    (ROOT/"reports/explanation_verification.json").write_text(json.dumps({k:v for k,v in explanation.items() if k != "features"}, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(8,5)); e = explanation["features"].head(10).sort_values("contribution")
    ax.barh(e.feature,e.contribution,color=["#167d9a" if v>0 else "#df9851" for v in e.contribution]); ax.set_xlabel(explanation["units"])
    fig.tight_layout(); fig.savefig(ROOT/"reports/figures/riverside_shap.png"); plt.close(fig)
    print(summary.to_string(index=False))
    print(groups.to_string(index=False))
    return summary

if __name__ == "__main__":
    build_results()
