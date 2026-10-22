#!/usr/bin/env python3
"""Rebuild the podcast group in data/entries.json from episode metadata + summaries.

Episode metadata lives in data/episodes.json (fetched with yt-dlp from the
public playlist). Curated 40-word summaries live in data/podcast_summaries.txt
as "@@ <video id>" blocks.

Usage:  python3 scripts/apply_podcast.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = 40

PLAYLIST = "https://www.youtube.com/playlist?list=PLUPyripldgZb2ZKSJOQ6p1DO3oCk9yT6G"
CHANNEL = "https://www.youtube.com/@SethuIyer95"

OVERVIEW_TITLE = "Space Time Cafe"
OVERVIEW_SUMMARY = (
    "A long-form video essay series in which physics, number theory, geometry and machine "
    "learning are argued through together. Fifty-one episodes published between February 2025 "
    "and August 2026 range over primes, infinity, chaos, operators, fairness and the limits of "
    "computation itself."
)


def human_duration(seconds: int) -> str:
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes == 0:
        return f"{secs}s"
    return f"{minutes}m {secs:02d}s"


def human_views(views: int) -> str:
    if views >= 1000:
        return f"{views / 1000:.1f}k views"
    return f"{views} views"


def iso_date(stamp: str) -> str:
    return f"{stamp[0:4]}-{stamp[4:6]}-{stamp[6:8]}"


def load_summaries() -> dict:
    raw = (ROOT / "data" / "podcast_summaries.txt").read_text()
    out = {}
    for block in re.split(r"^@@ ", raw, flags=re.M)[1:]:
        key, _, body = block.partition("\n")
        out[key.strip()] = " ".join(body.split())
    return out


def build_group(summaries: dict) -> dict:
    episodes = json.loads((ROOT / "data" / "episodes.json").read_text())
    entries = [{
        "title": OVERVIEW_TITLE,
        "url": PLAYLIST,
        "date": "2025-02-22",
        "meta": ["Playlist", f"{len(episodes)} videos"],
        "summary": OVERVIEW_SUMMARY,
        "site": CHANNEL,
    }]
    for episode in episodes:
        video_id = episode["id"]
        summary = summaries.get(video_id)
        if summary is None:
            raise SystemExit(f"no summary for video {video_id} ({episode['title']})")
        if len(summary.split()) != TARGET:
            raise SystemExit(f"{episode['title']}: {len(summary.split())} words (need {TARGET})")
        entries.append({
            "title": episode["title"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "date": iso_date(episode["date"]),
            "meta": ["Video", human_duration(episode["duration"]), human_views(episode["views"])],
            "summary": summary,
            "video": video_id,
        })
    return {
        "id": "podcast",
        "title": "Podcast — Space Time Cafe",
        "note": "{n} entries — the lab's argument in spoken form: one long-form video essay per topic, plus the playlist overview.",
        "entries": entries,
    }


def main() -> int:
    summaries = load_summaries()
    group = build_group(summaries)

    path = ROOT / "data" / "entries.json"
    data = json.loads(path.read_text())
    groups = [g for g in data["groups"] if g["id"] != "podcast"]
    index = next((i for i, g in enumerate(groups) if g["id"] == "elsewhere"), len(groups))
    groups.insert(index, group)
    data["groups"] = groups
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"podcast group rebuilt — {len(group['entries'])} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
