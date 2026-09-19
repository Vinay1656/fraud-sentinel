# Extension roadmap

## Product direction

Turn the working screening pipeline into a tool that helps an internal team find unusual activity, investigate it, and resolve it with the customer. The demonstration should tell one complete story: **find a sector hotspot → inspect the evidence → review related transactions → simulate customer verification → record the outcome**.

The baseline pipeline is implemented. Everything below is proposed until its checkpoint passes the stated acceptance checks. The user has authorized using or generating additional data where it helps. Metrics work is paused and will resume separately; no new performance claims are implied by these extensions.

## Priorities

| Order | Extension | Who benefits | Concrete result |
| --- | --- | --- | --- |
| 1 | Sector risk heatmap | Operations team | See where predicted alerts are concentrated and investigate a selected cell |
| 2 | Investigation queue and evidence timeline | Fraud analysts | Review cases in a consistent order with linked transaction evidence |
| 3 | Customer verification simulation | Customers and support | Resolve a questionable transaction without treating every alert as confirmed fraud |
| 4 | Feedback and label provenance | Analysts and model developers | Separate confirmed outcomes from model predictions and synthetic labels |
| 5 | Related-activity graph | Investigation team | Explore shared devices/accounts/merchants without claiming links prove fraud |
| 6 | Data-quality and drift view | Engineering and operations | Detect broken feeds and changed traffic before trusting more alerts |

The recommended first build combines priorities 1 and 2 in a local dashboard. That creates a useful end-to-end demo from existing data. Priorities 3 and 4 form the next checkpoint; graph exploration and drift monitoring follow only if time remains.

## 1. Sector heatmap

Use `merchant_category` as sector, with channel or hour-of-day on the other axis. Add a coarse city view only after the non-geographic view works. The supplied transaction table already contains these fields; missing categories become **Unknown**, and inconsistent category spelling is normalized through a documented mapping.

Each cell should expose:

- Unique transaction count and model-flagged transaction count.
- **Predicted alert rate = flagged unique transactions / all unique transactions in that cell.**
- Total transaction amount and flagged transaction amount, separated by currency.
- Missing-data count, date range, and whether support is too small to compare reliably.

Show rate and volume separately: a busy sector should not look riskier solely because it has more transactions. Do not call model flags confirmed fraud, flagged amount money lost, or uncalibrated model scores expected loss. Low-volume cells should be visibly muted with a configurable minimum-support threshold. Duplicate input rows must not inflate the heatmap.

Clicking a cell opens the matching investigation queue. Filters must apply consistently to the heatmap, counts, and case list.

Acceptance: hand-calculated fixture totals match the dashboard; duplicate rows do not change aggregates; unknown category and low-volume cells render; no names, emails, or phone numbers appear in an aggregate view; totals match across filtered views.

## 2. Investigation queue and timeline

For each flagged transaction, display the original behavioral evidence, missing-data flags, model/version, and the generated explanation. Add a chronological account history from strictly earlier transactions. Show supplied historical aggregates as supplied rather than silently presenting them as independently verified history.

Queue ordering should be explicit and configurable, for example score band followed by amount within the same currency. A score is not a calibrated fraud probability. Analysts can mark **needs review**, **awaiting verification**, or **resolved**; the original prediction remains immutable.

Acceptance: a heatmap selection yields exactly the corresponding cases; an account's timeline excludes future transactions; repeated review actions do not create duplicate cases; review state survives a local restart; original prediction and model version remain inspectable.

## 3. Customer verification simulation

Create a fictional customer view with a neutral question: “Do you recognize this transaction?” Support **Yes**, **No**, and **Not sure**. Show a plain-language explanation and a clear next step. Keep wording about the transaction, not accusations about the customer.

This checkpoint is a local simulation: it sends no real messages and blocks no accounts. A “No” response creates an analyst follow-up, not an automatic financial action. A “Yes” response is a customer claim, not automatically a verified negative training label.

Acceptance: all three response paths update the same case correctly; repeated clicks are idempotent; no other customer's case is shown in the simulated session; audit history records the actor, response, and time.

## 4. Feedback and training-data provenance

Store model prediction, customer response, analyst decision, and verified outcome as distinct fields. Preserve who supplied a label and when it became available. Only a documented review process promotes a record into labeled training data.

Acceptance: every eligible training label has provenance; unresolved cases and model-generated labels cannot masquerade as verified outcomes; splits prevent account/time leakage; retraining produces a new version rather than overwriting the historical decision.

## 5. Related-activity graph

Build account/device/merchant links using the existing IDs and time windows. Start with shared-device and repeated-merchant views. Shared merchants are common legitimate hubs, and shared devices may be legitimate, so a link is evidence for review, not a fraud verdict.

Acceptance: synthetic fixtures recover the intended links; common merchant hubs do not mark every customer suspicious; edge evidence and time range are visible; identifiers are masked in presentations.

## 6. Data-quality and drift view

Show missing-link rates, invalid amounts/timestamps, duplicate rates, unknown categories, and changes in feature distributions over time. A change can indicate a broken feed or changed customer activity, not necessarily fraud.

Acceptance: known corrupt fixtures trigger the correct data-quality counter; compare distributions only over comparable time windows; keep input quality separate from model risk.

## Delivery checkpoints

| Checkpoint | Definition of done | Git action |
| --- | --- | --- |
| Baseline | Runnable code/notebook, presentation, synthetic demo, passing CPU checks | Commit and push the working baseline |
| Product/data plan | Prioritized extensions, source candidates, honest evaluation boundaries | Commit and push the plan |
| Heatmap + queue | Connected drilldown, correct aggregates, tested filters, documented demo | Commit and push working dashboard |
| Verification + feedback | Local customer flow, persisted case state, auditable outcomes | Commit and push complete case workflow |
| Better data + evaluation | Documented sources, independent test design, metrics and comparison | Commit and push measured model update |

Before each implementation commit: run relevant tests, update the README and presentation for what actually works, inspect the staged files, then commit and push. Avoid committing unfinished feature claims, generated private datasets, or model weights.

## Proposed demo narrative

1. Load fictional relational data containing duplicates, corrupt values, and an injected note.
2. Show the pipeline preserving coverage while keeping the injected text out of the prompt.
3. Find a sector with a high predicted alert rate, alongside its sample size.
4. Open a case, inspect prior activity, and explain the available evidence.
5. Simulate a customer response and record analyst follow-up.
6. Close with reproducibility, measured limitations, and the saved audit trail.

This is a proposed narrative. The dashboard and customer flow must exist and pass their checks before appearing as working capabilities in the presentation.
