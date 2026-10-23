#!/usr/bin/env python3
"""Attach the live GitHub Pages URL to entries that have one.

Only URLs that actually serve a page (HTTP 200) are recorded, so a private
repository with a stale homepage never gets a dead link on the index.

The script is conservative: it clears a recorded site only when the probe
returns a definitive 404/410. A timeout, a 403 or a DNS failure leaves the
existing link in place, so a flaky network cannot strip the index.

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


def probe(url: str) -> str:
    """Return "live", "dead" (definitive 404/410) or "unknown"."""
    request = urllib.request.Request(url, headers={"User-Agent": "shunyabar-labs-index"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return "live" if response.status == 200 else "unknown"
    except urllib.error.HTTPError as error:
        return "dead" if error.code in (404, 410) else "unknown"
    except Exception:
        return "unknown"


def main() -> int:
    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())

    added = kept = cleared = 0
    for group in data["groups"]:
        for entry in group["entries"]:
            match = REPO_RE.match(entry.get("url", ""))
            if not match:
                continue
            owner, repo = match.group(1), match.group(2).removesuffix(".html")
            site = api(f"repos/{owner}/{repo}/pages")
            if not site:
                # the API does not always report Pages; probe the conventional URL
                site = f"https://{owner}.github.io/{repo}/"
            state = probe(site)
            if state == "live":
                if entry.get("site") != site:
                    entry["site"] = site
                    added += 1
                    print(f"  {owner}/{repo} -> {site}")
                else:
                    kept += 1
            elif state == "dead" and entry.get("site"):
                entry.pop("site", None)
                cleared += 1
                print(f"  {owner}/{repo} -> dead, link cleared")

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"site: {added} attached, {kept} already current, {cleared} cleared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
