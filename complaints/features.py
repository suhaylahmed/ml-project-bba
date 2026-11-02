"""Input contract shared by training, the dashboard, and CSV prediction."""

import numpy as np
import pandas as pd

CATEGORIES = {
    "product": ["Laptop", "Phone", "Headphones", "Smartwatch", "Tablet"],
    "ticket_type": ["Technical issue", "Billing inquiry", "Refund request", "General inquiry"],
    "subject": ["Device not working", "Payment problem", "Delivery delay", "Account access", "Product question"],
    "channel": ["Email", "Chat", "Phone", "Social media"],
}
CATEGORICAL = list(CATEGORIES)
NUMERIC = ["response_hours", "previous_contacts"]
TEXT = "complaint_text"
FEATURES = CATEGORICAL + NUMERIC + [TEXT]
TARGET = "escalation_required"
MAX_BATCH_ROWS = 10000


def prepare_features(data: pd.DataFrame) -> pd.DataFrame:
    """Select safe inputs; validate bad values; leave missing cells for imputation.

    response_hours is elapsed time, never the clock hour of a timestamp.
    Either supply it directly or supply created_at and first_response_at.
    """
    if data.empty:
        raise ValueError("The file has no tickets. Add at least one data row.")
    if data.columns.duplicated().any():
        raise ValueError("Column names must be unique.")
    frame = data.copy().reset_index(drop=True)
    has_dates = {"created_at", "first_response_at"}.issubset(frame.columns)
    if "response_hours" not in frame and has_dates:
        frame["response_hours"] = np.nan
    missing = sorted(set(FEATURES) - set(frame.columns))
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    for column, maximum in [("response_hours", 720), ("previous_contacts", 50)]:
        original = frame[column].replace(r"^\s*$", np.nan, regex=True)
        values = pd.to_numeric(original, errors="coerce")
        if (original.notna() & values.isna()).any():
            raise ValueError(f"{column} must contain numbers or empty cells.")
        if ((values < 0) | (values > maximum) | np.isinf(values)).any():
            raise ValueError(f"{column} must be between 0 and {maximum}.")
        if column == "previous_contacts" and ((values.dropna() % 1) != 0).any():
            raise ValueError("previous_contacts must be a whole number.")
        frame[column] = values.astype(float)

    if has_dates:
        dates = []
        for column in ["created_at", "first_response_at"]:
            original = frame[column].replace(r"^\s*$", np.nan, regex=True)
            parsed = pd.to_datetime(original, errors="coerce", utc=True, format="ISO8601")
            if (original.notna() & parsed.isna()).any():
                raise ValueError(f"Invalid {column}. Use ISO dates such as 2025-06-01T09:00:00Z.")
            dates.append(parsed)
        elapsed = (dates[1] - dates[0]).dt.total_seconds() / 3600
        if ((elapsed < 0) | (elapsed > 720)).any():
            raise ValueError("First response must be 0 to 720 hours after ticket creation.")
        both = frame.response_hours.notna() & elapsed.notna()
        if ((frame.loc[both, "response_hours"] - elapsed[both]).abs() > 0.02).any():
            raise ValueError("response_hours disagrees with the supplied timestamps.")
        frame["response_hours"] = frame.response_hours.fillna(elapsed)

    for column in CATEGORICAL:
        frame[column] = frame[column].map(
            lambda value: str(value).strip() if pd.notna(value) and str(value).strip() else np.nan
        )
        if frame[column].dropna().str.len().gt(100).any():
            raise ValueError(f"{column} values must have at most 100 characters.")
    text = frame[TEXT].fillna("").astype(str).str.strip()
    if text.str.len().gt(5000).any():
        raise ValueError("Each complaint_text must have at most 5,000 characters.")
    frame[TEXT] = text.replace("", "no description provided")
    return frame[FEATURES]


def get_target(data: pd.DataFrame) -> pd.Series:
    """Validate 0/1 labels and, when present, their agreement with priority."""
    priority_target = None
    if "priority" in data:
        priorities = data.priority.astype(str).str.strip().str.lower()
        if not priorities.isin(["low", "medium", "high", "critical"]).all():
            raise ValueError("priority must be Low, Medium, High, or Critical.")
        priority_target = priorities.isin(["high", "critical"]).astype(int)
    if TARGET not in data:
        if priority_target is None:
            raise ValueError("Training needs escalation_required (0/1) or priority.")
        return priority_target.rename(TARGET)
    labels = pd.to_numeric(data[TARGET], errors="coerce")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError("escalation_required must be 0 or 1 for every training row.")
    labels = labels.astype(int)
    if priority_target is not None and not labels.equals(priority_target.rename(TARGET)):
        raise ValueError("Labels disagree: High/Critical priority must map to 1; Low/Medium to 0.")
    return labels


def input_notes(data: pd.DataFrame, known_categories: dict | None = None) -> list[str]:
    """Report missing inputs and novel categories without rejecting valid new values."""
    features = prepare_features(data)
    notes = []
    count = int(features[CATEGORICAL + NUMERIC].isna().sum().sum())
    if count:
        noun = "cell" if count == 1 else "cells"
        notes.append(f"{count} empty input {noun} will use training-set imputations.")
    for column, known in (known_categories or CATEGORIES).items():
        unknown = sorted(set(features[column].dropna()) - set(known))
        if unknown:
            notes.append(f"Unfamiliar {column}: {', '.join(unknown[:5])}. The demo may generalize poorly.")
    return notes
