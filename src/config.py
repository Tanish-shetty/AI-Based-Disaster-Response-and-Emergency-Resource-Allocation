from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
DATASET_VERSION = "synthetic-flood-v1"
LABELS = ["Low", "Medium", "High", "Critical"]
ANCHORS = [20., 55., 77., 95.]
NUMERIC = ["flood_level", "rainfall_mm", "population", "population_density",
           "emergency_calls", "road_accessibility", "distance_to_hospital_km",
           "vulnerable_population", "hospital_capacity", "available_rescue_teams",
           "available_ambulances", "medical_emergencies", "infrastructure_damage",
           "evacuation_percentage", "historical_severity", "sensor_reliability"]
CATEGORICAL = ["area_category"]
FEATURES = NUMERIC + CATEGORICAL
BOUNDS = {"flood_level": (0, 6), "rainfall_mm": (0, 600),
          "population": (1, 200000), "population_density": (1, 50000),
          "emergency_calls": (0, 10000), "road_accessibility": (0, 1),
          "distance_to_hospital_km": (0, 100), "vulnerable_population": (0, 1),
          "hospital_capacity": (0, 5000), "available_rescue_teams": (0, 100),
          "available_ambulances": (0, 200), "medical_emergencies": (0, 10000),
          "infrastructure_damage": (0, 1), "evacuation_percentage": (0, 1),
          "historical_severity": (0, 1), "sensor_reliability": (0, 1)}
