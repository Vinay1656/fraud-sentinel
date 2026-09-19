import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class NotebookSetupTests(unittest.TestCase):
    def source(self):
        notebook = json.loads((ROOT / 'notebooks/fraud_sentinel.ipynb').read_text())
        return ''.join(next(cell for cell in notebook['cells'] if cell['cell_type'] == 'code')['source'])

    def test_installer_uses_current_kernel_without_shell_expansion(self):
        with patch('subprocess.check_call') as install:
            exec(compile(self.source(), 'notebook-setup', 'exec'), {})
        install.assert_called_once_with([sys.executable, '-m', 'pip', 'install', '-q',
                                         'mlx==0.32.2', 'mlx-lm[train]==0.31.3',
                                         'transformers==5.17.0', 'huggingface-hub==1.32.0'])

    def test_install_failure_stops_the_notebook(self):
        with patch('subprocess.check_call', side_effect=subprocess.CalledProcessError(1, ['pip'])):
            with self.assertRaises(subprocess.CalledProcessError):
                exec(compile(self.source(), 'notebook-setup', 'exec'), {})
