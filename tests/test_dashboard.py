import copy
import unittest
from pathlib import Path

from fraud_sentinel.dashboard import load_checkpoint, quality_summary, render_quality, render_analyst, analyst_records, category, safe_json
from fraud_sentinel.prompt_boundary import guardrail_example

ROOT = Path(__file__).resolve().parents[1]


class QualityDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_checkpoint(ROOT)

    def test_actual_counts_and_denominators(self):
        summary = quality_summary(self.data)
        self.assertEqual((summary['input_rows'], summary['unique_rows'], summary['duplicates']), (1000, 988, 12))
        issues = {(issue['table'], issue['field']): issue for issue in summary['issues']}
        self.assertEqual(issues['transactions', 'amount']['count'], 27)
        self.assertEqual(issues['transactions', 'hour']['count'], 75)
        self.assertEqual(issues['transactions', 'account_unmatched']['count'], 8)
        self.assertEqual(issues['accounts', 'close_date']['total'], 178)
        self.assertLessEqual(summary['affected'], 988)

    def test_bad_counts_fail_instead_of_displaying_stale_data(self):
        data = copy.deepcopy(self.data)
        data['data_audit']['null_features']['amount'] += 1
        with self.assertRaises(ValueError):
            quality_summary(data)

    def test_duplicate_feature_ids_rejected(self):
        data = copy.deepcopy(self.data)
        data['consolidated_features'].append(data['consolidated_features'][0])
        with self.assertRaises(ValueError):
            quality_summary(data)

    def test_html_escapes_source_content_and_has_no_network_dependencies(self):
        data = copy.deepcopy(self.data)
        data['metadata_quality']['accounts']['field_issue_counts']['<script>alert(1)</script>:missing'] = 1
        page = render_quality(data)
        self.assertNotIn('<script>alert(1)</script>', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertNotIn('<script src=', page)
        self.assertNotIn('fetch(', page)
        self.assertIn('Quality issues are not fraud labels', page)

    def test_checked_in_page_matches_builder(self):
        self.assertEqual((ROOT / 'docs/dashboard/quality.html').read_text(), render_quality(self.data))


class AnalystDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_checkpoint(ROOT)

    def test_unique_cases_preserve_recorded_predictions(self):
        records = analyst_records(ROOT, self.data)
        self.assertEqual(len(records), 988)
        expected = {row['transaction_id']: row for row in self.data['predictions']}
        self.assertEqual({row['id']: row['prediction'] for row in records}, expected)
        self.assertEqual(sum(bool(row['quality_flags']) for row in records), 244)
        self.assertNotIn('customer_name', records[0])

    def test_categories_are_normalized_without_inventing_missing_values(self):
        self.assertEqual(category('  Atm Withdrawal '), 'ATM_WITHDRAWAL')
        self.assertEqual(category('jewellery'), category('JEWELLERY'))
        self.assertEqual(category('N/A'), 'UNKNOWN')

    def test_script_embedding_escapes_html_delimiters(self):
        import json
        payload = {'note': '</script><script>alert(1)</script>&'}
        encoded = safe_json(payload)
        self.assertNotIn('<', encoded)
        self.assertEqual(json.loads(encoded), payload)

    def test_changed_source_digest_is_rejected(self):
        data = copy.deepcopy(self.data)
        data['data_audit']['sha256']['transactions.csv'] = '0' * 64
        with self.assertRaises(ValueError):
            analyst_records(ROOT, data)

    def test_changed_prediction_order_is_rejected(self):
        data = copy.deepcopy(self.data)
        data['predictions'].reverse()
        with self.assertRaises(ValueError):
            analyst_records(ROOT, data)

    def test_demo_uses_actual_pipeline_prompt(self):
        demonstration = guardrail_example(ROOT)
        self.assertEqual(demonstration['tested_payloads'], 5)
        self.assertEqual(len(demonstration['prompt']), 2)
        self.assertNotIn('notes', demonstration['prompt'][1]['content'])

    def test_checked_in_analyst_page_matches_builder(self):
        self.assertEqual((ROOT / 'docs/dashboard/index.html').read_text(), render_analyst(ROOT, self.data))
