#!/usr/bin/env python3
"""Fetch the lab's writing from the live sites into data/notebook.json.

Three collections:
  concepts  — the lab's concept notes      (sethuiyer.github.io/docs/concepts/)
  research  — long-form research essays    (research.shunyabar.foo/posts/)
  blog      — the working blog             (sethuiyer.github.io/docs/blog/)

Each item keeps the author's own lede (the page description) rather than a
rewritten summary, so the notebook never claims more than the source says.

Usage:  python3 scripts/fetch_notebook.py
"""
import concurrent.futures
import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = "https://sethuiyer.github.io/docs/"
RESEARCH = "https://research.shunyabar.foo/"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ShunyaBarLabs-index"}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(request, timeout=30).read().decode("utf-8", "ignore")


def meta(html: str, patterns: list) -> str:
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    return ""


def parse(html: str, url: str) -> dict:
    title = meta(html, [r'<meta property="og:title" content="([^"]+)"', r"<title>([^<]+)</title>"])
    title = re.sub(r"^ShunyaBar Labs\s*[—–-]\s*", "", title)
    title = re.sub(r"\s*[·|]\s*ShunyaBar Labs\s*$", "", title).strip()
    lede = meta(html, [r'<meta name="description" content="([^"]+)"',
                       r'<meta property="og:description" content="([^"]+)"'])
    date = meta(html, [r'<meta property="article:published_time" content="([^"]+)"',
                       r'<meta name="date" content="([^"]+)"',
                       r'<time[^>]*datetime="([^"]+)"'])
    if not date:
        match = re.search(r"(\w+ \d{1,2}, 20\d\d)", html)
        date = match.group(1) if match else ""
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return {"title": title, "url": url, "date": date, "lede": lede, "slug": slug}


def docs_pages(collection: str) -> list:
    sitemap = fetch(f"{DOCS}sitemap-0.xml")
    urls = sorted(set(re.findall(r"<loc>([^<]+)</loc>", sitemap)))
    urls = [u for u in urls if f"/docs/{collection}/" in u and "/tags/" not in u]
    urls = [u for u in urls if not u.rstrip("/").endswith(f"/docs/{collection}")]
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        return list(pool.map(lambda u: parse(fetch(u), u), urls))


def research_pages() -> list:
    index = fetch(RESEARCH)
    slugs = sorted(set(re.findall(r'href="\./posts/([a-z0-9\-]+)\.html"', index)))
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        return list(pool.map(
            lambda s: parse(fetch(f"{RESEARCH}posts/{s}.html"), f"{RESEARCH}posts/{s}.html"), slugs))


def base_title(title: str) -> str:
    """Drop a scraped subtitle (" | Constraint Intelligence Platform")."""
    return title.split(" | ")[0].strip()


def main() -> int:
    taxonomy = json.loads((ROOT / "data" / "taxonomy.json").read_text())
    promoted = {base_title(t) for t in taxonomy.get("promoted_posts", [])}
    data = {
        "concepts": docs_pages("concepts"),
        "research": research_pages(),
        "blog": docs_pages("blog"),
    }
    for collection in ("blog", "research"):
        for item in data[collection]:
            title = base_title(item["title"])
            item["promoted"] = any(title.startswith(t) for t in promoted)
    path = ROOT / "data" / "notebook.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote notebook.json — {len(data['concepts'])} concepts, "
          f"{len(data['research'])} research notes, {len(data['blog'])} blog posts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
