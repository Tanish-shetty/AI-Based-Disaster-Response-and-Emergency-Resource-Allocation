import re
from src.config import ROOT

def test_submission_complete():
    report = (ROOT/"reports/PROJECT_REPORT.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^## \d+\.",report,re.M)) == 21
    viva = (ROOT/"docs/VIVA_QUESTIONS.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^## \d+\.",viva,re.M)) >= 50
    slides = (ROOT/"presentation/PRESENTATION_OUTLINE.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^## Slide \d+:",slides,re.M)) == 15
    demo = (ROOT/"presentation/DEMO_SCRIPT.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^## \d+\.",demo,re.M)) == 15
    assert "legal liability" in report and "synthetic" in report.lower()
    for path in ["README.md","docs/ETHICAL_ANALYSIS.md","docs/DATA_CARD.md","docs/MODEL_CARD.md","reports/scenario_summary.csv"]:
        assert (ROOT/path).is_file()
