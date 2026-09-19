# Hackathon requirements audit

Audited against the problem statement supplied in the project conversation. This review checks the executed baseline, current public script, saved adapter, and existing prediction files. It does not retrain the model or resume the paused extended-metrics task.

## Conclusion

The end-to-end baseline has run successfully and produces the required JSON. Model loading, actual fine-tuning, adapter reload, inference, and output validation are complete for the supplied files. The metadata-cleaning gap has now been closed: all supplied dimension columns are typed, audited, and exported, with corrupt-metadata regression fixtures and a complete notebook rerun.

## Requirement mapping

| Requirement | Finding | Evidence |
| --- | --- | --- |
| Process all three datasets | Pass for supplied files | 1,000 transaction rows, 178 accounts, 124 customers are read |
| Clean transaction anomalies | Pass for model inputs | Typed numeric/boolean/date parsing; unusable values become null; duplicate input rows reuse predictions |
| Clean account/customer metadata | Pass for supported schema | All 21 account and 26 customer columns have typed rules, field flags, deterministic duplicate handling, quarantine, and local cleaned exports |
| Consolidate relational data | Pass | Cleaned dimensions are linked and exported per unique transaction; only the documented safe feature subset enters model prompts |
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

## Metadata checkpoint completed

Explicit dimension cleaning, cleaned/quarantined/source-row exports, and a full nested metadata join are implemented. Nineteen CPU tests pass, including dedicated corrupt-metadata and prompt-injection fixtures. The updated notebook completes top to bottom and produces 1,000 schema-valid records. See metadata-cleaning.md for rules and exclusions.

No additional data was needed for this cleaning checkpoint. Genuine fraud labels and an independent real-world benchmark remain unavailable. Extended metric work remains paused. Submission to the organizer's platform is still a separate action.

## Output behavior and portability

The model provides the risk decision. Python serializes JSON and builds a sentence from observed evidence. Confidence is an uncalibrated relative model score, not a verified fraud probability. Output is written as a JSON array to `outputs/predictions.json`; runtime logs are separate from that file. A unique-ID alternative is also exported.

The verified notebook uses Apple MLX and targets Apple Silicon. It is not a CUDA/Colab notebook. The public source notebook intentionally omits local output cells; the fully executed notebook remains in the local submission folder.

Measured final-run training and transaction inference took about 122 and 216 seconds respectively, excluding installation, download, and preparation. This does not establish compliance with an unknown remaining organizer deadline.
