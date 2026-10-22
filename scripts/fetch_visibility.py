#!/usr/bin/env python3
"""Tag entries whose GitHub repository is private.

Uses the `gh` CLI (already authenticated) to read each repository's
visibility, then marks those entries with a "private" chip so the index
can point readers at the access contact instead of a 404.

Usage:  python3 scripts/fetch_visibility.py
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_RE = re.compile(r"https://github\.com/([^/]+)/([^/#?]+)")


def visibility(owner: str, repo: str) -> str:
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}", "--jq", ".visibility"],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return "unknown"


def main() -> int:
    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())

    cache_path = ROOT / "data" / "visibility.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    changed = 0
    for group in data["groups"]:
        for entry in group["entries"]:
            m = REPO_RE.match(entry["url"])
            if not m:
                continue
            owner, repo = m.group(1), m.group(2).removesuffix(".html")
            key = f"{owner}/{repo}"
            if key not in cache:
                cache[key] = visibility(owner, repo)
                print(f"  {key}: {cache[key]}")
            vis = cache[key]
            meta = [x for x in entry.get("meta", []) if x != "private"]
            if vis == "private":
                meta.append("private")
                changed += 1
            entry["meta"] = meta

    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"tagged {changed} private entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
