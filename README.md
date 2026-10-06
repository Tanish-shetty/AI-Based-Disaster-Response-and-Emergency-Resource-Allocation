# Algorithmic Accountability: A Case Study on AI-Based Disaster Response and Emergency Resource Allocation

**Simulation only — not for real emergency decision-making.**

## 1. Title

Algorithmic Accountability: A Case Study on AI-Based Disaster Response and Emergency Resource Allocation

## 2. Abstract

An end-to-end academic simulator makes AI resource recommendations explainable, reviewable and traceable. It studies an accountability gap using synthetic urban flood observations and actual executed model/scenario outputs.

## 3. Problem Statement

When AI recommends which flood-affected areas receive scarce resources first, data providers, developers, organizations and human authorities can each contribute to an error. If their duties and decisions are not recorded, responsibility becomes difficult to investigate. The central question is: who is responsible if the AI-assisted allocation is wrong?

## 4. Case Study

DEMO-FLOOD-01 is a fictional urban flood affecting twelve named areas. The default budget is five rescue teams, ten ambulances, twenty medical supply units and thirty food/shelter units. Riverside has the highest baseline model score, but model correctness and sufficient assistance cannot be inferred from ranking alone.

In the executed missing-vulnerability scenario, Lake Colony's score changes from 53.35 to 51.93; its rank changes from 5 to 6 and it loses one rescue team. Outer Settlement changes from rank 7 to 4 and gains one team. Median imputation can increase or decrease scores, depending on the missing value's relation to the training median. These are real computed changes, not predetermined predictions.

There are no newly missed high-severity areas in this small demonstration incident under the five scenarios. We report that result openly. The held-out test nevertheless has 26 truly High/Critical records predicted below High, demonstrating model error independently of the demo. Allocation changes indicate possible harm, not observed injuries or deaths.

## 5. Ethical Issue

The primary issue is an accountability gap: an organization may defer to a provider, a provider may defer to a developer, and a coordinator may defer to the model, leaving affected people without an answer. Automation bias can convert a recommendation into an unexamined decision. Poor coverage, delayed calls, correlated features and insufficient testing can redistribute scarce assistance. Transparency and auditability help investigators identify the facts, but do not by themselves ensure fair allocation.

Ethical accountability is the obligation to justify decisions, answer questions and support remedy. Technical responsibility concerns model/data/interface engineering. Organizational responsibility concerns procurement, training, deployment and monitoring. Legal liability requires applicable laws and specific facts; this project provides no legal finding. Failure is evaluated as a chain of shared responsibilities, with evidence before blame.

## 6. Objectives

Implement reproducible ML; expose data-quality consequences; conserve scarce resources; explain predictions; require human approval; preserve decision evidence; map shared stakeholder duties without deciding legal liability.

## 7. Background

NIST AI RMF 1.0 organizes responsible-AI risk work through governance, context, measurement and management [1]. UNESCO's recommendation emphasizes oversight and accountability [2]. UNDRR's data strategy provides disaster-data governance context [4]. This project applies those ideas in a limited teaching simulation; it is an allocation study rather than flood forecasting.


