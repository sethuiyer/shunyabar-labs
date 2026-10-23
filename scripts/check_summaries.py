#!/usr/bin/env python3
"""Verify every curated summary is exactly 40 words.

Covers all three summary sources:

  data/entries.json            the index
  data/podcast_summaries.txt   Space Time Cafe, keyed by video id
  data/labs_summaries.txt      Shunyabar Labs podcast

Usage:  python3 scripts/check_summaries.py
Exit code 1 if any summary deviates from 40 words.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = 40
SUMMARY_FILES = [
    ("podcast_summaries.txt", "Space Time Cafe"),
    ("labs_summaries.txt", "Shunyabar Labs podcast"),
]


def check_file(name: str, label: str) -> list:
    raw = (ROOT / "data" / name).read_text()
    bad = []
    total = 0
    for block in re.split(r"^@@ ", raw, flags=re.M)[1:]:
        key, _, body = block.partition("\n")
        key = key.strip()
        if not key or not body.strip():
            continue
        total += 1
        words = body.split()
        if len(words) != TARGET:
            bad.append((label, key, len(words)))
    return total, bad


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
    index_bad = len(bad)

    grand_total = total
    for name, label in SUMMARY_FILES:
        count, problems = check_file(name, label)
        grand_total += count
        bad.extend(problems)
        print(f"{label}: {count - len(problems)}/{count} summaries at exactly {TARGET} words")

    for gid, title, n in bad:
        print(f"  {gid}/{title}: {n} words (need {TARGET})")
    print(f"index: {total - index_bad}/{total} entries at exactly {TARGET} words")
    print(f"total: {grand_total - len(bad)}/{grand_total} summaries at exactly {TARGET} words")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
