# 60 viva questions with answers

## 1. Why this topic?

AI recommendations can influence scarce-resource decisions. The project makes the resulting human and organizational duties visible.

## 2. What is algorithmic accountability?

The ability and obligation to explain, investigate and justify decisions involving algorithms, identify responsible roles and support correction.

## 3. Why disaster response?

Urgency, uncertainty and limited assistance make the consequences of incomplete data and overreliance easy to study in simulation.

## 4. Why is this an ethical issue?

An unjustified allocation can disadvantage affected communities, and unclear responsibility can obstruct explanation or remedy.

## 5. Can AI be responsible like a human?

A model has no human moral agency or institutional duty. Responsibility must be analyzed among people and organizations that collect, build, supply and use it.

## 6. What is a responsibility gap?

A gap occurs when several participants contribute to a consequential decision but none clearly accepts a duty to justify it or correct its effects.

## 7. What is automation bias?

It is excessive trust in automated advice, including accepting it despite contradictory evidence or failing to check its limits.

## 8. What is human-in-the-loop?

A person meaningfully reviews evidence and can change the recommendation before final authorization. Our portfolio has no final decision until sign-off.

## 9. Why explainability?

It gives reviewers evidence about model behavior and supports challenges. It cannot prove that a decision is safe or correct.

## 10. Why use SHAP?

SHAP provides model-derived signed feature attributions with an additive reconstruction of the selected model output.

## 11. What is data provenance?

It is evidence of the origin and version of data. We store synthetic record IDs, versions, hashes and complete observation snapshots.

## 12. Why auditability?

Investigators need to reconstruct what the AI saw and recommended, who reviewed it and what was finally authorized.

## 13. What happens with incomplete data?

The pipeline imputes trained medians. This can move a score either up or down and changes review flags; it does not restore missing knowledge.

## 14. What happens with delayed data?

Old or underreported calls can understate observed need even when values are numerically valid. The scenario explicitly reduces reported calls and medical cases.

## 15. What if the model is biased?

Investigate coverage, labels, errors and policy effects across relevant groups, improve evidence and suspend unsupported use. Synthetic group differences do not prove population bias.

## 16. Why synthetic data?

It permits reproducible ethical perturbations without exposing actual citizen or patient information.

## 17. Why not real disaster data?

This project has no governed representative real data. Real use would require permissions, documentation, quality checks and external validation.

## 18. How is priority calculated?

It is the probability-weighted average of class anchors 20, 55, 77 and 95. This is a documented academic decision layer.

## 19. How are resources allocated?

A proportional largest-remainder method rounds score-weighted quotas to integers while conserving each budget.

## 20. Why the chosen model?

Logistic Regression achieved the larger validation macro F1. Selection occurred before test evaluation, and the simpler model supports transparent explanations.

## 21. How was leakage prevented?

Ground truth, labels, IDs and response time are excluded; preprocessing fits only training rows; whole incidents stay within one split.

## 22. How was the model evaluated?

Accuracy, macro precision/recall/F1, per-class reports, confusion matrices, OvR ROC-AUC and multiclass Brier score on untouched test rows.

## 23. What are the limitations?

Synthetic assumptions, rare Critical examples, uncalibrated probability, limited fairness inference, simplified allocation and local academic audit security.

## 24. Can it be deployed now?

No. It is explicitly an academic simulation with no evidence of operational safety or generalization to actual disasters.

## 25. What changes before real deployment?

Representative governed data, external/temporal validation, calibrated uncertainty, logistics validation, authentication, monitoring, backups and organizational procedures.

## 26. Who is accountable if AI is wrong?

Examine the evidence chain. Data, engineering, provision, deployment, review and final authorization may involve shared responsibility; no automatic blame rule is defensible.

## 27. What if the human reviewer is wrong?

The reviewer must justify the decision, while the organization must examine information access, training, workload and supervision.

## 28. What if both AI and human are wrong?

Investigate both failures and their interaction, including automation bias and whether safeguards were adequate. Their errors do not cancel responsibility.

## 29. How are accountability gaps reduced?

Separate pending advice from final decisions, retain provenance/explanations, require sign-off and reasons, and identify stakeholder duties.

## 30. What is model versioning?

A release identifier links a recommendation to the model/data configuration used. It enables comparison and reconstruction across releases.

## 31. Why record model versions?

A later model may behave differently on the same data. Without the earlier release, the original recommendation is harder to investigate.

## 32. Why keep recommendation history?

