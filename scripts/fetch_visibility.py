#!/usr/bin/env python3
"""Tag entries whose GitHub repository is private.

Uses the `gh` CLI (already authenticated) to read each repository's
visibility, then marks those entries with a "private" chip so the index
can point readers at the access contact instead of a 404.

The cache in data/visibility.json keeps runs cheap, but it expires: entries
older than MAX_AGE_DAYS (and any "unknown" result) are re-queried, so a
repository that flips to public stops showing a stale `private` chip.

Usage:  python3 scripts/fetch_visibility.py [--refresh]
"""
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_RE = re.compile(r"https://github\.com/([^/]+)/([^/#?]+)")
MAX_AGE_DAYS = 7


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


def cache_age_days(path: pathlib.Path) -> float:
    if not path.exists():
        return float("inf")
    return (time.time() - path.stat().st_mtime) / 86400


def main() -> int:
    force = "--refresh" in sys.argv
    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())

    cache_path = ROOT / "data" / "visibility.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    stale = force or cache_age_days(cache_path) > MAX_AGE_DAYS
    if stale:
        print(f"cache {'forced' if force else 'expired'}; re-querying every repository")

    queried = 0
    for group in data["groups"]:
        for entry in group["entries"]:
            match = REPO_RE.match(entry.get("url", ""))
            if not match:
                continue
            owner, repo = match.group(1), match.group(2).removesuffix(".html")
            key = f"{owner}/{repo}"
            if stale or key not in cache or cache[key] == "unknown":
                cache[key] = visibility(owner, repo)
                queried += 1
                print(f"  {key}: {cache[key]}")
            meta = [x for x in entry.get("meta", []) if x != "private"]
            if cache[key] == "private":
                meta.append("private")
            entry["meta"] = meta

    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    private = sum(1 for v in cache.values() if v == "private")
    print(f"queried {queried} repositories; {private} private in cache")
    return 0


if __name__ == "__main__":
    sys.exit(main())