1. NIST (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. [Official publication](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf). Governance, context, measurement and risk management inform our responsibility framework.
2. UNESCO (2021). *Recommendation on the Ethics of Artificial Intelligence*. [Official recommendation](https://www.unesco.org/en/legal-affairs/recommendation-ethics-artificial-intelligence). Human oversight, transparency and accountability inform the safeguards.
3. Lundberg, S. M., and Lee, S.-I. (2017). *A Unified Approach to Interpreting Model Predictions*. [Original paper](https://arxiv.org/abs/1705.07874). Basis for SHAP attribution.
4. UNDRR. *Data strategy and roadmap 2023–2027*. [Official strategy](https://www.undrr.org/data-strategy-and-roadmap-2023-2027). Context for disaster data governance; this project does not reproduce a UNDRR operational system.
5. scikit-learn. [Classification metrics](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html) and [GroupShuffleSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html). Implementation references.
6. SHAP. [LinearExplainer](https://shap.readthedocs.io/en/latest/generated/shap.LinearExplainer.html) and [TreeExplainer](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html). Explainability implementation.
7. Streamlit. [App testing](https://docs.streamlit.io/develop/api-reference/app-testing). Interface verification.

Sources accessed 7 October 2026. Ethical sources guide the design; they do not validate the synthetic simulator, score anchors or allocation policy.


## 8. Ethical Principles

| Ethical principle | System feature |
| --- | --- |
| Accountability | Versioned recommendations and named synthetic sign-off |
| Transparency | Input snapshots, scoring formula and documented limitations |
| Human Oversight | All final portfolios require coordinator and authority confirmation |
| Fairness | Synthetic group miss rates and data-quality scenario comparisons |
| Data Responsibility | Schema/range validation, provenance and missing-data flags |
| Reliability | Incident-disjoint validation/test metrics and automated tests |
| Explainability | Signed local SHAP contributions with output units |
| Auditability | Linked recommendation/review events, JSON export and hash checking |

## 9. Dataset

The dataset has 3,000 synthetic area-incident records, 250 incidents and twelve recurring area identifiers. NumPy seed 42 fixes generation; the separate complete demo uses seed 2026. No patient, citizen or actual disaster data is used. Columns include flood depth (m), rainfall (mm), population, density (people/km²), calls, accessibility (0–1), distance (km), vulnerable-population fraction (0–1), hospital beds, local resources, medical emergencies, infrastructure damage (0–1), evacuation fraction, historical severity, reliability and diagnostic response time. `true_severity` is a noisy latent simulator value, and `priority_label` bins it at 40, 70 and 85. These thresholds are academic assumptions, not clinical standards.

Flood intensity, vulnerable population, response difficulty and damage generally increase latent need; evacuation generally reduces it. Population and medical demand contribute, and Gaussian noise represents omitted conditions. Observations are correlated; no causal inference is claimed. Approximately 2.5% missingness is introduced independently in three training-data fields. The complete demonstration omits that random missingness to establish a clean comparison. Ground-truth severity is never recomputed after observational corruption.

## 10. Methodology

Required features are explicitly allowlisted and checked for finite values, valid categories and physical ranges. NaN is allowed and imputed inside the fitted pipeline. Numeric medians and StandardScaler parameters come only from the 1,800 training rows; categorical values use most-frequent imputation and OneHotEncoder. Validation and test each contain 600 rows. GroupShuffleSplit keeps every incident wholly inside one split, preventing same-incident leakage; recurring area types remain across splits, so the evaluation is not an unseen-city test. IDs, true severity, labels and response time are excluded from model inputs. Label-driven selection or post-event outcomes are never input features.

Four-class severity classification supports uncertainty through predicted probabilities. Logistic Regression and Random Forest are fitted on the same training split. Validation macro F1 selects the final model before test evaluation. Neither model is refitted on the test data. Random Forest uses 180 trees, minimum leaf size three and 80% feature sampling; Logistic Regression uses C=1 and a 1,500-iteration limit. Hyperparameter search was deliberately omitted to keep the experiment understandable.

Emergency score = 20·P(Low) + 55·P(Medium) + 77·P(High) + 95·P(Critical). These within-band anchors are a transparent project decision layer. Scores lie within 0–100 (the expected anchors practically span 20–95). Score bands are Low <40, Medium <70, High <85, Critical ≥85. The most probable model class and score band can differ; neither is silently substituted for the other.

Resource quotas are proportional to score, then integer counts are assigned by largest remainders. Ties follow stable rank and area ID. The algorithm conserves each resource budget. Zero-score portfolios use equal weights. Allocation does not optimize travel, actual demand, team capability, hospital congestion or predicted lives saved. Available local teams/ambulances are context features rather than deductions from the new centrally supplied resource budget.

## 11. Architecture

```mermaid
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


## 12. ML Models

| Model | Validation macro F1 | Test accuracy | Test precision (macro) | Test recall (macro) | Test macro F1 | Test ROC-AUC (OvR macro) |
| --- | --- | --- | --- | --- | --- | --- |
| Logistic Regression | 0.7895 | 0.8500 | 0.8157 | 0.7076 | 0.7524 | 0.9627 |
| Random Forest | 0.7615 | 0.8383 | 0.8609 | 0.6508 | 0.7196 | 0.9548 |

## 13. Explainability

The selected Logistic Regression uses SHAP LinearExplainer on transformed features and a training-only background. Contributions explain the predicted class logit before softmax: positive values support that class, negative values oppose it. They are not priority-score points or calibrated probabilities. Random Forest support uses TreeExplainer and predicted-class probability units. Numeric transformed names remain recognizable; encoded area-category contributions appear separately.

For every recommendation, the audit stores the leading six actual contributions and their method/units. The XAI page shows the full table, signed chart, base value and reconstructed output. An automated test checks base plus all contributions equals the model output. Global unsigned model importance is an explicit fallback for supported SHAP failures; it is never presented as signed local attribution. SHAP worked in this execution. Correlated predictors and background choice limit attribution interpretation; explanation does not prove causation, correctness or fairness.

## 14. Accountability Framework

1. Data Provenance
2. Data Quality Validation
3. Model Documentation
4. Model Versioning
5. Explainable Predictions
6. Confidence Thresholds
7. Human Review
8. Human Override
9. Decision Logging
10. Post-Incident Auditing
11. Continuous Monitoring
12. Responsibility Assignment

SQLite stores recommendation events and linked review events. Every recommendation includes decision/incident/area IDs, timestamp, model and data versions, dataset SHA-256, original input record ID, full input snapshot and its hash, predicted class, score, confidence, leading explanation features, resource recommendation, mandatory-review flag, scenario, budget, threshold and pending reviewer/final fields. Review events add synthetic reviewer, decision, override flag/reason, final allocation, authority and review time. The merged audit view answers what the AI advised, what evidence it used and how a human changed it.

Stable context IDs make reruns idempotent. SQLite transactions enforce whole-portfolio review; triggers reject event updates/deletions. SHA-256 chains detect local alterations and JSON exports allow investigation. The local database owner can rewrite the journal and its hashes; no external anchor, authentication, retention policy or backup automation is implemented. Joblib files must be project-generated and trusted; untrusted model uploads are unsupported. Model version identifies this dataset/configuration release, not an independent cryptographic signature of every source-file change. Changing implementation requires a deliberate new version.

The **Project-Defined Accountability Readiness Score** averages seven equally weighted binary dimensions (0 or 100): working SHAP for all active records; complete current human sign-off; complete audit records plus valid hash chain; no missing input fields and sensor reliability ≥0.7; High test recall ≥80% plus at least thirty Critical test examples; report file existence; sustained monitoring. The reliability dimension fails here; monitoring also remains zero because deployment monitoring is absent. With complete inputs and the report present, a pending baseline portfolio scores 57.14/100; after full review it scores 71.43/100. These values follow the executed conditions and formula, and the dashboard recomputes them. A stale but nonmissing call count can pass this limited data-quality check; that limitation is explicit. It is a teaching checklist, not a legal or international standard, and no score certifies operational safety.

## 15. Human-in-the-Loop

Every recommendation is pending until the complete portfolio receives explicit sign-off. Confidence is the largest class probability, not a certified uncertainty bound. The configurable default threshold is 70%; low confidence, any missing features or sensor reliability below 0.7 flag mandatory review. Higher confidence still requires human authorization.

Human Review allows integer resource edits for every area. A changed plan requires a meaningful reason of at least eight characters, complete-area coverage, nonnegative integer counts and totals within every budget. Reviewer and authority are selected only from synthetic aliases. A confirmation checkbox records that evidence and flags were reviewed. All twelve review events are committed atomically; rejected plans leave every decision pending. Accepted recommendations and overrides remain distinguishable. A reviewed context cannot be reviewed twice; a new scenario/budget/threshold creates a separate context, while baseline data remains fixed. This demonstrates oversight, but aliases are not authentication, and a checkbox cannot prove a human thoughtfully reviewed evidence.

## 16. Ethical Simulations

1. Complete Data: unchanged observation and final selected model.
2. Missing Vulnerable Population Data: all peripheral-area vulnerability observations become NaN; trained medians handle them.
3. Delayed Emergency Call Data: peripheral calls retain 20% of current counts and medical reports retain 35%, representing a joint reporting delay.
4. Noisy Sensor Data: fixed-seed perturbations change flood depth and rainfall within physical bounds; reliability becomes 0.4.
5. Underrepresented Area Data: retain only the first 10% of peripheral training records in an alternate fitted model, plus missing vulnerability and halved peripheral calls in demo inputs. Validation and test never become training data. This deliberately combines training and observation disadvantages and does not isolate either causal effect.

Each scenario reruns inference and allocation, compares against complete-data baseline with the same budget, and preserves true need. Measures include score differences, rank differences (positive means deterioration), half the absolute resource-count differences (units reassigned), false High/Critical predictions, missed High/Critical reference areas, high-severity areas without rescue, confidence and missing cells. Scenario exports and PNG/interactive HTML charts are produced by actual execution.

## 17. Results

| scenario | mean_absolute_score_change | changed_ranks | rescue_units_reassigned | missed_high_severity_areas | false_high_prioritizations | high_severity_without_rescue | mean_confidence | missing_feature_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Complete Data | 0.0000 | 0 | 0 | 0 | 0 | 0 | 0.9148 | 0 |
| Missing Vulnerable Population Data | 0.5744 | 4 | 1 | 0 | 0 | 0 | 0.9108 | 5 |
| Delayed Emergency Call Data | 1.1275 | 0 | 0 | 0 | 0 | 0 | 0.8879 | 0 |
| Noisy Sensor Data | 5.3151 | 9 | 2 | 0 | 0 | 0 | 0.7949 | 0 |
| Underrepresented Area Data | 1.0365 | 4 | 1 | 0 | 0 | 0 | 0.9083 | 5 |

Detailed class metrics: reports/metrics.json; report: reports/PROJECT_REPORT.md; diagrams/plots: reports/figures/; tests: python -m pytest -q.

## 18. Recommendations

Require data provenance and freshness indicators, validate missing and implausible observations, evaluate rare severe cases and undercovered areas, and make model limits visible. Give reviewers time, local information and authority to challenge recommendations. Separate AI advice from human authorization and preserve override reasons. Review data/model/organization/human contributions jointly after incidents, with avenues for correction and remedy. Assign owners for monitoring, backups and data contracts. Suspend use when evidence quality or validation becomes inadequate.

## 19. Limitations

Synthetic labels encode designer assumptions and omit many social, geographic and logistical variables. Only one fixed split and one generator are evaluated; generalization to actual cities is unknown. Seven Critical test examples provide weak evidence. No independently calibrated uncertainty, temporal freshness metadata, validated harm estimates or routing optimization is available. The underrepresentation experiment is confounded by intentional input corruption. Twelve-area comparisons are descriptive, and synthetic area categories are not protected demographics. Local aliases and hash checking are academic mechanisms, not secure organizational identity or tamper-proof storage. Review confirmation cannot eliminate automation bias. This system must not guide real emergencies.

## 20. Future Scope

With appropriate permissions and governance, use representative event-disjoint and temporal external validation, stronger severe-case support, calibrated probabilities, timestamps for source freshness, logistics-aware constrained allocation, uncertainty-sensitive escalation, authenticated reviewer roles, external audit anchoring, disaster recovery, drift monitoring and stakeholder participation. Evaluate resulting policy choices with emergency professionals before any operational consideration.

## 21. Installation

Python 3.13 is the verified runtime. From the repository root:

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


## 22. How to Run

Start with `python -m streamlit run app.py`. Navigate from Overview to AI Priority Analysis, Explainable AI, Ethical Risk Simulator, Human Review and Accountability Audit. The sidebar scenario and budget are shared across pages. Read presentation/DEMO_SCRIPT.md for the exact professor demonstration.

For a complete fresh rebuild and verification, run `python -m scripts.verify_project`. This regenerates synthetic data, trains both models, exports results, rebuilds documents, creates a separate sample override audit and runs tests. The rebuild checks dataset, model-comparison and scenario-output hashes against the prior execution. Test output is saved to reports/test_results.txt and verification.json. The example reviewed audit is reports/demo_audit.json; it does not finalize the live dashboard's pending portfolio. Optional browser smoke check: install playwright and run `python -m scripts.browser_check` with Chrome installed and Streamlit serving locally.

## 23. Project Structure

```text
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
```
