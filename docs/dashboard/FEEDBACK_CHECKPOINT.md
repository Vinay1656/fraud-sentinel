# Feedback and injection checkpoint

- Feedback is saved separately from model predictions in browser-local storage. Actual-case tests exercise save, restart/reload, append history, deduplication, export schema, and import merging.
- Invalid checkpoint/transaction references, false verified-label claims, conflicting event IDs, storage quota failures, stale-tab changes, and corrupt storage are tested. Hostile notes render as text rather than executable HTML.
- A browser-created feedback export is also checked by the Python validator against the published transaction IDs and model/data identity.
- Actual Python feature/prompt functions are checked for all 988 unique source transactions, with three injected-note variants each (2,964 poisoned cases), plus existing synthetic boundary cases. The browser lets a reviewer select any actual transaction prompt and type an excluded note.
- No model predictions, model weights, or training metrics change. Analyst opinions remain unverified and are never automatically eligible for training.
- Storage is local, user-editable, and unauthenticated; this is not a production multi-user case-management or verified-label system. Export backups before switching browsers or clearing data.

Run the full suite with `CHROME_BINARY` set to Chrome to include the real-browser tests. The presentation includes the feedback workflow and the actual-case injection demonstration.
