# Synthetic dataset card

The dataset has 3,000 synthetic area-incident records, 250 incidents and twelve recurring area identifiers. NumPy seed 42 fixes generation; the separate complete demo uses seed 2026. No patient, citizen or actual disaster data is used. Columns include flood depth (m), rainfall (mm), population, density (people/km²), calls, accessibility (0–1), distance (km), vulnerable-population fraction (0–1), hospital beds, local resources, medical emergencies, infrastructure damage (0–1), evacuation fraction, historical severity, reliability and diagnostic response time. `true_severity` is a noisy latent simulator value, and `priority_label` bins it at 40, 70 and 85. These thresholds are academic assumptions, not clinical standards.

Flood intensity, vulnerable population, response difficulty and damage generally increase latent need; evacuation generally reduces it. Population and medical demand contribute, and Gaussian noise represents omitted conditions. Observations are correlated; no causal inference is claimed. Approximately 2.5% missingness is introduced independently in three training-data fields. The complete demonstration omits that random missingness to establish a clean comparison. Ground-truth severity is never recomputed after observational corruption.

Required features are explicitly allowlisted and checked for finite values, valid categories and physical ranges. NaN is allowed and imputed inside the fitted pipeline. Numeric medians and StandardScaler parameters come only from the 1,800 training rows; categorical values use most-frequent imputation and OneHotEncoder. Validation and test each contain 600 rows. GroupShuffleSplit keeps every incident wholly inside one split, preventing same-incident leakage; recurring area types remain across splits, so the evaluation is not an unseen-city test. IDs, true severity, labels and response time are excluded from model inputs. Label-driven selection or post-event outcomes are never input features.

Dataset version: synthetic-flood-v1

SHA-256: `5f86bbbf89be4e22f59792e266fbc5463479683d8c9327ead9b214d1303cbc9e`

Class counts: {"Medium": 1914, "Low": 767, "High": 270, "Critical": 49}

Variable bounds and allowlisted features are authoritative in src/config.py. Incident IDs identify synthetic storm groups; area names are fictional location descriptors. The unobserved outcome formula is in src/data_generation.py and is a pedagogical assumption. No geographic or demographic representativeness is claimed.
