"""Generate submission Markdown from executed metrics, never invented numbers."""
import json
import pandas as pd
from src.config import ROOT
from src.governance import MATRIX, PRINCIPLES, FRAMEWORK, STAKEHOLDERS

TITLE = "Algorithmic Accountability: A Case Study on AI-Based Disaster Response and Emergency Resource Allocation"
REFERENCES = """
1. NIST (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. [Official publication](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf). Governance, context, measurement and risk management inform our responsibility framework.
2. UNESCO (2021). *Recommendation on the Ethics of Artificial Intelligence*. [Official recommendation](https://www.unesco.org/en/legal-affairs/recommendation-ethics-artificial-intelligence). Human oversight, transparency and accountability inform the safeguards.
3. Lundberg, S. M., and Lee, S.-I. (2017). *A Unified Approach to Interpreting Model Predictions*. [Original paper](https://arxiv.org/abs/1705.07874). Basis for SHAP attribution.
4. UNDRR. *Data strategy and roadmap 2023–2027*. [Official strategy](https://www.undrr.org/data-strategy-and-roadmap-2023-2027). Context for disaster data governance; this project does not reproduce a UNDRR operational system.
5. scikit-learn. [Classification metrics](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html) and [GroupShuffleSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html). Implementation references.
6. SHAP. [LinearExplainer](https://shap.readthedocs.io/en/latest/generated/shap.LinearExplainer.html) and [TreeExplainer](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html). Explainability implementation.
7. Streamlit. [App testing](https://docs.streamlit.io/develop/api-reference/app-testing). Interface verification.

Sources accessed 7 October 2026. Ethical sources guide the design; they do not validate the synthetic simulator, score anchors or allocation policy.
"""

def md_table(data):
    columns = data.columns.tolist()
    lines = ["| "+" | ".join(columns)+" |", "| "+" | ".join(["---"]*len(columns))+" |"]
    for _, row in data.iterrows():
        cells = [f"{v:.4f}" if isinstance(v,float) else str(v) for v in row]
        lines.append("| "+" | ".join(cells)+" |")
    return "\n".join(lines)

def write(path,text):
    destination = ROOT/path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text.strip()+"\n",encoding="utf-8")

