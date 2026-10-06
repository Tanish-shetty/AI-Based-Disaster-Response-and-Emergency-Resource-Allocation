"""Rebuild data/models/results/docs in a fresh process, then execute the test suite."""
import contextlib
import hashlib
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from src.config import ROOT
from src.train import train_project
from scripts.build_results import build_results
from scripts.build_docs import build_docs
from scripts.demo_audit import build_demo_audit

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def main():
    tracked = [ROOT/"data/raw/synthetic_flood.csv", ROOT/"reports/model_comparison.csv", ROOT/"reports/scenario_summary.csv"]
    before = {str(path.relative_to(ROOT)):digest(path) for path in tracked}
    with (ROOT/"reports/fresh_run.log").open("w",encoding="utf-8") as output, contextlib.redirect_stdout(output):
        train_project()
        build_results()
        build_docs()
        build_demo_audit()
    after = {str(path.relative_to(ROOT)):digest(path) for path in tracked}
    reproducible = all(before[name] is None or before[name] == value for name,value in after.items())
    temp = ROOT/".test-tmp"/str(uuid.uuid4())
    temp.parent.mkdir(parents=True,exist_ok=True)
    test = subprocess.run([sys.executable,"-m","pytest","-q","--basetemp",str(temp)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace")
    (ROOT/"reports/test_results.txt").write_text(test.stdout+test.stderr,encoding="utf-8")
    result = {"timestamp_utc":datetime.now(timezone.utc).isoformat(),
              "fresh_training_and_results":True,"deterministic_artifact_hashes_match":reproducible,
              "artifact_sha256":after,"test_exit_code":test.returncode,"test_output":test.stdout.strip(),
              "note":"Dashboard browser render check is separately saved in browser_verification.json; AppTest checks pages and forms."}
    (ROOT/"reports/verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
    if test.returncode or not reproducible:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
