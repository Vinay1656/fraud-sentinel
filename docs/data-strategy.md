# Data strategy

The three original hackathon CSVs remain local. They contain customer information and are not redistributed in the public repository. Public demos use fictional records created by `scripts/create_demo_data.py`.

The existing model uses 512 synthetic training scenarios and a separate 128-example synthetic holdout. A separate seed prevents exact row overlap but does not create an independent real-world benchmark. New data work must improve scenario coverage and evaluation independence, not just increase row counts.

## Expand useful coverage first

Generate chronological customer/account histories, then inject controlled fraud scenarios and independent data defects. Cover ordinary travel, a legitimate new phone, planned large purchases, refunds, payroll bursts, and repeat subscriptions as well as rapid transfers, new-device/location combinations, and unusually high spending. Include multiple sectors and channels for the dashboard.

Keep decimal formatting, ID patterns, missingness, and text length independent of class labels unless they are deliberately studied features. The initial run showed why this matters: inconsistent decimal precision created an artificial learning shortcut.

Use separate partitions by customer/account and time before fitting preprocessing or generating training augmentations. Hold out entire scenario families and independently author test cases. Keep an imbalanced operational evaluation set separate from any class-balanced training sample. Test on several prevalence assumptions instead of equating the current 50/50 synthetic mix with real traffic.

Do not inflate the dataset simply by paraphrasing the same examples. Synthetic rows provide known assumptions, not verified real fraud labels.

## Candidate external sources

| Source | Potential use | Important limitation |
| --- | --- | --- |
| [Fraud Detection Handbook simulator](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_3_GettingStarted/SimulatedDataset.html) | Customer/terminal/time/amount histories and time-dependent labeled scenarios | It is simulated; labels reflect the simulator's assumptions |
| [PaySim](https://github.com/EdgarLopezPhD/PaySim) | Mobile-money transaction patterns and transfer scenarios | Different domain and schema; simulator/code terms and distributed-data terms must be checked separately |
| [ULB/Worldline credit-card dataset](https://www.kaggle.com/mlg-ulb/creditcardfraud/data) | A separate labeled benchmark for the fields it actually provides | Anonymized features do not supply our customer/account relationships or sector metadata; do not fabricate a relational join |

These are researched candidates, not datasets already integrated into the model. Prefer the handbook-style temporal simulator for a compatible demo and investigate a genuinely labeled benchmark separately. Record source URL, version, license, checksum, column mapping, and label provenance before using any download. Publish retrieval instructions rather than redistributing data when permissions are unclear.

## Source adapters

Keep each dataset in its own namespace and maintain an explicit mapping to supported features. Unknown features remain unknown. Never attach fabricated sectors, locations, or customer identities to externally labeled records and present them as observations. Report results per source before making any pooled claim.

## Improvement gate

Resume the paused metrics work as a separate checkpoint. Fix the evaluation split and threshold policy before retraining. Compare the existing model with the candidate model on the same untouched test set and report precision, recall, F1, a confusion matrix, ranking metrics, runtime, and support counts. Real and synthetic labels must have separate result sections. More data counts as progress only if measured behavior improves without breaking schema validity or the injection boundary.
