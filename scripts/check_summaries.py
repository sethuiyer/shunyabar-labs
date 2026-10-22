#!/usr/bin/env python3
"""Verify every entry summary in data/entries.json is exactly 40 words.

Usage:  python3 scripts/check_summaries.py
Exit code 1 if any summary deviates from 40 words.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = 40


def main() -> int:
    data = json.loads((ROOT / "data" / "entries.json").read_text())
    bad = []
    total = 0
    for group in data["groups"]:
        for entry in group["entries"]:
            total += 1
            words = entry["summary"].split()
            if len(words) != TARGET:
                bad.append((group["id"], entry["title"], len(words)))

    for gid, title, n in bad:
        print(f"  {gid}/{title}: {n} words (need {TARGET})")
    print(f"{total - len(bad)}/{total} summaries at exactly {TARGET} words")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
