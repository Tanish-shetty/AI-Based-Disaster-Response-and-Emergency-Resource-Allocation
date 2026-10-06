import numpy as np
from .config import LABELS, ANCHORS

def priority_scores(probabilities, classes) -> np.ndarray:
    p = np.asarray(probabilities, dtype=float)
    if p.ndim != 2 or p.shape[1] != len(classes) or not np.isfinite(p).all() or (p < 0).any() or not np.allclose(p.sum(axis=1), 1):
        raise ValueError("Invalid class probabilities.")
    return p @ np.array([ANCHORS[LABELS.index(c)] for c in classes])

def score_band(score: float) -> str:
    if not np.isfinite(score) or not 0 <= score <= 100:
        raise ValueError("Score must be in [0, 100].")
    return LABELS[np.digitize(score, [40, 70, 85])]
