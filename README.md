# Complaint Review

A complete **classroom prototype in Python** based on the supplied complaint-escalation presentation. It includes fictional data, model comparison, a saved model, a dashboard, CSV prediction, tests, and presentation support.

**Application:** assess individual tickets, process CSV review queues, inspect model analytics and explore records. The interface opens directly to ticket assessment.

**Separate companion:** [Application and Presentation Guide — 18 pages](docs/Application_and_Presentation_Guide.pdf). It explains setup, every field and control, exports, the ML pipeline, a live demonstration, presentation timing, viva answers and troubleshooting. Its editable source is `docs/APPLICATION_GUIDE.md`. Read `docs/PDF_REVIEW.md` for a deeper review of the original slides.

## A simple classroom demonstration

Use **Dataset → Ticket assessment → Batch processing → Analytics** for your demonstration. Compare Routine question with Work disrupted. Keep the routing threshold at 0.12 for the main demo. Routing settings and detailed analytics are expandable. **Reset workspace** clears the assessment, restores the saved threshold and opens a blank new ticket. The teaching material is in the separate PDF.

Show `data/teacher_preview.csv` to explain one row; `data/complaints.csv` is the exact 3,000-row labelled sample used by the experiment. `data/batch_examples.csv` is ready for upload. The three live form examples are exported in `data/demo_scenarios.csv`. All are synthetic. External sources and adaptation caveats are in `docs/DATA_SOURCES.md`.

## Run it in one command

