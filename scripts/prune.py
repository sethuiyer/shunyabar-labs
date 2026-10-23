#!/usr/bin/env python3
"""Audit the index against the central idea and prune what does not fit.

Criterion
---------
An entry stays in the index only if the work does one of these:

  A. constructs or analyses a representation / abstraction / quotient / encoding
     of a system, and says what information it keeps or throws away;
  B. identifies distinctions that must be preserved for a decision, guarantee
     or evaluation to remain valid.

Everything else is infrastructure, tooling, publishing, or unrelated physics
and number theory. Removed entries are archived in data/removed.json so they
can be reinstated with one command.

The script is idempotent and self-healing:

  * a title that is already archived is not an error;
  * an archived title that is back in the index counts as reinstated and is
    dropped from the archive;
  * the criterion text and the tier glossary in data/removed.json are always
    preserved.

Usage:  python3 scripts/prune.py [--dry-run]
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

CRITERION = ("An entry stays only if it (A) constructs or analyses a representation / "
             "abstraction / quotient / encoding and states what it keeps or discards, "
             "or (B) identifies distinctions that must be preserved for a decision, "
             "guarantee or evaluation to remain valid.")

TIERS = {
    "A": "infrastructure, tooling, publishing, meta",
    "B": "near misses: physics, number theory and search work with no stated criterion",
}

# title -> (tier, reason)
REMOVE = {
    # tier A — infrastructure, tooling, publishing, meta
    "tensor-to-tenant": ("A", "Curriculum and course site. Publishing and teaching, not representation."),
    "miwa-discord-bot": ("A", "Application code. No abstraction or decision-preservation content."),
    "shunyabar.lua": ("A", "Utility library. Bounded memory, but nothing about preserving distinctions."),
    "shunyabar-labs": ("A", "The earlier collection repository, now the archive. Self-referential."),
    "fooshunyabar": ("A", "Loose scratch files. Working notes, not a claim."),
    "playlist-ed": ("A", "A YouTube player. Product, not research."),
    "sethuiyer.github.com": ("A", "Personal website. Infrastructure."),
    "navbar": ("A", "Small Lua helper. Utility."),
    "Research Contributions": ("A", "Archive index page. Meta."),
    "TSP on the Self-Stabilizing Optimizer: A Complete Implementation Plan": ("A", "Implementation plan for a solver. Procedure, not principle."),
    "Convergence Frontiers: Literature Survey of Interdisciplinary Research Paradigms": ("A", "Literature survey. Positions the work against prior art, states no criterion."),

    # tier B — near misses: physics, number theory and search work that never
    # asks which distinctions must be preserved
    "axiom-synergy": ("B", "Measures synergy between rules. About rule interaction, not about representation."),
    "thermodynamic-number-line": ("B", "Primes as thermodynamic fuel. Physics metaphor, no decision criterion."),
    "floer-hardness-certificates": ("B", "Hardness certificates via persistent homology. Certifies difficulty, not safe compression."),
    "Observations on Exponential Functions in Complex Systems": ("B", "Pattern notes on exponential growth. No representation claim."),
    "Majorana Topological Superconductors: From Quantum Particles to the Riemann Hypothesis": ("B", "Quantum physics to the Riemann hypothesis. No abstraction criterion."),
    "The Quantum Rhythm Hypothesis: Mathematics as Condensed Matter Physics": ("B", "Primes as quasiparticles. Condensed matter framing, no abstraction criterion."),
}


def load_archive(path: pathlib.Path) -> dict:
    if not path.exists():
        return {"criterion": CRITERION, "removed": [], "tiers": dict(TIERS)}
    archive = json.loads(path.read_text())
    archive.setdefault("removed", [])
    archive["criterion"] = CRITERION
    archive["tiers"] = dict(TIERS)
    return archive


def main() -> int:
    dry = "--dry-run" in sys.argv
    entries_path = ROOT / "data" / "entries.json"
    archive_path = ROOT / "data" / "removed.json"

    data = json.loads(entries_path.read_text())
    archive = load_archive(archive_path)
    indexed = {entry["title"] for group in data["groups"] for entry in group["entries"]}

    # Reinstated: archived entries that are back in the index.
    reinstated = [r["title"] for r in archive["removed"] if r["title"] in indexed]
    archive["removed"] = [r for r in archive["removed"] if r["title"] not in indexed]
    archived = {r["title"] for r in archive["removed"]}

    removed = []
    kept = []
    for group in data["groups"]:
        keep = []
        for entry in group["entries"]:
            title = entry["title"]
            if title in REMOVE:
                tier, reason = REMOVE[title]
                removed.append({"group": group["id"], "title": title, "url": entry["url"],
                                "tier": tier, "reason": reason, "summary": entry["summary"],
                                "meta": entry.get("meta", []), "date": entry.get("date", "")})
            else:
                keep.append(entry)
                kept.append(title)
        group["entries"] = keep

    unknown = set(REMOVE) - archived - {r["title"] for r in removed}
    if unknown:
        print("no such entry (not in the index, not archived):", sorted(unknown))
        return 1

    archive["removed"].extend(removed)
    archive["removed"].sort(key=lambda r: r["title"].lower())

    for group in list(data["groups"]):
        if not group["entries"]:
            data["groups"].remove(group)

    print(f"keeping {len(kept)} entries, removing {len(removed)}")
    for r in removed:
        print(f"  [{r['tier']}] {r['title']} — {r['reason']}")
    for title in reinstated:
        print(f"  reinstated {title} — dropped from the archive")
    print(f"archive holds {len(archive['removed'])} removed entries")

    if dry:
        print("(dry run; nothing written)")
        return 0

    entries_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    archive_path.write_text(json.dumps(archive, indent=2, ensure_ascii=False) + "\n")
    print("wrote data/entries.json and data/removed.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
