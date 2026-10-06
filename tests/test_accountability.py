import sqlite3
import pytest
from src.accountability import AuditStore,readiness_score
from src.ethical_simulation import run_scenario, SCENARIOS
from src.explainability import explain_record
from src.resource_allocation import DEFAULT_BUDGET

@pytest.fixture
def journal(tmp_path,data,bundle):
    store = AuditStore(tmp_path/"test.sqlite")
    run = run_scenario(data,SCENARIOS[0],bundle)
    explanations = {row.area_id:explain_record(data.loc[[index]],bundle) for index,row in data.iterrows()}
    ids = store.log_recommendations(run["predictions"],data,bundle,explanations,SCENARIOS[0],DEFAULT_BUDGET,.7)
    return store,ids,run,explanations

def plan(store):
    return {r["area_id"]:r["ai_recommendation"].copy() for r in store.records()}

def test_pending_and_idempotent(journal,data,bundle):
    store,ids,run,explanations = journal
    assert len(store.records()) == 12 and all(r["final_decision"] is None for r in store.records())
    repeated = store.log_recommendations(run["predictions"],data,bundle,explanations,SCENARIOS[0],DEFAULT_BUDGET,.7)
    assert ids == repeated and len(store.records()) == 12
    assert store.verify_integrity()
    assert all(r["input_snapshot"] and r["top_explanation_features"] for r in store.records())

def test_accept_and_immutable_history(journal):
    store,ids,_,_ = journal
    store.review_portfolio(ids,plan(store),"SIM-Coordinator-01","SIM-Authority-01")
    assert all(r["human_decision"] == "Accept" for r in store.records())
    assert all(r["responsible_authority"] == "SIM-Authority-01" for r in store.records())
    assert store.verify_integrity()
    with sqlite3.connect(store.path) as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE events SET payload='{}'")
    with pytest.raises(ValueError):
        store.review_portfolio(ids,plan(store),"SIM-Coordinator-01","SIM-Authority-01")

def test_override_requires_reason_and_respects_budget(journal):
    store,ids,_,_ = journal
    final = plan(store)
    donor = next(k for k,v in final.items() if v["rescue_teams"] > 0)
    recipient = next(k for k in final if k != donor)
    final[donor]["rescue_teams"] -= 1; final[recipient]["rescue_teams"] += 1
    with pytest.raises(ValueError):
        store.review_portfolio(ids,final,"SIM-Coordinator-01","SIM-Authority-01","")
    assert all(r["final_decision"] is None for r in store.records())
    store.review_portfolio(ids,final,"SIM-Coordinator-01","SIM-Authority-01","New simulated field evidence changes urgency.")
    overridden = [r for r in store.records() if r["human_override"]]
    assert len(overridden) == 2 and all(r["override_reason"] for r in overridden)
    assert store.verify_integrity()

def test_invalid_portfolios_roll_back(journal):
    store,ids,_,_ = journal
    final = plan(store); first = next(iter(final)); final[first]["rescue_teams"] += 1
    with pytest.raises(ValueError):
        store.review_portfolio(ids,final,"SIM-Coordinator-01","SIM-Authority-01","Evidence")
    with pytest.raises(ValueError):
        store.review_portfolio(ids[:-1],plan(store),"SIM-Coordinator-01","SIM-Authority-01")
    assert all(r["final_decision"] is None for r in store.records())

def test_readiness_definition():
    keys = ["Explainability","Human Oversight","Auditability","Data Quality","Model Reliability","Documentation","Monitoring"]
    result = readiness_score(dict.fromkeys(keys,True))
    assert result["score"] == 100 and result["label"].startswith("Project-Defined")

def test_hash_check_detects_admin_alteration(journal):
    store,_,_,_ = journal
    with sqlite3.connect(store.path) as db:
        db.execute("DROP TRIGGER no_updates")
        db.execute("UPDATE events SET payload='{}' WHERE sequence=1")
    assert not store.verify_integrity()
