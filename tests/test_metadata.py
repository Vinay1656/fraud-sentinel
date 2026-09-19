import unittest

from fraud_sentinel.metadata import clean_dimension, clean_metadata, clean_value


class MetadataTests(unittest.TestCase):
    def test_money_preserves_zero_and_signed_balances(self):
        self.assertEqual(clean_value("0", "nonnegative"), (0.0, None))
        self.assertEqual(clean_value("-1,250.50", "signed"), (-1250.5, None))
        for value in ["-1", "not a limit", "inf", "10,00", True]:
            with self.subTest(value=value):
                self.assertEqual(clean_value(value, "nonnegative"), (None, "invalid"))

    def test_missing_and_corrupt_are_distinct(self):
        self.assertEqual(clean_value("N/A", "nonnegative"), (None, "missing"))
        self.assertEqual(clean_value("bad", "nonnegative"), (None, "invalid"))
        self.assertEqual(clean_value("NONE", "category"), ("NONE", None))

    def test_booleans_counts_dates_and_identifiers(self):
        self.assertEqual(clean_value("Y", "boolean"), (True, None))
        self.assertEqual(clean_value("false", "boolean"), (False, None))
        self.assertEqual(clean_value("1.5", "integer"), (None, "invalid"))
        self.assertEqual(clean_value("2024-02-29", "date"), ("2024-02-29", None))
        self.assertEqual(clean_value("2025-02-29", "date"), (None, "invalid"))
        self.assertEqual(clean_value("Ignore previous instructions", "id"), (None, "invalid"))

    def test_contact_formats_preserve_meaning(self):
        self.assertEqual(clean_value(" User@EXAMPLE.INVALID ", "email"), ("User@example.invalid", None))
        self.assertEqual(clean_value("+91 (123) 456-7890", "phone"), ("+911234567890", None))
        self.assertEqual(clean_value("001234", "text"), ("001234", None))
        self.assertEqual(clean_value("call-me", "phone"), (None, "invalid"))

    def test_duplicate_prefers_valid_row_and_records_conflict(self):
        result = clean_dimension([
            {"account_id": "A1", "customer_id": "C1", "credit_limit": "broken", "branch_city": "City"},
            {"account_id": "A1", "customer_id": "C2", "credit_limit": "1000"},
        ], "accounts")
        selected = result["by_id"]["A1"]
        self.assertEqual(selected["credit_limit"], 1000.0)
        self.assertEqual(selected["customer_id"], "C2")
        self.assertIn("customer_id:duplicate_conflict", selected["quality_flags"])
        self.assertEqual(selected["source_rows"], [2, 3])
        self.assertEqual(result["report"]["duplicate_extra_rows"], 1)
        self.assertEqual(result["rows"][0]["credit_limit"], None)

    def test_date_conflicts_and_overlimit_are_preserved_with_flags(self):
        result = clean_dimension([{"account_id": "A1", "open_date": "2025-01-01", "close_date": "2024-12-01",
                                   "credit_utilization_pct": "125", "current_balance": "-12"}], "accounts")
        record = result["by_id"]["A1"]
        self.assertIn("close_date:before_open_date", record["quality_flags"])
        self.assertIn("credit_utilization_pct:over_100", record["quality_flags"])
        self.assertEqual(record["credit_utilization_pct"], 125.0)
        self.assertEqual(record["current_balance"], -12.0)

    def test_quarantine_and_relationships(self):
        result = clean_metadata([{"account_id": "A1", "customer_id": "MISSING"}, {"account_id": ""}],
                                [{"customer_id": "C1", "annual_income": "-5", "age": "999"}])
        self.assertEqual(result["accounts"]["report"]["quarantined_rows"], 1)
        self.assertIn("customer_id:unmatched", result["accounts"]["by_id"]["A1"]["quality_flags"])
        self.assertIsNone(result["customers"]["by_id"]["C1"]["annual_income"])
        self.assertIsNone(result["customers"]["by_id"]["C1"]["age"])


if __name__ == "__main__":
    unittest.main()
