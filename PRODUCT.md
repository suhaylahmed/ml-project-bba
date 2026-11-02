# Complaint Review

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

The user selected a simple Python dashboard, training scripts, and a presentation guide. The authored application is Python, with native Streamlit components for the local browser dashboard. No custom HTML, CSS, or JavaScript is required.

## Users

The user is learning, reviewing, and presenting the machine-learning project described in the supplied PDF. The project must be easy to run and its code and results easy to explain.

## Product Purpose

Provide a complete classroom prototype with sample data, reproducible model training, single-ticket and CSV predictions, measured evaluation, and learning and presentation materials.

## Operating Context

Run locally with `python start.py`; the launcher prepares the environment and starts the dashboard. Package installation requires internet access; the included data and saved model support local use after setup. Terminal scripts also generate data, train models, and score a CSV.

The dashboard offers four normal workspaces: Ticket assessment, Batch processing, Analytics and Dataset. It opens on a blank new-ticket form. A shared routing threshold controls predictions and the validation explorer; frozen test results retain the saved evaluation threshold. Review queues can be filtered and exported. Reset workspace clears session inputs and restores the saved policy. The complete application and presentation guide is supplied as a separate PDF; the app contains no tutorial or presentation route.

## Capabilities and Constraints

- The supplied PDF maps High/Critical priority to the positive escalation label and Low/Medium to the negative label. This is a priority-based proxy, not an observed future escalation event.
- Prediction occurs at the first agent review. Inputs are complaint text, product, ticket type, subject, channel, elapsed response wait, and previous contacts. Priority and closing-time fields are excluded from model inputs.
- All delivered tickets are synthetic. The project does not include the original Kaggle CSV referenced by the PDF.
- The project compares kNN, Random Forest, AdaBoost, Logistic Regression, and a dummy baseline. Model selection uses training cross-validation; cutoff selection uses validation data; final reporting uses held-out test data.
- This is a local classroom prototype. Recommendations require human review, and synthetic performance does not establish real-world effectiveness.
- Preserve simple, clean Python code and native Streamlit controls. Production deployment and operational use are outside the established scope.

## Evidence on Hand

- `docs/PDF_REVIEW.md`: review of the supplied presentation and its limitations.
- `data/`: included synthetic tickets, fictional batch examples, and a CSV template.
- `artifacts/`: saved pipeline and metadata.
- `reports/`: measured metrics, split records, predictions, and figures from the delivered experiment.
- `docs/PROJECT_GUIDE.md` and `docs/APPLICATION_GUIDE.md`: explanation and presentation support.

No original training CSV or trained model was supplied with the PDF. Do not present its reported accuracy or recall as independently reproduced evidence.

## Product Principles

- Keep the complete experiment runnable and understandable in Python.
- Show the prediction moment, label meaning, and data provenance explicitly.
- Report measured results and their limits without real-world claims.
- Keep human review visible in every recommendation workflow.