def build_docs():
    meta = json.loads((ROOT/"reports/metrics.json").read_text())
    metrics = meta["test"][meta["model_name"]]
    summary = pd.read_csv(ROOT/"reports/scenario_summary.csv")
    comparison = pd.read_csv(ROOT/"reports/model_comparison.csv")
    groups = pd.read_csv(ROOT/"reports/test_group_diagnostics.csv")
    missing = pd.read_csv(ROOT/"reports/missing_vulnerable_population_data_comparison.csv")
    lake = missing.loc[missing.area_name.eq("Lake Colony")].iloc[0]
    outer = missing.loc[missing.area_name.eq("Outer Settlement")].iloc[0]
    architecture = """```mermaid
flowchart LR
    D[Synthetic observations] --> V[Validate and impute]
    V --> M[Versioned ML model]
    M --> S[Score and constrained allocation]
    S --> E[SHAP explanation]
    E --> H[Coordinator review]
    H --> F[Final authority authorization]
    F --> A[Append-only audit events]
    A --> I[Post-incident accountability analysis]
    Q[Data-quality scenarios] --> V
```
"""
    framework = "\n".join(f"{i}. {name}" for i,name in enumerate(FRAMEWORK,1))
    framework_visual = "```mermaid\nflowchart TD\n"+"\n".join(f'    N{i}["{FRAMEWORK[i-1]}"] --> N{i+1}["{FRAMEWORK[i]}"]' for i in range(1,len(FRAMEWORK)))+"\n```"
    problem = "When AI recommends which flood-affected areas receive scarce resources first, data providers, developers, organizations and human authorities can each contribute to an error. If their duties and decisions are not recorded, responsibility becomes difficult to investigate. The central question is: who is responsible if the AI-assisted allocation is wrong?"
    case = f"""DEMO-FLOOD-01 is a fictional urban flood affecting twelve named areas. The default budget is five rescue teams, ten ambulances, twenty medical supply units and thirty food/shelter units. Riverside has the highest baseline model score, but model correctness and sufficient assistance cannot be inferred from ranking alone.

In the executed missing-vulnerability scenario, Lake Colony's score changes from {lake.priority_score_baseline:.2f} to {lake.priority_score:.2f}; its rank changes from {int(lake.rank_baseline)} to {int(lake['rank'])} and it loses one rescue team. Outer Settlement changes from rank {int(outer.rank_baseline)} to {int(outer['rank'])} and gains one team. Median imputation can increase or decrease scores, depending on the missing value's relation to the training median. These are real computed changes, not predetermined predictions.

There are no newly missed high-severity areas in this small demonstration incident under the five scenarios. We report that result openly. The held-out test nevertheless has {metrics['confusion_matrix'][2][1]+metrics['confusion_matrix'][3][1]} truly High/Critical records predicted below High, demonstrating model error independently of the demo. Allocation changes indicate possible harm, not observed injuries or deaths."""
    dataset = """The dataset has 3,000 synthetic area-incident records, 250 incidents and twelve recurring area identifiers. NumPy seed 42 fixes generation; the separate complete demo uses seed 2026. No patient, citizen or actual disaster data is used. Columns include flood depth (m), rainfall (mm), population, density (people/km²), calls, accessibility (0–1), distance (km), vulnerable-population fraction (0–1), hospital beds, local resources, medical emergencies, infrastructure damage (0–1), evacuation fraction, historical severity, reliability and diagnostic response time. `true_severity` is a noisy latent simulator value, and `priority_label` bins it at 40, 70 and 85. These thresholds are academic assumptions, not clinical standards.

Flood intensity, vulnerable population, response difficulty and damage generally increase latent need; evacuation generally reduces it. Population and medical demand contribute, and Gaussian noise represents omitted conditions. Observations are correlated; no causal inference is claimed. Approximately 2.5% missingness is introduced independently in three training-data fields. The complete demonstration omits that random missingness to establish a clean comparison. Ground-truth severity is never recomputed after observational corruption."""
    preparation = """Required features are explicitly allowlisted and checked for finite values, valid categories and physical ranges. NaN is allowed and imputed inside the fitted pipeline. Numeric medians and StandardScaler parameters come only from the 1,800 training rows; categorical values use most-frequent imputation and OneHotEncoder. Validation and test each contain 600 rows. GroupShuffleSplit keeps every incident wholly inside one split, preventing same-incident leakage; recurring area types remain across splits, so the evaluation is not an unseen-city test. IDs, true severity, labels and response time are excluded from model inputs. Label-driven selection or post-event outcomes are never input features."""
    methodology = """Four-class severity classification supports uncertainty through predicted probabilities. Logistic Regression and Random Forest are fitted on the same training split. Validation macro F1 selects the final model before test evaluation. Neither model is refitted on the test data. Random Forest uses 180 trees, minimum leaf size three and 80% feature sampling; Logistic Regression uses C=1 and a 1,500-iteration limit. Hyperparameter search was deliberately omitted to keep the experiment understandable.

Emergency score = 20·P(Low) + 55·P(Medium) + 77·P(High) + 95·P(Critical). These within-band anchors are a transparent project decision layer. Scores lie within 0–100 (the expected anchors practically span 20–95). Score bands are Low <40, Medium <70, High <85, Critical ≥85. The most probable model class and score band can differ; neither is silently substituted for the other.

Resource quotas are proportional to score, then integer counts are assigned by largest remainders. Ties follow stable rank and area ID. The algorithm conserves each resource budget. Zero-score portfolios use equal weights. Allocation does not optimize travel, actual demand, team capability, hospital congestion or predicted lives saved. Available local teams/ambulances are context features rather than deductions from the new centrally supplied resource budget."""
    explanation = """The selected Logistic Regression uses SHAP LinearExplainer on transformed features and a training-only background. Contributions explain the predicted class logit before softmax: positive values support that class, negative values oppose it. They are not priority-score points or calibrated probabilities. Random Forest support uses TreeExplainer and predicted-class probability units. Numeric transformed names remain recognizable; encoded area-category contributions appear separately.

For every recommendation, the audit stores the leading six actual contributions and their method/units. The XAI page shows the full table, signed chart, base value and reconstructed output. An automated test checks base plus all contributions equals the model output. Global unsigned model importance is an explicit fallback for supported SHAP failures; it is never presented as signed local attribution. SHAP worked in this execution. Correlated predictors and background choice limit attribution interpretation; explanation does not prove causation, correctness or fairness."""
    oversight = """Every recommendation is pending until the complete portfolio receives explicit sign-off. Confidence is the largest class probability, not a certified uncertainty bound. The configurable default threshold is 70%; low confidence, any missing features or sensor reliability below 0.7 flag mandatory review. Higher confidence still requires human authorization.

Human Review allows integer resource edits for every area. A changed plan requires a meaningful reason of at least eight characters, complete-area coverage, nonnegative integer counts and totals within every budget. Reviewer and authority are selected only from synthetic aliases. A confirmation checkbox records that evidence and flags were reviewed. All twelve review events are committed atomically; rejected plans leave every decision pending. Accepted recommendations and overrides remain distinguishable. A reviewed context cannot be reviewed twice; a new scenario/budget/threshold creates a separate context, while baseline data remains fixed. This demonstrates oversight, but aliases are not authentication, and a checkbox cannot prove a human thoughtfully reviewed evidence."""
    simulations = """1. Complete Data: unchanged observation and final selected model.
2. Missing Vulnerable Population Data: all peripheral-area vulnerability observations become NaN; trained medians handle them.
3. Delayed Emergency Call Data: peripheral calls retain 20% of current counts and medical reports retain 35%, representing a joint reporting delay.
4. Noisy Sensor Data: fixed-seed perturbations change flood depth and rainfall within physical bounds; reliability becomes 0.4.
5. Underrepresented Area Data: retain only the first 10% of peripheral training records in an alternate fitted model, plus missing vulnerability and halved peripheral calls in demo inputs. Validation and test never become training data. This deliberately combines training and observation disadvantages and does not isolate either causal effect.

Each scenario reruns inference and allocation, compares against complete-data baseline with the same budget, and preserves true need. Measures include score differences, rank differences (positive means deterioration), half the absolute resource-count differences (units reassigned), false High/Critical predictions, missed High/Critical reference areas, high-severity areas without rescue, confidence and missing cells. Scenario exports and PNG/interactive HTML charts are produced by actual execution."""
    ethical = """The primary issue is an accountability gap: an organization may defer to a provider, a provider may defer to a developer, and a coordinator may defer to the model, leaving affected people without an answer. Automation bias can convert a recommendation into an unexamined decision. Poor coverage, delayed calls, correlated features and insufficient testing can redistribute scarce assistance. Transparency and auditability help investigators identify the facts, but do not by themselves ensure fair allocation.

Ethical accountability is the obligation to justify decisions, answer questions and support remedy. Technical responsibility concerns model/data/interface engineering. Organizational responsibility concerns procurement, training, deployment and monitoring. Legal liability requires applicable laws and specific facts; this project provides no legal finding. Failure is evaluated as a chain of shared responsibilities, with evidence before blame."""
    results = md_table(comparison)+"\n\n"+md_table(summary)+"\n\n"+f"Selected: {meta['model_name']}. Accuracy {metrics['accuracy']:.2%}, macro precision {metrics['precision_macro']:.4f}, macro recall {metrics['recall_macro']:.4f}, macro F1 {metrics['f1_macro']:.4f}, OvR macro ROC-AUC {metrics['roc_auc_ovr_macro']:.4f}. High recall is {metrics['classification_report']['High']['recall']:.2%}; Critical recall is {metrics['classification_report']['Critical']['recall']:.2%} on only {int(metrics['classification_report']['Critical']['support'])} Critical test examples. Class imbalance makes aggregate accuracy insufficient. Multi-class Brier score is {metrics['multiclass_brier']:.4f}; probabilities have not been independently calibrated.\n\n"+case+"\n\n"+md_table(groups)+"\n\nGroup miss rates condition on true High/Critical need. Groups with fewer than thirty high-severity cases are explicitly flagged; no population fairness, causal disparity or demographic claim follows from these synthetic groups. Unequal mean allocations may reflect unequal modeled need and cannot alone establish unfairness.\n\n![Model comparison](figures/model_comparison.png)\n\n![Confusion matrix](figures/confusion_matrix.png)\n\n![Missing observations](figures/missing_vulnerable_population_data.png)\n\n![Local explanation](figures/riverside_shap.png)"
    audit = """SQLite stores recommendation events and linked review events. Every recommendation includes decision/incident/area IDs, timestamp, model and data versions, dataset SHA-256, original input record ID, full input snapshot and its hash, predicted class, score, confidence, leading explanation features, resource recommendation, mandatory-review flag, scenario, budget, threshold and pending reviewer/final fields. Review events add synthetic reviewer, decision, override flag/reason, final allocation, authority and review time. The merged audit view answers what the AI advised, what evidence it used and how a human changed it.

Stable context IDs make reruns idempotent. SQLite transactions enforce whole-portfolio review; triggers reject event updates/deletions. SHA-256 chains detect local alterations and JSON exports allow investigation. The local database owner can rewrite the journal and its hashes; no external anchor, authentication, retention policy or backup automation is implemented. Joblib files must be project-generated and trusted; untrusted model uploads are unsupported. Model version identifies this dataset/configuration release, not an independent cryptographic signature of every source-file change. Changing implementation requires a deliberate new version."""
    readiness = """The **Project-Defined Accountability Readiness Score** averages seven equally weighted binary dimensions (0 or 100): working SHAP for all active records; complete current human sign-off; complete audit records plus valid hash chain; no missing input fields and sensor reliability ≥0.7; High test recall ≥80% plus at least thirty Critical test examples; report file existence; sustained monitoring. The reliability dimension fails here; monitoring also remains zero because deployment monitoring is absent. With complete inputs and the report present, a pending baseline portfolio scores 57.14/100; after full review it scores 71.43/100. These values follow the executed conditions and formula, and the dashboard recomputes them. A stale but nonmissing call count can pass this limited data-quality check; that limitation is explicit. It is a teaching checklist, not a legal or international standard, and no score certifies operational safety."""
    recommendations = """Require data provenance and freshness indicators, validate missing and implausible observations, evaluate rare severe cases and undercovered areas, and make model limits visible. Give reviewers time, local information and authority to challenge recommendations. Separate AI advice from human authorization and preserve override reasons. Review data/model/organization/human contributions jointly after incidents, with avenues for correction and remedy. Assign owners for monitoring, backups and data contracts. Suspend use when evidence quality or validation becomes inadequate."""
    limitations = """Synthetic labels encode designer assumptions and omit many social, geographic and logistical variables. Only one fixed split and one generator are evaluated; generalization to actual cities is unknown. Seven Critical test examples provide weak evidence. No independently calibrated uncertainty, temporal freshness metadata, validated harm estimates or routing optimization is available. The underrepresentation experiment is confounded by intentional input corruption. Twelve-area comparisons are descriptive, and synthetic area categories are not protected demographics. Local aliases and hash checking are academic mechanisms, not secure organizational identity or tamper-proof storage. Review confirmation cannot eliminate automation bias. This system must not guide real emergencies."""
    future = "With appropriate permissions and governance, use representative event-disjoint and temporal external validation, stronger severe-case support, calibrated probabilities, timestamps for source freshness, logistics-aware constrained allocation, uncertainty-sensitive escalation, authenticated reviewer roles, external audit anchoring, disaster recovery, drift monitoring and stakeholder participation. Evaluate resulting policy choices with emergency professionals before any operational consideration."
    sections = [
        ("Introduction", "This mini-project examines AI-assisted allocation as an ethics and accountability case study. It implements the entire evidence chain from observations to authorized decisions and post-incident scrutiny."),
        ("Problem Definition",problem), ("Objectives","Implement reproducible ML; expose data-quality consequences; conserve scarce resources; explain predictions; require human approval; preserve decision evidence; map shared stakeholder duties without deciding legal liability."),
        ("Background / Context", "NIST AI RMF 1.0 organizes responsible-AI risk work through governance, context, measurement and management [1]. UNESCO's recommendation emphasizes oversight and accountability [2]. UNDRR's data strategy provides disaster-data governance context [4]. This project applies those ideas in a limited teaching simulation; it is an allocation study rather than flood forecasting."),
        ("Case Study",case), ("Ethical Issue Identification",ethical),
        ("Relevant Ethical Principles",md_table(PRINCIPLES)), ("Dataset",dataset), ("Data Preparation",preparation),
        ("Methodology and Analysis",methodology+"\n\n"+architecture),
        ("ML Model",md_table(comparison)+"\n\nValidation-selected winner: "+meta["model_name"]+". Selection favors validation macro F1 over aggregate accuracy; test metrics are reported after selection. Full class reports and matrices are in metrics.json."),
        ("Explainable AI",explanation),
        ("Accountability Framework",framework+"\n\n"+framework_visual+"\n\n"+audit+"\n\n"+md_table(MATRIX)+"\n\n"+"\n\n".join(f"**{k}:** {v}" for k,v in STAKEHOLDERS.items())+"\n\n"+readiness),
        ("Human Oversight",oversight), ("Ethical Risk Simulation",simulations), ("Results / Findings",results),
        ("Proposed Solution / Recommendations",recommendations), ("Limitations",limitations), ("Future Scope",future),
        ("Conclusion","The executed experiments show how incomplete observations can change resource allocations even when the affected area does not cross a severity class boundary. High overall accuracy coexists with missed severe records. Explanations, review gates and traceable evidence make distributed responsibility investigable, while meaningful oversight and governance remain human and organizational duties."),
        ("References",REFERENCES)]
    write("reports/PROJECT_REPORT.md", "# "+TITLE+"\n\nSubject: Ethics in Artificial Intelligence & Data Science\n\nAcademic simulation only. All results below are generated by this repository.\n\n"+"\n\n".join(f"## {i}. {heading}\n\n{body}" for i,(heading,body) in enumerate(sections,1)))
    install = r"""Python 3.13 is the verified runtime. From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m src.train
.venv\Scripts\python -m scripts.build_results
.venv\Scripts\python -m scripts.build_docs
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m streamlit run app.py
```

If the pinned libraries are already installed, use `python` for each command instead. Training models and generated results are supplied, so the initial dashboard can start immediately. The browser URL is http://localhost:8501. Stop the server with Ctrl+C. The first SHAP import can take several seconds. Run only trusted local model artifacts.
"""
    structure = """```text
app.py                         ten dashboard workspaces
requirements.txt               pinned verified Python libraries
.streamlit/config.toml         dashboard theme/server settings
src/                           data, ML, explanation, allocation, scenarios, audit
scripts/                       results, documentation and verification commands
data/raw/                      3,000-row dataset and complete demo incident
data/processed/                incident-disjoint split manifest
models/                        selected and underrepresentation model bundles
logs/                          local append-only SQLite audit (created at runtime)
reports/                       report, metrics, CSV outputs, figures and verification
presentation/                  15-slide outline and six-minute demonstration script
docs/                          architecture, data/model cards, ethics and 60 viva answers
tests/                         model, data, allocation, simulation, audit and UI tests
```"""
    readme_sections = [("Title",TITLE),("Abstract","An end-to-end academic simulator makes AI resource recommendations explainable, reviewable and traceable. It studies an accountability gap using synthetic urban flood observations and actual executed model/scenario outputs."),
        ("Problem Statement",problem),("Case Study",case),("Ethical Issue",ethical),("Objectives",sections[2][1]),
        ("Background",sections[3][1]+"\n\n"+REFERENCES),("Ethical Principles",md_table(PRINCIPLES)),("Dataset",dataset),
        ("Methodology",preparation+"\n\n"+methodology),("Architecture",architecture),("ML Models",md_table(comparison)),
        ("Explainability",explanation),("Accountability Framework",framework+"\n\n"+audit+"\n\n"+readiness),
        ("Human-in-the-Loop",oversight),("Ethical Simulations",simulations),("Results",md_table(summary)+"\n\nDetailed class metrics: reports/metrics.json; report: reports/PROJECT_REPORT.md; diagrams/plots: reports/figures/; tests: python -m pytest -q."),
        ("Recommendations",recommendations),("Limitations",limitations),("Future Scope",future),("Installation",install),
        ("How to Run","Start with `python -m streamlit run app.py`. Navigate from Overview to AI Priority Analysis, Explainable AI, Ethical Risk Simulator, Human Review and Accountability Audit. The sidebar scenario and budget are shared across pages. Read presentation/DEMO_SCRIPT.md for the exact professor demonstration.\n\nFor a complete fresh rebuild and verification, run `python -m scripts.verify_project`. This regenerates synthetic data, trains both models, exports results, rebuilds documents, creates a separate sample override audit and runs tests. The rebuild checks dataset, model-comparison and scenario-output hashes against the prior execution. Test output is saved to reports/test_results.txt and verification.json. The example reviewed audit is reports/demo_audit.json; it does not finalize the live dashboard's pending portfolio. Optional browser smoke check: install playwright and run `python -m scripts.browser_check` with Chrome installed and Streamlit serving locally."),
        ("Project Structure",structure)]
    write("README.md", "# "+TITLE+"\n\n**Simulation only — not for real emergency decision-making.**\n\n"+"\n\n".join(f"## {i}. {heading}\n\n{body}" for i,(heading,body) in enumerate(readme_sections,1)))
    write("docs/SYSTEM_ARCHITECTURE.md", "# System architecture\n\n"+architecture+"\n\n"+structure+"\n\n"+preparation+"\n\n"+audit+"\n\nTraining: `python -m src.train` → results: `python -m scripts.build_results` → documentation: `python -m scripts.build_docs` → tests: `python -m pytest -q` → dashboard: `python -m streamlit run app.py`. Regenerate reports after retraining. To preserve a prior release, archive its artifacts and audit database before deliberate version changes.")
    write("docs/ETHICAL_ANALYSIS.md", "# Ethical case study\n\n"+problem+"\n\n"+case+"\n\n"+ethical+"\n\n"+md_table(MATRIX)+"\n\n"+md_table(PRINCIPLES)+"\n\n"+framework_visual+"\n\n## Investigator questions\n\nWas the source complete and current? Were ranges and coverage validated? Was rare severe-case recall sufficient? Did the organization test corrupted-data conditions? Did the coordinator have time and local evidence? Did the authority authorize the final portfolio? Is the recommendation distinct from the decision? Check the retained input snapshot, explanation units, versions and review event before attributing responsibility.\n\n"+recommendations+"\n\n"+REFERENCES)
    write("docs/DATA_CARD.md", "# Synthetic dataset card\n\n"+dataset+"\n\n"+preparation+"\n\nDataset version: "+meta["dataset_version"]+"\n\nSHA-256: `"+meta["dataset_sha256"]+"`\n\nClass counts: "+json.dumps(meta["class_counts"])+"\n\nVariable bounds and allowlisted features are authoritative in src/config.py. Incident IDs identify synthetic storm groups; area names are fictional location descriptors. The unobserved outcome formula is in src/data_generation.py and is a pedagogical assumption. No geographic or demographic representativeness is claimed.")
    write("docs/MODEL_CARD.md", "# Model card\n\nSelected model: "+meta["model_name"]+"\n\nVersion: "+meta["model_version"]+"\n\n"+methodology+"\n\n"+md_table(comparison)+"\n\n"+explanation+"\n\n"+limitations+"\n\nIntended use: undergraduate demonstration of decision traceability. Prohibited operational interpretation: triage, dispatch or actual disaster prediction. Probabilities are uncalibrated. Use the Critical class report and sample counts alongside accuracy. Model artifacts retain the fitted preprocessing pipeline, training background and metadata.")
    slides = [
        ("Title",[TITLE,"Ethics in Artificial Intelligence & Data Science","Academic simulation, no real citizen data"],"Title and data-to-audit chain"),
        ("Motivation",["Emergency help is scarce","Recommendations can influence consequential choices","Consequences require reasons and evidence"],"Four resource-budget cards"),
        ("Problem Statement",["Who is answerable when an AI-assisted allocation is wrong?","Data, engineering, deployment and human decisions interact"],"Six stakeholder nodes"),
        ("Urban Flood Case",["Twelve fictional areas","Five rescue teams and ten ambulances","Riverside has highest baseline score"],"reports/complete_data_allocation.csv table"),
        ("Central Ethical Question",["Advice passes through human review","A responsibility gap can obscure who did what","The project does not determine legal liability"],"Recommendation → review → final decision"),
        ("Ethical Issues",["Automation bias and inadequate oversight","Incomplete or delayed observations","Traceability, potential harm and distributed responsibility"],"Failure chain"),
        ("Ethical Principles",["Accountability → audit","Transparency → explanations","Fairness → conditional group checks","Oversight → explicit authorization"],"Principles mapping table"),
        ("Proposed System",["Validation → model → score → allocation","Explanation → review → immutable events","Five real data/model perturbations"],"Architecture Mermaid diagram"),
        ("ML Methodology",["3,000 records; incident-disjoint 1,800/600/600 split","Logistic Regression vs Random Forest","Select by validation macro F1 before test"],"reports/figures/model_comparison.png"),
        ("Explainable AI",["Actual SHAP LinearExplainer values","Signed predicted-class logit contributions","Explanation is not proof of correctness"],"reports/figures/riverside_shap.png"),
        ("Accountability Framework",["Twelve safeguards from provenance to responsibility assignment","Input snapshots, model/data versions and review events","Shared stakeholder matrix"],"Framework diagram and audit record"),
        ("Ethical Simulation",["Missing vulnerability changes four ranks and one rescue unit","Noisy sensors change nine ranks and two rescue units","No new missed severe areas in the small demo: report honestly"],"reports/figures/missing_vulnerable_population_data.png"),
        ("Measured Results",[f"Winner: {meta['model_name']}",f"Test accuracy {metrics['accuracy']:.1%}, macro F1 {metrics['f1_macro']:.3f}",f"High recall {metrics['classification_report']['High']['recall']:.1%}; only seven Critical test records","Aggregate accuracy hides missed severe need"],"Confusion matrix and scenario CSV"),
        ("Recommendations",["Validate data freshness and coverage","Require meaningful review and record reasons","Monitor severe-case recall and preserve provenance","Readiness score is project-defined"],"Recommendations and readiness checklist"),
        ("Conclusion",["AI recommendations need human and organizational accountability","Evidence supports investigation of shared duties","Synthetic results cannot justify real deployment"],"Final data-to-accountability chain")]
    write("presentation/PRESENTATION_OUTLINE.md", "# 15-slide presentation outline\n\n"+"\n\n".join(f"## Slide {i}: {heading}\n\n"+"\n".join("- "+item for item in bullets)+"\n\n**Visual:** "+visual for i,(heading,bullets,visual) in enumerate(slides,1)))
    steps = [
        ("0:00–0:20","Open application","Run python -m streamlit run app.py, then open Overview.","This academic simulation studies who is answerable for an AI-assisted decision. It does not dispatch real emergency services."),
        ("0:20–0:45","Explain case","Point to the case description and budgets.","A flood affects twelve fictional areas. We have only five rescue teams. Our ethical problem is the decision chain, not predicting a flood."),
        ("0:45–1:05","Show disaster areas","Open Disaster Scenario with Complete Data selected.","Flood depth, vulnerability and road access describe simulated need. True severity is hidden from the model and used only to evaluate the experiment."),
        ("1:05–1:25","Show AI ranking","Open AI Priority Analysis.","The model produces class probabilities. We turn these into a transparent expected-anchor score. Riverside is highest in this baseline."),
        ("1:25–1:45","Show resource allocation","Point to the resource columns.","Integer allocations follow a proportional largest-remainder rule. Totals exactly match the limited budget, but the policy does not guarantee sufficient help."),
        ("1:45–2:00","Select one area","Open Explainable AI and select Riverside.","We can examine the particular observation that produced this recommendation."),
        ("2:00–2:25","Show SHAP explanation","Point to signed contributions and reconstructed logit.","These are actual model contributions. Positive values support the predicted class and negative values oppose it. They are logits, not priority points, and do not prove correctness."),
        ("2:25–2:45","Simulate missing data","Open Ethical Risk Simulator and choose Missing Vulnerable Population Data in the sidebar.","This removes vulnerability observations for peripheral areas and reruns the fitted pipeline. It does not change a caption or invent a result."),
        ("2:45–3:10","Show ranking change","Inspect Lake Colony and Outer Settlement in the comparison table.","Lake Colony drops from fifth to sixth and loses one rescue team; Outer Settlement rises from seventh to fourth and gains it. A small score change can move an indivisible resource."),
        ("3:10–3:35","Explain ethical consequence","Point to missing cells, confidence and mandatory-review flags.","Missing observations can transfer assistance without changing severity classes. This is potential harm, not measured casualties. Data providers, developers and the organization have different but overlapping duties."),
        ("3:35–3:55","Open human review","Open Human Review while the missing-data scenario stays active.","The recommendation is pending. The coordinator and final authority must inspect evidence. A high model probability cannot replace authorization."),
        ("3:55–4:35","Override AI","Transfer one rescue team from Outer Settlement back to Lake Colony, select synthetic aliases, enter 'Simulated field report confirms Lake Colony needs rescue support.', check review confirmation and authorize.","I retain the original AI recommendation, conserve the five-team budget, and give a reason for this simulated correction. Both changed areas receive override events."),
        ("4:35–5:00","Show audit log","Open Accountability Audit and inspect an overridden area's record; optionally export JSON.","This records the data snapshot, versions, prediction, explanation, reviewer, reason, final resources and authority. The original recommendation remains available for investigation."),
        ("5:00–5:30","Show accountability matrix","Open Stakeholder Accountability.","We analyze shared responsibility rather than automatically blaming a developer or coordinator. Ethical accountability and organizational duties are different from legal liability."),
        ("5:30–6:15","Show recommendations","Briefly show Results & Findings, then Recommendations.",f"Test accuracy was {metrics['accuracy']:.1%}, but High recall was only {metrics['classification_report']['High']['recall']:.1%}. The safeguards are data governance, meaningful oversight, explanations, logs and monitoring. Synthetic success cannot authorize real deployment.")]
    write("presentation/DEMO_SCRIPT.md", "# Six-minute demonstration script\n\nBefore the presentation, use the default budget and threshold. If the missing-data portfolio was already finalized in a rehearsal, choose a new budget or threshold to create a distinct context; preserve the earlier journal. Never pretend that prior decisions are new.\n\n"+"\n\n".join(f"## {i}. {title} ({timing})\n\n**Action:** {action}\n\n**Say:** “{say}”" for i,(timing,title,action,say) in enumerate(steps,1))+"\n\nIf live training is unnecessary, use the supplied fitted artifacts. If a professor asks whether all scenarios worsen outcomes, show the actual zero-miss demo results and explain the held-out severe-class errors. Never claim a guaranteed score drop or measured injury.")
    build_viva(meta,metrics)
    print("Generated README, full 21-section report, architecture/ethics/data/model cards, 15 slides, demo and 60 viva answers.")

