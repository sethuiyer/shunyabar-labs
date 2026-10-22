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

Usage:  python3 scripts/prune.py [--dry-run]
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

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
    "The Dynamic Prime Cantor Set: A Fractal Woven from the Primes": ("B", "Fractal construction from prime gaps. Structure, not decision-relevant distinctions."),
    "Observations on Exponential Functions in Complex Systems": ("B", "Pattern notes on exponential growth. No representation claim."),
    "Majorana Topological Superconductors: From Quantum Particles to the Riemann Hypothesis": ("B", "Quantum physics to the Riemann hypothesis. No abstraction criterion."),
    "The Prime Walk: Spontaneous Symmetry Breaking from Number Theory to the Riemann Hypothesis": ("B", "Random walk on prime powers. Physics bridge, no decision criterion."),
    "The Quantum Rhythm Hypothesis: Mathematics as Condensed Matter Physics": ("B", "Primes as quasiparticles. Condensed matter framing, no abstraction criterion."),
}


def main() -> int:
    dry = "--dry-run" in sys.argv
    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())

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

    missing = set(REMOVE) - {r["title"] for r in removed}
    if missing:
        print("no such entry:", missing)
        return 1

    for group in data["groups"]:
        if not group["entries"]:
            data["groups"].remove(group)

    print(f"keeping {len(kept)} entries, removing {len(removed)}")
    for r in removed:
        print(f"  [{r['tier']}] {r['title']} — {r['reason']}")

    if dry:
        print("(dry run; nothing written)")
        return 0

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "data" / "removed.json").write_text(
        json.dumps({"criterion": REMOVE and "", "removed": removed}, indent=2, ensure_ascii=False) + "\n")
    print("wrote data/entries.json and data/removed.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
