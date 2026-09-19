# Prompt-injection boundary

The primary protection is **excluding untrusted text from model context**. It does not rely on a blacklist of known attack phrases or on the model obeying a warning.

1. Read and clean the input tables outside the model.
2. Build a fixed feature object containing known numeric, boolean, and null fields.
3. Reject unexpected feature keys or raw string values at the prompt boundary; serialize with nonfinite JSON values prohibited.
4. Use a fixed system instruction and the typed feature object as the complete prompt.
5. Attach the original transaction ID and construct the final JSON outside the model.

Notes, merchant names/categories, customer names, contact details, and source IDs never become model instructions. Account/customer metadata is cleaned and exported locally but does not expand the prompt allowlist.

Regression tests use the actual pipeline feature/prompt functions without loading the GPU model. They check ordinary instruction attacks, role delimiters, Unicode text, code-block attacks, and long payloads across excluded fields. They also check malicious text in metadata, numeric/date/boolean fields, and IDs.

For excluded text, tests require the entire prompt to remain identical. For malformed typed fields, values become null; for invalid identifiers, linkage becomes unknown. Those changes can legitimately affect an assessment because the available data changed, but the injected text still cannot reach the model as instructions.

This does not prove immunity to every attack. An attacker can still falsify plausible numeric facts, and the model can make classification errors. The tests verify the input boundary, not calibrated accuracy or resistance to all data poisoning. Run the pipeline normally (not with Python assertion checks disabled).
