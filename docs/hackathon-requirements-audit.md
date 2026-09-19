# Hackathon requirements audit

Audited against the problem statement supplied in the project conversation. This review checks the executed baseline, current public script, saved adapter, and existing prediction files. It does not retrain the model or resume the paused extended-metrics task.

## Conclusion

The end-to-end baseline has run successfully and produces the required JSON. Model loading, actual fine-tuning, adapter reload, inference, and output validation are complete for the supplied files. The full claim of cleaning all account/customer metadata is not yet supported; that scope should be resolved before treating every requirement as closed and moving to extensions.

## Requirement mapping

| Requirement | Finding | Evidence |
| --- | --- | --- |
| Process all three datasets | Pass for supplied files | 1,000 transaction rows, 178 accounts, 124 customers are read |
| Clean transaction anomalies | Pass for model inputs | Typed numeric/boolean/date parsing; unusable values become null; duplicate input rows reuse predictions |
| Clean account/customer metadata | Partial | Whitespace normalization, missing sentinels for row completeness, duplicate resolution, and key linkage exist; most metadata fields are excluded rather than fully normalized |
| Consolidate relational data | Pass, limited feature scope | Account owner/customer lookups produce match/conflict flags; this is not a full joined export of every source column |
| Neutralize prompt injections before model context | Pass for tested boundary | Prompts contain fixed instructions and typed allowlisted features; notes, names, category text, and source IDs are excluded |
| Use an open-weight model below 3B | Pass | Llama-3.2-1B-Instruct, public 4-bit MLX conversion; 1,235,814,400 base parameters |
| Actually fine-tune | Pass | 120 QLoRA optimizer steps on 512 synthetic examples; 851,968 trainable parameters; adapter saved and reload verified |
| Show performance improvement | Demonstrated only on synthetic checks | Separate 128-row synthetic holdout agreement rose from 50% to 75%; genuine fraud performance is unknown |
| Exact JSON schema per record | Pass | All 1,000 outputs have the four required fields, correct types, finite confidence in [0,1], and a single-sentence justification |
| Top-to-bottom notebook execution | Pass for the saved local submission | Eight code cells have execution counts and no saved errors |
| Export script/notebook | Pass | Local executed notebook and submission ZIP exist; runnable source notebook and Python script are public |
| Public GitHub repository | Pass | https://github.com/Vinay1656/fraud-sentinel |
| Submission before the organizer deadline | Not established by code execution | No platform submission has been performed; the organizer's timer is not available to this audit |

## Checks repeated during this audit

- Revalidated `outputs/predictions.json` against all original transaction IDs and their exact input order: 1,000 rows and 988 unique IDs.
- Required identical predictions for repeated transaction IDs and checked strict output keys/types/ranges.
- Tested injected instruction strings, role-style text, Unicode text, and a 10,000-character payload in excluded fields; none changed the model prompt.
- Tested malformed amount/date values, an unknown account, nonfinite numbers, mixed boolean encodings, and dimension duplicate resolution.
- Confirmed the actual model parameter count, training steps, and adapter reload flag from the completed run.
- Confirmed all eight code cells in the executed notebook completed without recorded errors.

Among the 988 unique transactions, the saved preprocessing audit reports 27 unusable amounts, 75 unusable timestamps, and eight unmatched account references. Source rows are preserved; missing data is not silently replaced with zero.

The supplied version has no notes column, no duplicate account/customer primary IDs, and no nonempty credit limits that fail the generic numeric parser used in this audit. Those observations do not prove future faulty account metadata is fully handled.

## Remaining baseline work

1. Add explicit typed cleaning and quality flags for the account/customer columns that the solution claims to support, including credit limits; export or document the cleaned dimension tables. Add fixtures for corrupt dimension metadata rather than relying only on this supplied file version.
2. Document which relational attributes contribute to risk and which are deliberately excluded because their point-in-time provenance is unknown. Do not call existing linkage flags a complete merge of all metadata.
3. Keep the synthetic-only training/evaluation limitation visible. Obtain genuine labels before claiming real fraud precision, recall, F1, or calibrated confidence; extended metric work remains paused for now.

## Output behavior and portability

The model provides the risk decision. Python serializes JSON and builds a sentence from observed evidence. Confidence is an uncalibrated relative model score, not a verified fraud probability. Output is written as a JSON array to `outputs/predictions.json`; runtime logs are separate from that file. A unique-ID alternative is also exported.

The verified notebook uses Apple MLX and targets Apple Silicon. It is not a CUDA/Colab notebook. The public source notebook intentionally omits local output cells; the fully executed notebook remains in the local submission folder.

Measured final-run training and transaction inference took about 122 and 216 seconds respectively, excluding installation, download, and preparation. This does not establish compliance with an unknown remaining organizer deadline.