An override should not overwrite the AI's original advice. Both events are necessary to reconstruct influence and decision responsibility.

## 33. What is model drift?

A change in data or outcomes can make a formerly evaluated model less reliable. Monitoring requires fresh evidence; this prototype has no sustained production monitoring.

## 34. How do principles map to features?

Accountability maps to logs, transparency to snapshots and explanations, oversight to review, reliability to held-out evaluation and fairness to conditional scenario diagnostics.

## 35. Ethical accountability versus legal liability?

Ethical accountability concerns justification and duties. Legal liability depends on applicable law and facts and is not determined by this simulation.

## 36. What is the actual test performance?

Accuracy 85.0%, macro F1 0.752 and macro ROC-AUC 0.963; interpret them alongside class counts and severe-case recall.

## 37. Why is accuracy insufficient?

The Medium class dominates. High recall is only 55.7%, so an 85% accuracy headline hides missed serious cases.

## 38. What is macro F1?

Compute F1 separately for each class and average equally, so a common class does not receive more weight simply because it has more examples.

## 39. What is confidence?

The maximum predicted class probability. It is uncalibrated here and cannot be interpreted as a guaranteed probability that the allocation is safe.

## 40. Does high confidence remove review?

No. Every portfolio requires authorization. Low confidence, missing features and unreliable sensors add mandatory-review flags.

## 41. Why do prediction and score band differ?

Prediction chooses the most probable class; score averages all class anchors. An uncertain distribution can produce an expected score in another band.

## 42. What do SHAP values mean here?

For Logistic Regression they explain the selected class logit before softmax. For Random Forest they explain class probability. Units are displayed explicitly.

## 43. Are SHAP values causal?

No. They explain fitted model behavior relative to a background. Correlated inputs and background choice affect attribution.

## 44. What if SHAP fails?

The code reports a global unsigned importance fallback with its cause. It never labels global importance as signed local SHAP.

## 45. How is SHAP verified?

A test adds the base value and all contributions and compares the result with the selected model output.

## 46. Does missingness always reduce priority?

No. Imputing a median can raise a low actual value or lower a high actual value. The executed demo includes both directions.

## 47. What changed in the missing-data demo?

Four ranks changed, and one rescue team moved from Lake Colony to Outer Settlement. No newly missed severe area appeared in that twelve-area incident.

## 48. What changed with noisy sensors?

Nine ranks changed and two rescue units were reassigned in the fixed demonstration. Reliability is lowered and mandatory review is flagged.

## 49. How is underrepresentation implemented?

An alternate model retains 10% of peripheral training records; demo peripheral vulnerability and calls are also corrupted. Combined effects are reported without a causal isolation claim.

## 50. What is the fairness measure?

A descriptive miss rate conditional on true High/Critical severity within synthetic area categories. Small denominators are flagged; this is not demographic fairness proof.

## 51. What is false prioritization?

A Low/Medium simulator reference record is predicted High/Critical. It may draw attention from others, although actual harm is not measured.

## 52. What is a missed high-severity area?

An area labeled High/Critical by fixed simulated ground truth is predicted Low/Medium. Ground truth does not change when observations are corrupted.

## 53. Does the readiness score certify safety?

No. It is a seven-dimension project-defined binary checklist, with disclosed evidence and equal weighting, not an international or legal standard.

## 54. Why is readiness not 100?

Severe-case reliability criteria fail and sustained monitoring is absent. Pending human approval and corrupted observations can lower other dimensions.

## 55. Can an override exceed the budget?

No. All area edits are validated together; negative, fractional or over-budget resource counts are rejected before any review event is committed.

## 56. Why require an override reason?

It preserves the evidence motivating a changed decision and helps distinguish justified intervention from arbitrary edits.

## 57. Are the audit logs tamper-proof?

No. Triggers prevent ordinary edits and a hash chain detects local alterations, but a database administrator could rewrite everything. External anchoring would be needed.

## 58. Do synthetic aliases authenticate reviewers?

No. They prevent collecting real personal information and demonstrate role attribution. Production authentication is absent.

## 59. What prevents duplicate decisions on rerun?

A stable context ID combines inputs, scenario, model version, budget and threshold. Unique recommendation keys make identical reruns idempotent.

## 60. What is the main conclusion?

Data defects and model errors can influence scarce-resource recommendations. Meaningful oversight, clear role duties and traceable evidence support investigation, but do not guarantee fair or safe decisions.
