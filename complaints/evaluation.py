"""Small metric functions; threshold tuning never touches the test labels."""

import math

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss, confusion_matrix,
    f1_score, fbeta_score, precision_score, recall_score, roc_auc_score,
)


def metrics(y, scores, threshold: float) -> dict:
    prediction = np.asarray(scores) >= threshold
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    return {
        "accuracy": float(accuracy_score(y, prediction)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "f1": float(f1_score(y, prediction, zero_division=0)),
        "f2": float(fbeta_score(y, prediction, beta=2, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, scores)),
        "average_precision": float(average_precision_score(y, scores)),
        "brier_score": float(brier_score_loss(y, scores)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "rows": int(len(y)), "positives": int(np.sum(y)),
        "flagged": int(prediction.sum()), "threshold": float(threshold),
    }


def choose_threshold(y, scores, min_recall: float = 0.85) -> tuple[float, pd.DataFrame]:
    """Maximize validation F2 among cutoffs meeting the desired validation recall.

    If none meet that goal, use the highest validation F2 and report the miss.
    F2 gives recall four times the weight of precision in its harmonic mean.
    """
    rows = [metrics(y, scores, float(t)) for t in np.linspace(0.05, 0.95, 91)]
    table = pd.DataFrame(rows)
    eligible = table[table.recall >= min_recall]
    pool = eligible if not eligible.empty else table
    best = pool.sort_values(["f2", "precision", "threshold"], ascending=[False, False, False]).iloc[0]
    return float(best.threshold), table


def wilson_interval(successes: int, total: int) -> list[float]:
    """Approximate 95% interval for a binomial rate on a fixed holdout."""
    if not total:
        return [0.0, 1.0]
    z = 1.96
    p = successes / total
    center = (p + z * z / (2 * total)) / (1 + z * z / total)
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return [max(0.0, center - radius), min(1.0, center + radius)]
