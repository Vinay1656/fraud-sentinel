# Submission readiness

## Verified locally

- The complete metadata-cleaning notebook ran through all eight code cells without errors.
- Llama-3.2-1B-Instruct was fine-tuned for 120 steps and the adapter was reloaded successfully.
- 1,000 prediction records passed the strict four-field schema, original-order, and duplicate-consistency checks.
- All 178 accounts and 124 customers were retained in typed cleaned exports.
- Forty-six regression tests pass, including seven real-browser tests, actual-data injection checks, and notebook installer regressions.
- The public executed-results notebook now records the fresh real-Jupyter verification run, including dependency installation and all inference outputs. Local paths are redacted; transaction examples are authorized dummy data.
- The user confirmed the inputs are dummy hackathon data and authorized publication. Original CSVs, a trained adapter, and recorded outputs are now published in data/raw and artifacts/checkpoint-1. Frozen base weights remain a pinned external download.

## What a reviewer can open

- README: setup instructions, scope, results, and limitations.
- `notebooks/fraud_sentinel.ipynb`: clean runnable source notebook.
- `notebooks/executed_results.ipynb`: recorded outputs from the completed run.
- `docs/presentation.pptx`: downloadable PowerPoint, including the metadata checkpoint.
- `docs/results.md` and `docs/metadata-checkpoint.md`: concise measured results.
- `docs/prompt-injection.md`: guardrail implementation and tested boundaries.

## Execution constraints

The verified runtime is Python 3.11 on an Apple Silicon Mac using MLX. Anyone can inspect the public files, but rerunning training requires compatible hardware, dependencies, input files, and the pinned model download. GitHub is a code/notebook viewer, not a hosted training environment. A synthetic demo generator is provided for users without the hackathon CSVs.

## Interpretation

There are no true fraud labels for the supplied transactions. The 75% result is agreement on synthetic held-out scenarios, not verified real-world fraud accuracy. Extended metrics remain paused. Prompt isolation protects against text instructions crossing the tested boundary; it does not make falsified numeric facts trustworthy or guarantee accurate predictions.

Repository accessibility and the latest commit's hosted checks are verified after pushing this checkpoint. Submission to the organizer's platform is a separate action.

## Judge-readiness rerun

See [judge walkthrough](judge-review.md) and [measured verification report](judge-review-report.json). The current notebook was run from top to bottom in a real Jupyter kernel after fixing shell expansion in its installer. The README no longer attempts to regenerate data over the already-included CSVs. The live dashboard and release artifacts were checked separately. Model execution still requires Apple Silicon; browser demos do not.
