#!/usr/bin/env python3
"""Render the three pages of the index.

  index.html      the index itself: start-here path, tribes, layers, entries
  broadcast.html  the two podcasts, clustered into research arcs
  notebook.html   concept notes, research essays and the blog

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
    return html.escape(str(text), quote=True)


def read_json(name: str):
    return json.loads((ROOT / "data" / name).read_text())


def human_duration(seconds: int) -> str:
    minutes, secs = divmod(int(seconds or 0), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes == 0:
        return f"{secs}s"
    return f"{minutes}m {secs:02d}s"


def human_views(views: int) -> str:
    if views and views >= 1000:
        return f"{views / 1000:.1f}k views"
    return f"{views} views"


def iso_date(stamp: str) -> str:
    stamp = (stamp or "").strip()
    if re.fullmatch(r"\d{8}", stamp):
        return f"{stamp[0:4]}-{stamp[4:6]}-{stamp[6:8]}"
    return stamp


def load_summaries(path: str) -> dict:
    raw = (ROOT / "data" / path).read_text()
    out = {}
    for block in re.split(r"^@@ ", raw, flags=re.M)[1:]:
        key, _, body = block.partition("\n")
        out[key.strip()] = " ".join(body.split())
    return out


# ---------------------------------------------------------------- entries ---

def render_entry(index: int, entry: dict) -> str:
    tags = [m for m in entry.get("meta", []) if m != "private"]
    meta = " &middot; ".join(esc(m) for m in tags)
    date = esc(entry.get("date", ""))
    chip = ""
    if "private" in entry.get("meta", []):
        chip = ' <span class="chip">private</span>'
    links = ""
    for key, label in (("site", "site"), ("details", "details"), ("app", "app")):
        if entry.get(key):
            links += (f' &middot; <a class="site-link" href="{esc(entry[key])}" rel="noopener">'
                      f'{label} &#8599;</a>')
    if entry.get("doi"):
        links += f' &middot; <a class="site-link" href="{esc(entry["doi"])}" rel="noopener">doi</a>'
    meta_line = (f'<span class="meta">{meta} &middot; <span class="date">{date}</span>'
                 f'{chip}{links}</span>')
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
    rows = []
    for entry in group["entries"]:
        counter[0] += 1
        rows.append(render_entry(counter[0], entry))
    note = ""
    if group.get("note"):
        note = f'<p class="group-note">{esc(group["note"].replace("{n}", str(len(group["entries"]))))}</p>'
    return f"""    <section class="group" id="{esc(group['id'])}">
      <div class="group-head">
        <h2>{esc(group['title'])}</h2>
        <span class="count">{len(group['entries'])} entries</span>
      </div>
      {note}
{chr(10).join(rows)}
    </section>"""


# ------------------------------------------------------------ start / cards ---

def render_start_here(data: dict, entries_by_title: dict, glosses: dict) -> str:
    rows = []
    for i, title in enumerate(data.get("start_here", []), start=1):
        entry = entries_by_title.get(title, {})
        url = entry.get("url", "#")
        gloss = glosses.get(title, "")
        rows.append(f"""        <li>
          <span class="step">{i}</span>
          <a href="{esc(url)}" rel="noopener">{esc(title)}</a>
          <span class="gloss">{esc(gloss)}</span>
        </li>""")
    return "\n".join(rows)


def render_tribe_cards(taxonomy: dict) -> str:
    cards = []
    for tribe in taxonomy["tribes"]:
        cards.append(f"""      <a class="card" href="#{esc(tribe['id'])}">
        <h3>{esc(tribe['title'])}</h3>
        <p>{esc(tribe['note'])}</p>
      </a>""")
    return "\n".join(cards)


def render_layers(layers: list) -> str:
    rows = []
    for layer in layers:
        rows.append(f"""        <li>
          <span class="label">{esc(layer['label'])}</span>
          <span class="text">{esc(layer['text'])}</span>
          <span class="where">{esc(layer['where'])}</span>
        </li>""")
    return "\n".join(rows)


# --------------------------------------------------------------- broadcast ---

def render_arcs(arcs: list, episodes: list, summaries: dict, counter: list) -> str:
    by_id = {e["id"]: e for e in episodes}
    blocks = []
    for arc in arcs:
        rows = []
        for video_id in arc["ids"]:
            episode = by_id.get(video_id)
            if episode is None:
                continue
            counter[0] += 1
            summary = summaries.get(video_id, "")
            if summary and len(summary.split()) != TARGET:
                print(f"  !! {episode['title']}: summary is {len(summary.split())} words")
            meta = " &middot; ".join([
                esc(human_duration(episode.get("duration", 0))),
                esc(human_views(episode.get("views", 0))),
                esc(iso_date(episode.get("date", ""))),
            ])
            rows.append(f"""      <article class="entry">
        <span class="num">{counter[0]:02d}</span>
        <div>
          <div class="entry-title">
            <a href="https://www.youtube.com/watch?v={esc(video_id)}" rel="noopener">{esc(episode['title'])}</a>
            <span class="arrow" aria-hidden="true">&#8599;</span>
            <span class="meta">{meta}</span>
          </div>
          <p class="summary">{esc(summary)}</p>
        </div>
      </article>""")
        blocks.append(f"""    <section class="group" id="arc-{esc(arc['id'])}">
      <div class="group-head">
        <h2>{esc(arc['title'])}</h2>
        <span class="count">{len(arc['ids'])} episodes</span>
      </div>
      <p class="group-note">{esc(arc['note'])}</p>
{chr(10).join(rows)}
    </section>""")
    return "\n\n".join(blocks)


# ---------------------------------------------------------------- notebook ---

def render_note_items(items: list, counter: list) -> str:
    rows = []
    for item in items:
        counter[0] += 1
        lede = item.get("lede") or ""
        promoted = ' <span class="chip">promoted</span>' if item.get("promoted") else ""
        date = esc(item.get("date", ""))
        rows.append(f"""      <article class="entry">
        <span class="num">{counter[0]:02d}</span>
        <div>
          <div class="entry-title">
            <a href="{esc(item['url'])}" rel="noopener">{esc(item['title'])}</a>
            <span class="arrow" aria-hidden="true">&#8599;</span>
            <span class="meta">{date}</span>{promoted}
          </div>
          <p class="summary">{esc(lede)}</p>
        </div>
      </article>""")
    return "\n".join(rows)


# -------------------------------------------------------------------- main ---

def build_index(data: dict, taxonomy: dict) -> str:
    template = (ROOT / "templates" / "index.html").read_text()
    entries_by_title = {e["title"]: e for g in data["groups"] for e in g["entries"]}

    counter = [0]
    groups = "\n\n".join(render_group(g, counter) for g in data["groups"])
    total = counter[0]

    counts = {g["id"]: len(g["entries"]) for g in data["groups"]}
    tribes = [g for g in data["groups"] if g["id"] in
              {t["id"] for t in taxonomy["tribes"]}]
    tribe_count = sum(len(g["entries"]) for g in tribes)
    private = sum(1 for g in data["groups"] for e in g["entries"] if "private" in e.get("meta", []))

    summary_line = (f"{total} entries &middot; {len(tribes)} tribes &middot; {tribe_count} in tribes "
                    f"&middot; {counts.get('foundations', 0)} foundations "
                    f"&middot; {counts.get('citable', 0)} citable records "
                    f"&middot; {counts.get('releases', 0)} release lines "
                    f"&middot; {counts.get('broadcast', 0)} broadcasts "
                    f"&middot; {counts.get('elsewhere', 0)} elsewhere "
                    f"&middot; {private} held private")

    out = (template
           .replace("{{GROUPS}}", groups)
           .replace("{{COUNTS}}", summary_line)
           .replace("{{STARTHERE}}", render_start_here(data, entries_by_title,
                                                       taxonomy.get("start_glosses", {})))
           .replace("{{TRIBE_CARDS}}", render_tribe_cards(taxonomy))
           .replace("{{LAYERS}}", render_layers(data.get("layers", [])))
           .replace("{{TRIBE_COUNT}}", str(tribe_count)))
    (ROOT / "index.html").write_text(out)
    return f"index.html — {total} entries"


def build_broadcast() -> str:
    template = (ROOT / "templates" / "broadcast.html").read_text()
    arcs = read_json("arcs.json")
    episodes = read_json("episodes.json")
    labs = read_json("labs_episodes.json")
    stc_summaries = load_summaries("podcast_summaries.txt")
    labs_summaries = load_summaries("labs_summaries.txt")

    counter = [0]
    stc_blocks = render_arcs(arcs["stc"], episodes, stc_summaries, counter)
    labs_blocks = render_arcs(arcs["labs"], labs, labs_summaries, counter)
    public_labs = sum(1 for e in labs if e.get("available"))

    counts = (f"{len(episodes)} long-form episodes &middot; {public_labs} of {len(labs)} "
              f"short-form episodes public &middot; {len(arcs['stc'])} research arcs")
    out = (template
           .replace("{{STC_ARCS}}", stc_blocks)
           .replace("{{LABS_ARCS}}", labs_blocks)
           .replace("{{COUNTS}}", counts)
           .replace("{{STC_COUNT}}", str(len(episodes)))
           .replace("{{LABS_COUNT}}", str(len(labs)))
           .replace("{{LABS_PUBLIC}}", str(public_labs)))
    (ROOT / "broadcast.html").write_text(out)
    return f"broadcast.html — {len(episodes)} + {len(labs)} episodes"


def build_notebook() -> str:
    template = (ROOT / "templates" / "notebook.html").read_text()
    notebook = read_json("notebook.json")
    taxonomy = read_json("taxonomy.json")

    counter = [0]
    concepts = render_note_items(notebook["concepts"], counter)
    research = render_note_items(notebook["research"], counter)
    blog = render_note_items(notebook["blog"], counter)

    promoted = [item["title"] for item in notebook["research"] + notebook["blog"] if item.get("promoted")]
    promoted_line = ", ".join(promoted)

    counts = (f"{len(notebook['concepts'])} concept notes &middot; {len(notebook['research'])} research essays "
              f"&middot; {len(notebook['blog'])} blog posts &middot; {len(promoted)} promoted into the index")
    out = (template
           .replace("{{CONCEPTS}}", concepts)
           .replace("{{RESEARCH}}", research)
           .replace("{{BLOG}}", blog)
           .replace("{{COUNTS}}", counts)
           .replace("{{CONCEPTS_COUNT}}", str(len(notebook["concepts"])))
           .replace("{{RESEARCH_COUNT}}", str(len(notebook["research"])))
           .replace("{{BLOG_COUNT}}", str(len(notebook["blog"])))
           .replace("{{PROMOTED_COUNT}}", str(len(promoted)))
           .replace("{{PROMOTED_LIST}}", promoted_line))
    (ROOT / "notebook.html").write_text(out)
    return f"notebook.html — {len(notebook['concepts'])} + {len(notebook['research'])} + {len(notebook['blog'])} notes"


def main() -> int:
    data = read_json("entries.json")
    taxonomy = read_json("taxonomy.json")
    for line in (build_index(data, taxonomy), build_broadcast(), build_notebook()):
        print(f"wrote {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
