import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from complaints.data import generate_tickets
from complaints.evaluation import metrics
from complaints.features import FEATURES, get_target, prepare_features
from complaints.inference import safe_csv, score_tickets

ROOT = Path(__file__).resolve().parents[1]


def test_midnight_elapsed_time(ticket):
    ticket = ticket.drop(columns="response_hours")
    ticket["created_at"] = "2025-06-01T23:00:00Z"
    ticket["first_response_at"] = "2025-06-02T02:00:00Z"
    assert prepare_features(ticket).response_hours.iloc[0] == 3


def test_multiple_days_are_not_clock_hours(ticket):
    ticket = ticket.drop(columns="response_hours")
    ticket["created_at"] = "2025-06-01T23:00:00Z"
    ticket["first_response_at"] = "2025-06-03T02:30:00Z"
    assert prepare_features(ticket).response_hours.iloc[0] == 27.5


@pytest.mark.parametrize("column,value", [
    ("response_hours", -1), ("response_hours", 721), ("response_hours", "tomorrow"),
    ("response_hours", np.inf), ("previous_contacts", 1.5), ("previous_contacts", -1),
])
def test_invalid_numeric_inputs_fail_clearly(ticket, column, value):
    ticket[column] = value
    with pytest.raises(ValueError, match=column):
        prepare_features(ticket)


def test_conflicting_timestamps_fail(ticket):
    ticket["created_at"] = "2025-06-01T23:00:00Z"
    ticket["first_response_at"] = "2025-06-02T04:00:00Z"
    with pytest.raises(ValueError, match="disagrees"):
        prepare_features(ticket)


def test_missing_columns_and_empty_files_fail(ticket):
    with pytest.raises(ValueError, match="Missing columns"):
        prepare_features(ticket.drop(columns="product"))
    with pytest.raises(ValueError, match="no tickets"):
        prepare_features(ticket.head(0))


def test_labels_cannot_contradict_priority():
    with pytest.raises(ValueError, match="disagree"):
        get_target(pd.DataFrame({"priority": ["High", "Low"], "escalation_required": [0, 1]}))


def test_generator_is_repeatable_and_labels_overlap():
    data = generate_tickets(300, 8)
    pd.testing.assert_frame_equal(data, generate_tickets(300, 8))
    assert data.escalation_required.nunique() == 2
    assert ((data.priority.isin(["High", "Critical"]).astype(int)) == data.escalation_required).all()


def test_partitions_do_not_overlap_and_cover_every_ticket(trained):
    root, data, _, _ = trained
    manifest = pd.read_csv(root / "reports" / "split_manifest.csv")
    assert manifest.ticket_id.is_unique
    assert set(manifest.ticket_id) == set(data.ticket_id)
    assert manifest.split.value_counts().to_dict() == {"train": 180, "validation": 60, "test": 60}


def test_preprocessing_has_not_seen_held_out_text(trained):
    _, _, _, bundle = trained
    vocabulary = bundle["pipeline"].named_steps["inputs"].named_transformers_["text"].vocabulary_
    assert "nevertrainmarker" not in vocabulary


def test_fitted_numeric_medians_use_training_rows(trained):
    root, data, _, bundle = trained
    ids = pd.read_csv(root / "reports" / "split_manifest.csv")
    train_ids = set(ids.loc[ids.split == "train", "ticket_id"])
    expected = prepare_features(data[data.ticket_id.isin(train_ids)]).loc[:, ["response_hours", "previous_contacts"]].median()
    actual = bundle["pipeline"].named_steps["inputs"].named_transformers_["numeric"].named_steps["impute"].statistics_
    np.testing.assert_allclose(actual, expected.to_numpy())


def test_target_demographics_and_closing_fields_cannot_change_predictions(trained):
    _, data, _, bundle = trained
    original = data.head(12).copy()
    modified = original.copy()
    for column in ["priority", "escalation_required", "customer_age", "customer_gender", "satisfaction_rating", "final_status", "ticket_id"]:
        modified[column] = "excluded-field-changed"
    np.testing.assert_allclose(score_tickets(original, bundle).escalation_score,
                               score_tickets(modified, bundle).escalation_score)


def test_missing_cells_and_novel_categories_can_be_scored(trained, ticket):
    bundle = trained[3]
    ticket["product"] = "Unseen product"
    ticket["response_hours"] = np.nan
    ticket["previous_contacts"] = np.nan
    ticket["complaint_text"] = None
    result = score_tickets(ticket, bundle)
    assert result.escalation_score.between(0, 1).all()
    assert result.missing_input_cells.iloc[0] == 2


