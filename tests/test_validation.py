import unittest

from fraud_sentinel import validate_predictions


def prediction(**changes):
    record = {"transaction_id": "DEMO_001", "is_fraud": True, "confidence": 0.8,
              "justification": "A new device accompanies an unusual amount."}
    record.update(changes)
    return record


class ValidationTests(unittest.TestCase):
    def test_valid_records_and_consistent_duplicates(self):
        records = [prediction(), prediction()]
        self.assertEqual(validate_predictions(records, ["DEMO_001", "DEMO_001"]),
                         {"records": 2, "unique_transactions": 1})

    def test_nonfinite_and_non_numeric_confidence(self):
        for value in [float("nan"), float("inf"), -0.1, 1.1, True, "0.8"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_predictions([prediction(confidence=value)])

    def test_exact_fields_and_boolean(self):
        for record in [prediction(extra="unexpected"), prediction(is_fraud="true"), prediction(is_fraud=1)]:
            with self.subTest(record=record), self.assertRaises(ValueError):
                validate_predictions([record])

    def test_conflicting_duplicate_and_reordered_output(self):
        with self.assertRaises(ValueError):
            validate_predictions([prediction(), prediction(is_fraud=False)])
        with self.assertRaises(ValueError):
            validate_predictions([prediction()], ["DEMO_002"])

    def test_single_sentence_with_decimal(self):
        validate_predictions([prediction(justification="The amount is 2.5 times the average.")])
        for explanation in ["", "No punctuation", "First sentence. Second sentence.", "A sentence.\n"]:
            with self.subTest(explanation=explanation), self.assertRaises(ValueError):
                validate_predictions([prediction(justification=explanation)])

    def test_empty_input_and_identifier(self):
        for records in [[], {}, [prediction(transaction_id=" ")]]:
            with self.subTest(records=records), self.assertRaises(ValueError):
                validate_predictions(records)


if __name__ == "__main__":
    unittest.main()