def build_viva(meta,metrics):
    qa = [
        ("Why this topic?","AI recommendations can influence scarce-resource decisions. The project makes the resulting human and organizational duties visible."),
        ("What is algorithmic accountability?","The ability and obligation to explain, investigate and justify decisions involving algorithms, identify responsible roles and support correction."),
        ("Why disaster response?","Urgency, uncertainty and limited assistance make the consequences of incomplete data and overreliance easy to study in simulation."),
        ("Why is this an ethical issue?","An unjustified allocation can disadvantage affected communities, and unclear responsibility can obstruct explanation or remedy."),
        ("Can AI be responsible like a human?","A model has no human moral agency or institutional duty. Responsibility must be analyzed among people and organizations that collect, build, supply and use it."),
        ("What is a responsibility gap?","A gap occurs when several participants contribute to a consequential decision but none clearly accepts a duty to justify it or correct its effects."),
        ("What is automation bias?","It is excessive trust in automated advice, including accepting it despite contradictory evidence or failing to check its limits."),
        ("What is human-in-the-loop?","A person meaningfully reviews evidence and can change the recommendation before final authorization. Our portfolio has no final decision until sign-off."),
        ("Why explainability?","It gives reviewers evidence about model behavior and supports challenges. It cannot prove that a decision is safe or correct."),
        ("Why use SHAP?","SHAP provides model-derived signed feature attributions with an additive reconstruction of the selected model output."),
        ("What is data provenance?","It is evidence of the origin and version of data. We store synthetic record IDs, versions, hashes and complete observation snapshots."),
        ("Why auditability?","Investigators need to reconstruct what the AI saw and recommended, who reviewed it and what was finally authorized."),
        ("What happens with incomplete data?","The pipeline imputes trained medians. This can move a score either up or down and changes review flags; it does not restore missing knowledge."),
        ("What happens with delayed data?","Old or underreported calls can understate observed need even when values are numerically valid. The scenario explicitly reduces reported calls and medical cases."),
        ("What if the model is biased?","Investigate coverage, labels, errors and policy effects across relevant groups, improve evidence and suspend unsupported use. Synthetic group differences do not prove population bias."),
        ("Why synthetic data?","It permits reproducible ethical perturbations without exposing actual citizen or patient information."),
        ("Why not real disaster data?","This project has no governed representative real data. Real use would require permissions, documentation, quality checks and external validation."),
        ("How is priority calculated?","It is the probability-weighted average of class anchors 20, 55, 77 and 95. This is a documented academic decision layer."),
        ("How are resources allocated?","A proportional largest-remainder method rounds score-weighted quotas to integers while conserving each budget."),
        ("Why the chosen model?",f"{meta['model_name']} achieved the larger validation macro F1. Selection occurred before test evaluation, and the simpler model supports transparent explanations."),
        ("How was leakage prevented?","Ground truth, labels, IDs and response time are excluded; preprocessing fits only training rows; whole incidents stay within one split."),
        ("How was the model evaluated?","Accuracy, macro precision/recall/F1, per-class reports, confusion matrices, OvR ROC-AUC and multiclass Brier score on untouched test rows."),
        ("What are the limitations?","Synthetic assumptions, rare Critical examples, uncalibrated probability, limited fairness inference, simplified allocation and local academic audit security."),
        ("Can it be deployed now?","No. It is explicitly an academic simulation with no evidence of operational safety or generalization to actual disasters."),
        ("What changes before real deployment?","Representative governed data, external/temporal validation, calibrated uncertainty, logistics validation, authentication, monitoring, backups and organizational procedures."),
        ("Who is accountable if AI is wrong?","Examine the evidence chain. Data, engineering, provision, deployment, review and final authorization may involve shared responsibility; no automatic blame rule is defensible."),
        ("What if the human reviewer is wrong?","The reviewer must justify the decision, while the organization must examine information access, training, workload and supervision."),
        ("What if both AI and human are wrong?","Investigate both failures and their interaction, including automation bias and whether safeguards were adequate. Their errors do not cancel responsibility."),
        ("How are accountability gaps reduced?","Separate pending advice from final decisions, retain provenance/explanations, require sign-off and reasons, and identify stakeholder duties."),
        ("What is model versioning?","A release identifier links a recommendation to the model/data configuration used. It enables comparison and reconstruction across releases."),
        ("Why record model versions?","A later model may behave differently on the same data. Without the earlier release, the original recommendation is harder to investigate."),
        ("Why keep recommendation history?","An override should not overwrite the AI's original advice. Both events are necessary to reconstruct influence and decision responsibility."),
        ("What is model drift?","A change in data or outcomes can make a formerly evaluated model less reliable. Monitoring requires fresh evidence; this prototype has no sustained production monitoring."),
        ("How do principles map to features?","Accountability maps to logs, transparency to snapshots and explanations, oversight to review, reliability to held-out evaluation and fairness to conditional scenario diagnostics."),
        ("Ethical accountability versus legal liability?","Ethical accountability concerns justification and duties. Legal liability depends on applicable law and facts and is not determined by this simulation."),
        ("What is the actual test performance?",f"Accuracy {metrics['accuracy']:.1%}, macro F1 {metrics['f1_macro']:.3f} and macro ROC-AUC {metrics['roc_auc_ovr_macro']:.3f}; interpret them alongside class counts and severe-case recall."),
        ("Why is accuracy insufficient?",f"The Medium class dominates. High recall is only {metrics['classification_report']['High']['recall']:.1%}, so an 85% accuracy headline hides missed serious cases."),
        ("What is macro F1?","Compute F1 separately for each class and average equally, so a common class does not receive more weight simply because it has more examples."),
        ("What is confidence?","The maximum predicted class probability. It is uncalibrated here and cannot be interpreted as a guaranteed probability that the allocation is safe."),
        ("Does high confidence remove review?","No. Every portfolio requires authorization. Low confidence, missing features and unreliable sensors add mandatory-review flags."),
        ("Why do prediction and score band differ?","Prediction chooses the most probable class; score averages all class anchors. An uncertain distribution can produce an expected score in another band."),
        ("What do SHAP values mean here?","For Logistic Regression they explain the selected class logit before softmax. For Random Forest they explain class probability. Units are displayed explicitly."),
        ("Are SHAP values causal?","No. They explain fitted model behavior relative to a background. Correlated inputs and background choice affect attribution."),
        ("What if SHAP fails?","The code reports a global unsigned importance fallback with its cause. It never labels global importance as signed local SHAP."),
        ("How is SHAP verified?","A test adds the base value and all contributions and compares the result with the selected model output."),
        ("Does missingness always reduce priority?","No. Imputing a median can raise a low actual value or lower a high actual value. The executed demo includes both directions."),
        ("What changed in the missing-data demo?","Four ranks changed, and one rescue team moved from Lake Colony to Outer Settlement. No newly missed severe area appeared in that twelve-area incident."),
        ("What changed with noisy sensors?","Nine ranks changed and two rescue units were reassigned in the fixed demonstration. Reliability is lowered and mandatory review is flagged."),
        ("How is underrepresentation implemented?","An alternate model retains 10% of peripheral training records; demo peripheral vulnerability and calls are also corrupted. Combined effects are reported without a causal isolation claim."),
        ("What is the fairness measure?","A descriptive miss rate conditional on true High/Critical severity within synthetic area categories. Small denominators are flagged; this is not demographic fairness proof."),
        ("What is false prioritization?","A Low/Medium simulator reference record is predicted High/Critical. It may draw attention from others, although actual harm is not measured."),
        ("What is a missed high-severity area?","An area labeled High/Critical by fixed simulated ground truth is predicted Low/Medium. Ground truth does not change when observations are corrupted."),
        ("Does the readiness score certify safety?","No. It is a seven-dimension project-defined binary checklist, with disclosed evidence and equal weighting, not an international or legal standard."),
        ("Why is readiness not 100?","Severe-case reliability criteria fail and sustained monitoring is absent. Pending human approval and corrupted observations can lower other dimensions."),
        ("Can an override exceed the budget?","No. All area edits are validated together; negative, fractional or over-budget resource counts are rejected before any review event is committed."),
        ("Why require an override reason?","It preserves the evidence motivating a changed decision and helps distinguish justified intervention from arbitrary edits."),
        ("Are the audit logs tamper-proof?","No. Triggers prevent ordinary edits and a hash chain detects local alterations, but a database administrator could rewrite everything. External anchoring would be needed."),
        ("Do synthetic aliases authenticate reviewers?","No. They prevent collecting real personal information and demonstrate role attribution. Production authentication is absent."),
        ("What prevents duplicate decisions on rerun?","A stable context ID combines inputs, scenario, model version, budget and threshold. Unique recommendation keys make identical reruns idempotent."),
        ("What is the main conclusion?","Data defects and model errors can influence scarce-resource recommendations. Meaningful oversight, clear role duties and traceable evidence support investigation, but do not guarantee fair or safe decisions.")]
    assert len(qa) >= 50
    write("docs/VIVA_QUESTIONS.md", "# 60 viva questions with answers\n\n"+"\n\n".join(f"## {i}. {question}\n\n{answer}" for i,(question,answer) in enumerate(qa,1)))

if __name__ == "__main__":
    build_docs()
