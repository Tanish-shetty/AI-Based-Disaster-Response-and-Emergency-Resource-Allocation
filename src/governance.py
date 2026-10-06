import pandas as pd

FRAMEWORK = ["Data Provenance", "Data Quality Validation", "Model Documentation", "Model Versioning",
             "Explainable Predictions", "Confidence Thresholds", "Human Review", "Human Override",
             "Decision Logging", "Post-Incident Auditing", "Continuous Monitoring", "Responsibility Assignment"]
MATRIX = pd.DataFrame([
    ("Missing or delayed data", "Data Provider + Disaster Management Organization", "Data / organizational", "Provenance, freshness checks, field confirmation"),
    ("Poor model design", "AI Developer + AI/System Provider", "Technical / ethical", "Leakage checks, evaluation, limitations disclosure"),
    ("Insufficient scenario validation", "AI Developer + Disaster Management Organization", "Technical / organizational", "Pre-deployment scenario and group tests"),
    ("Unreliable deployment", "AI/System Provider + Disaster Management Organization", "Organizational / technical", "Safe defaults, access controls, incident response"),
    ("Blindly accepting recommendations", "Human Emergency Coordinator + Disaster Management Organization", "Operational / ethical", "Training, evidence review, justified sign-off"),
    ("Inappropriate final allocation", "Final Decision Authority + Human Emergency Coordinator", "Decision / ethical", "Budget checks, local evidence, independent review"),
    ("Missing audit records", "AI/System Provider + Disaster Management Organization", "Governance / technical", "Append-only history, backups, integrity checks"),
    ("Model or data drift", "AI Developer + Disaster Management Organization", "Monitoring / organizational", "Periodic validation, drift alerts, suspend use")
], columns=["Failure/Event", "Stakeholder(s)", "Type of Responsibility", "Preventive Measure"])
PRINCIPLES = pd.DataFrame([
    ("Accountability", "Versioned recommendations and named synthetic sign-off"),
    ("Transparency", "Input snapshots, scoring formula and documented limitations"),
    ("Human Oversight", "All final portfolios require coordinator and authority confirmation"),
    ("Fairness", "Synthetic group miss rates and data-quality scenario comparisons"),
    ("Data Responsibility", "Schema/range validation, provenance and missing-data flags"),
    ("Reliability", "Incident-disjoint validation/test metrics and automated tests"),
    ("Explainability", "Signed local SHAP contributions with output units"),
    ("Auditability", "Linked recommendation/review events, JSON export and hash checking")
], columns=["Ethical principle", "System feature"])
STAKEHOLDERS = {
    "Data Provider": "Document collection coverage, sensor reliability, timeliness and missing values; correct reported errors.",
    "AI Developer": "Choose defensible targets and models, prevent leakage, evaluate uncertainty and group limitations, version releases.",
    "AI/System Provider": "Deliver reliable interfaces, preserve model provenance and audit records, disclose unsupported uses.",
    "Disaster Management Organization": "Validate suitability, resource policies and data contracts; train reviewers and monitor incidents.",
    "Human Emergency Coordinator": "Inspect recommendations and local evidence, recognize automation bias and justify overrides.",
    "Final Decision Authority": "Authorize the complete constrained plan and remain answerable for its operational justification."}
