import hashlib
import html
import json
from pathlib import Path


STYLE = """
:root{color-scheme:light;--ink:#162b43;--muted:#50647a;--teal:#006b68;--line:#d6e1e8}
*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:var(--ink);font:16px/1.55 system-ui,sans-serif}
header{background:#122b43;color:white;padding:36px max(24px,calc((100vw - 1180px)/2))}
header p{color:#c9dee9;max-width:850px}h1{font-size:clamp(28px,4vw,42px);line-height:1.2;margin:8px 0}
h2{font-size:23px;margin:0 0 10px}h3{margin:0 0 8px}a{color:var(--teal)}header a{color:#aff5e8}
main{max-width:1228px;margin:auto;padding:24px}section{background:white;border:1px solid var(--line);border-radius:14px;padding:24px;margin:22px 0}
.eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:12px;font-weight:700}.muted,small{color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}.card{background:white;border:1px solid var(--line);border-radius:12px;padding:20px}.value{display:block;font-size:32px;font-weight:750;color:var(--teal)}
.notice{background:#fff5df;border-left:4px solid #bb7700;padding:16px 20px;border-radius:8px}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;text-align:left}th,td{padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}th{background:#eef4f7;font-size:13px}td{font-size:14px}caption{text-align:left;padding:8px 0;color:var(--muted)}
input,select,textarea,button{font:inherit;padding:10px 12px;border:1px solid #8c9eae;border-radius:7px;max-width:100%}button{cursor:pointer;background:var(--teal);color:white}button:hover{background:#004c4a}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid #df9500;outline-offset:3px}
label{display:block;font-weight:600;margin:8px 0}.filters{display:flex;flex-wrap:wrap;gap:16px;align-items:end}.filters>div{flex:1;min-width:160px}.badge{display:inline-block;border-radius:5px;background:#e6f4f0;color:#005b52;padding:3px 8px;font-size:12px}.warn{background:#fff0d4;color:#785000}progress{width:100%;max-width:160px;accent-color:var(--teal)}[hidden]{display:none!important}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#edf3f7;padding:16px;border-radius:8px;font-size:13px}footer{padding:24px;color:var(--muted);font-size:13px}details{margin:14px 0}summary{cursor:pointer;font-weight:600}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
@media(max-width:600px){main{padding:12px}section{padding:16px}th,td{padding:9px}header{padding:24px}.value{font-size:27px}}
"""


def escape(value):
    return html.escape(str(value), quote=True)


def document(title, subtitle, body, script=""):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Fraud Sentinel</title>
<style>{STYLE}</style></head><body><header><div class="eyebrow">Fraud Sentinel / recorded checkpoint</div>
<h1>{escape(title)}</h1><p>{escape(subtitle)}</p>
<a href="https://github.com/Vinay1656/fraud-sentinel">Repository and runnable notebook</a></header>
<main>{body}</main><footer>Dummy hackathon data, published with permission. Offline snapshot, not a live bank feed. No external scripts, analytics, or model execution.</footer>
<script>{script}</script></body></html>'''


def load_checkpoint(root):
    checkpoint = Path(root) / "artifacts/checkpoint-1"
    manifest = json.loads((checkpoint / "SHA256SUMS.json").read_text())
    for name, digest in manifest.items():
        source = (checkpoint / name).resolve()
        if not source.is_relative_to(checkpoint.resolve()) or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Checkpoint integrity mismatch: {name}")
    results = checkpoint / "results"
    return {name: json.loads((results / f"{name}.json").read_text()) for name in
            ["data_audit", "metadata_quality", "consolidated_features", "predictions", "evaluation"]}


def quality_summary(data):
    audit = data["data_audit"]
    features = data["consolidated_features"]
    unique_count = len(features)
    if not unique_count or len({row["transaction_id"] for row in features}) != unique_count:
        raise ValueError("Features must contain nonempty unique transaction IDs")
    issues = []
    for field, count in audit["null_features"].items():
        measured = sum(row[field] is None for row in features)
        if measured != count:
            raise ValueError(f"Null count mismatch: {field}")
        if count:
            issues.append({"table": "transactions", "field": field, "kind": "Unknown feature",
                           "count": count, "total": unique_count,
                           "action": "Check source value or unavailable history; do not infer fraud from missingness."})
    for field, count in audit["relationship_flags"].items():
        if sum(row[field] is True for row in features) != count:
            raise ValueError(f"Relationship count mismatch: {field}")
        if count:
            issues.append({"table": "transactions", "field": field, "kind": "Relationship",
                           "count": count, "total": unique_count,
                           "action": "Reconcile account/customer references before interpreting the assessment."})
    for table, report in data["metadata_quality"].items():
        for key, count in report["field_issue_counts"].items():
            field, kind = key.rsplit(":", 1)
            issues.append({"table": table, "field": field, "kind": kind.capitalize(),
                           "count": count, "total": report["input_rows"],
                           "action": "May be expected for an open account; confirm account lifecycle." if field == "close_date" else "Review source completeness; missing metadata is not proof of fraud."})
    affected = sum(any(value is None for key, value in row.items() if key != "transaction_id") or
                   any(row[field] for field in audit["relationship_flags"]) for row in features)
    total = audit["rows"]["transactions.csv"]
    if total - unique_count != audit["exact_transaction_duplicates"]:
        raise ValueError("Transaction coverage mismatch")
    return {"input_rows": total, "unique_rows": unique_count,
            "duplicates": total - unique_count, "affected": affected,
            "issues": sorted(issues, key=lambda item: (-item["count"] / max(item["total"], 1), item["table"], item["field"]))}


def render_quality(data):
    summary = quality_summary(data)
    cards = "".join(f'<div class="card">{escape(label)}<span class="value">{value:,}</span><small>{escape(note)}</small></div>' for label, value, note in [
        ("Source transaction rows", summary["input_rows"], "Preserved in prediction output"),
        ("Unique transactions", summary["unique_rows"], "Denominator for transaction issues"),
        ("Exact duplicate rows", summary["duplicates"], "Reused decisions, not extra unique cases"),
        ("Unique rows with issues", summary["affected"], "Union of unknown features / relationship flags"),
    ])
    rows = []
    for issue in summary["issues"]:
        rate = 100 * issue["count"] / max(issue["total"], 1)
        rows.append(f'''<tr data-table="{escape(issue['table'])}"><td>{escape(issue['table'])}</td><td>{escape(issue['field'])}</td>