def test_threshold_controls_only_the_decision(trained, ticket):
    bundle = trained[3]
    lower = score_tickets(ticket, bundle, 0.0)
    upper = score_tickets(ticket, bundle, 1.0)
    np.testing.assert_allclose(lower.escalation_score, upper.escalation_score)
    assert lower.predicted_escalation.iloc[0] == 1
    assert upper.predicted_escalation.iloc[0] == 0
    with pytest.raises(ValueError, match="Threshold"):
        score_tickets(ticket, bundle, np.nan)


def test_saved_metrics_reproduce_from_frozen_predictions(trained):
    root, _, report, _ = trained
    predictions = pd.read_csv(root / "reports" / "test_predictions.csv")
    recomputed = metrics(predictions.actual_proxy_label, predictions.escalation_score, report["metadata"]["threshold"])
    for key in ["accuracy", "recall", "precision", "roc_auc", "average_precision", "tn", "fp", "fn", "tp"]:
        assert recomputed[key] == pytest.approx(report["test"][key])
    assert report["metadata"]["data_provenance"].startswith("synthetic")
    assert set(report["metadata"]["features"]) == set(FEATURES)


def test_csv_exports_do_not_create_formulas():
    data = pd.DataFrame({"complaint_text": ["=1+1", "  @SUM(A1)", "ordinary text"], "score": [0.1, 0.2, 0.3]})
    result = safe_csv(data)
    assert "'=1+1" in result and "'  @SUM" in result


def test_cli_scores_included_sample(tmp_path):
    output = tmp_path / "scored.csv"
    command = [sys.executable, str(ROOT / "predict.py"), "--input", str(ROOT / "data" / "batch_examples.csv"), "--output", str(output)]
    completed = subprocess.run(command, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    result = pd.read_csv(output)
    assert len(result) == 20 and result.escalation_score.between(0, 1).all()


def test_dashboard_pages_and_assessment():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not app.exception
    assert app.sidebar.radio[0].value == "Ticket assessment"
    assert app.text_area[0].value == ""
    app.selectbox[0].set_value("Routine question").run()
    next(button for button in app.button if button.label == "Assess ticket").click().run()
    assert not app.exception
    assert any(item.value == "Standard support review" for item in app.subheader)
    for page in ["Batch processing", "Analytics", "Dataset", "Ticket assessment"]:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, f"Application failed on {page}"
        visible = " ".join(str(item.value) for group in [app.title, app.subheader, app.caption, app.markdown] for item in group).lower()
        assert not any(word in visible for word in ["your teacher", "presentation", "tutorial", "start here"])


def test_dashboard_rejects_blank_complaint():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    next(button for button in app.button if button.label == "Assess ticket").click().run()
    assert not app.exception
    assert any("Complaint text is required" in value.value for value in app.error)


def test_workspace_reset_and_second_scenario():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.selectbox[0].set_value("Work disrupted").run()
    next(button for button in app.button if button.label == "Assess ticket").click().run()
    assert not app.exception
    assert any(item.value == "Escalate for review" for item in app.subheader)
    app.sidebar.slider[0].set_value(0.01).run()
    app.sidebar.radio[0].set_value("Dataset").run()
    next(button for button in app.button if button.label == "Reset workspace").click().run()
    assert not app.exception
    assert app.sidebar.radio[0].value == "Ticket assessment"
    assert app.sidebar.slider[0].value == 0.12
    assert app.selectbox[0].value == "New ticket"
    assert app.text_area[0].value == ""
    assert "assessment" not in app.session_state


def test_batch_filter_controls_displayed_queue():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.sidebar.radio[0].set_value("Batch processing").run()
    assert any("Upload a CSV" in item.value for item in app.info)
    next(radio for radio in app.radio if radio.label == "Data source").set_value("Sample batch").run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 20
    app.selectbox[0].set_value("Flagged for review").run()
    assert len(app.dataframe[0].value) == 14
    app.selectbox[0].set_value("Standard handling").run()
    assert len(app.dataframe[0].value) == 6


def test_teacher_data_exports_match_actual_inputs():
    from complaints.demo import DEMO_TICKETS
    full = pd.read_csv(ROOT / "data" / "complaints.csv")
    preview = pd.read_csv(ROOT / "data" / "teacher_preview.csv")
    pd.testing.assert_frame_equal(preview, full[["ticket_id"] + FEATURES + ["priority", "escalation_required"]].head(12))
    scenarios = pd.read_csv(ROOT / "data" / "demo_scenarios.csv").set_index("scenario")
    pd.testing.assert_frame_equal(scenarios[FEATURES], pd.DataFrame.from_dict(DEMO_TICKETS, orient="index")[FEATURES], check_names=False)
