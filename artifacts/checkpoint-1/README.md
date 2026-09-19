# Llama-3.2 Fraud Sentinel: trained checkpoint

Built with Llama. This package contains the actual trained MLX QLoRA adapter, not a merged standalone model. The frozen base weights are downloaded separately from the exact revision in `model_provenance.json`.

## What is included

- `adapter/`: saved rank-8 QLoRA weights and configuration; 851,968 trainable parameters across 16 layers, query/value projections.
- `results/`: all 1,000 predictions, 988 unique predictions, cleaned metadata, audits, validation, evaluation, and the 512 synthetic training examples.
- `SHA256SUMS.json`: integrity hashes for the checkpoint files.
- `UPSTREAM_MODEL_CARD.md`: original base-model documentation and embedded Llama 3.2 license terms. Those terms and its linked acceptable-use policy apply; this is not an unrestricted model license.

The user confirmed the supplied CSVs are dummy hackathon data and authorized public publication. Originals are in `data/raw/`. The synthetic training labels are heuristic scenarios, not genuine fraud labels. The 128-example holdout shares the training generator: agreement increased from 50% to 75%, which does not establish real-world accuracy. Confidence is uncalibrated.

## Load without retraining (Apple Silicon, Python 3.11)

From the repository root, install `requirements-mlx.txt` in a virtual environment. Then:

```python
from huggingface_hub import snapshot_download
from mlx_lm import load

base = snapshot_download(
    'mlx-community/Llama-3.2-1B-Instruct-4bit',
    revision='08231374eeacb049a0eade7922910865b8fce912',
)
model, tokenizer = load(base, adapter_path='artifacts/checkpoint-1/adapter')
```

This loads the trained model; it does not itself execute the full scoring pipeline. The runnable notebook demonstrates the typed feature prompt and SAFE/FRAUD likelihood scoring, but its Run All path retrains. Saved predictions can be inspected on any platform without MLX. Model loading requires Apple Silicon and internet access for the initial base download. The original completed run verified adapter reloading before generating predictions.

## Training recipe

Frozen 4-bit Llama-3.2-1B-Instruct; QLoRA rank 8, scale 2, dropout 0.05; q_proj/v_proj in all 16 layers; seed 42; batch size 4; 120 optimizer steps. Only answer tokens contribute to loss. See the notebook and evaluation report for the complete implementation and measured run.
