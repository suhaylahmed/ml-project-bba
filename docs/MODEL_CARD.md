# Model card

## Purpose and scope

Educational decision-support prototype for estimating a high-priority escalation proxy at the first agent review. The model recommends review; it does not autonomously escalate tickets. The raw priority label is excluded from inputs.

The original PDF defines the target from ticket priority. This is not an observed future-escalation outcome. Changing that definition requires new labels, a prediction horizon and a fresh experiment.

## Data and experiment

- Included data: 3,000 synthetic labelled tickets, generated locally with seed 42.
- Separate inference sample: 20 tickets generated with a different seed, without labels in the exported sample.
- Safe inputs: four categorical columns, two numeric columns and free complaint text.
- Excluded: identifiers, labels, priority, demographics, satisfaction, final status, raw timestamps and provenance.
- Split: stratified IID random 60% training / 20% validation / 20% test.
- Candidate configurations: dummy prior, Logistic Regression, kNN, Random Forest, AdaBoost.
- Selection: highest mean five-fold training average precision, dummy excluded.
- Cutoff: maximize validation F2 while aiming for a configured minimum validation recall of 0.85; record a miss if no candidate meets the constraint.
- Final fit: training partition only. The validation-selected model and cutoff are frozen for test evaluation.

See `artifacts/metadata.json` for the dataset hash, exact feature list, versions, selected model, cutoff and split sizes. If trained on user data, provenance is marked unverified unless the file matches the included synthetic manifest.

## Included measured result

Logistic Regression was selected. At cutoff 0.12 on the 600-ticket frozen test set:

| Measure | Value |
|---|---|
| Accuracy | 55.8% |
| Precision | 42.4% |
| Recall | 93.9% |
| F1 | 0.584 |
| ROC-AUC | 0.802 |
| Average precision | 0.666 |
| Positive share / no-skill AP | 0.330 |
| TN / FP / FN / TP | 149 / 253 / 12 / 186 |
| Flagged for review | 439 / 600 (73.2%) |
| Approximate 95% recall interval | 89.7%-96.5% |

The always-negative dummy policy at 0.5 has 67.0% accuracy and 0% recall on this test set. The selected policy trades accuracy and precision for recall. A review workload of 73.2% is substantial and may not be acceptable operationally. These outcomes illustrate the need for capacity- and cost-based policy selection on validation data.

The values above describe the delivered run. Retraining can replace the artifacts; the authoritative current values are always in `reports/metrics.json`. Five-fold variation and the Wilson interval describe sampling in this experiment, not uncertainty about deploying on different real data.

## Explainability

Validation permutation importance measures global dependence on raw inputs through the full pipeline. It does not provide causal explanations, fairness guarantees or individual decision explanations. There is no SHAP/LIME dependency. The prototype deliberately uses a small classical ML stack that can be explained during a presentation.

## Limitations

- The data-generation process is invented; performance may reflect generator patterns.
- Labels are a priority proxy; neither business benefit nor future escalation prediction is established.
- Scores are uncalibrated and must not be described as validated real-world risk percentages.
- Response time makes the model unsuitable for scoring at the instant of ticket arrival without redesign.
- Text is template-based English; multilingual, sarcastic and out-of-domain complaints are unvalidated.
- A random split assumes IID rows. Repeat-customer and time-based real data require different splits.
- Omitting age and gender does not eliminate demographic proxy effects or prove fairness.
- Thresholds and feature importance are dataset-specific. Workload and false-alarm costs require human judgment.
- No production identity management, ticket-system integration or real-time monitoring is included; those are outside a local classroom prototype.

## Reproducibility and intended use

Python 3.12 with pinned direct dependencies; a complete tested environment snapshot is supplied separately. Seed 42 fixes the experiment. Data hash and partition IDs are saved. Tests check timing, excluded columns, held-out vocabulary, training-only imputations, serialization, CLI scoring and dashboard paths.

Use this project to learn, demonstrate and compare policies. Before any real deployment, establish data permissions and target meaning, validate timing, evaluate on representative future/group-separated data, calibrate scores, inspect subgroup behavior and choose a policy that the team can staff.
