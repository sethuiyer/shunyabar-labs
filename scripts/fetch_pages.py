#!/usr/bin/env python3
"""Attach the live GitHub Pages URL to entries that have one.

Only URLs that actually serve a page (HTTP 200) are recorded, so a private
repository with a stale homepage never gets a dead link on the index.

Usage:  python3 scripts/fetch_pages.py
"""
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_RE = re.compile(r"https://github\.com/([^/]+)/([^/#?]+)")


def api(path: str) -> str:
    out = subprocess.run(["gh", "api", path, "--jq", ".html_url"],
                         capture_output=True, text=True, timeout=30)
    return out.stdout.strip() if out.returncode == 0 else ""


def live(url: str) -> bool:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "shunyabar-labs-index"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        return e.code == 200
    except Exception:
        return False


def main() -> int:
    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())

    found = 0
    for group in data["groups"]:
        for entry in group["entries"]:
            m = REPO_RE.match(entry["url"])
            if not m:
                continue
            owner, repo = m.group(1), m.group(2).removesuffix(".html")
            site = api(f"repos/{owner}/{repo}/pages")
            if not site:
                # the API does not always report Pages; probe the conventional URL
                candidate = f"https://{owner}.github.io/{repo}/"
                site = candidate if live(candidate) else ""
            if site and live(site):
                entry["site"] = site
                found += 1
                print(f"  {owner}/{repo} -> {site}")
            else:
                entry.pop("site", None)

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"attached {found} live Pages URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
