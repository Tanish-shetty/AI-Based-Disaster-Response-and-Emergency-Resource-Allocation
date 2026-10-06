# 15-slide presentation outline

## Slide 1: Title

- Algorithmic Accountability: A Case Study on AI-Based Disaster Response and Emergency Resource Allocation
- Ethics in Artificial Intelligence & Data Science
- Academic simulation, no real citizen data

**Visual:** Title and data-to-audit chain

## Slide 2: Motivation

- Emergency help is scarce
- Recommendations can influence consequential choices
- Consequences require reasons and evidence

**Visual:** Four resource-budget cards

## Slide 3: Problem Statement

- Who is answerable when an AI-assisted allocation is wrong?
- Data, engineering, deployment and human decisions interact

**Visual:** Six stakeholder nodes

## Slide 4: Urban Flood Case

- Twelve fictional areas
- Five rescue teams and ten ambulances
- Riverside has highest baseline score

**Visual:** reports/complete_data_allocation.csv table

## Slide 5: Central Ethical Question

- Advice passes through human review
- A responsibility gap can obscure who did what
- The project does not determine legal liability

**Visual:** Recommendation → review → final decision

## Slide 6: Ethical Issues

- Automation bias and inadequate oversight
- Incomplete or delayed observations
- Traceability, potential harm and distributed responsibility

**Visual:** Failure chain

## Slide 7: Ethical Principles

- Accountability → audit
- Transparency → explanations
- Fairness → conditional group checks
- Oversight → explicit authorization

**Visual:** Principles mapping table

## Slide 8: Proposed System

- Validation → model → score → allocation
- Explanation → review → immutable events
- Five real data/model perturbations

**Visual:** Architecture Mermaid diagram

## Slide 9: ML Methodology

- 3,000 records; incident-disjoint 1,800/600/600 split
- Logistic Regression vs Random Forest
- Select by validation macro F1 before test

**Visual:** reports/figures/model_comparison.png

## Slide 10: Explainable AI

- Actual SHAP LinearExplainer values
- Signed predicted-class logit contributions
- Explanation is not proof of correctness

**Visual:** reports/figures/riverside_shap.png

## Slide 11: Accountability Framework

- Twelve safeguards from provenance to responsibility assignment
- Input snapshots, model/data versions and review events
- Shared stakeholder matrix

**Visual:** Framework diagram and audit record

## Slide 12: Ethical Simulation

- Missing vulnerability changes four ranks and one rescue unit
- Noisy sensors change nine ranks and two rescue units
- No new missed severe areas in the small demo: report honestly

**Visual:** reports/figures/missing_vulnerable_population_data.png

## Slide 13: Measured Results

- Winner: Logistic Regression
- Test accuracy 85.0%, macro F1 0.752
- High recall 55.7%; only seven Critical test records
- Aggregate accuracy hides missed severe need

**Visual:** Confusion matrix and scenario CSV

## Slide 14: Recommendations

- Validate data freshness and coverage
- Require meaningful review and record reasons
- Monitor severe-case recall and preserve provenance
- Readiness score is project-defined

**Visual:** Recommendations and readiness checklist

## Slide 15: Conclusion

- AI recommendations need human and organizational accountability
- Evidence supports investigation of shared duties
- Synthetic results cannot justify real deployment

**Visual:** Final data-to-accountability chain
