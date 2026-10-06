"""Append-only SQLite event journal with atomic portfolio review and hash checking.

Integrity checking detects accidental changes; a database owner can rewrite a chain.
This is a local academic audit, not an independently anchored production ledger.
"""
import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from .config import ROOT
from .resource_allocation import DEFAULT_BUDGET

REVIEWERS = ["SIM-Coordinator-01", "SIM-Coordinator-02"]
AUTHORITIES = ["SIM-Authority-01", "SIM-Authority-02"]

def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value

def canonical(value):
    return json.dumps(clean_json(value), sort_keys=True, separators=(",", ":"), allow_nan=False)

class AuditStore:
    def __init__(self, path=None):
        self.path = Path(path or os.environ.get("AUDIT_DB", str(ROOT/"logs/audit.sqlite")))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL, decision_id TEXT NOT NULL,
                    kind TEXT NOT NULL CHECK(kind IN ('recommendation','review')),
                    payload TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL);
                CREATE UNIQUE INDEX IF NOT EXISTS recommendation_once ON events(decision_id) WHERE kind='recommendation';
                CREATE UNIQUE INDEX IF NOT EXISTS review_once ON events(decision_id) WHERE kind='review';
                CREATE TRIGGER IF NOT EXISTS no_updates BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'Audit events are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS no_deletes BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'Audit events are append-only'); END;
            """)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=20)
        db.row_factory = sqlite3.Row
        return db

    def _append(self, db, decision_id, kind, payload):
        last = db.execute("SELECT event_hash FROM events ORDER BY sequence DESC LIMIT 1").fetchone()
        previous = last[0] if last else "GENESIS"
        event_id = str(uuid.uuid4())
        encoded = canonical(payload)
        digest = hashlib.sha256((previous+event_id+decision_id+kind+encoded).encode()).hexdigest()
        db.execute("INSERT INTO events(event_id,decision_id,kind,payload,previous_hash,event_hash) VALUES(?,?,?,?,?,?)",
                   (event_id, decision_id, kind, encoded, previous, digest))

    def log_recommendations(self, allocations, inputs, bundle, explanations, scenario, budget, threshold):
        metadata = bundle["metadata"]
        context = {"inputs": inputs.to_dict("records"), "model_version": metadata["model_version"],
                   "scenario": scenario, "budget": budget, "threshold": threshold}
        portfolio_id = hashlib.sha256(canonical(context).encode()).hexdigest()[:24]
        identifiers = []
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for _, row in allocations.iterrows():
                decision_id = f"{portfolio_id}-{row.area_id}"
                identifiers.append(decision_id)
                if db.execute("SELECT 1 FROM events WHERE decision_id=? AND kind='recommendation'", (decision_id,)).fetchone():
                    continue
                snapshot = inputs.loc[inputs.area_id.eq(row.area_id)].iloc[0].to_dict()
                explanation = explanations[row.area_id]
                payload = {"decision_id": decision_id, "portfolio_id": portfolio_id,
                    "incident_id": str(row.incident_id), "area_id": str(row.area_id),
                    "timestamp": datetime.now(timezone.utc).isoformat(), "model_name": metadata["model_name"],
                    "model_version": metadata["model_version"], "dataset_version": metadata["dataset_version"],
                    "dataset_sha256": metadata["dataset_sha256"],
                    "input_record_identifier": str(row.input_record_identifier), "input_snapshot": snapshot,
                    "input_sha256": hashlib.sha256(canonical(snapshot).encode()).hexdigest(),
                    "prediction": str(row.prediction), "priority_score": float(row.priority_score),
                    "score_band": str(row.score_band), "confidence": float(row.confidence),
                    "top_explanation_features": explanation["features"].head(6).to_dict("records"),
                    "explanation_method": explanation["method"], "explanation_units": explanation["units"],
                    "ai_recommendation": {r: int(row[r]) for r in DEFAULT_BUDGET},
                    "scenario": scenario, "budget": budget, "confidence_threshold": threshold,
                    "mandatory_review": bool(row.mandatory_review), "human_reviewer": None,
                    "human_decision": "Pending", "human_override": False, "override_reason": None,
                    "final_decision": None, "responsible_authority": None}
                self._append(db, decision_id, "recommendation", payload)
        return identifiers

    def records(self):
        with self.connect() as db:
            events = db.execute("SELECT * FROM events ORDER BY sequence").fetchall()
        records = {}
        for event in events:
            payload = json.loads(event["payload"])
            if event["kind"] == "recommendation":
                records[event["decision_id"]] = payload
            elif event["decision_id"] in records:
                records[event["decision_id"]].update(payload)
        return list(records.values())

    def review_portfolio(self, decision_ids, final_allocations, reviewer, authority, reason=""):
        if reviewer not in REVIEWERS or authority not in AUTHORITIES:
            raise ValueError("Use the provided synthetic reviewer and authority aliases.")
        if not decision_ids or len(decision_ids) != len(set(decision_ids)):
            raise ValueError("Unique decision IDs required.")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = []
            for decision_id in decision_ids:
                event = db.execute("SELECT payload FROM events WHERE decision_id=? AND kind='recommendation'", (decision_id,)).fetchone()
                if not event:
                    raise ValueError("Recommendation not found.")
                if db.execute("SELECT 1 FROM events WHERE decision_id=? AND kind='review'", (decision_id,)).fetchone():
                    raise ValueError("This portfolio is already finalized; choose a new simulation context.")
                rows.append(json.loads(event[0]))
            portfolio = rows[0]["portfolio_id"]
            all_ids = {r[0] for r in db.execute("SELECT decision_id FROM events WHERE kind='recommendation' AND json_extract(payload,'$.portfolio_id')=?", (portfolio,))}
            if len({r["portfolio_id"] for r in rows}) != 1 or set(decision_ids) != all_ids:
                raise ValueError("Review the complete portfolio atomically.")
            areas = {r["area_id"] for r in rows}
            if set(final_allocations) != areas:
                raise ValueError("Final plan must include each area exactly once.")
            for allocation in final_allocations.values():
                if set(allocation) != set(DEFAULT_BUDGET):
                    raise ValueError("Specify all supported resources.")
                if any(isinstance(v, bool) or not isinstance(v, (int, np.integer)) or v < 0 for v in allocation.values()):
                    raise ValueError("Final resources must be nonnegative integers.")
            budget = rows[0]["budget"]
            if any(sum(a[r] for a in final_allocations.values()) > budget[r] for r in budget):
                raise ValueError("Final allocation exceeds the available budget.")
            overridden = any(final_allocations[r["area_id"]] != r["ai_recommendation"] for r in rows)
            if overridden and len(reason.strip()) < 8:
                raise ValueError("An override requires a meaningful reason of at least eight characters.")
            timestamp = datetime.now(timezone.utc).isoformat()
            for row in rows:
                final = final_allocations[row["area_id"]]
                override = final != row["ai_recommendation"]
                self._append(db, row["decision_id"], "review", {
                    "human_reviewer": reviewer, "human_decision": "Override" if override else "Accept",
                    "human_override": override, "override_reason": reason.strip() if override else None,
                    "review_timestamp": timestamp, "final_decision": final, "responsible_authority": authority})

    def verify_integrity(self):
        previous = "GENESIS"
        with self.connect() as db:
            rows = db.execute("SELECT * FROM events ORDER BY sequence").fetchall()
        for row in rows:
            digest = hashlib.sha256((previous+row["event_id"]+row["decision_id"]+row["kind"]+row["payload"]).encode()).hexdigest()
            if row["previous_hash"] != previous or row["event_hash"] != digest:
                return False
            previous = digest
        return True

def readiness_score(evidence):
    """Equal-weight binary local checklist, explicitly project-defined and nonstandard."""
    dimensions = ["Explainability", "Human Oversight", "Auditability", "Data Quality", "Model Reliability", "Documentation", "Monitoring"]
    if set(evidence) != set(dimensions):
        raise ValueError("Evidence must cover all readiness dimensions.")
    values = {k: int(bool(evidence[k]))*100 for k in dimensions}
    return {"label": "Project-Defined Accountability Readiness Score", "score": sum(values.values())/len(values), "dimensions": values}
