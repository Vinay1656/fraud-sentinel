import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROME = os.environ.get('CHROME_BINARY')


@unittest.skipUnless(CHROME, 'Set CHROME_BINARY to run real headless browser interaction tests')
class DashboardBrowserTests(unittest.TestCase):
    def run_browser(self, filename, checks):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            page = (ROOT / 'docs/dashboard' / filename).read_text()
            probe = "<script>try{" + checks + ";document.body.dataset.browserTest='PASS';}catch(error){document.body.dataset.browserTest='FAIL:'+error.message;}</script>"
            target = folder / 'test.html'
            target.write_text(page.replace('</body>', probe + '</body>'))
            result = subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu',
                                     '--no-first-run', '--disable-background-networking',
                                     '--user-data-dir=' + str(folder / 'profile'), '--dump-dom',
                                     '--timeout=10000', target.as_uri()], capture_output=True, text=True, timeout=40)
            self.assertEqual(result.returncode, 0, result.stderr[-1500:])
            self.assertIn('data-browser-test="PASS"', result.stdout, result.stdout[-2500:])

    def test_quality_filters_in_browser(self):
        self.run_browser('quality.html', """
const select=document.getElementById('table-filter');select.value='accounts';select.dispatchEvent(new Event('change'));
const visible=[...document.querySelectorAll('#issues tr')].filter(row=>!row.hidden);
if(!visible.length||visible.some(row=>row.dataset.table!=='accounts'))throw Error('table filter');
const search=document.getElementById('issue-search');search.value='no_such_field';search.dispatchEvent(new Event('input'));
if(document.getElementById('empty-issues').hidden)throw Error('empty state');
select.value='all';search.value='amount';search.dispatchEvent(new Event('input'));
if(![...document.querySelectorAll('#issues tr')].some(row=>!row.hidden&&row.textContent.includes('27 / 988')))throw Error('amount count');
""")
