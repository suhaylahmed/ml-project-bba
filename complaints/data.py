"""Reproducible fictional tickets. No customer data or external downloads."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from complaints.features import CATEGORIES, FEATURES
from complaints.demo import DEMO_TICKETS

ISSUES = {
    "Device not working": ["the device keeps restarting", "the screen stops responding", "the battery will not charge"],
    "Payment problem": ["a payment appears twice", "the invoice amount looks wrong", "my payment has not been credited"],
    "Delivery delay": ["the delivery date has passed", "tracking has stopped updating", "the package has not arrived"],
    "Account access": ["I cannot sign in", "my account is locked", "the reset link does not work"],
    "Product question": ["I need help with setup", "I need to understand the warranty", "I have a question about compatibility"],
}
TONES = [
    ["Please explain the next step when you can.", "I can wait for a regular update.", "A short explanation would be helpful."],
    ["This is inconvenient and I would like an update.", "I am disappointed with the experience.", "Please help me resolve this soon."],
    ["This is disrupting my work and needs prompt attention.", "I have tried the suggested steps without success.", "I am frustrated that the problem is still unresolved."],
    ["I cannot continue my work and need help urgently.", "This is causing a serious disruption to my business.", "Repeated attempts have failed and I need immediate assistance."],
]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_tickets(n: int = 3000, seed: int = 42) -> pd.DataFrame:
    """Draw labels probabilistically, so similar tickets can have different outcomes.

    Latent severity affects wording, wait and contacts. Random unobserved factors
    and a Bernoulli draw create overlap. Priority is assigned AFTER that draw.
    Do not use priority, satisfaction, or lifecycle fields as model inputs.
    """
    if n < 100:
        raise ValueError("Generate at least 100 tickets.")
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        severity = int(rng.choice(4, p=[0.34, 0.30, 0.24, 0.12]))
        product = rng.choice(CATEGORIES["product"])
        kind = rng.choice(CATEGORIES["ticket_type"])
        subject = rng.choice(CATEGORIES["subject"])
        channel = rng.choice(CATEGORIES["channel"], p=[0.40, 0.30, 0.20, 0.10])
        wait = round(float(min(rng.gamma(1.6, 4 + severity * 2.8), 96)), 2)
        contacts = int(min(rng.poisson(0.5 + severity * 0.7), 12))
        complaint = f"My {product.lower()} request concerns this issue: {rng.choice(ISSUES[subject])}. {rng.choice(TONES[severity])}"
        complaint += " " + rng.choice(["Please contact me by email.", "I can provide more details.", "Thank you for checking.", "Please review the ticket history."])
        logit = (-3.0 + 0.85 * severity + 0.04 * min(wait, 60) + 0.38 * contacts
                 + 0.30 * (kind == "Refund request") + 0.25 * (subject == "Payment problem")
                 + 0.20 * (channel == "Social media") + rng.normal(0, 0.65))
        label = int(rng.random() < 1 / (1 + np.exp(-logit)))
        priority = rng.choice(["High", "Critical"], p=[0.8, 0.2]) if label else rng.choice(["Low", "Medium"])
        created = pd.Timestamp("2025-01-01", tz="UTC") + pd.Timedelta(minutes=int(rng.integers(0, 365 * 24 * 60)))
        responded = created + pd.Timedelta(hours=wait)
        status = rng.choice(["Open", "Pending", "Closed"], p=[0.3, 0.3, 0.4])
        rows.append({
            "ticket_id": f"SYN-{seed}-{i + 1:05d}", "created_at": created.isoformat(),
            "first_response_at": responded.isoformat(), "product": product,
            "ticket_type": kind, "subject": subject, "channel": channel,
            "complaint_text": complaint, "response_hours": wait,
            "previous_contacts": contacts, "priority": priority,
            "escalation_required": label, "customer_age": int(rng.integers(18, 81)),
            "customer_gender": rng.choice(["Female", "Male", "Non-binary", "Undisclosed"]),
            "final_status": status,
            "satisfaction_rating": int(np.clip(round(rng.normal(3.8 - 1.4 * label, 1)), 1, 5)) if status == "Closed" else np.nan,
            "data_source": "synthetic",
        })
    frame = pd.DataFrame(rows)
    for column, fraction in [("previous_contacts", 0.025), ("product", 0.01), ("complaint_text", 0.01)]:
        frame.loc[rng.random(n) < fraction, column] = np.nan
    missing_wait = rng.random(n) < 0.02
    frame.loc[missing_wait, ["response_hours", "first_response_at"]] = np.nan
    return frame


def write_sample_data(root: Path, n: int = 3000, seed: int = 42) -> Path:
    folder = root / "data"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "complaints.csv"
    frame = generate_tickets(n, seed)
    frame.to_csv(path, index=False)
    frame[["ticket_id"] + FEATURES + ["priority", "escalation_required"]].head(12).to_csv(
        folder / "teacher_preview.csv", index=False)
    pd.DataFrame.from_dict(DEMO_TICKETS, orient="index").rename_axis("scenario").reset_index().to_csv(
        folder / "demo_scenarios.csv", index=False)
    batch = generate_tickets(100, seed + 100).head(20)
    batch[["ticket_id"] + FEATURES].to_csv(folder / "batch_examples.csv", index=False)
    pd.DataFrame(columns=["ticket_id"] + FEATURES).to_csv(folder / "batch_template.csv", index=False)
    manifest = {
        "kind": "synthetic", "rows": n, "seed": seed, "sha256": file_hash(path),
        "generator": "complaints/data.py", "contains_real_customers": False,
        "target": "High/Critical priority proxy, not an observed future escalation",
        "label_generation": "Noisy logistic probability followed by a Bernoulli draw; priority assigned afterwards",
    }
    (folder / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path
