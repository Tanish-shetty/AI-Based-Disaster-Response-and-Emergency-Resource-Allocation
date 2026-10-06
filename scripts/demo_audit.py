"""Save a separate simulated override example without finalizing the live dashboard."""
import json
import pandas as pd
from src.config import ROOT
from src.prediction import load_bundle
from src.ethical_simulation import run_scenario,SCENARIOS
from src.explainability import explain_record
from src.resource_allocation import DEFAULT_BUDGET
from src.accountability import AuditStore, clean_json

def build_demo_audit():
    data = pd.read_csv(ROOT/"data/raw/demo_incident.csv")
    bundle = load_bundle()
    run = run_scenario(data,SCENARIOS[1],bundle)
    explanations = {row.area_id:explain_record(run["inputs"].loc[[index]],bundle) for index,row in run["inputs"].iterrows()}
    store = AuditStore(ROOT/"logs/demo_audit.sqlite")
    ids = store.log_recommendations(run["predictions"],run["inputs"],bundle,explanations,SCENARIOS[1],DEFAULT_BUDGET,.7)
    records = [r for r in store.records() if r["decision_id"] in ids]
    if all(r["final_decision"] is None for r in records):
        final = {r["area_id"]:r["ai_recommendation"].copy() for r in records}
        final["AREA-12"]["rescue_teams"] -= 1
        final["AREA-10"]["rescue_teams"] += 1
        store.review_portfolio(ids,final,"SIM-Coordinator-01","SIM-Authority-01",
                               "Simulated field report confirms Lake Colony needs rescue support.")
    assert store.verify_integrity()
    records = [r for r in store.records() if r["decision_id"] in ids]
    (ROOT/"reports/demo_audit.json").write_text(json.dumps(clean_json(records),indent=2),encoding="utf-8")
    print(f"Saved {len(records)} reviewed area records; {sum(r['human_override'] for r in records)} justified overrides; hash chain valid.")

if __name__ == "__main__":
    build_demo_audit()
