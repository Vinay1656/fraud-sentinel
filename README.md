# Fraud Sentinel

A local pipeline for cleaning relational transaction data, screening it with Llama 3.2, and producing auditable JSON predictions.

Built for **The Relational Data Wrangler & Fraud Sentinel** hackathon. The working baseline runs on an Apple Silicon Mac; it includes a reproducible notebook, a Python pipeline, and a presentation.

## What works today

- Joins transactions, accounts, and customers while tracking missing links and duplicates.
- Cleans all supplied account/customer columns with typed values, quality flags, and quarantine exports.
- Keeps raw notes and arbitrary strings out of model prompts.
- Fine-tunes Llama-3.2-1B-Instruct with QLoRA using Apple MLX.
- Saves and reloads adapters, then produces exactly four JSON fields per transaction.
- Preserves input order and checks output types, confidence values, and duplicate consistency.

## Start here

- [Offline data-quality dashboard](docs/dashboard/README.md) — browser-only viewing, no MLX dependencies.
- [Runnable notebook](notebooks/fraud_sentinel.ipynb)
- [Executed notebook with visible results](notebooks/executed_results.ipynb)
- [Presentation](docs/presentation.pptx)
- [Recorded run](docs/results.md)
- [Extension roadmap](docs/roadmap.md)
- [Data strategy](docs/data-strategy.md)
- [Metadata cleaning](docs/metadata-cleaning.md)
- [Prompt-injection guardrail](docs/prompt-injection.md)
- [Submission checks](docs/submission-checklist.md)

## Run on Apple Silicon

Python 3.11 or later is required. The tested machine has 16 GB unified memory. Initial setup downloads a pinned 4-bit MLX conversion of Llama-3.2-1B-Instruct; no cloud inference service is used.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e . -r requirements-mlx.txt
python scripts/create_demo_data.py --output-dir data/raw
python scripts/train_and_predict.py
```

The demo generator creates fictional CSVs and refuses to overwrite existing inputs. To run with the hackathon files, put `transactions.csv`, `accounts.csv`, and `customers.csv` in `data/raw/` instead. The notebook uses the same inputs. For Jupyter, run `python -m pip install jupyterlab` in that environment, then `python -m jupyter lab` from the repository root and open the notebook. The MLX backend requires Apple Silicon; GitHub displays notebooks but does not execute them.

Predictions and reports appear in `outputs/`, and adapters in `adapters/llama_fraud_qlora/`. Running the pipeline again retrains from the base checkpoint and replaces generated outputs. The runnable notebook has clean output cells. A separate executed-results notebook retains aggregate execution evidence without individual customer/transaction examples.

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

The supplied dummy CSVs are public in `data/raw/`, with user authorization. The trained adapter and recorded results are public in `artifacts/checkpoint-1/`. Downloaded base weights and working output directories remain excluded from Git. The model source is [mlx-community/Llama-3.2-1B-Instruct-4bit](https://huggingface.co/mlx-community/Llama-3.2-1B-Instruct-4bit), revision `08231374eeacb049a0eade7922910865b8fce912`.

## Checks

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```

These checks run without a GPU. Model training and full inference require Apple Silicon and the MLX dependencies.

## Development checkpoints

Commit a working, verified increment at each checkpoint. Planned extensions are tracked separately from working features; the next proposal is a sector risk heatmap with a linked investigation queue.

## Published trained checkpoint

[Adapter, predictions, cleaned data, and loading instructions](artifacts/checkpoint-1/README.md). [Download checkpoint ZIP](https://github.com/Vinay1656/fraud-sentinel/releases/tag/checkpoint-1). Built with Llama. The base model is not bundled; its exact download revision and upstream terms are included.
