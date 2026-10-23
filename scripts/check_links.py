#!/usr/bin/env python3
"""Sweep every link the site publishes and report anything that is not 200.

Checks the index (`url`, `site`, `details`, `doi`, `app`) and every notebook
link. It is an audit, not part of the deploy: GitHub Pages, GitHub and Zenodo
rate-limit aggressive sweeps, and private repositories answer 404 to
anonymous requests. Those two cases are reported but do not fail the run.

Exit code 1 if a link is unexpectedly dead.

Usage:  python3 scripts/check_links.py [--timeout 20]
"""
import concurrent.futures
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYS = ("url", "site", "details", "doi", "app")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ShunyaBarLabs-link-sweep"}


def timeout() -> int:
    for index, arg in enumerate(sys.argv):
        if arg == "--timeout" and index + 1 < len(sys.argv):
            return int(sys.argv[index + 1])
    return 20


def targets() -> dict:
    """url -> {"private": bool, "labels": [...]}"""
    found = {}
    data = json.loads((ROOT / "data" / "entries.json").read_text())
    for group in data["groups"]:
        for entry in group["entries"]:
            private = "private" in entry.get("meta", [])
            for key in KEYS:
                url = entry.get(key)
                if not url:
                    continue
                slot = found.setdefault(url, {"private": False, "labels": []})
                slot["private"] = slot["private"] or private
                slot["labels"].append(f'{group["id"]}/{entry["title"]}')

    notebook = json.loads((ROOT / "data" / "notebook.json").read_text())
    for collection, items in notebook.items():
        for item in items:
            url = item.get("url")
            if not url:
                continue
            slot = found.setdefault(url, {"private": False, "labels": []})
            slot["labels"].append(f"notebook/{collection}: {item['title']}")
    return found


def probe(url: str) -> tuple:
    request = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(request, timeout=timeout()) as response:
            return url, response.status
    except urllib.error.HTTPError as error:
        return url, error.code
    except Exception as error:
        return url, str(error)[:60]


def main() -> int:
    found = targets()
    with concurrent.futures.ThreadPoolExecutor(10) as pool:
        results = list(pool.map(probe, sorted(found)))

    ok = throttled = expected_private = 0
    failures = []
    for url, status in results:
        if status == 200:
            ok += 1
        elif status in (403, 429):
            throttled += 1
        elif status == 404 and found[url]["private"]:
            expected_private += 1
        else:
            failures.append((url, status, found[url]["labels"][:2]))

    print(f"{len(results)} links: {ok} ok, {throttled} throttled, "
          f"{expected_private} private (404 to anonymous), {len(failures)} dead")
    for url, status, labels in failures:
        print(f"  {status} {url}")
        for label in labels:
            print(f"      from {label}")
    if throttled:
        print("  (403/429 are rate limits, not dead links; re-run later)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
