# Recorded local run

This report describes the completed run on the supplied hackathon files, which are not redistributed here. The public demo generator produces a different dataset; its outputs should not be expected to match these counts.

| Item | Recorded value |
| --- | --- |
| Base model | Llama-3.2-1B-Instruct, public 4-bit MLX conversion |
| Base parameters | 1,235,814,400 |
| Trainable adapter parameters | 851,968 |
| Training examples | 512 synthetic scenarios |
| Optimizer steps | 120 |
| Training time | 121.9 seconds |
| Inference time | 215.6 seconds |
| Original transaction rows | 1,000 |
| Unique transaction IDs | 988 |
| Schema-valid output rows | 1,000 |
| Adapter reload | Verified against pre-save scores |

## What was evaluated

Agreement on eight development sanity checks improved from 50.0% to 62.5%. Agreement on a separate 128-example synthetic holdout improved from 50.0% to 75.0%.

The holdout uses a different random seed but shares the training scenario generator. It therefore measures agreement with synthetic assumptions, not real-world fraud accuracy. The provided transaction files have no genuine fraud labels. Extended precision/recall/F1 reporting is pending and is not claimed here.

The model flagged 398 of the 1,000 input rows; 602 were not flagged. These are model predictions, not confirmed fraud outcomes. Confidence is uncalibrated.

The source CSV hashes were checked, duplicate predictions were consistent, input order was preserved, and all notebook code cells completed without errors. An initial experiment with inconsistent synthetic number formatting is retained locally for traceability; the reported final run uses consistently rounded values.

The executed submission notebook, adapter, model weights, and raw files remain local. The public [notebook](../notebooks/fraud_sentinel.ipynb) and [pipeline](../scripts/train_and_predict.py) reproduce the workflow when given inputs and the documented runtime. The [presentation](presentation.pptx) includes the measured results and limitations.
