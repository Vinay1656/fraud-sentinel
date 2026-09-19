import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fraud_sentinel.dashboard import load_checkpoint, render_quality, render_analyst


def main():
    parser = argparse.ArgumentParser(description="Build offline dashboards without MLX or third-party dependencies")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/dashboard")
    arguments = parser.parse_args()
    data = load_checkpoint(ROOT)
    page = render_quality(data)
    analyst = render_analyst(ROOT, data)
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    (arguments.output_dir / "quality.html").write_text(page, encoding="utf-8")
    (arguments.output_dir / "index.html").write_text(analyst, encoding="utf-8")
    print(f"Built {arguments.output_dir / 'quality.html'}")
    print(f"Built {arguments.output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
