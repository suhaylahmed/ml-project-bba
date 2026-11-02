# How the project works

## Your one-sentence explanation

"I built a reproducible Python triage prototype that learns a high-priority escalation proxy from complaint text and ticket context, compares several models without test leakage, and lets a user examine the recall-workload tradeoff."

## The ML concepts you need

**Supervised learning:** train from examples with known labels. A feature is an input, such as a complaint's words. The target is the answer the model learns, here 0 or 1.

**Classification versus regression:** classification predicts a category; regression predicts a continuous value. A classifier can also output a probability-like score used to rank tickets.

**Training, validation and test:** training teaches parameters, validation chooses an operating cutoff, and test estimates performance after those decisions. The included split is 1,800 / 600 / 600 tickets. Five-fold cross-validation happens only inside the 1,800-row training partition.

**Overfitting:** a model can memorize quirks of its training examples and perform worse on unseen examples. Held-out data helps detect this. Synthetic data can make a task unrealistically easy or unrealistic in other ways, so held-out synthetic results do not replace external validation.

**Stratification:** preserve approximately the same positive/negative proportions in each partition. It does not prevent customer duplication or chronological leakage in real datasets.

## The data flow

1. `generate_data.py` creates 3,000 fictional tickets with seed 42, a separate 20-ticket inference batch, and a manifest with a SHA-256 hash.
2. `features.py` validates columns and values, derives elapsed response time if needed, selects exactly seven safe raw inputs, and validates labels.
3. `training.py` removes exact duplicate rows and rejects conflicting duplicate IDs. It creates stratified 60/20/20 partitions.
4. `models.py` gives every classifier the same preprocessing pipeline. Each CV fold fits its own preprocessing.
5. The classifier with highest mean five-fold training average precision is selected, excluding the dummy.
6. The selected pipeline is fitted on the training partition only. Validation F2 chooses a cutoff while aiming for at least 85% recall.
7. The model and cutoff are frozen. The test set is evaluated once and saved with predictions and metrics.
8. `inference.py` loads the entire fitted pipeline. Both the app and CLI use that same scoring function.

The final model is deliberately not refitted on train+validation: that keeps its probability scale and the validation-selected cutoff tied to the exact model evaluated on the test set.

## Preprocessing in plain language

| Input kind | Transformation | Why |
|---|---|---|
| Numeric: wait and contacts | Median imputation, then StandardScaler | Fill missing cells using training values; avoid distances being dominated by large units. |
| Categorical: product, type, subject, channel | Missing category `Unknown`, then one-hot encoding | Separate indicator columns avoid inventing an order. New categories do not crash prediction. |
| Complaint text | TF-IDF unigrams/bigrams, up to 600 features | Turn words and adjacent word pairs into a small numeric representation. |

TF-IDF gives weight to terms that distinguish documents. It is not a language model and it does not deeply understand the complaint. The subject field is a category; the free complaint text is a separate field.

## The five compared candidates

| Model | Intuition | Limitation |
|---|---|---|
| Dummy baseline | Always outputs the training positive share | Does not learn from ticket content. |
| Logistic Regression | Adds weighted feature contributions and converts the sum to a score | Captures a linear boundary in the transformed features. |
| kNN, k=5 | Finds similar historical tickets and votes | Distance can be less useful in high-dimensional text. |
| Random Forest, 100 trees | Combines many decision trees | More complex; text is sparse and correlations can split importance. |
| AdaBoost, 50 learners | Fits weak learners sequentially, increasing attention to mistakes | Can struggle with noisy labels; not guaranteed to win. |

These are small fixed configurations, not an exhaustive hyperparameter search. This keeps the project teachable and quick to rerun. Model selection uses **average precision**, a ranking metric interpreted relative to the positive share. It is separate from the operating cutoff.

## The threshold and why accuracy is not enough

The score alone is not a decision. Predict 1 when `score >= threshold`. Lowering the cutoff usually increases both caught positives and false alarms. Precision may decrease; recall usually increases. The cutoff does not retrain the model or change its scores.

The training script evaluates 91 candidate cutoffs from 0.05 through 0.95 on validation data. Among those meeting the desired validation recall, it maximizes F2; if none meet the goal, it uses the best F2 and records that the goal was missed. Desired validation recall is not a guarantee on the test set or future tickets.

F2 = 5 * precision * recall / (4 * precision + recall). It weights recall more strongly than F1. The saved operating policy is intentionally recall-focused and can create a large review workload. A real team would choose a validation-based policy using staff capacity and measured error costs.

## Read a confusion matrix

| | Predicted standard | Predicted escalation |
|---|---|---|
| Actual standard | TN: correct routine | FP: false alarm |
| Actual escalation proxy | FN: missed positive | TP: caught positive |

Accuracy = (TP+TN)/all. Precision = TP/(TP+FP). Recall = TP/(TP+FN). F1 balances precision and recall. ROC-AUC measures how often positives rank above negatives across cutoffs. Average precision summarizes the precision-recall curve. Brier score measures squared error of score estimates; lower is better.

In an imbalanced problem an always-negative predictor can have high accuracy while catching no positives. This project's recall-focused cutoff can have lower accuracy than that predictor, while catching many more positives. Neither fact alone establishes that the policy is useful: look at both the error costs and the number of alerts.

## Understand the actual included run

Read `reports/RUN_SUMMARY.md`. It reports the values calculated by the code, not manually entered scores. On the included run Logistic Regression was selected; the cutoff was 0.12. The frozen test set contains 600 tickets and 198 positives. It caught 186 positives, missed 12, and incorrectly flagged 253 standard tickets. Thus 439 of 600 tickets were flagged, precision was about 42.4%, recall 93.9%, and accuracy 55.8%. The test positive share was 33%, and average precision was about 0.666.

This is a useful ranking model on this synthetic task, paired with an aggressive review policy. It is not ready for deployment. You can demonstrate a stricter cutoff on validation data to show how workload changes without using test results to select a new operating policy.

## Explainability without overclaiming

Permutation importance shuffles one raw input column on validation data and measures the drop in average precision. A bigger drop suggests greater predictive reliance. This explains global reliance, not the reason for one individual decision, and it is not causal evidence. Correlated inputs may divide importance. Error bars here are standard deviations across five shuffles.

The app labels score percentages as uncalibrated. A value of 0.80 does not establish that 80% of similar real tickets will escalate. Calibrating on representative data and checking reliability would be a separate experiment.

## How to move to real data

1. Define whether the target is priority or a later recorded escalation. For later escalation, define a prediction time and horizon, and avoid unresolved/censored labels.
2. Keep only features available at that prediction moment. An arrival-time model cannot use first-response wait.
3. Remove identifiers and personal details from text, and establish permission to use the dataset.
4. Split chronologically and/or by customer before preprocessing so repeat customers and future information do not cross partitions.
5. Select configurations and thresholds without test access. Check calibration, subgroup behavior, workload and error costs.
6. Validate on new tickets, keep agents in the decision process, and monitor drift after a controlled pilot.

These are future deployment steps; they are not claims about the included classroom prototype.
