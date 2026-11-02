# Data dictionary

`data/complaints.csv`: 3,000 fictional labelled tickets; 17 columns. `data/batch_examples.csv`: 20 separately generated unlabelled tickets. `data/batch_template.csv`: header-only input template. Generator seed and file hash are in `data/dataset_manifest.json`.

## Model inputs

| Column | Type / values | Timing and handling |
|---|---|---|
| `product` | Laptop, Phone, Headphones, Smartwatch, Tablet | Known at first review. Empty cells become Unknown; new categories are accepted. |
| `ticket_type` | Technical issue, Billing inquiry, Refund request, General inquiry | Known at review; one-hot encoded. |
| `subject` | Device not working, Payment problem, Delivery delay, Account access, Product question | Categorical topic, separate from free text. |
| `channel` | Email, Chat, Phone, Social media | Submission channel; one-hot encoded. |
| `response_hours` | Number from 0 through 720 | Elapsed hours from creation to first response. Empty cells use the training median. May instead be derived from two timestamps. |
| `previous_contacts` | Whole number from 0 through 50 | Prior contacts about this issue, known at review. Empty cells use the training median. |
| `complaint_text` | Text, up to 5,000 characters | Text available before the score. Empty cells get `no description provided`; TF-IDF learns its vocabulary only from training. |

CSV column names are case-sensitive. Missing required columns are rejected. An empty cell is different from an absent column. Category values are case-sensitive and are trimmed of surrounding whitespace. Numeric cells can be empty but cannot be negative, infinite, or nonnumeric.

## Identity, timestamps and labels

| Column | Purpose | Used as a model feature? |
|---|---|---|
| `ticket_id` | Synthetic unique ID; retained for traceability | No |
| `created_at` | ISO timestamp with timezone; ticket creation | No; only used to derive/validate elapsed hours |
| `first_response_at` | ISO timestamp; first response | No; only used to derive/validate elapsed hours |
| `priority` | Low / Medium / High / Critical | No; defines the priority-based target |
| `escalation_required` | 0 for Low/Medium, 1 for High/Critical | Target only |

When both timestamps are present and valid, `response_hours` can be absent or empty. If both a duration and timestamps are supplied, they must agree within 0.02 hours. Dates must be ISO 8601, for example `2025-06-01T23:00:00Z`. Negative elapsed durations or waits over 720 hours are rejected. Two empty timestamps leave the duration missing for imputation.

For training, all labels must be present. Either provide a 0/1 target or derive it from priority. When both are present, contradictory labels are rejected. Each training ID must be unique after exact duplicate removal. If no ID column is supplied, row IDs are created.

## Included teaching fields, excluded from modeling

| Column | Meaning | Reason excluded |
|---|---|---|
| `customer_age` | Fictional integer, 18-80 | No established need for demographic triage |
| `customer_gender` | Fictional category | No established need for demographic triage |
| `final_status` | Fictional Open/Pending/Closed lifecycle snapshot | May be determined after the prediction moment |
| `satisfaction_rating` | Fictional 1-5 rating for closed tickets; otherwise missing | Post-resolution field; intentional leakage example |
| `data_source` | Literal `synthetic` | Provenance metadata, not a predictive signal |

The synthetic generator uses hidden severity, response wait, previous contacts and ticket context to form a noisy probability. It draws a binary outcome, then assigns a consistent priority. Similar tickets can therefore have different labels. Missing inputs are injected deliberately. No latent severity column or true generating probability is exported as a feature.

## Prediction exports

The input rows are preserved in order, with these added columns:

| Column | Meaning |
|---|---|
| `escalation_score` | Model score between 0 and 1 for the priority proxy |
| `decision_threshold` | Cutoff used for the decision |
| `predicted_escalation` | 1 if score is at least the cutoff; otherwise 0 |
| `recommendation` | Escalate for review / Standard support review |
| `missing_input_cells` | Number of missing numeric/category cells after duration derivation |

The missing-input count does not count blank text; blank text uses the documented placeholder. CSV exports prefix formula-like text with an apostrophe to keep spreadsheet software from interpreting it as a formula. This can change that exported text representation; it does not change the text used for prediction.
