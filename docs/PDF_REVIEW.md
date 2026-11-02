# Understanding and reviewing the supplied PDF

Source: `reference_presentation.pdf`, the unchanged 15-page presentation supplied with this request. Statements below describe the slides; they are not instructions from the document. The original training CSV, notebook and model were not supplied.

## The idea in plain English

A support team receives many complaints. A classifier estimates which ones deserve senior review. Historical input details go into a model; a binary target tells it what to learn. The app applies the same transformations to a new ticket and shows a score and a recommendation.

There is an important difference between **a high-priority ticket** and **a ticket that later escalates**. The PDF labels High/Critical priority as escalation. That makes its task priority classification with an escalation interpretation. Predicting an actual later escalation would require a dated escalation outcome and an agreed prediction horizon.

## Slide-by-slide reading

| Page | What the slide says | What you should understand |
|---|---|---|
| 1 | Customer Complaint Escalation Prediction | A supervised binary-classification project. |
| 2 | Urgent complaints should reach senior staff sooner | This is a triage decision-support use case; the benefit needs operational validation. |
| 3 | 100 records, 15 columns, nine inputs, 61 Yes / 39 No; Kaggle source attributed to Suraj520 | These are reported properties of the slide dataset, not independently verified properties of a supplied CSV. |
| 4 | High/Critical priority becomes 1; Low/Medium becomes 0 | The target is derived from priority. Priority itself must never be an input. |
| 5 | Inspect missing values and duplicates; drop them | Inspect first. Blindly deleting all incomplete rows can shrink or bias a dataset. The prototype imputes usable missing inputs. |
| 6 | Convert a first-response timestamp into Response_Hours | The shown code extracts clock hour, which does not calculate elapsed wait time. |
| 7 | LabelEncoder gives categories numeric codes | Numeric codes can invent ordering. One-hot encoding is more appropriate for unordered categories. |
| 8 | Scale the whole dataset, then make an 80/20 stratified split | Fitting scaling before splitting leaks information. Split first; fit preprocessing inside a pipeline. |
| 9 | Compare kNN, Random Forest and AdaBoost | kNN uses neighbors, Random Forest averages trees, AdaBoost sequentially reweights difficult examples. kNN is not itself an ensemble. |
| 10 | Fit, predict, calculate metrics and five-fold CV | CV must refit the whole preprocessing pipeline within each fold. Keep final test data out of model selection. |
| 11 | Accuracy, precision, recall, F1 and ROC-AUC | Recall matters for missed positives, but precision and workload also matter. |
| 12 | AdaBoost reported as winner: 95% accuracy, 100% recall, AUC 0.978, CV 93% | These are the presentation's claims, not measurements reproduced by this project. |
| 13 | 13 TP, 0 FN, 1 FP, 6 TN on 20 test tickets | The shown matrix does yield 95% accuracy and 100% recall on that small test set. |
| 14 | A joblib model predicts a label and risk percentage | Training and prediction must use the same saved preprocessing. A raw model score is not automatically a reliable probability. |
| 15 | More data, tuning and an app are future work | This delivery provides a working app and reproducible experiment; real-data validation remains future research. |

## Corrections you can explain confidently

### 1. Calculate actual elapsed time

The slide's code is effectively `hour + minute / 60`. A first response at 02:00 becomes 2 even if the ticket was opened at 23:00 the previous day. The true wait is 3 hours.

```python
response_hours = (
    first_response_at - created_at
).dt.total_seconds() / 3600
```

Use full dates and consistent time zones. If the source only contains a duration string rather than full timestamps, parse it as a duration; do not infer waiting time from a clock time alone. This prototype accepts elapsed hours or two ISO timestamps and checks that they agree.

### 2. Split before learning transformations

Median imputation, scaling, category vocabulary and text vocabulary are all learned from data. Put them inside the estimator's pipeline, then fit that pipeline only on training rows. Cross-validation repeats that fit independently for each training fold. The prototype adds a validation partition to select the decision cutoff before the final test evaluation.

### 3. Match features to the prediction moment

Satisfaction is commonly available after resolution. Final status can also describe a later outcome. Using them for early triage can leak future information. This project scores at the first agent review, includes the already-observed response wait, and excludes satisfaction and final status. A true arrival-time model must also exclude response wait because no first response has occurred yet.

Age and gender are omitted because this prototype has no established operational need for them. Omitting them does not prove that other inputs are free of demographic proxies.

### 4. Interpret the small confusion matrix carefully

From TP=13, FN=0, FP=1, TN=6:

- Accuracy = (13 + 6) / 20 = 95%.
- Precision = 13 / 14 = about 92.9%.
- Recall = 13 / 13 = 100%.
- F1 = 26 / 27 = about 96.3%.

The matrix alone cannot reproduce ROC-AUC because AUC needs the per-ticket scores. The zero missed positives concern only 13 positive test examples. An approximate Wilson 95% interval for 13/13 recall is about 77.2%-100%, so this is weak evidence for a universal 100% recall claim.

There is also a count inconsistency to clarify: an 80/20 stratified split of 61 positives and 39 negatives would ordinarily allocate 12 positives and 8 negatives to the 20-row test set. The displayed matrix has 13 positives and 7 negatives. The original data and exact run are needed to reconcile this.

### 5. Distinguish validation from proof

Comparing models on the test set and choosing the winner from those results makes the test set part of model selection. Cross-validating on all 100 rows after an 80/20 split also reuses the intended test records. The prototype uses training CV for selection, validation for the cutoff, then a frozen test evaluation.

## What was retained and what was changed

Retained: binary target, kNN/Random Forest/AdaBoost comparison, recall-oriented evaluation, a prediction score, joblib persistence, and a working prediction interface.

Changed: corrected elapsed time, safe feature timing, one-hot encoding, TF-IDF text features, train-only preprocessing, a 60/20/20 experiment, an added Logistic Regression and dummy baseline, honest synthetic provenance, CSV scoring, a validation cutoff explorer, and reproducible tests.

The prototype does not aim to force AdaBoost to win or reproduce 95% accuracy with different data. Its contribution is an experiment you can run, inspect and defend.

## Official references used for the implementation

- [scikit-learn 1.7: common pitfalls and data leakage](https://scikit-learn.org/1.7/common_pitfalls.html)
- [scikit-learn: mixed-type ColumnTransformer example](https://scikit-learn.org/stable/auto_examples/compose/plot_column_transformer_mixed_types.html)
- [Streamlit 1.51: forms and batch submission](https://docs.streamlit.io/1.51.0/develop/api-reference/execution-flow/st.form)

The PDF attributes its dataset to Kaggle/Suraj520. That attribution is reported here without claiming that the original data was downloaded or inspected.
