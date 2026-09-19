# Completed local run

Model: Llama-3.2-1B-Instruct, 4-bit MLX conversion, executed on this Mac's Apple GPU.

- Base parameters: 1,235,814,400; trainable QLoRA parameters: 851,968.
- Training: 120 optimizer steps, 512 synthetic examples, 121.9 seconds.
- Eight development sanity checks: 50.0% base agreement → 62.5% tuned agreement.
- Separate 128-example synthetic holdout: 50.0% → 75.0%.
- Inference: 215.6 seconds; 1,000 validated output rows, 988 unique IDs.
- Adapter save/reload verified. All notebook code cells completed without errors.
- Prediction counts: 398 flagged, 602 not flagged; these are predictions, not verified fraud labels.

No genuine fraud labels were provided. Synthetic holdout examples share the training scenario generator with a different seed, so agreement is not real-world fraud accuracy. Confidence is uncalibrated. Initial experiment results are retained under outputs/experiments/.

Submit Fraud_Sentinel_executed.ipynb or fraud_sentinel_submission.zip as required by the platform. The model weights stay locally in models/ and are reproducibly downloadable by pinned revision; the submission ZIP includes the adapter rather than the full base weights.
