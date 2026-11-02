"""Local complaint assessment and batch review application."""

import json
from pathlib import Path
import pandas as pd
import streamlit as st
from complaints.demo import DEMO_TICKETS
from complaints.evaluation import metrics
from complaints.features import CATEGORIES, FEATURES, MAX_BATCH_ROWS, input_notes
from complaints.inference import load_bundle, safe_csv, score_tickets

ROOT = Path(__file__).resolve().parent
PAGES = ["Ticket assessment", "Batch processing", "Analytics", "Dataset"]
st.set_page_config(page_title="Complaint Review", layout="wide")


@st.cache_resource
def model_bundle(modified_time: int):
    return load_bundle(ROOT)


def reset_workspace(saved_cutoff):
    for key in list(st.session_state):
        del st.session_state[key]
    st.session_state["page"] = "Ticket assessment"
    st.session_state["routing_threshold"] = saved_cutoff


def figure(name, caption):
    path = ROOT / "reports" / "figures" / name
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")


def assessment_page(bundle, threshold):
    st.title("Ticket assessment")
    st.write("Assess a complaint and route it for the appropriate level of review.")
    source = st.selectbox("Load sample ticket", ["New ticket"] + list(DEMO_TICKETS))
    defaults = dict(product="Laptop", ticket_type="Technical issue", subject="Device not working",
                    channel="Email", response_hours=0.0, previous_contacts=0, complaint_text="")
    ticket = DEMO_TICKETS.get(source, defaults)
    with st.form(f"ticket_{source}"):
        text = st.text_area("Complaint text", ticket["complaint_text"], height=120, max_chars=5000)
        left, right = st.columns(2)
        with left:
            product = st.selectbox("Product", CATEGORIES["product"], index=CATEGORIES["product"].index(ticket["product"]))
            kind = st.selectbox("Ticket type", CATEGORIES["ticket_type"], index=CATEGORIES["ticket_type"].index(ticket["ticket_type"]))
            wait = st.number_input("Response wait (hours)", 0.0, 720.0, ticket["response_hours"], 0.5,
                                   help="Elapsed time from ticket creation to the first agent response.")
        with right:
            subject = st.selectbox("Subject", CATEGORIES["subject"], index=CATEGORIES["subject"].index(ticket["subject"]))
            channel = st.selectbox("Channel", CATEGORIES["channel"], index=CATEGORIES["channel"].index(ticket["channel"]))
            contacts = st.number_input("Previous contacts", 0, 50, ticket["previous_contacts"])
        submitted = st.form_submit_button("Assess ticket", type="primary")
    if submitted:
        if not text.strip():
            st.session_state.pop("assessment", None)
            st.session_state.pop("assessment_source", None)
            st.error("Complaint text is required.")
        else:
            st.session_state["assessment"] = pd.DataFrame([dict(product=product, ticket_type=kind,
                subject=subject, channel=channel, response_hours=wait, previous_contacts=contacts, complaint_text=text)])
            st.session_state["assessment_source"] = source
    if "assessment" in st.session_state and st.session_state.get("assessment_source") == source:
        frame = st.session_state["assessment"]
        result = score_tickets(frame, bundle, threshold)
        row = result.iloc[0]
        st.divider()
        st.subheader(row.recommendation)
        st.write(f"Priority score: **{row.escalation_score:.1%}** · Routing threshold: **{threshold:.2f}**")
        st.caption("Decision support only. Scores are uncalibrated estimates for a high-priority proxy label.")
        st.info("Senior review recommended." if row.predicted_escalation else "Continue standard support handling.")
        with st.expander("Submitted ticket"):
            st.dataframe(frame, hide_index=True, width="stretch")
        st.caption("Assessment reflects the submitted ticket details.")
        st.download_button("Export assessment", safe_csv(result), "ticket_assessment.csv", "text/csv")


