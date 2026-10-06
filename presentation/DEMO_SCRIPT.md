# Six-minute demonstration script

Before the presentation, use the default budget and threshold. If the missing-data portfolio was already finalized in a rehearsal, choose a new budget or threshold to create a distinct context; preserve the earlier journal. Never pretend that prior decisions are new.

## 1. Open application (0:00–0:20)

**Action:** Run python -m streamlit run app.py, then open Overview.

**Say:** “This academic simulation studies who is answerable for an AI-assisted decision. It does not dispatch real emergency services.”

## 2. Explain case (0:20–0:45)

**Action:** Point to the case description and budgets.

**Say:** “A flood affects twelve fictional areas. We have only five rescue teams. Our ethical problem is the decision chain, not predicting a flood.”

## 3. Show disaster areas (0:45–1:05)

**Action:** Open Disaster Scenario with Complete Data selected.

**Say:** “Flood depth, vulnerability and road access describe simulated need. True severity is hidden from the model and used only to evaluate the experiment.”

## 4. Show AI ranking (1:05–1:25)

**Action:** Open AI Priority Analysis.

**Say:** “The model produces class probabilities. We turn these into a transparent expected-anchor score. Riverside is highest in this baseline.”

## 5. Show resource allocation (1:25–1:45)

**Action:** Point to the resource columns.

**Say:** “Integer allocations follow a proportional largest-remainder rule. Totals exactly match the limited budget, but the policy does not guarantee sufficient help.”

## 6. Select one area (1:45–2:00)

**Action:** Open Explainable AI and select Riverside.

**Say:** “We can examine the particular observation that produced this recommendation.”

## 7. Show SHAP explanation (2:00–2:25)

**Action:** Point to signed contributions and reconstructed logit.

**Say:** “These are actual model contributions. Positive values support the predicted class and negative values oppose it. They are logits, not priority points, and do not prove correctness.”

## 8. Simulate missing data (2:25–2:45)

**Action:** Open Ethical Risk Simulator and choose Missing Vulnerable Population Data in the sidebar.

**Say:** “This removes vulnerability observations for peripheral areas and reruns the fitted pipeline. It does not change a caption or invent a result.”

## 9. Show ranking change (2:45–3:10)

**Action:** Inspect Lake Colony and Outer Settlement in the comparison table.

**Say:** “Lake Colony drops from fifth to sixth and loses one rescue team; Outer Settlement rises from seventh to fourth and gains it. A small score change can move an indivisible resource.”

## 10. Explain ethical consequence (3:10–3:35)

**Action:** Point to missing cells, confidence and mandatory-review flags.

**Say:** “Missing observations can transfer assistance without changing severity classes. This is potential harm, not measured casualties. Data providers, developers and the organization have different but overlapping duties.”

## 11. Open human review (3:35–3:55)

**Action:** Open Human Review while the missing-data scenario stays active.

**Say:** “The recommendation is pending. The coordinator and final authority must inspect evidence. A high model probability cannot replace authorization.”

## 12. Override AI (3:55–4:35)

**Action:** Transfer one rescue team from Outer Settlement back to Lake Colony, select synthetic aliases, enter 'Simulated field report confirms Lake Colony needs rescue support.', check review confirmation and authorize.

**Say:** “I retain the original AI recommendation, conserve the five-team budget, and give a reason for this simulated correction. Both changed areas receive override events.”

## 13. Show audit log (4:35–5:00)

**Action:** Open Accountability Audit and inspect an overridden area's record; optionally export JSON.

**Say:** “This records the data snapshot, versions, prediction, explanation, reviewer, reason, final resources and authority. The original recommendation remains available for investigation.”

## 14. Show accountability matrix (5:00–5:30)

**Action:** Open Stakeholder Accountability.

**Say:** “We analyze shared responsibility rather than automatically blaming a developer or coordinator. Ethical accountability and organizational duties are different from legal liability.”

## 15. Show recommendations (5:30–6:15)

**Action:** Briefly show Results & Findings, then Recommendations.

**Say:** “Test accuracy was 85.0%, but High recall was only 55.7%. The safeguards are data governance, meaningful oversight, explanations, logs and monitoring. Synthetic success cannot authorize real deployment.”

If live training is unnecessary, use the supplied fitted artifacts. If a professor asks whether all scenarios worsen outcomes, show the actual zero-miss demo results and explain the held-out severe-class errors. Never claim a guaranteed score drop or measured injury.
