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
- The guardrail demo displays a fixed prompt produced by the actual pipeline functions. The build tests five attacks. Browser note edits are inert text excluded from that prompt, not live Python execution or model inference. The full regression suite separately tests the pipeline boundary.
- No customer blocking, messaging, live transactions, new model predictions, or persistent analyst decisions occur.

The analyst build additionally verifies original CSV hashes and exact prediction IDs/order. A changed dataset requires a new matching pipeline checkpoint; the dashboard refuses to combine mismatched snapshots.
