# ShunyaBar Labs

A master index of the lab's research, built around one idea:

> **Decision-preserving abstraction** — preserve the distinctions that matter for a decision,
> and discard everything else.

Live at **https://sethuiyer.github.io/shunyabar-labs/** (deployed by GitHub Pages from
`.github/workflows/pages.yml` on every push to `main`).

Two more pages hang off the index:

- **Broadcast** — `broadcast.html`, the two podcast playlists clustered into five research arcs
- **Notebook** — `notebook.html`, the concept notes, research essays and blog, with the eight
  pieces promoted into the index marked

Every entry in the index carries a **40-word summary**, and the summaries are enforced:
`scripts/check_summaries.py` fails the build if any summary is not exactly forty words.

Entries carry up to three extra links next to the repository link:

- **site ↗** — the project's own GitHub Pages site, when it serves a live page
- **details ↗** — the lab's own long-form write-up of the project, at `sethuiyer.github.io/docs`
- **app** — a browser build, when the project has one
- **doi** — the Zenodo record, the version of record for the artifact

Every link is verified to resolve before it is attached, so the index carries no dead URLs.

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
index.html            generated — the index page (do not edit by hand)
broadcast.html        generated — the podcasts, clustered into research arcs
notebook.html         generated — concepts, research essays and the blog
templates/            page templates with {{...}} placeholders
data/entries.json     the index: groups, titles, links, dates, tags, summaries
data/taxonomy.json    the five tribes, the five layers, the Start Here path, new entries
data/summaries.txt    the curated 40-word summaries, one block per entry
data/citable_records.json     the Zenodo records, with their DOIs
data/episodes.json    Space Time Cafe episode metadata (fetched with yt-dlp)
data/labs_episodes.json  Shunyabar Labs podcast episode metadata
data/arcs.json        the five research arcs, and which episode sits in which
data/notebook.json    concept notes, research essays and blog posts, with the author's ledes
data/podcast_summaries.txt  40-word summaries for Space Time Cafe, keyed by video id
data/labs_summaries.txt     40-word summaries for the Shunyabar Labs podcast
assets/style.css      stylesheet: light / dark / auto
assets/theme.js       theme toggle (auto → light → dark), persisted in localStorage
scripts/build.py      renders the three pages from data + templates
scripts/apply_summaries.py  copies data/summaries.txt into data/entries.json
scripts/apply_taxonomy.py   regroups the index into tribes and layers
scripts/check_summaries.py  verifies every summary is exactly 40 words
scripts/fetch_visibility.py  tags entries whose repository is private
scripts/fetch_pages.py       attaches live GitHub Pages URLs to entries
scripts/fetch_details.py     attaches the lab's own project write-ups
scripts/fetch_podcast.py     fetches both playlists and assigns the research arcs
scripts/fetch_notebook.py    fetches the concept notes, essays and blog
scripts/prune.py             prunes entries that fail the central criterion
data/removed.json            the pruned entries, with reasons, so nothing is lost
```

## Workflow

```bash
python3 scripts/apply_summaries.py   # refresh summaries in entries.json
python3 scripts/apply_taxonomy.py    # regroup into tribes and layers
python3 scripts/check_summaries.py   # 71/71 summaries at exactly 40 words
python3 scripts/fetch_visibility.py  # re-tag private repositories
python3 scripts/fetch_pages.py       # attach live GitHub Pages URLs
python3 scripts/fetch_details.py     # attach the lab's project write-ups
python3 scripts/fetch_podcast.py     # refresh episodes and research arcs
python3 scripts/fetch_notebook.py    # refresh concepts, essays and blog
python3 scripts/build.py             # regenerate the three pages
```

## Groups

**Research tribes** — where the idea is explored:

| Tribe | What it holds |
|---|---|
| Core Theory | the phenomenon itself: the Arithmetic Manifold, the Architecture of Axioms, behavioural quotients, the phantom clock |
| Representation / Memory | the encoding chosen for it: FUTCache, PDI, novelty geometry, model2vec, obs-ai |
| Optimization / Search | the behaviour it produces: BAHA, NitroSAT, Navokoj, Casimir SAT, NoetherLeap, the spectral–multiplicative framework |
| Agents / Authority | who may ask and who may act: authorization lattice, agent guardrail, factor agent, reify |
| Learning / Physics | representation meets physics: eigen-attention, multiplicative PINNs, Fock-space computation |

**Publication and access layers** — orthogonal to the tribes:

| Group | What it holds |
|---|---|
| Foundations | the lab's long-form documents on the docs site |
| Citable records | Zenodo DOIs, the version of record for each artifact |
| Released artifacts | published versions, grouped by project |
| Broadcast | the two podcasts and the writing index, each with its own page |
| Elsewhere | the notebook, the shipping API, the evidence ledger |

## Layers

Every project in the index moves through the same five layers:

**core** the phenomenon → **mirror** the representation chosen for it →
**shadow** the behaviour that representation produces → **record** what was frozen and given
a DOI → **story** how the idea becomes reconstructible in someone else's head.

BAHA is the worked example: the divergence of a partition function's log-derivative (core),
the multi-sheeted analytic surface (mirror), the stall that ordinary annealing suffers and
the branch-aware one does not (shadow), DOI 10.5281/zenodo.18373732 (record), and episode 21
plus the browser build (story).

## Start here

Arithmetic Manifold → Architecture of Axioms → Behavioral Quotients → Phantom Clock → FUTCache.
What structure exists, what representations preserve it, when equivalence is legitimate, what
goes wrong when distinctions collapse, and how to compress safely.
| Elsewhere | the notebook, the shipping API, the evidence ledger |

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
3. Fix the count, re-run `scripts/apply_taxonomy.py`, then `scripts/build.py`.
4. Commit `data/entries.json` and the three generated pages.

To move an entry to another tribe, edit its membership in `data/taxonomy.json` and re-run
`scripts/apply_taxonomy.py`; the entry keeps its metadata and summary, only its group changes.

## Design

Minimal and paper-like: no web fonts, no frameworks, no trackers, no build-time
dependencies beyond the Python standard library. Two themes driven by CSS custom
properties, with `prefers-color-scheme` as the default and a manual override that
persists. Type is a serif for prose and headings, a mono for metadata.

## Licence

MIT — see `LICENSE`.
