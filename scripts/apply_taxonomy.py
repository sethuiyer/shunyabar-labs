#!/usr/bin/env python3
"""Rebuild data/entries.json around the research taxonomy.

The taxonomy lives in data/taxonomy.json: five research tribes, the five
layers (core, mirror, shadow, record, story), the Start Here path, and the
entries that are new to the index.

Existing entries keep their metadata and summaries; this script only decides
which group each one belongs in, and adds the new entries from their stubs.

Usage:  python3 scripts/apply_taxonomy.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = 40

LAYER_GROUPS = [
    ("foundations", "Foundations",
     "The long-form documents: what the idea is, where it stops, and what it rests on."),
    ("citable", "Citable records",
     "Every artifact with a permanent identifier — the version of record, not a pointer to one."),
    ("releases", "Released artifacts",
     "Published versions, grouped by project: what froze, and when."),
    ("broadcast", "Broadcast",
     "How the idea becomes reconstructible in someone else's head."),
    ("elsewhere", "Elsewhere",
     "The lab's other surfaces: notebook, shipping API, evidence ledger, community."),
]


def curated_summaries() -> dict:
    raw = (ROOT / "data" / "summaries.txt").read_text()
    out = {}
    for block in raw.split("@@ ")[1:]:
        title, _, body = block.partition("\n")
        out[title.strip()] = " ".join(body.split())
    return out


def main() -> int:
    taxonomy = json.loads((ROOT / "data" / "taxonomy.json").read_text())
    summaries = curated_summaries()

    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())

    existing = {}
    for group in data["groups"]:
        if group["id"] == "podcast":
            continue
        for entry in group["entries"]:
            existing[entry["title"]] = entry

    groups = []
    for tribe in taxonomy["tribes"]:
        entries = []
        for title in tribe["members"]:
            if title in existing:
                entries.append(existing[title])
                continue
            stub = next((n for n in taxonomy["new_entries"] if n["title"] == title), None)
            if stub is None:
                print(f"  !! no entry or stub for {title}")
                return 1
            summary = summaries.get(title)
            if summary is None:
                print(f"  !! no summary for {title}")
                return 1
            if len(summary.split()) != TARGET:
                print(f"  !! {title}: {len(summary.split())} words (need {TARGET})")
                return 1
            entry = {k: v for k, v in stub.items() if k not in ("group", "promoted")}
            entry["summary"] = summary
            entries.append(entry)
        groups.append({"id": tribe["id"], "title": tribe["title"],
                       "note": tribe["note"], "entries": entries})

    by_group = {}
    for group in data["groups"]:
        if group["id"] == "podcast":
            continue
        by_group[group["id"]] = [e["title"] for e in group["entries"]]

    relocate = taxonomy.get("relocate", {})
    used = set()
    for tribe in taxonomy["tribes"]:
        used.update(tribe["members"])

    for group_id, group_title, note in LAYER_GROUPS:
        if group_id == "citable":
            records = json.loads((ROOT / "data" / "citable_records.json").read_text())
            members = [r["title"] for r in records]
            members += [n["title"] for n in taxonomy["new_entries"] if n["group"] == "citable"]
        elif group_id == "broadcast":
            members = [n["title"] for n in taxonomy["new_entries"] if n["group"] == "broadcast"]
        else:
            members = [t for t in by_group.get(group_id, []) if t not in used]
            for reloc_title, target in relocate.items():
                if target == group_id and reloc_title not in members:
                    members.append(reloc_title)
        entries = []
        records = {r["title"]: r for r in
                   json.loads((ROOT / "data" / "citable_records.json").read_text())}
        for member_title in members:
            if member_title in records and member_title not in existing:
                entry = dict(records[member_title])
                entry["summary"] = summaries.get(member_title, entry.get("summary", ""))
                entries.append(entry)
                continue
            if member_title in existing:
                entries.append(existing[member_title])
                continue
            stub = next((n for n in taxonomy["new_entries"] if n["title"] == member_title), None)
            if stub is None:
                print(f"  !! no entry or stub for {member_title}")
                return 1
            summary = summaries.get(member_title)
            if summary is None or len(summary.split()) != TARGET:
                print(f"  !! bad summary for {member_title}")
                return 1
            entry = {k: v for k, v in stub.items() if k not in ("group", "promoted")}
            entry["summary"] = summary
            entries.append(entry)
        groups.append({"id": group_id, "title": group_title, "note": note, "entries": entries})

    placed = {entry["title"] for group in groups for entry in group["entries"]}
    dropped = sorted(set(existing) - placed)
    if dropped:
        print(f"  !! {len(dropped)} existing entries were not placed in any group: {dropped}")
        return 1
    unused = sorted({n["title"] for n in taxonomy["new_entries"]} - placed)
    if unused:
        print(f"  !! {len(unused)} taxonomy stubs were not placed in any group: {unused}")
        return 1

    data["groups"] = groups
    data["start_here"] = taxonomy["start_here"]
    data["layers"] = taxonomy["layers"]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    total = sum(len(g["entries"]) for g in groups)
    print(f"wrote entries.json — {total} entries in {len(groups)} groups")
    return 0


if __name__ == "__main__":
    sys.exit(main())
