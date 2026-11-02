"""One prediction path used by both app.py and predict.py."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

from complaints.features import CATEGORICAL, FEATURES, MAX_BATCH_ROWS, prepare_features


def load_bundle(root: Path) -> dict:
    """Load only this project's trusted local artifact, with version checks."""
    path = root / "artifacts" / "model.joblib"
    if not path.exists():
        raise ValueError("No trained model. Run python train.py first.")
    meta = json.loads((root / "artifacts" / "metadata.json").read_text(encoding="utf-8"))
    if meta["versions"]["scikit-learn"] != sklearn.__version__:
        raise ValueError("The scikit-learn version changed. Run python train.py to rebuild the model.")
    bundle = joblib.load(path)
    if bundle.get("features") != FEATURES or bundle.get("schema_version") != 1:
        raise ValueError("Model input schema changed. Run python train.py to rebuild the model.")
    return bundle


def score_tickets(data: pd.DataFrame, bundle: dict, threshold: float | None = None) -> pd.DataFrame:
    if len(data) > MAX_BATCH_ROWS:
        raise ValueError(f"Use at most {MAX_BATCH_ROWS:,} tickets per batch.")
    cutoff = float(bundle["threshold"] if threshold is None else threshold)
    if not np.isfinite(cutoff) or not 0 <= cutoff <= 1:
        raise ValueError("Threshold must be a finite number between 0 and 1.")
    features = prepare_features(data)
    probability = bundle["pipeline"].predict_proba(features)[:, 1]
    result = data.reset_index(drop=True).copy()
    result["escalation_score"] = probability
    result["decision_threshold"] = cutoff
    result["predicted_escalation"] = (probability >= cutoff).astype(int)
    result["recommendation"] = np.where(probability >= cutoff, "Escalate for review", "Standard support review")
    result["missing_input_cells"] = features[CATEGORICAL + ["response_hours", "previous_contacts"]].isna().sum(axis=1)
    return result


def safe_csv(data: pd.DataFrame) -> str:
    """Keep free text from becoming a spreadsheet formula in exported CSV files."""
    result = data.copy()
    for column in result.select_dtypes(include=["object", "string"]):
        result[column] = result[column].map(
            lambda value: "'" + value if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")) else value
        )
    return result.to_csv(index=False)
