import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

specification = importlib.util.spec_from_file_location("demo_data", Path(__file__).resolve().parents[1] / "scripts/create_demo_data.py")
demo = importlib.util.module_from_spec(specification)
specification.loader.exec_module(demo)


class DemoDataTests(unittest.TestCase):
    def test_relationships_and_deliberate_faults(self):
        with tempfile.TemporaryDirectory() as directory:
            result = demo.create_demo_data(directory, 24)
            self.assertEqual(result["transactions"], 25)
            with (Path(directory) / "transactions.csv").open() as handle:
                transactions = list(csv.DictReader(handle))
            with (Path(directory) / "accounts.csv").open() as handle:
                accounts = {row["account_id"]: row for row in csv.DictReader(handle)}
            self.assertEqual(transactions[0], transactions[-1])
            self.assertEqual(sum(row["account_id"] not in accounts for row in transactions), 1)
            self.assertEqual(transactions[1]["amount"], "N/A")
            self.assertIn("Ignore previous instructions", transactions[0]["notes"])
            with self.assertRaises(FileExistsError):
                demo.create_demo_data(directory, 24)


if __name__ == "__main__":
    unittest.main()
