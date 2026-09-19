import ast
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "notebooks"
sources = {}
for name in ["fraud_sentinel.ipynb", "executed_results.ipynb"]:
    notebook = json.loads((root / name).read_text())
    assert notebook["nbformat"] == 4
    cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(cells) == 8, "Expected eight code cells"
    sources[name] = []
    for cell in cells:
        source = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
        sources[name].append(ast.dump(ast.parse(source)))
        if name == "fraud_sentinel.ipynb":
            assert not cell["outputs"], "Runnable notebook must have clean output cells"
        else:
            assert type(cell["execution_count"]) is int and cell["execution_count"] > 0
            assert not any(output.get("output_type") == "error" for output in cell["outputs"])
assert sources["fraud_sentinel.ipynb"] == sources["executed_results.ipynb"], "Executed code differs from runnable notebook"
print("Both notebooks parse; executed cells match runnable code and contain no errors")
