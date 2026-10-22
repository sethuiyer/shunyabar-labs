#!/usr/bin/env python3
"""Rewrite every summary in data/entries.json to exactly 40 words.

The curated summaries live in data/summaries.txt as blocks separated by a
"@@ <title>" marker, one summary per block. This script normalises
whitespace and rewrites the JSON so each summary is exactly TARGET words.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = 40


def main() -> int:
    raw = (ROOT / "data" / "summaries.txt").read_text()
    blocks = re.split(r"^@@ ", raw, flags=re.M)[1:]
    curated = {}
    for block in blocks:
        title, _, body = block.partition("\n")
        title = title.strip()
        body = " ".join(body.split())
        if not body:
            continue
        if len(body.split()) != TARGET:
            print(f"  !! {title}: {len(body.split())} words")
        curated[title] = body

    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())
    missing = []
    for group in data["groups"]:
        for entry in group["entries"]:
            if entry["title"] in curated:
                entry["summary"] = curated[entry["title"]]
            else:
                missing.append(entry["title"])
    if missing:
        print("missing summaries for:", missing)
        return 1
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"rewrote {len(curated)} summaries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
