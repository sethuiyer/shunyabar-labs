# ShunyaBar Labs

A master index of the lab's research, built around one idea:

> **Decision-preserving abstraction** — preserve the distinctions that matter for a decision,
> and discard everything else.

Live at **https://sethuiyer.github.io/shunyabar-labs/** (deployed by GitHub Pages from
`.github/workflows/pages.yml` on every push to `main`).

Every entry in the index carries a **40-word summary**, and the summaries are enforced:
`scripts/check_summaries.py` fails the build if any summary is not exactly forty words.

Entries with a live GitHub Pages site carry a **site ↗** link next to the repository link.

## Access

Some repositories and essays are **private** and are marked with a `private` chip in the
index. To request access, write to **rxgtoing@gmail.com**.

## Repository layout

| Repo | Purpose |
|---|---|
| `sethuiyer/shunyabar-labs` | this index site (public) |
| `sethuiyer/shunyabar-labs-archive` | the earlier collection, with the published essays and figures (private) |

## Layout of this repo

```
index.html            generated — the site (do not edit by hand)
templates/index.html  page template with {{GROUPS}} / {{COUNTS}} placeholders
data/entries.json     the index: groups, titles, links, dates, tags, summaries
data/summaries.txt    the curated 40-word summaries, one block per entry
assets/style.css      stylesheet: light / dark / auto
assets/theme.js       theme toggle (auto → light → dark), persisted in localStorage
scripts/build.py      renders index.html from data + templates
scripts/apply_summaries.py  copies data/summaries.txt into data/entries.json
scripts/check_summaries.py  verifies every summary is exactly 40 words
scripts/fetch_visibility.py  tags entries whose repository is private
scripts/fetch_pages.py       attaches live GitHub Pages URLs to entries
scripts/prune.py             prunes entries that fail the central criterion
data/removed.json            the pruned entries, with reasons, so nothing is lost
```

## Workflow

```bash
python3 scripts/apply_summaries.py   # refresh summaries in entries.json
python3 scripts/check_summaries.py   # 55/55 summaries at exactly 40 words
python3 scripts/fetch_visibility.py  # re-tag private repositories
python3 scripts/fetch_pages.py       # attach live GitHub Pages URLs
python3 scripts/build.py             # regenerate index.html
```

## The criterion

An entry stays in the index only if the work does one of two things:

- **A.** constructs or analyses a representation, abstraction, quotient or encoding of a
  system, and states what information it keeps or discards;
- **B.** identifies distinctions that must be preserved for a decision, guarantee or
  evaluation to remain valid.

`scripts/prune.py` applies that criterion. Removed entries are written to
`data/removed.json` with a reason, so any of them can be reinstated.

Serve locally:

```bash
python3 -m http.server 8000
```

## Editing an entry

1. Edit the summary block in `data/summaries.txt` (title must match the entry title exactly).
2. Run `scripts/apply_summaries.py` — it reports any summary that is not exactly 40 words.
3. Fix the count, re-run, then `scripts/build.py`.
4. Commit both `data/entries.json` and `index.html`.

## Design

Minimal and paper-like: no web fonts, no frameworks, no trackers, no build-time
dependencies beyond the Python standard library. Two themes driven by CSS custom
properties, with `prefers-color-scheme` as the default and a manual override that
persists. Type is a serif for prose and headings, a mono for metadata.

## Licence

MIT — see `LICENSE`.
