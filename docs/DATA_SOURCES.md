# Sample data and sources

Checked November 2, 2026. The classroom demo runs entirely on included synthetic data. External datasets below are optional sources for future experiments; none was downloaded or used to train the delivered model.

## Exact files to show your teacher

| File inside the project | What it contains | Use |
|---|---|---|
| `data/complaints.csv` | All 3,000 labelled synthetic tickets, 17 columns | Exact sample used for the 60/20/20 experiment |
| `data/teacher_preview.csv` | First 12 rows of that file; ID, seven inputs, priority and target | Easy column explanation; not a performance benchmark |
| `data/batch_examples.csv` | 20 separately generated unlabelled tickets | Batch upload and prediction demo |
| `data/demo_scenarios.csv` | Exact three fictional examples offered by the prediction form | Rehearse routine, disruption and billing examples |
| `data/batch_template.csv` | Header-only input template | Prepare another CSV in the accepted format |

Separate copies outside the project use descriptive names: `Sample_Data_3000_Tickets.csv`, `Teacher_Preview_12_Tickets.csv`, `Batch_Demo_20_Tickets.csv` and `Live_Demo_3_Scenarios.csv`. The full dataset copy is byte-for-byte identical to `data/complaints.csv`. Its SHA-256 is recorded in `data/dataset_manifest.json` and the model metadata.

Say: "I generated fictional customer tickets in Python so the prototype is reproducible and contains no real customers. High/Critical priority defines the positive label. The CSV I am showing is the same sample used by the experiment."

The generator uses seed 42. It combines varied complaint wording and ticket context with noisy random outcomes. Missing inputs are deliberate. All seven feature values are selected explicitly; priority and the target never enter the model as inputs.

## Optional external sources

### Kaggle: Customer Support Ticket Dataset (Suraj520)

[Dataset page](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset)

This is the source attributed by the supplied presentation. The page describes technology-product tickets with descriptions, product, ticket type, priority, channel, response time and satisfaction. It lists a CSV and a CC0 license. A download may require a Kaggle sign-in. We verified the page, not the complete downloaded CSV.

This would be the closest source for a future priority-classification experiment. Rename and validate columns; inspect how response time is stored; do not infer elapsed waiting time from a clock hour. The app also expects prior-contact counts, which must be genuinely available or handled as missing. Use only information available at the chosen prediction time. The listed fields do not establish an observed future-escalation target.

### CFPB: Consumer Complaint Database

[Official data page](https://www.consumerfinance.gov/data-research/consumer-complaints/) · [Field reference](https://cfpb.github.io/api/ccdb/fields.html)

The US Consumer Financial Protection Bureau provides downloadable financial-service complaint data, filters and an API. It is useful for a different complaint-text research project. CFPB states that these complaints are not a statistical sample representative of all consumers' experiences.

The domain and schema differ from this technology-product demo. A meaningful target and prediction time must be defined from suitable available fields; this is not a ready-to-upload replacement for the current training CSV. Do not invent High/Critical or future-escalation labels simply to reuse the app.

## Tomorrow's recommendation

Use the included files for the live presentation. Mention these sources as future work. Downloading, adapting and retraining on a new dataset during the presentation adds uncertainty and changes the results you rehearsed.
