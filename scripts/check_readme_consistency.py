"""Check localized README files for required API key prerequisite text."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bindu.utils.readme_consistency import missing_api_key_prerequisite_files


def main() -> int:
    """Run README consistency checks and report missing files."""
    parser = argparse.ArgumentParser(
        description="Validate localized README files include API key prerequisites."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root path (default: current working directory).",
    )
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    missing_files = missing_api_key_prerequisite_files(repo_root)

    if not missing_files:
        print("All localized README files include API key prerequisites.")
        return 0

    print("Missing API key prerequisite in:")
    for file_path in missing_files:
        print(f"- {file_path.relative_to(repo_root)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
