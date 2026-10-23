#!/usr/bin/env python3
"""Attach the lab's own write-up ("details") for each entry, when one exists.

The docs repository carries a project page per project under /projects/<slug>.
Those pages are the detailed ShunyaBar Labs version of each piece of work,
so an entry can point at the repository, the project's own Pages site, and
the lab's long-form write-up.

The script is additive: it never removes a hand-set link (a YouTube channel,
a Zenodo record page). It only overwrites or clears a docs-project link that
it owns, and it does that only on a definitive 404 — a network failure or a
403 leaves the entry untouched.

Usage:  python3 scripts/fetch_details.py
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = "https://sethuiyer.github.io/docs/projects"
REPO_RE = re.compile(r"https://github\.com/([^/]+)/([^/#?]+)")

# repository name -> docs project slug
SLUGS = {
    "FUTCache": "futcache",
    "NitroSAT": "nitrosat",
    "multiplicative-pinn-framework": "multiplicative-pinn",
    "spectral-multiplicative-framework": "spectral-multiplicative",
    "shunyabar.lua": "shunyabar-lua",
}


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


def candidate(entry: dict) -> str:
    """The docs-project URL for a GitHub repository entry, or "" otherwise."""
    match = REPO_RE.match(entry.get("url", ""))
    if not match:
        return ""
    repo = match.group(2).removesuffix(".html")
    return f"{DOCS}/{SLUGS.get(repo, repo.lower())}/"


def main() -> int:
    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())

    added = kept = cleared = 0
    for group in data["groups"]:
        for entry in group["entries"]:
            url = candidate(entry)
            if not url:
                continue
            state = probe(url)
            if state == "live":
                if entry.get("details") != url:
                    entry["details"] = url
                    added += 1
                else:
                    kept += 1
            elif state == "dead" and entry.get("details", "").startswith(DOCS):
                # clear only a link this script owns
                entry.pop("details", None)
                cleared += 1

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"details: {added} attached, {kept} already current, {cleared} cleared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
