import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fraud_sentinel.dashboard import load_checkpoint
from fraud_sentinel.feedback import checkpoint_identity, validate_feedback


def main():
    parser = argparse.ArgumentParser(description="Validate exported analyst feedback without loading a model")
    parser.add_argument("file", type=Path)
    arguments = parser.parse_args()
    if arguments.file.stat().st_size > 20_000_000:
        raise ValueError("Feedback file exceeds 20 MB")
    data = load_checkpoint(ROOT)
    report = validate_feedback(json.loads(arguments.file.read_text()), checkpoint_identity(ROOT),
                               [row["transaction_id"] for row in data["consolidated_features"]])
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
