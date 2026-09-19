import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fraud_sentinel.dashboard import load_checkpoint, render_quality


def main():
    parser = argparse.ArgumentParser(description="Build offline dashboards without MLX or third-party dependencies")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/dashboard")
    arguments = parser.parse_args()
    page = render_quality(load_checkpoint(ROOT))
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    (arguments.output_dir / "quality.html").write_text(page, encoding="utf-8")
    print(f"Built {arguments.output_dir / 'quality.html'}")


if __name__ == "__main__":
    main()
