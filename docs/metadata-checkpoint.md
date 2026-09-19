# Metadata-cleaning checkpoint

The baseline metadata gap is closed. The complete notebook rerun cleaned and retained 178 accounts and 124 customers, retrained the Llama adapter, verified adapter reload, and exported 1,000 prediction rows for 988 unique transactions.

- All supplied dimension columns have documented parsing rules and field-level quality flags.
- Zero credit limits, signed balances, and over-limit utilization are preserved appropriately.
- Missing/invalid primary IDs are quarantined; duplicate conflicts retain source lineage.
- A full cleaned metadata join is exported locally, while private fields remain outside model prompts.
- Nineteen CPU tests pass. The PowerPoint now includes this checkpoint.
- Training time: 122.4 seconds; inference time: 218.9 seconds.
- Synthetic holdout agreement: 50% base → 75% tuned; this is not genuine fraud accuracy.

Local cleaned metadata outputs contain private fields and are excluded from Git. Additional training-data work and product extensions remain separate checkpoints.
