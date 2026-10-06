"""Optional local visual smoke check; requires playwright and an installed Chrome.

Not a dashboard runtime dependency. Screenshots verify local rendering only.
"""
import json
from playwright.sync_api import sync_playwright
from src.config import ROOT

def main():
    result = {"url":"http://127.0.0.1:8501", "pages":[], "browser_errors":[]}
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width":1440,"height":1050})
        page.on("pageerror",lambda error:result["browser_errors"].append(str(error)))
        page.goto(result["url"])
        page.get_by_role("heading",name="Who is answerable when AI recommends the wrong allocation?",exact=True).wait_for(timeout=60000)
        page.screenshot(path=str(ROOT/"reports/figures/dashboard_overview.png"),full_page=True)
        for label, heading in [("AI Priority Analysis","Recommendations awaiting human authorization"),
                               ("Explainable AI",None),("Ethical Risk Simulator","Complete Data"),
                               ("Human Review","Coordinator review and final authority sign-off"),
                               ("Accountability Audit","Traceable recommendations and final decisions")]:
            page.get_by_text(label,exact=True).click()
            if heading:
                page.get_by_role("heading",name=heading,exact=True).wait_for(timeout=30000)
            else:
                page.get_by_text("Area to explain",exact=True).wait_for(timeout=30000)
            tails={"AI Priority Analysis":"Download filtered recommendations","Explainable AI":"Download this explanation",
                   "Ethical Risk Simulator":"Download the complete scenario comparison","Human Review":"Authorize reviewed portfolio",
                   "Accountability Audit":"Export filtered audit JSON"}
            page.get_by_role("button",name=tails[label],exact=True).wait_for(timeout=30000)
            page.locator("[data-testid='stStatusWidget']").wait_for(state="hidden",timeout=30000)
            if page.locator("[data-testid='stException']").count():
                raise RuntimeError(page.locator("[data-testid='stException']").inner_text())
            page.screenshot(path=str(ROOT/"reports/figures"/(label.lower().replace(" ","_")+"_dashboard.png")),full_page=True)
            result["pages"].append(label)
        page.get_by_text("Ethical Risk Simulator",exact=True).click()
        sidebar=page.locator("[data-testid='stSidebar']")
        sidebar.locator("[data-testid='stSelectbox']").first.get_by_role("combobox").click()
        page.get_by_role("option",name="Missing Vulnerable Population Data",exact=True).click()
        page.get_by_role("heading",name="Missing Vulnerable Population Data",exact=True).wait_for(timeout=30000)
        page.get_by_text("Score change",exact=True).click()
        page.get_by_role("button",name="Download the complete scenario comparison",exact=True).wait_for(timeout=30000)
        page.locator("[data-testid='stStatusWidget']").wait_for(state="hidden",timeout=30000)
        page.screenshot(path=str(ROOT/"reports/figures/interactive_scenario_dashboard.png"),full_page=True)
        result["interactive_scenario_switch"]=True
        page.get_by_text("Overview",exact=True).click()
        page.get_by_role("heading",name="A city under pressure",exact=True).wait_for(timeout=30000)
        page.set_viewport_size({"width":390,"height":844})
        sidebar.get_by_role("button").first.click()
        sidebar.wait_for(state="hidden",timeout=10000)
        page.screenshot(path=str(ROOT/"reports/figures/dashboard_mobile.png"),full_page=True)
        result["mobile_render"]=True
        browser.close()
    (ROOT/"reports/browser_verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    assert not result["browser_errors"],result["browser_errors"]
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    main()
