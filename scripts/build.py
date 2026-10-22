#!/usr/bin/env python3
"""Render index.html from data/entries.json + templates/index.html.

Usage:  python3 scripts/build.py
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = 40


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def render_entry(index: int, entry: dict) -> str:
    tags = [m for m in entry.get("meta", []) if m != "private"]
    meta = " &middot; ".join(esc(m) for m in tags)
    date = esc(entry.get("date", ""))
    chip = ""
    if "private" in entry.get("meta", []):
        chip = ' <span class="chip">private</span>'
    site = ""
    if entry.get("site"):
        site = (f' &middot; <a class="site-link" href="{esc(entry["site"])}" rel="noopener">'
                f'site &#8599;</a>')
    details = ""
    if entry.get("details"):
        details = (f' &middot; <a class="site-link" href="{esc(entry["details"])}" rel="noopener">'
                   f'details &#8599;</a>')
    app = ""
    if entry.get("app"):
        app = (f' &middot; <a class="site-link" href="{esc(entry["app"])}" rel="noopener">'
               f'app &#8599;</a>')
    doi = ""
    if entry.get("doi"):
        doi = (f' &middot; <a class="site-link" href="{esc(entry["doi"])}" rel="noopener">'
               f'doi</a>')
    meta_line = (f'<span class="meta">{meta} &middot; <span class="date">{date}</span>'
                 f'{chip}{site}{details}{app}{doi}</span>')
    summary_words = len(entry["summary"].split())
    if summary_words != TARGET:
        print(f"  !! {entry['title']}: summary is {summary_words} words")
    return f"""      <article class="entry">
        <span class="num">{index:02d}</span>
        <div>
          <div class="entry-title">
            <a href="{esc(entry['url'])}" rel="noopener">{esc(entry['title'])}</a>
            <span class="arrow" aria-hidden="true">&#8599;</span>
            {meta_line}
          </div>
          <p class="summary">{esc(entry['summary'])}</p>
        </div>
      </article>"""


def render_group(group: dict, counter: list) -> str:
    entries = group["entries"]
    rows = []
    for entry in entries:
        counter[0] += 1
        rows.append(render_entry(counter[0], entry))

    note = f'<p class="group-note">{esc(group["note"].replace("{n}", str(len(entries))))}</p>' if group.get("note") else ""
    return f"""    <section class="group" id="{esc(group['id'])}">
      <div class="group-head">
        <h2>{esc(group['title'])}</h2>
        <span class="count">{len(entries)} entries</span>
      </div>
      {note}
{chr(10).join(rows)}
    </section>"""


def main() -> int:
    data = json.loads((ROOT / "data" / "entries.json").read_text())
    template = (ROOT / "templates" / "index.html").read_text()

    counter = [0]
    groups = "\n\n".join(render_group(g, counter) for g in data["groups"])

    total = counter[0]
    repos = sum(len(g["entries"]) for g in data["groups"] if g["id"] == "repos")
    gists = sum(len(g["entries"]) for g in data["groups"] if g["id"] == "gists")
    essays = sum(len(g["entries"]) for g in data["groups"] if g["id"] == "essays")
    rel = sum(len(g["entries"]) for g in data["groups"] if g["id"] == "releases")
    zen = sum(len(g["entries"]) for g in data["groups"] if g["id"] == "zenodo")
    cont = sum(len(g["entries"]) for g in data["groups"] if g["id"] == "continued")
    found = sum(len(g["entries"]) for g in data["groups"] if g["id"] == "foundations")
    private = sum(1 for g in data["groups"] for e in g["entries"] if "private" in e.get("meta", []))
    counts = (f"{total} entries &middot; {repos} repositories &middot; {cont} continuing "
              f"&middot; {gists} gists &middot; {essays} essays &middot; {found} foundations "
              f"&middot; {zen} citable records &middot; {rel} release lines &middot; "
              f"{private} held private")

    out = template.replace("{{GROUPS}}", groups).replace("{{COUNTS}}", counts)
    (ROOT / "index.html").write_text(out)
    print(f"wrote index.html — {total} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
