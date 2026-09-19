import math
import re


def validate_predictions(records, expected_ids=None):
    if not isinstance(records, list) or not records:
        raise ValueError("Predictions must be a nonempty list")
    required = {"transaction_id", "is_fraud", "confidence", "justification"}
    seen = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != required:
            raise ValueError(f"Record {index} must contain exactly the four output fields")
        identifier = record["transaction_id"]
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError(f"Record {index} has an invalid transaction ID")
        if type(record["is_fraud"]) is not bool:
            raise ValueError(f"Record {index} must use a JSON boolean for is_fraud")
        confidence = record["confidence"]
        if type(confidence) not in (int, float) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError(f"Record {index} has invalid confidence")
        explanation = record["justification"]
        if not isinstance(explanation, str) or not explanation.strip() or "\n" in explanation or "\r" in explanation:
            raise ValueError(f"Record {index} needs a plain-text sentence")
        if len(re.findall(r"[.!?](?:\s|$)", explanation)) != 1 or explanation[-1] not in ".!?":
            raise ValueError(f"Record {index} needs exactly one sentence")
        if identifier in seen and seen[identifier] != record:
            raise ValueError(f"Conflicting predictions for duplicate ID {identifier!r}")
        seen[identifier] = record
    if expected_ids is not None and [record["transaction_id"] for record in records] != list(expected_ids):
        raise ValueError("Predictions do not preserve the expected input IDs and order")
    return {"records": len(records), "unique_transactions": len(seen)}
