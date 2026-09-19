# Offline data-quality dashboard

Download `quality.html` using GitHub's Download raw file button, then open it in any modern browser. It is a self-contained file: no Python, Apple Silicon, model download, network access, or web server is needed to view and filter it. GitHub's normal HTML file page shows source, not the rendered dashboard.

To regenerate it from the published checkpoint using Python 3.11:

```sh
python scripts/build_dashboards.py
```

The build verifies checkpoint hashes and cross-checks transaction counts against the saved features. It never retrains or edits predictions. All rendering escapes source text. Transaction denominators use 988 unique transactions, not 1,000 source rows. Metadata denominators use their respective input rows. The affected-row total is a union, not a sum of overlapping issue counts. Missing optional metadata is not evidence of fraud.

Tests: `PYTHONPATH=src python -m unittest discover -s tests -v`. To additionally exercise real browser controls, set `CHROME_BINARY` to a Chrome executable. No browser automation library is required.
