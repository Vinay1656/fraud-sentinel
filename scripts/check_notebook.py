import ast
import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "notebooks/fraud_sentinel.ipynb"
notebook = json.loads(path.read_text())
assert notebook["nbformat"] == 4
for cell in notebook["cells"]:
    if cell["cell_type"] != "code":
        continue
    source = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
    if not source.startswith("%pip"):
        ast.parse(source)
    assert not cell["outputs"], "Public notebook must not contain local data outputs"
print("Notebook code parses and contains no local execution outputs")
