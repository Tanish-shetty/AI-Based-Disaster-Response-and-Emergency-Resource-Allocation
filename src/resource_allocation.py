"""Integer proportional allocation by largest remainders, never exceeds budget."""
import numbers
import numpy as np

DEFAULT_BUDGET = {"rescue_teams": 5, "ambulances": 10, "medical_supplies": 20, "food_shelter_units": 30}

def allocate_resources(predictions, budget=None):
    budget = DEFAULT_BUDGET if budget is None else budget
    if set(budget) != set(DEFAULT_BUDGET):
        raise ValueError("Budget must specify every supported resource.")
    if any(isinstance(v, bool) or not isinstance(v, numbers.Integral) or v < 0 for v in budget.values()):
        raise ValueError("Resource totals must be nonnegative integers.")
    result = predictions.sort_values(["rank", "area_id"]).copy()
    if result.area_id.duplicated().any():
        raise ValueError("Allocation expects one record per area in one incident.")
    scores = result.priority_score.to_numpy(float)
    if not np.isfinite(scores).all() or (scores < 0).any():
        raise ValueError("Invalid allocation scores.")
    weights = scores/scores.sum() if scores.sum() else np.full(len(scores), 1/max(1,len(scores)))
    for resource, total in budget.items():
        quota = weights*total
        assigned = np.floor(quota).astype(int)
        remaining = total-int(assigned.sum())
        if len(assigned):
            order = np.argsort(-(quota-assigned), kind="stable")
            assigned[order[:remaining]] += 1
        result[resource] = assigned
    return result
