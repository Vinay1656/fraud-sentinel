# Offline dashboards

Two independent HTML files are included: `quality.html` for data quality, and `index.html` for the analyst overview, category/channel heatmap, review queue, and prompt-injection demonstration. Keep both in the same directory for navigation between them.

Open the [hosted analyst dashboard](https://vinay1656.github.io/fraud-sentinel/dashboard/) or [hosted data-quality dashboard](https://vinay1656.github.io/fraud-sentinel/dashboard/quality.html) directly. GitHub Pages serves exactly the checked-in static files; nothing is computed on a server.

Download `quality.html` using GitHub's Download raw file button, then open it in any modern browser. It is a self-contained file: no Python, Apple Silicon, model download, network access, or web server is needed to view and filter it. GitHub's normal HTML file page shows source, not the rendered dashboard.

To regenerate it from the published checkpoint using Python 3.11:

```sh
python scripts/build_dashboards.py
```

The build verifies checkpoint hashes and cross-checks transaction counts against the saved features. It never retrains or edits predictions. All rendering escapes source text. Transaction denominators use 988 unique transactions, not 1,000 source rows. Metadata denominators use their respective input rows. The affected-row total is a union, not a sum of overlapping issue counts. Missing optional metadata is not evidence of fraud.

Tests: `PYTHONPATH=src python -m unittest discover -s tests -v`. To additionally exercise real browser controls, set `CHROME_BINARY` to a Chrome executable. No browser automation library is required.

## Analyst interpretation

- All analysis uses the 988 unique cases. The original required JSON still retains all 1,000 source rows; this dashboard does not overwrite it.
- Global filters affect overview, heatmap, and queue. Decision and transaction-ID filters apply only to the queue. Reset clears both sets.
- Merchant category is a sector proxy. Category/channel spelling and whitespace are normalized; missing categories stay UNKNOWN. Low-sample heatmap cells have fewer than 20 cases; this is a display caution, not a statistical test.
- Heatmap rates are model-flag rates, not confirmed fraud rates. Amounts are transaction amounts, not losses, and are kept separate by currency. Unknown amounts are counted, not silently imputed.
- Inspect opens the recorded justification, typed input features, and transaction-level quality warnings. The data-quality view separately covers account/customer metadata. This is not a causal model explanation or a case-management database.
- Download matching JSON exports all matching unique cases (not just the current page) using only the original four schema fields. Empty exports are disabled.
- The guardrail demo lets you choose any of the 988 actual cases and displays its prompt produced by the actual pipeline functions. The build tests five example attacks; regression tests additionally verify three attacks against every unique source transaction. Browser note edits are inert text excluded from that prompt, not live Python execution or model inference.
- No customer blocking, messaging, live transactions, or new model predictions occur. Analyst decisions now persist locally; they are not shared server-side.

The analyst build additionally verifies original CSV hashes and exact prediction IDs/order. A changed dataset requires a new matching pipeline checkpoint; the dashboard refuses to combine mismatched snapshots.

## Feedback capture

1. Click **Inspect** beside a transaction. The page scrolls to its evidence and feedback form.
2. Enter a reviewer alias, assessment, and reason. Optionally add a non-sensitive evidence reference.
3. Click **Save feedback locally**. The case history appends an event; the original prediction stays unchanged. Repeating exactly the latest assessment is a no-op.
4. Use **Export feedback JSON** to back up every event. This is separate from **Download matching JSON**, which exports original model predictions only.
5. Import a backup on the same checkpoint to merge events. Event IDs are deduplicated; conflicting duplicate IDs, unknown transactions, bad schema, and mismatched checkpoints are rejected. Newly imported events append in file order; latest appended event means current assessment, regardless of client timestamps.

Feedback records include event ID, transaction ID, reviewer, assessment, reason, evidence reference, and UTC timestamp. The envelope binds them to hashes of predictions, source transactions, and the trained adapter plus the base-model revision. Every event is explicitly `unverified_analyst_feedback` with `eligible_for_training: false`.

Validate a downloaded backup without loading MLX:

```sh
python scripts/validate_feedback.py /path/to/analyst_feedback.json
```

**Limits:** localStorage belongs to this browser and origin; another device/browser, incognito session, or a downloaded HTML file may have a different store. Clearing browser data loses history. Prefer the hosted HTTPS dashboard, export backups, and do not store real personal data or secrets in notes. Reviewer names and browser-clock timestamps are self-reported; this is not an authenticated or tamper-proof audit system. It is a single-browser prototype, not an atomic multi-user database. Common stale-tab writes are rejected, but use one editing tab at a time. If storage is unavailable, corrupt, or full, the UI reports failure rather than claiming a save. Corrupt stored data is not silently overwritten. Import is capped at 20 MB and 5,000 events; browser quotas may be lower.

Feedback is a foundation for future adjudicated labels—not automatic ground truth. A separate verified-outcome process and leakage-safe evaluation design are required before using these decisions for training. No retraining or precision/recall claims are added here.