Public repository: [suhaylahmed/ml-project-bba](https://github.com/suhaylahmed/ml-project-bba). Clone it or download and extract the ZIP from GitHub's Code menu.

```text
git clone https://github.com/suhaylahmed/ml-project-bba.git
cd ml-project-bba
python start.py
```

Install **Python 3.12** from [python.org](https://www.python.org/downloads/) if needed. Python 3.10-3.13 is supported by the launcher; 3.12 is the version tested for this delivery.

1. Extract the ZIP completely.
2. Open a terminal in the extracted `complaint_escalation_project` folder (the folder containing this file).
3. Run:

```text
python start.py
```

On Windows, `py -3.12 start.py` also works. On macOS/Linux, use `python3 start.py` if `python` is unavailable.

The first run creates `.venv` and installs the pinned dependencies. **Internet is needed only for package installation.** The trained model and sample data are included. After setup, the demo runs locally without API keys or external data services. Your browser opens at **http://localhost:8501**. Stop it with **Ctrl+C** in the terminal.

If port 8501 is busy:

```text
python start.py --port 8502
```

For setup without opening the app, use `python start.py --setup-only`. For an existing environment with the dependencies installed, use `python run.py`. The launcher automatically retrains when the model is missing or its scikit-learn version differs.

## What you can demonstrate

- Assess a single complaint and download its result.
- Compare routine, work-disruption and repeated-billing examples.
- Change the decision cutoff and explain recall versus false alarms.
- Score the 20-ticket sample batch or upload a CSV, filter the review queue, and export the selected rows.
- Inspect the frozen test confusion matrix, ROC/PR curves and actual metrics.
- Compare kNN, Random Forest, AdaBoost, Logistic Regression and a dummy baseline.
- Explain validation permutation importance and explore sample-data quality.

## What this project predicts

The supplied PDF defines `Escalation_Required` from **ticket priority**: High/Critical means 1, Low/Medium means 0. This project preserves that target as a **priority-based proxy for escalation**. It does not claim to predict observed future escalations.

The prediction moment is the **first agent review**. Inputs are complaint text, product, ticket type, subject, channel, elapsed hours until first response, and previous contacts about the issue. Priority, labels, demographics, satisfaction and final status are excluded. This is a deliberate correction to avoid using information that arrives too late.

**All included tickets are synthetic.** They are not the Kaggle dataset mentioned by the slides. No original CSV or trained model was supplied, so the slides' 95% accuracy and 100% recall cannot be independently reproduced. This prototype's actual measurements are in `reports/RUN_SUMMARY.md` and `reports/metrics.json`. Synthetic scores do not establish real-world effectiveness or guarantee a grade.

## Read the project in this order

| File | What it helps you understand |
|---|---|
| `docs/PDF_REVIEW.md` | All 15 slides, their meaning, and the corrections |
| `docs/PROJECT_GUIDE.md` | ML concepts, data flow, and how the code works |
| `docs/APPLICATION_GUIDE.md` | Every control, slide outline, speaking notes, live demo and viva answers |
| `reports/RUN_SUMMARY.md` | Actual metrics from the included model |
| `docs/DATA_DICTIONARY.md` | Every field, allowed values, missing values and timing |
| `docs/MODEL_CARD.md` | Intended use, limitations and next steps |
| `docs/VALIDATION.md` | Checks performed for this delivery |

## Reproduce the experiment

After automatic setup, use the environment's Python directly. Activation is optional.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe generate_data.py --rows 3000 --seed 42
.\.venv\Scripts\python.exe train.py
.\.venv\Scripts\python.exe predict.py --input data/batch_examples.csv --output reports/my_predictions.csv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

**macOS/Linux:**

```bash
.venv/bin/python generate_data.py --rows 3000 --seed 42
.venv/bin/python train.py
.venv/bin/python predict.py --input data/batch_examples.csv --output reports/my_predictions.csv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Generating data replaces the sample CSV and its manifest. Training replaces the saved model and reports. Keep a copy of any run you want to retain before regenerating. The seed makes the sample reproducible in the tested environment.

## Use another CSV

The dashboard can score up to **10,000 rows / 5 MB** at a time. Download its template, fill the seven feature columns, and upload it. Empty numeric or category cells are allowed; missing columns and invalid values receive clear errors. Unfamiliar categories are accepted with a warning. `response_hours` can instead be derived from `created_at` and `first_response_at`.

To train on your own labelled file:

```text
python train.py --data path/to/labelled_tickets.csv --min-recall 0.85
```

Run this inside the prepared environment. A training CSV needs the feature columns and `escalation_required` as 0/1, or a `priority` column with Low/Medium/High/Critical. If both labels and priority are supplied, they must agree. You need at least 100 rows and at least 20 examples in each class. This generic random-split pipeline is intended for IID classroom experiments. Real repeated-customer or chronological data needs a group-aware or time-based evaluation before making performance claims.

## Project structure

```text
app.py                 Streamlit dashboard
start.py               Automatic environment setup and launch
run.py                 Launch from an existing environment
generate_data.py       Reproducible fictional data
train.py               Compare, select, evaluate and save
predict.py             Batch prediction from the terminal
complaints/
  data.py              Synthetic generator and provenance hash
  features.py          Shared validation and elapsed-time calculation
  models.py            Preprocessing pipelines and five candidates
  evaluation.py        Metrics, threshold selection and intervals
  training.py          Full training workflow
  inference.py         Saved-model loading, scoring and CSV export
  plots.py             Presentation-ready figures
data/                  3,000 labelled tickets, 20 unlabelled examples, template
artifacts/             Saved pipeline and metadata
reports/               Metrics, charts, split IDs and frozen predictions
docs/                  Learning and presentation materials
tests/                 Data, leakage, inference, CLI and dashboard checks
```

## Troubleshooting

| Problem | Fix |
|---|---|
| Python is not recognized | Install Python; reopen the terminal. On Windows try `py -3.12 start.py`. |
| Package installation fails | Check internet access; retry `python start.py`. Use Python 3.12. |
| Browser does not open | Visit http://localhost:8501 manually while the terminal is running. |
| Port is in use | Run `python start.py --port 8502`. |
| Version mismatch or missing model | Run `python start.py --retrain`. |
| CSV rejected | Check `docs/DATA_DICTIONARY.md`; download the dashboard template. |
| Script cannot be found | Open the extracted project folder before running commands. Do not run from inside the ZIP. |

The app binds to your local machine. It does not send ticket text to an external model. Use only the model artifact supplied here or one you train yourself; Python joblib files are executable serialization, so model uploads are deliberately not supported.
