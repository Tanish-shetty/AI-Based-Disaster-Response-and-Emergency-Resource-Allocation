"""Generate observations separately from a noisy latent severity, never real records."""
import numpy as np
import pandas as pd
from .config import SEED, LABELS

AREAS = ["Central Market", "Riverside", "Old Town", "East Gardens", "Hill Junction",
         "South Ward", "North Estate", "Canal Quarter", "West Park", "Lake Colony",
         "Industrial Ward", "Outer Settlement"]

def generate_dataset(n: int = 3000, seed: int = SEED, missing: bool = True) -> pd.DataFrame:
    if n < 2000:
        raise ValueError("Training dataset must have at least 2,000 records.")
    rng = np.random.default_rng(seed)
    area = np.arange(n) % 12
    category = np.array(["Central", "Peripheral", "Central", "Residential", "Residential",
                         "Peripheral", "Residential", "Peripheral", "Residential",
                         "Peripheral", "Central", "Peripheral"])[area]
    storm = rng.uniform(.15, 1, int(np.ceil(n / 12)))
    flood = np.clip(storm[np.arange(n)//12] * 3.4 + rng.normal(.5, .8, n), .05, 5.8)
    population = rng.integers(2500, 65000, n)
    vulnerability = np.clip(rng.beta(2, 5, n) + (category == "Peripheral")*.12, .04, .8)
    road = np.clip(1 - flood*.14 - (category == "Peripheral")*.12 + rng.normal(0, .12, n), .02, 1)
    damage = np.clip(flood/6 + rng.normal(0, .12, n), 0, 1)
    evacuation = np.clip(rng.beta(2, 4, n) + .08*flood, 0, .95)
    calls = rng.poisson(np.maximum(2, population/450 * (.3 + flood/3)))
    medical = rng.poisson(np.maximum(1, calls * (.12 + vulnerability*.4)))
    distance = rng.uniform(1, 22, n) + (category == "Peripheral")*9
    capacity = rng.integers(40, 450, n)
    # Unobserved rescue need has multiple drivers plus irreducible uncertainty.
    latent = (8 + 9*flood + 17*vulnerability + 10*(1-road) + 9*damage
              + 6*np.log1p(population/10000) + 9*np.minimum(medical/100, 1)
              + .12*distance - 8*evacuation + rng.normal(0, 5, n))
    severity = np.clip(latent, 0, 100)
    frame = pd.DataFrame({
        "incident_id": [f"SYN-{i//12:04d}" for i in range(n)],
        "area_id": [f"AREA-{i+1:02d}" for i in area],
        "area_name": np.array(AREAS)[area], "area_category": category,
        "input_record_identifier": [f"REC-{i:05d}" for i in range(n)],
        "flood_level": flood, "rainfall_mm": np.clip(flood*65 + rng.normal(40, 30, n), 0, 600),
        "population": population, "population_density": rng.integers(500, 20000, n),
        "emergency_calls": calls, "road_accessibility": road,
        "distance_to_hospital_km": distance, "vulnerable_population": vulnerability,
        "hospital_capacity": capacity, "available_rescue_teams": rng.integers(0, 4, n),
        "available_ambulances": rng.integers(0, 8, n), "medical_emergencies": medical,
        "infrastructure_damage": damage, "evacuation_percentage": evacuation,
        "historical_severity": rng.uniform(.1, .9, n), "sensor_reliability": rng.uniform(.65, 1, n),
        "response_time_minutes": np.clip(10 + distance*2 + 40*(1-road) + rng.normal(0, 5, n), 5, 150),
        "true_severity": severity,
        "priority_label": np.array(LABELS)[np.digitize(severity, [40, 70, 85])]})
    if missing:
        for feature in ["vulnerable_population", "emergency_calls", "hospital_capacity"]:
            frame.loc[rng.random(n) < .025, feature] = np.nan
    return frame

def demo_incident(seed: int = 2026) -> pd.DataFrame:
    """Unseen complete incident from the same generator, separate seed, no tailored predictions."""
    return generate_dataset(2004, seed, missing=False).iloc[:12].copy().assign(incident_id="DEMO-FLOOD-01")