def batch_page(bundle, threshold):
    st.title("Batch processing")
    st.write("Score a CSV of complaints and export a review queue.")
    source = st.radio("Data source", ["Upload CSV", "Sample batch"], horizontal=True)
    with st.expander("CSV requirements"):
        st.download_button("Download CSV template", (ROOT / "data/batch_template.csv").read_bytes(), "batch_template.csv", "text/csv")
        st.write("Required columns: " + ", ".join(FEATURES))
        st.caption("Limit: 10,000 rows / 5 MB. response_hours: 0-720; previous_contacts: whole numbers 0-50. created_at and first_response_at can replace response_hours. Empty cells are handled by the saved pipeline.")
    upload = None
    if source == "Upload CSV":
        upload = st.file_uploader("Ticket CSV", type=["csv"])
        if upload is None:
            st.info("Upload a CSV to generate the review queue.")
            return
    else:
        st.download_button("Download sample batch", (ROOT / "data/batch_examples.csv").read_bytes(), "sample_batch.csv", "text/csv")
    try:
        frame = pd.read_csv(upload if upload is not None else ROOT / "data/batch_examples.csv")
        if len(frame) > MAX_BATCH_ROWS:
            raise ValueError(f"Use at most {MAX_BATCH_ROWS:,} rows per file.")
        encoder = bundle["pipeline"].named_steps["inputs"].named_transformers_["category"].named_steps["encode"]
        for note in input_notes(frame, dict(zip(CATEGORIES, encoder.categories_))):
            st.warning(note)
        result = score_tickets(frame, bundle, threshold)
    except (ValueError, OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"Cannot process this file: {error}")
        return
    st.subheader(f"{int(result.predicted_escalation.sum())} of {len(result)} tickets flagged for review")
    selected = st.selectbox("Review queue", ["All tickets", "Flagged for review", "Standard handling"])
    queue = result
    if selected != "All tickets":
        queue = result[result.predicted_escalation == int(selected == "Flagged for review")]
    columns = (["ticket_id"] if "ticket_id" in queue else []) + ["escalation_score", "recommendation", "complaint_text"]
    st.dataframe(queue.sort_values("escalation_score", ascending=False)[columns], hide_index=True, width="stretch",
                 column_config={"escalation_score": st.column_config.NumberColumn("Priority score", format="%.3f")})
    st.caption(f"{len(queue)} rows in this queue · threshold {threshold:.2f}. Export follows the selected filter and preserves input order.")
    st.download_button("Export queue", safe_csv(queue), "review_queue.csv", "text/csv", type="primary")


def analytics_page(bundle, threshold):
    st.title("Model analytics")
    report = json.loads((ROOT / "reports/metrics.json").read_text(encoding="utf-8"))
    test, meta = report["test"], report["metadata"]
    st.write(f"**{meta['selected_model']}** · {test['rows']} held-out synthetic tickets · evaluation threshold **{meta['threshold']:.2f}**")
    st.caption("This saved test evaluation is fixed. The routing threshold affects new assessments, batches and validation analysis.")
    st.subheader("Evaluation summary")
    st.dataframe(pd.DataFrame([
        ["Recall", f"{test['recall']:.1%}"], ["Precision", f"{test['precision']:.1%}"],
        ["Accuracy", f"{test['accuracy']:.1%}"], ["F1", f"{test['f1']:.3f}"],
    ], columns=["Metric", "Value"]), hide_index=True, width="stretch")
    st.table(pd.DataFrame([[test['tn'], test['fp']], [test['fn'], test['tp']]],
                          index=["Actually standard", "Actually high priority"],
                          columns=["Predicted standard", "Flagged for review"]))
    st.warning(f"Review workload: {test['flagged']}/{test['rows']} tickets flagged ({test['flagged']/test['rows']:.1%}); {test['fp']} false alarms and {test['fn']} missed positives.")
    with st.expander("Model comparison"):
        comparison = pd.read_csv(ROOT / "reports/model_comparison.csv")
        st.dataframe(comparison[["model", "cv_ap_mean", "cv_ap_std"]].round(3), hide_index=True, width="stretch")
        figure("model_comparison.png", "Five-fold training cross-validation average precision, mean and standard deviation.")
    with st.expander("Feature importance"):
        figure("feature_importance.png", "Validation permutation importance. Predictive association is not causal attribution or an individual explanation.")
    with st.expander("Threshold analysis"):
        val = pd.read_csv(ROOT / "reports/validation_predictions.csv")
        live = metrics(val.actual_proxy_label, val.escalation_score, threshold)
        st.write(f"Validation at threshold {threshold:.2f}: recall {live['recall']:.1%}, precision {live['precision']:.1%}, {live['flagged']}/{live['rows']} flagged, {live['fn']} missed positives.")
        figure("threshold_tradeoff.png", f"Saved policy: validation F2 selection with a {meta['desired_validation_recall']:.0%} desired recall constraint.")
    with st.expander("Detailed evaluation"):
        st.write(f"ROC-AUC: {test['roc_auc']:.3f} · Average precision: {test['average_precision']:.3f} · Brier score: {test['brier_score']:.3f}")
        st.caption(f"Positive share: {test['positives']/test['rows']:.3f}. Approximate 95% recall interval: {test['recall_95ci'][0]:.1%}-{test['recall_95ci'][1]:.1%}.")
        figure("roc_precision_recall.png", "Frozen test ranking diagnostics.")
        st.write(f"Train: {meta['splits']['train']} · Validation: {meta['splits']['validation']} · Test: {meta['splits']['test']}")
    st.download_button("Export metrics", (ROOT / "reports/metrics.json").read_bytes(), "metrics.json", "application/json")


