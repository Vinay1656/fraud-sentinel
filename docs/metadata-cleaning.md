# Account and customer metadata cleaning

The pipeline applies explicit parsing rules to all 21 supplied account columns and all 26 supplied customer columns before selecting dimension rows and joining them to transactions. The implementation is in `src/fraud_sentinel/metadata.py`; the standalone notebook embeds the same code.

## Rules

| Field group | Policy |
| --- | --- |
| Primary and relationship IDs | Trim; allow bounded alphanumeric IDs with underscores/hyphens; missing or invalid primary IDs are quarantined |
| Balances | Finite signed numbers; valid negative balances remain negative |
| Credit limit and annual income | Finite nonnegative numbers; zero is valid; missing/corrupt values become null |
| Utilization and transaction averages | Finite nonnegative values; utilization over 100 is retained with a flag |
| Counts and age | Nonnegative integers; fractional counts are invalid; age uses an explicit 0–120 plausibility range |
| Dates | Validate ISO calendar dates, including leap years; flag inconsistent date ordering without guessing a correction |
| Booleans | Normalize Y/N, yes/no, true/false, and 1/0 to actual booleans |
| Currency and country | Uppercase codes with three/two letters respectively; format validation is not membership verification |
| Categorical labels | Trim, uppercase, and normalize spaces; labels are not inferred from a closed domain vocabulary |
| Email and phone | Validate structure and normalize formatting; this does not verify contact ownership |
| Names, locations, occupation, postal code | Trim bounded text; preserve leading zeros in string fields; reject control characters |

Correctly grouped thousands separators are accepted in numbers. Invalid numbers, nonfinite values, and malformed grouping are rejected. Sentinel values remain null. Literal `NONE` is retained as a categorical label so a legitimate no-card value is not lost.

Missing and invalid are different audit categories. A missing optional field, such as the close date of an open account, is not proof of a defect or fraud. Quality flags record availability and inconsistencies; the model does not receive these arbitrary strings.

## Duplicate and relationship handling

For repeated dimension IDs, select the row with the fewest invalid fields, then the most populated cleaned fields; ties retain source order. Do not invent a composite customer by merging conflicting values. Preserve source line numbers, all cleaned source rows, and field-level duplicate conflict flags. Unmatched account-to-customer references are flagged.

The full cleaned account/customer records are linked to unique transactions in `consolidated_metadata.json`. Only the pre-existing numeric/boolean model feature allowlist is sent to Llama. Contact information, demographic fields, and account snapshots stay out of prompts; their inclusion in a local cleaned join is not a claim that they are suitable predictors or historically available at transaction time.

## Local outputs

- `accounts_cleaned.json` and `customers_cleaned.json`: selected, typed dimension records with quality flags.
- `accounts_cleaned_source_rows.json` and `customers_cleaned_source_rows.json`: all cleaned source rows before duplicate selection.
- `accounts_quarantine.json` and `customers_quarantine.json`: rows whose primary IDs cannot be used safely.
- `metadata_quality.json`: counts by table, field, and issue category.
- `consolidated_metadata.json`: transaction ID plus its linked cleaned account/customer records.

These files live under `outputs/` and can contain personal information. They remain excluded from Git and the public notebook's output cells. Original source CSVs are unchanged.

## Verification

Regression fixtures cover corrupt credit limits, zero limits, signed balances, missing sentinels, invalid dates, over-limit utilization, malformed contacts, conflicting duplicate owners, quarantined IDs, and unmatched relationships. The supplied files retain all 178 account IDs and 124 customer IDs. No external data is needed to verify these parsing rules; additional training data is tracked separately in the data strategy.
