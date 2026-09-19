import math
import re
from collections import Counter
from datetime import date


MISSING = {"", "na", "n/a", "null", "none", "nan"}
ACCOUNT_SCHEMA = {
    "account_id": "id", "customer_id": "id", "account_type": "category",
    "account_status": "category", "currency": "currency", "open_date": "date",
    "close_date": "date", "branch_code": "id", "branch_city": "text",
    "current_balance": "signed", "avg_monthly_balance_6m": "signed",
    "credit_limit": "nonnegative", "credit_utilization_pct": "nonnegative",
    "overdraft_enabled": "boolean", "card_type": "category", "is_joint_account": "boolean",
    "num_linked_devices": "integer", "mobile_banking_enrolled": "boolean",
    "last_login_date": "date", "avg_monthly_txn_count": "nonnegative", "account_tier": "category",
}
CUSTOMER_SCHEMA = {
    "customer_id": "id", "first_name": "text", "last_name": "text", "gender": "category",
    "date_of_birth": "date", "age": "age", "email": "email", "phone_number": "phone",
    "city": "text", "state": "text", "country": "country", "postal_code": "text",
    "occupation": "text", "annual_income": "nonnegative", "marital_status": "category",
    "education_level": "category", "employment_status": "category", "customer_since": "date",
    "customer_segment": "category", "kyc_status": "category", "risk_rating": "category",
    "is_politically_exposed": "boolean", "preferred_channel": "category",
    "email_verified": "boolean", "phone_verified": "boolean", "num_complaints_last_year": "integer",
}


def clean_value(value, kind):
    if value is None:
        return None, "missing"
    text = str(value).strip()
    if kind == "category" and text.upper() == "NONE":
        return "NONE", None
    if text.casefold() in MISSING:
        return None, "missing"
    if len(text) > 256 or any(ord(character) < 32 for character in text):
        return None, "invalid"
    if kind == "boolean":
        if text.casefold() in {"true", "yes", "y", "1"}:
            return True, None
        if text.casefold() in {"false", "no", "n", "0"}:
            return False, None
        return None, "invalid"
    if kind in {"signed", "nonnegative", "integer", "age"}:
        if isinstance(value, bool):
            return None, "invalid"
        if "," in text and not re.fullmatch(r"[+-]?\d{1,3}(,\d{3})+(\.\d+)?", text):
            return None, "invalid"
        try:
            number = float(text.replace(",", ""))
        except ValueError:
            return None, "invalid"
        if not math.isfinite(number) or abs(number) > 1e15 or (kind != "signed" and number < 0):
            return None, "invalid"
        if kind in {"integer", "age"}:
            if not number.is_integer() or (kind == "age" and number > 120):
                return None, "invalid"
            return int(number), None
        return number, None
    if kind == "date":
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
                return None, "invalid"
            return date.fromisoformat(text).isoformat(), None
        except ValueError:
            return None, "invalid"
    if kind == "id":
        return (text, None) if re.fullmatch(r"[A-Za-z0-9_-]{1,128}", text) else (None, "invalid")
    if kind in {"currency", "country"}:
        length = 3 if kind == "currency" else 2
        return (text.upper(), None) if re.fullmatch(rf"[A-Za-z]{{{length}}}", text) else (None, "invalid")
    if kind == "email":
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", text):
            return None, "invalid"
        local, domain = text.rsplit("@", 1)
        return local + "@" + domain.lower(), None
    if kind == "phone":
        if not re.fullmatch(r"\+?[0-9 ()-]+", text):
            return None, "invalid"
        normalized = re.sub(r"[ ()-]", "", text)
        return (normalized, None) if re.fullmatch(r"\+?\d{7,15}", normalized) else (None, "invalid")
    if kind == "category":
        return re.sub(r"\s+", "_", text.upper()), None
    return text, None


def clean_dimension(rows, table):
    schema = ACCOUNT_SCHEMA if table == "accounts" else CUSTOMER_SCHEMA if table == "customers" else None
    if schema is None:
        raise ValueError("Unknown metadata table")
    key = "account_id" if table == "accounts" else "customer_id"
    cleaned, grouped, quarantine = [], {}, []
    field_counts = Counter()
    for index, row in enumerate(rows):
        record, flags = {}, []
        for field, kind in schema.items():
            record[field], issue = clean_value(row.get(field), kind)
            if issue:
                field_counts[f"{field}:{issue}"] += 1
                flags.append(f"{field}:{issue}")
        pairs = [("open_date", "close_date"), ("open_date", "last_login_date")] if table == "accounts" else [("date_of_birth", "customer_since")]
        for earlier, later in pairs:
            if record[earlier] and record[later] and record[later] < record[earlier]:
                flags.append(f"{later}:before_{earlier}")
        if table == "accounts" and record["credit_utilization_pct"] is not None and record["credit_utilization_pct"] > 100:
            flags.append("credit_utilization_pct:over_100")
        record["quality_flags"] = sorted(flags)
        record["source_rows"] = [index + 2]
        cleaned.append(record)
        if record[key] is None:
            quarantine.append(record)
        else:
            grouped.setdefault(record[key], []).append(record)
    selected = {}
    conflicts = {}
    for identifier, candidates in grouped.items():
        best = max(candidates, key=lambda candidate: (
            -sum(flag.endswith(":invalid") for flag in candidate["quality_flags"]),
            sum(candidate[field] is not None for field in schema),
        ))
        best = dict(best)
        conflict_fields = [field for field in schema if len({candidate[field] for candidate in candidates if candidate[field] is not None}) > 1]
        best["quality_flags"] = sorted(set(best["quality_flags"] + [f"{field}:duplicate_conflict" for field in conflict_fields]))
        best["source_rows"] = [source for candidate in candidates for source in candidate["source_rows"]]
        if conflict_fields:
            conflicts[identifier] = conflict_fields
        selected[identifier] = best
    report = {
        "input_rows": len(rows), "selected_rows": len(selected), "quarantined_rows": len(quarantine),
        "duplicate_extra_rows": sum(len(candidates) - 1 for candidates in grouped.values()),
        "duplicate_conflict_groups": len(conflicts), "field_issue_counts": dict(sorted(field_counts.items())),
        "selected_rows_with_flags": sum(bool(record["quality_flags"]) for record in selected.values()),
    }
    return {"by_id": selected, "rows": cleaned, "quarantine": quarantine, "report": report}


def clean_metadata(account_rows, customer_rows):
    accounts = clean_dimension(account_rows, "accounts")
    customers = clean_dimension(customer_rows, "customers")
    for account in accounts["by_id"].values():
        if account["customer_id"] not in customers["by_id"]:
            account["quality_flags"] = sorted(set(account["quality_flags"] + ["customer_id:unmatched"]))
    accounts["report"]["unmatched_customer_references"] = sum(account["customer_id"] not in customers["by_id"] for account in accounts["by_id"].values())
    accounts["report"]["selected_rows_with_flags"] = sum(bool(account["quality_flags"]) for account in accounts["by_id"].values())
    return {"accounts": accounts, "customers": customers}