<td>{escape(issue['kind'])}</td><td>{issue['count']} / {issue['total']}</td><td>{rate:.1f}%<br><progress aria-label="{escape(issue['field'])} affected rate" value="{rate}" max="100"></progress></td><td>{escape(issue['action'])}</td></tr>''')
    dimensions = "".join(f'<tr><td>{escape(table)}</td><td>{report["input_rows"]}</td><td>{report["selected_rows"]}</td><td>{report["quarantined_rows"]}</td><td>{report["duplicate_extra_rows"]}</td><td>{report["selected_rows_with_flags"]}</td></tr>' for table, report in data["metadata_quality"].items())
    body = f'''<div class="cards">{cards}</div>
<p class="notice"><strong>Quality issues are not fraud labels.</strong> Counts can overlap. Optional fields can be legitimately empty. In particular, missing close dates may describe open accounts. No invented overall “quality score.”</p>
<section><h2>Where data needs attention</h2><p class="muted">Transaction rates use unique transactions; account/customer rates use source rows. Unknown history is shown separately from confirmed corruption.</p>
<div class="filters"><div><label for="table-filter">Table</label><select id="table-filter"><option value="all">All tables</option><option>transactions</option><option>accounts</option><option>customers</option></select></div><div><label for="issue-search">Find a field or issue</label><input id="issue-search" type="search" placeholder="Try amount, timestamp (hour), or missing"></div></div>
<p id="issue-count" role="status" aria-live="polite"></p><div class="scroll"><table><caption>Field-level issues from the verified cleaning checkpoint</caption><thead><tr><th>Table</th><th>Field</th><th>Issue</th><th>Affected / denominator</th><th>Rate</th><th>Suggested next step</th></tr></thead><tbody id="issues">{''.join(rows)}</tbody></table></div><p id="empty-issues" hidden>No matching issues. Clear the filters to see all fields.</p></section>
<section><h2>Account and customer reconciliation</h2><div class="scroll"><table><thead><tr><th>Table</th><th>Source rows</th><th>Selected IDs</th><th>Quarantined</th><th>Extra duplicates</th><th>Selected rows with flags</th></tr></thead><tbody>{dimensions}</tbody></table></div><p class="muted">Flags include optional missing values, not only invalid data. Source rows and conflicts are retained by the cleaning pipeline.</p></section>
<section><h2>Evidence and interpretation</h2><p>This view is generated from checkpoint-1. The builder verifies checkpoint file hashes, transaction coverage, and feature counts before rendering. No model is loaded.</p><p>“hour” unknown means the source timestamp could not be parsed. “amount_ratio” and “minutes_since_previous” can be unknown because history is unavailable.</p><details><summary>Source CSV SHA-256 hashes</summary><pre>{escape(json.dumps(data['data_audit']['sha256'], indent=2))}</pre></details></section>'''
    script = '''function filterIssues(){const table=document.getElementById('table-filter').value;const query=document.getElementById('issue-search').value.toLowerCase().trim();let count=0;document.querySelectorAll('#issues tr').forEach(row=>{row.hidden=!((table==='all'||row.dataset.table===table)&&row.textContent.toLowerCase().includes(query));if(!row.hidden)count++;});document.getElementById('issue-count').textContent=count+' issue categories shown';document.getElementById('empty-issues').hidden=count!==0;}document.getElementById('table-filter').addEventListener('change',filterIssues);document.getElementById('issue-search').addEventListener('input',filterIssues);filterIssues();'''
    return document("Data-quality dashboard", "Find incomplete values and broken relationships before interpreting model risk.", body, script)
