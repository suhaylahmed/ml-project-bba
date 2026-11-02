# Delivery validation — November 2, 2026

Checked on Windows with CPython 3.12.10. Direct runtime dependencies are pinned in requirements.txt. The model, full labelled dataset and frozen experiment results are unchanged by the interface revision.

## Automated checks

The current full suite passed: **28 tests in 15.67 seconds**. Coverage includes disjoint partitions, training-only vocabulary and numeric imputation, ignored outcome/demographic fields, elapsed response hours, label consistency, reproducible data exports, missing values and unfamiliar categories, threshold decisions, saved metrics, CSV formula escaping, CLI inference, startup recovery when pip is missing, and the four application workspaces.

Application checks cover the blank initial form, required complaint text, routine and work-disruption samples, assessment, resetting the workspace/page/threshold, the empty upload state, and queue filters (20 all / 14 flagged / 6 standard at threshold 0.12). Tests also check that tutorial and presentation wording is absent from the visible app text.

Command: `python -m pytest tests -q`. The restricted authoring shell needed a writable test temporary directory and an allowed non-sandboxed invocation for Windows temporary-file permissions. This is not a requirement for normal project use.

## Setup and inference

A separate fresh environment was prepared through start.py --setup-only and scored the 20-ticket batch. A real environment initially missing pip successfully bootstrapped pip and installed the pinned requirements. pip check reported no broken requirements. Startup regression tests preserve that recovery path.

## Rendered evidence

The 18-page Application and Presentation Guide was rendered and visually checked, including its field table and demonstration sequence. The app uses native Streamlit controls and the existing readable theme. Current normal-workspace screenshots replace the earlier guided interface captures. Browser verification and queue-export details are recorded in docs/screenshots/README.md.

## Interpretation

The selected Logistic Regression pipeline produces routine 2.1%, work disruption 98.3% and repeated billing 82.4% scores for the fixed examples. The synthetic test run catches 186 of 198 positives, misses 12, and flags 253 negatives at the saved 0.12 threshold. Recall is 93.9%, precision 42.4%, accuracy 55.8%; review workload is 439/600. These are measured synthetic results, not proof of real-world effectiveness or calibrated future escalation probabilities.

The bundle includes sample-data provenance, saved pipeline, exact split IDs, frozen predictions and metrics. Model uploads are unsupported. Read MODEL_CARD.md and PDF_REVIEW.md for the methodological limits.
