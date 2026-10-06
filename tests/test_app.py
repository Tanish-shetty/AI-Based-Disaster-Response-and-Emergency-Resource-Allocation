import pytest
from streamlit.testing.v1 import AppTest
from src.config import ROOT
from src.accountability import AuditStore

PAGES = ["Overview", "Disaster Scenario", "AI Priority Analysis", "Explainable AI", "Ethical Risk Simulator",
         "Human Review", "Accountability Audit", "Stakeholder Accountability", "Results & Findings", "Recommendations"]

def test_all_pages_and_scenarios(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_DB",str(tmp_path/"ui.sqlite"))
    app = AppTest.from_file(str(ROOT/"app.py"),default_timeout=30).run()
    assert not app.exception
    for page in PAGES:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, (page,app.exception)
    app.sidebar.radio[0].set_value("Ethical Risk Simulator").run()
    for scenario in app.sidebar.selectbox[0].options:
        app.sidebar.selectbox[0].set_value(scenario).run()
        assert not app.exception, (scenario,app.exception)
    assert len(AuditStore(tmp_path/"ui.sqlite").records()) == 60

def test_review_form_enforces_confirmation_and_accepts(tmp_path,monkeypatch):
    path = tmp_path/"review.sqlite"
    monkeypatch.setenv("AUDIT_DB",str(path))
    app = AppTest.from_file(str(ROOT/"app.py"),default_timeout=30).run()
    app.sidebar.radio[0].set_value("Human Review").run()
    next(button for button in app.button if button.label == "Authorize reviewed portfolio").click().run()
    assert any("authorization" in item.value for item in app.error)
    assert all(r["final_decision"] is None for r in AuditStore(path).records())
    app.checkbox[0].check()
    next(button for button in app.button if button.label == "Authorize reviewed portfolio").click().run()
    assert not app.exception
    assert all(r["human_decision"] == "Accept" for r in AuditStore(path).records())
    assert any("finalized" in item.value for item in app.success)

def test_ui_override_is_retained(tmp_path,monkeypatch):
    path = tmp_path/"override.sqlite"
    monkeypatch.setenv("AUDIT_DB",str(path))
    app = AppTest.from_file(str(ROOT/"app.py"),default_timeout=30).run()
    app.sidebar.radio[0].set_value("Human Review").run()
    # Streamlit editor state stores row edits; baseline rank rows 0..4 have rescue teams.
    editor_key = "final_plan_"+AuditStore(path).records()[0]["portfolio_id"]
    app.session_state[editor_key] = {"edited_rows":{0:{"rescue_teams":0},5:{"rescue_teams":1}},"added_rows":[],"deleted_rows":[]}
    app.text_area[0].set_value("Simulated local evidence redirects one rescue team.")
    app.checkbox[0].check()
    next(button for button in app.button if button.label == "Authorize reviewed portfolio").click().run()
    assert not app.exception
    overridden = [r for r in AuditStore(path).records() if r["human_override"]]
    assert len(overridden) == 2
    assert all(r["override_reason"] for r in overridden)

def test_overview_navigation_and_priority_filters(tmp_path,monkeypatch):
    monkeypatch.setenv("AUDIT_DB",str(tmp_path/"interactive.sqlite"))
    app=AppTest.from_file(str(ROOT/"app.py"),default_timeout=30).run()
    next(button for button in app.button if button.label == "Explore the full ranking →").click().run()
    assert app.sidebar.radio[0].value == "AI Priority Analysis"
    next(widget for widget in app.text_input if widget.label == "Search areas").set_value("Riverside").run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 1
    assert app.dataframe[0].value.area_name.iloc[0] == "Riverside"
    next(widget for widget in app.text_input if widget.label == "Search areas").set_value("unknown-area").run()
    assert any("No areas match" in item.value for item in app.info)

def test_transfer_preview_restore_and_budget_conservation(tmp_path,monkeypatch):
    path=tmp_path/"transfer.sqlite"
    monkeypatch.setenv("AUDIT_DB",str(path))
    app=AppTest.from_file(str(ROOT/"app.py"),default_timeout=30).run()
    app.sidebar.radio[0].set_value("Human Review").run()
    next(button for button in app.button if button.label == "Apply transfer").click().run()
    assert not app.exception
    editor=next(widget for widget in app.dataframe if "area_id" in widget.value and "area_name" in widget.value and "rank" not in widget.value)
    assert editor.value.rescue_teams.iloc[0] == 0
    assert editor.value.rescue_teams.iloc[1] == 2
    assert editor.value.rescue_teams.sum() == 5
    assert all(record["final_decision"] is None for record in AuditStore(path).records())
    next(button for button in app.button if button.label == "Restore AI proposal").click().run()
    editor=next(widget for widget in app.dataframe if "area_id" in widget.value and "area_name" in widget.value and "rank" not in widget.value)
    assert editor.value.rescue_teams.iloc[0] == 1
    assert editor.value.rescue_teams.iloc[1] == 1

def test_audit_filter_and_scenario_view(tmp_path,monkeypatch):
    monkeypatch.setenv("AUDIT_DB",str(tmp_path/"filters.sqlite"))
    app=AppTest.from_file(str(ROOT/"app.py"),default_timeout=30).run()
    app.sidebar.radio[0].set_value("Accountability Audit").run()
    next(widget for widget in app.selectbox if widget.label == "Decision status").set_value("Override").run()
    assert any("No audit entries" in item.value for item in app.info)
    app.sidebar.radio[0].set_value("Ethical Risk Simulator").run()
    next(widget for widget in app.checkbox if widget.label == "Show changed areas only").check().run()
    assert any("No score changes" in item.value for item in app.info)
    app.sidebar.selectbox[0].set_value("Missing Vulnerable Population Data").run()
    next(widget for widget in app.radio if widget.label == "Comparison view").set_value("Rank movement").run()
    assert not app.exception
