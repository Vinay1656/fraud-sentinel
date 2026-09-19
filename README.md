# Fraud Sentinel

A local pipeline for cleaning relational transaction data, screening it with Llama 3.2, and producing auditable JSON predictions.

Built for **The Relational Data Wrangler & Fraud Sentinel** hackathon. The working baseline runs on an Apple Silicon Mac; it includes a trained-run notebook, a reproducible Python pipeline, and a presentation.

## What works today

- Joins transactions, accounts, and customers while tracking missing links and duplicates.
- Keeps raw notes and arbitrary strings out of model prompts.
- Fine-tunes Llama-3.2-1B-Instruct with QLoRA using Apple MLX.
- Saves and reloads adapters, then produces exactly four JSON fields per transaction.
- Preserves input order and checks output types, confidence values, and duplicate consistency.

## Start here

- [Notebook](notebooks/fraud_sentinel.ipynb)
- [Presentation](docs/presentation.pptx)
- [Recorded run](docs/results.md)
- [Extension roadmap](docs/roadmap.md)
- [Data strategy](docs/data-strategy.md)

## Run on Apple Silicon

Python 3.11 or later is required. The tested machine has 16 GB unified memory. Initial setup downloads a pinned 4-bit MLX conversion of Llama-3.2-1B-Instruct; no cloud inference service is used.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e . -r requirements-mlx.txt
python scripts/create_demo_data.py --output-dir data/raw
python scripts/train_and_predict.py
```

The demo generator creates fictional CSVs and refuses to overwrite existing inputs. To run with the hackathon files, put `transactions.csv`, `accounts.csv`, and `customers.csv` in `data/raw/` instead. The notebook uses the same inputs; open it with the environment above and run all cells.

Predictions and reports appear in `outputs/`, and adapters in `adapters/llama_fraud_qlora/`. Running the pipeline again retrains from the base checkpoint and replaces generated outputs. The public notebook omits local execution output; the original executed submission remains available locally.

## Output

```json
{
  "transaction_id": "DEMO_TXN_00001",
  "is_fraud": true,
  "confidence": 0.82,
  "justification": "A new device accompanies an unusually large transaction."
}
```

This example illustrates the schema. Confidence is an uncalibrated model score, not a proven probability of fraud.

## Recorded results and limits

The completed local run used 120 QLoRA steps and generated 1,000 valid prediction records from 988 unique transactions. Agreement on 128 held-out synthetic examples increased from 50% to 75%. Those examples share a generator with the synthetic training set; these numbers do not establish performance on genuine unseen fraud.

The provided CSVs have no fraud labels. Real-world precision, recall, and F1 remain unknown. Extended metric reporting is pending; it is not presented as completed. See [results](docs/results.md) for the measured scope.

## Repository layout

```text
notebooks/          runnable notebook
scripts/            training pipeline and synthetic demo generator
src/fraud_sentinel/ reusable output validation
tests/              CPU-only contract and demo-data checks
docs/               presentation, results, roadmap, and data plan
```

Original customer data, downloaded weights, trained adapters, local outputs, and submission archives are excluded from Git. The model source is [mlx-community/Llama-3.2-1B-Instruct-4bit](https://huggingface.co/mlx-community/Llama-3.2-1B-Instruct-4bit), revision `08231374eeacb049a0eade7922910865b8fce912`.

## Checks

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```

These checks run without a GPU. Model training and full inference require Apple Silicon and the MLX dependencies.

## Development checkpoints

Commit a working, verified increment at each checkpoint. Planned extensions are tracked separately from working features; the next proposal is a sector risk heatmap with a linked investigation queue.
