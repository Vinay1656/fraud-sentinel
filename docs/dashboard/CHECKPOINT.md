# Dashboard checkpoint verification

The smaller data-quality dashboard was tested and pushed first (`5b41e1a`), before implementing the connected analyst dashboard.

## Verified locally

- 35 tests pass with Chrome enabled: 31 Python contract/regression tests and four browser tests. The mobile test exercises both pages at a true 390-pixel viewport.
- Browser checks cover table/field filters, heatmap drilldown, pagination, case evidence, empty states, export schema and Blob creation, separate-currency sums, hand-calculated heatmap rates, low-sample warnings, and inert malicious-note rendering.
- Dashboard builds validate recorded artifact hashes; analyst builds additionally validate original CSV hashes and prediction IDs/order. Tests require checked-in HTML to match the builder output.
- The same recorded 1,000 predictions remain untouched. Analyst counts use 988 unique transactions: 393 flagged unique cases versus 398 flagged source rows including repeated rows. Neither count is a confirmed fraud count.
- The quality view identifies 244 unique cases with at least one unknown typed feature or relationship flag. Issue categories overlap; optional metadata can legitimately be missing.
- The presentation now includes both extensions (17 slides). Desktop layout was visually reviewed; mobile overflow is covered by real-browser assertions.

## Runtime boundary

Viewing or filtering either HTML file requires only a browser with JavaScript enabled. No server, MLX, model, database, external JavaScript library, or CDN is required. The Python builder uses the standard library and project modules only. Model training is unchanged and still requires the documented Apple Silicon environment.

These extensions inspect recorded predictions. They do not add new accuracy measurements, run fresh inference, persist review decisions, or contact customers. The original model checkpoint release remains unchanged.
