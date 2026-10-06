# Model card

Selected model: Logistic Regression

Version: v1-5f86bbbf

Four-class severity classification supports uncertainty through predicted probabilities. Logistic Regression and Random Forest are fitted on the same training split. Validation macro F1 selects the final model before test evaluation. Neither model is refitted on the test data. Random Forest uses 180 trees, minimum leaf size three and 80% feature sampling; Logistic Regression uses C=1 and a 1,500-iteration limit. Hyperparameter search was deliberately omitted to keep the experiment understandable.

Emergency score = 20·P(Low) + 55·P(Medium) + 77·P(High) + 95·P(Critical). These within-band anchors are a transparent project decision layer. Scores lie within 0–100 (the expected anchors practically span 20–95). Score bands are Low <40, Medium <70, High <85, Critical ≥85. The most probable model class and score band can differ; neither is silently substituted for the other.

Resource quotas are proportional to score, then integer counts are assigned by largest remainders. Ties follow stable rank and area ID. The algorithm conserves each resource budget. Zero-score portfolios use equal weights. Allocation does not optimize travel, actual demand, team capability, hospital congestion or predicted lives saved. Available local teams/ambulances are context features rather than deductions from the new centrally supplied resource budget.

| Model | Validation macro F1 | Test accuracy | Test precision (macro) | Test recall (macro) | Test macro F1 | Test ROC-AUC (OvR macro) |
| --- | --- | --- | --- | --- | --- | --- |
| Logistic Regression | 0.7895 | 0.8500 | 0.8157 | 0.7076 | 0.7524 | 0.9627 |
| Random Forest | 0.7615 | 0.8383 | 0.8609 | 0.6508 | 0.7196 | 0.9548 |

The selected Logistic Regression uses SHAP LinearExplainer on transformed features and a training-only background. Contributions explain the predicted class logit before softmax: positive values support that class, negative values oppose it. They are not priority-score points or calibrated probabilities. Random Forest support uses TreeExplainer and predicted-class probability units. Numeric transformed names remain recognizable; encoded area-category contributions appear separately.

For every recommendation, the audit stores the leading six actual contributions and their method/units. The XAI page shows the full table, signed chart, base value and reconstructed output. An automated test checks base plus all contributions equals the model output. Global unsigned model importance is an explicit fallback for supported SHAP failures; it is never presented as signed local attribution. SHAP worked in this execution. Correlated predictors and background choice limit attribution interpretation; explanation does not prove causation, correctness or fairness.

Synthetic labels encode designer assumptions and omit many social, geographic and logistical variables. Only one fixed split and one generator are evaluated; generalization to actual cities is unknown. Seven Critical test examples provide weak evidence. No independently calibrated uncertainty, temporal freshness metadata, validated harm estimates or routing optimization is available. The underrepresentation experiment is confounded by intentional input corruption. Twelve-area comparisons are descriptive, and synthetic area categories are not protected demographics. Local aliases and hash checking are academic mechanisms, not secure organizational identity or tamper-proof storage. Review confirmation cannot eliminate automation bias. This system must not guide real emergencies.

Intended use: undergraduate demonstration of decision traceability. Prohibited operational interpretation: triage, dispatch or actual disaster prediction. Probabilities are uncalibrated. Use the Critical class report and sample counts alongside accuracy. Model artifacts retain the fitted preprocessing pipeline, training background and metadata.
