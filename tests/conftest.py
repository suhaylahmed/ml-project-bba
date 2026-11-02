import json
from pathlib import Path
import sys

import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from complaints.data import file_hash, write_sample_data
from complaints.inference import load_bundle
from complaints.training import train_project


@pytest.fixture(scope="session")
def trained(tmp_path_factory):
    root = tmp_path_factory.mktemp("trained_project")
    path = write_sample_data(root, n=300, seed=42)
    data = pd.read_csv(path)
    # This word exists only outside training. Its absence from the vocabulary
    # proves that the final preprocessing did not see held-out text.
    _, held_out = train_test_split(range(len(data)), test_size=0.4,
                                   stratify=data.escalation_required, random_state=42)
    data.loc[held_out, "complaint_text"] = data.loc[held_out, "complaint_text"].fillna("") + " nevertrainmarker"
    data.to_csv(path, index=False)
    manifest_path = root / "data" / "dataset_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["sha256"] = file_hash(path)
    manifest_path.write_text(json.dumps(manifest))
    report = train_project(root, path)
    return root, data, report, load_bundle(root)


@pytest.fixture
def ticket():
    return pd.DataFrame([{
        "product": "Laptop", "ticket_type": "Technical issue", "subject": "Device not working",
        "channel": "Email", "response_hours": 3.0, "previous_contacts": 1,
        "complaint_text": "The device keeps restarting. Please help me resolve this soon.",
    }])
