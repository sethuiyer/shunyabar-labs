#!/usr/bin/env python3
"""Attach the lab's own write-up ("details") for each entry, when one exists.

The docs repository carries a project page per project under /projects/<slug>.
Those pages are the detailed ShunyaBar Labs version of each piece of work,
so an entry can point at the repository, the project's own Pages site, and
the lab's long-form write-up.

Usage:  python3 scripts/fetch_details.py
"""
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = "https://sethuiyer.github.io/docs/projects"

# repository name -> docs project slug
SLUGS = {
    "FUTCache": "futcache",
    "NitroSAT": "nitrosat",
    "multiplicative-pinn-framework": "multiplicative-pinn",
    "spectral-multiplicative-framework": "spectral-multiplicative",
    "shunyabar.lua": "shunyabar-lua",
}


def slug_for(name: str) -> str:
    if name in SLUGS:
        return SLUGS[name]
    return name.lower()


def live(url: str) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "shunyabar-labs-index"})
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
            name = entry["title"]
            url = f"{DOCS}/{slug_for(name)}/"
            if live(url):
                entry["details"] = url
                found += 1
            elif "/zenodo/" not in entry.get("details", ""):
                # keep hand-set detail links (Zenodo record pages)
                entry.pop("details", None)

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"attached {found} lab write-ups")
    return 0


if __name__ == "__main__":
    sys.exit(main())
