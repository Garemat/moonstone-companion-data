#!/usr/bin/env python3
"""
Aggregate individual JSON files into build/ artifacts for local development.
Run this before lint_data.py to prepare the build directory.

Usage:
    python3 scripts/aggregate.py
    python3 scripts/lint_data.py
"""

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(ROOT, "build")

SOURCES = [
    ("characters", "characters/**/*.json"),
    ("upgrades",   "upgrades/**/*.json"),
    ("campaign",   "campaign/**/*.json"),
]


def aggregate():
    os.makedirs(BUILD_DIR, exist_ok=True)
    ok = True

    for kind, pattern in SOURCES:
        files = sorted(glob.glob(os.path.join(ROOT, pattern), recursive=True))
        if not files:
            print(f"WARNING: no files matched {pattern}", file=sys.stderr)
            ok = False
            continue

        entries = []
        for path in files:
            try:
                with open(path, encoding="utf-8") as f:
                    entries.append(json.load(f))
            except json.JSONDecodeError as e:
                print(f"ERROR: invalid JSON in {os.path.relpath(path, ROOT)}: {e}", file=sys.stderr)
                ok = False

        out_path = os.path.join(BUILD_DIR, f"{kind}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

        print(f"  {kind}: {len(entries)} entries → build/{kind}.json")

    return ok


if __name__ == "__main__":
    print("Aggregating JSON data...")
    if aggregate():
        print("Done. Run 'python3 scripts/lint_data.py' to validate.")
    else:
        sys.exit(1)
