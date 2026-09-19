import hashlib
import json
import re
from datetime import datetime

DECISIONS = {"needs_review", "suspected_fraud", "likely_legitimate", "inconclusive"}
EVENT_FIELDS = {"event_id", "transaction_id", "analyst", "decision", "note", "evidence_reference",
                "recorded_at", "label_status", "eligible_for_training"}


def checkpoint_identity(root):
    checkpoint = root / "artifacts/checkpoint-1"
    audit = json.loads((checkpoint / "results/data_audit.json").read_text())
    provenance = json.loads((checkpoint / "model_provenance.json").read_text())
    return {"predictions_sha256": hashlib.sha256((checkpoint / "results/predictions.json").read_bytes()).hexdigest(),
            "transactions_sha256": audit["sha256"]["transactions.csv"], "model_revision": provenance["revision"],
            "adapter_sha256": hashlib.sha256((checkpoint / "adapter/adapters.safetensors").read_bytes()).hexdigest()}


def validate_feedback(ledger, identity, transaction_ids):
    if not isinstance(ledger, dict) or set(ledger) != {"schema_version", "checkpoint", "events"}:
        raise ValueError("Invalid feedback envelope")
    if type(ledger["schema_version"]) is not int or ledger["schema_version"] != 1 or ledger["checkpoint"] != identity:
        raise ValueError("Unsupported schema or mismatched prediction/data checkpoint")
    events = ledger["events"]
    if not isinstance(events, list) or len(events) > 5000:
        raise ValueError("Expected at most 5,000 feedback events")
    allowed_ids = set(transaction_ids)
    seen = set()
    for event in events:
        if not isinstance(event, dict) or set(event) != EVENT_FIELDS:
            raise ValueError("Unexpected feedback event fields")
        identifier = event["event_id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{8,80}", identifier) or identifier in seen:
            raise ValueError("Invalid or duplicate event ID")
        seen.add(identifier)
        if not isinstance(event["transaction_id"], str) or event["transaction_id"] not in allowed_ids:
            raise ValueError("Feedback references an unknown transaction")
        if not isinstance(event["decision"], str) or event["decision"] not in DECISIONS:
            raise ValueError("Unknown analyst decision")
        for field, limit, required in [("analyst", 80, True), ("note", 2000, True), ("evidence_reference", 300, False)]:
            value = event[field]
            if not isinstance(value, str) or len(value.encode('utf-16-le')) // 2 > limit or (required and not value.strip()):
                raise ValueError(f"Invalid {field}")
        stamp = event["recorded_at"]
        if not isinstance(stamp, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", stamp):
            raise ValueError("Expected UTC millisecond timestamp")
        try:
            datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("Invalid timestamp") from error
        if event["label_status"] != "unverified_analyst_feedback" or event["eligible_for_training"] is not False:
            raise ValueError("Analyst feedback cannot masquerade as verified training labels")
    return {"events": len(events), "reviewed_transactions": len({event["transaction_id"] for event in events}),
            "eligible_training_labels": 0}