def dataset_page():
    st.title("Sample dataset")
    data = pd.read_csv(ROOT / "data/complaints.csv")
    st.caption(f"{len(data):,} synthetic labelled records · included evaluation dataset")
    records, distribution, quality = st.tabs(["Records", "Distribution", "Data quality"])
    with records:
        selected = st.selectbox("Ticket ID", data.ticket_id.head(12).tolist())
        row = data.loc[data.ticket_id == selected].iloc[0]
        st.write(str(row.complaint_text) if pd.notna(row.complaint_text) else "No complaint text available.")
        st.write(f"Priority: **{row.priority}** · Reference label: **{int(row.escalation_required)}**")
        fields = [column for column in FEATURES if column != "complaint_text"]
        st.table(pd.DataFrame({"Field": fields, "Value": [str(row[column]) if pd.notna(row[column]) else "Missing" for column in fields]}))
        with st.expander("Record preview"):
            st.dataframe(data[["ticket_id"] + FEATURES + ["priority", "escalation_required"]].head(12), hide_index=True, width="stretch")
        st.download_button("Export preview", (ROOT / "data/teacher_preview.csv").read_bytes(), "sample_preview.csv", "text/csv")
    with distribution:
        st.bar_chart(data.escalation_required.map({0: "Standard (0)", 1: "High priority (1)"}).value_counts(), color="#12616C")
    with quality:
        st.dataframe(data.isna().sum().rename("Missing cells"), width="stretch")
    st.download_button("Export full dataset", (ROOT / "data/complaints.csv").read_bytes(), "synthetic_complaints.csv", "text/csv")


def main():
    try:
        path = ROOT / "artifacts/model.joblib"
        bundle = model_bundle(path.stat().st_mtime_ns if path.exists() else 0)
    except (ValueError, OSError, KeyError) as error:
        st.error(str(error)); st.stop()
    with st.sidebar:
        st.header("Complaint Review")
        page = st.radio("Workspace", PAGES, key="page")
        st.caption(bundle["metadata"]["selected_model"])
        st.caption("High-priority proxy · synthetic sample environment")
        with st.expander("Routing settings"):
            threshold = st.slider("Routing threshold", 0.0, 1.0, float(bundle["threshold"]), 0.01,
                                  key="routing_threshold", help="Flag tickets when the score reaches this value.")
        st.button("Reset workspace", on_click=reset_workspace, args=(float(bundle["threshold"]),))
    if page == "Ticket assessment":
        assessment_page(bundle, threshold)
    elif page == "Batch processing":
        batch_page(bundle, threshold)
    elif page == "Analytics":
        analytics_page(bundle, threshold)
    else:
        dataset_page()


main()
