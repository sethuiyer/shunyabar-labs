#!/usr/bin/env python3
"""Fetch both podcast playlists and cluster the episodes into research arcs.

Two playlists:
  Space Time Cafe   — the long-form show (51 episodes)
  Shunyabar Labs    — the lab's own short-form channel (15 episodes, 10 public)

Metadata comes from yt-dlp; the arc assignment is expressed here so the
broadcast page always shows the same five arcs.

Usage:  python3 scripts/fetch_podcast.py
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

STC_PLAYLIST = "https://www.youtube.com/playlist?list=PLUPyripldgZb2ZKSJOQ6p1DO3oCk9yT6G"
LABS_PLAYLIST = "https://www.youtube.com/playlist?list=PLUPyripldgZZMq2qkUzxhj_N9aVh6w2XV"

STC_ARCS = [
    {
        "id": "arithmetic",
        "title": "Arithmetic & primes",
        "note": "The number-theoretic spine: primes as structure rather than as enumeration — "
                "fibonacci, chaos, the p-adic vortex, prime fractals, the arithmetic resistor.",
        "numbers": {3, 5, 6, 7, 8, 9, 10, 16, 17, 21, 40, 41},
        "extra": [],
    },
    {
        "id": "invariants",
        "title": "Invariants & operators",
        "note": "What stays fixed when everything else moves: invariants, concurrency invariants, "
                "the terminal algebra of horizons, symmetry confinement, self-adjoint operators.",
        "numbers": {11, 12, 13, 20, 23, 24},
        "extra": ["Encrypting with Chaos"],
    },
    {
        "id": "geometry",
        "title": "Geometry & complexity",
        "note": "Shape as the cause: hyperbolic space, gerbes, bent problem spaces, "
                "chaos and order, Ramanujan graphs, fair division, the shape of fairness.",
        "numbers": {14, 15, 18, 19, 27, 28, 29, 30, 32, 37, 39},
        "extra": ["Episode 27 Trailer"],
    },
    {
        "id": "information",
        "title": "Information & intelligence",
        "note": "Representation and mind: substrate intelligence, purpose as thermodynamics, "
                "the physics of thought, rhythms of encryption, reality, the speed limit of intelligence.",
        "numbers": {25, 26, 31, 33, 34, 35, 36, 38, 42},
        "extra": ["Are we in a Simulation?"],
    },
    {
        "id": "physics",
        "title": "Physics & foundations",
        "note": "Where the argument starts: Majorana fermions, infinity, the physics of storytelling, "
                "divergent computation, and the physics/ML bridge.",
        "numbers": {1, 2, 4, 22},
        "extra": ["The Physics of Divergent Computation",
                  "Gravity Is Just Biased Attention",
                  "Ep  20 Trailer",
                  "Podcast Introduction"],
    },
]

LABS_ARCS = [
    {
        "id": "labs-primes",
        "title": "Primes & arithmetic",
        "note": "Arithmetic rigidity, primes as curvature defects, prime fractals, prime-gated fluids.",
        "titles": ["Extreme Computation", "Primes as Curvature Defects", "A Fractal Woven from Primes",
                   "Prime Gated Navier Stokes"],
    },
    {
        "id": "labs-search",
        "title": "Search & hardness",
        "note": "Statistical mechanics for NP-hard search, and a branch-aware optimiser that feels unfair.",
        "titles": ["Escaping NP-Hard Search", "The Algorithm That Feels Like Cheating"],
    },
    {
        "id": "labs-solvers",
        "title": "Solvers in production",
        "note": "The engines themselves: NitroSAT, Navokoj, and SAT solved by vacuum dynamics.",
        "titles": ["Introducing NitroSAT", "Navokoj:", "Solving SAT with Quantum Vacuum Dynamics"],
    },
    {
        "id": "labs-foundations",
        "title": "Foundations",
        "note": "The four-step engine of complexity, and the claim that truth is condensed history.",
        "titles": ["Truth as Thermal History"],
    },
]


def yt_dlp(url: str) -> list:
    out = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--dump-json", "--ignore-errors", url],
        capture_output=True, text=True).stdout
    return [json.loads(line) for line in out.splitlines() if line.strip().startswith("{")]


def yt_dlp_full(url: str) -> dict:
    out = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-warnings", "--skip-download", "--ignore-errors", url],
        capture_output=True, text=True).stdout
    videos = {}
    for line in out.splitlines():
        if not line.strip().startswith("{"):
            continue
        data = json.loads(line)
        videos[data["id"]] = {
            "id": data["id"],
            "title": data["title"],
            "date": data.get("upload_date") or "",
            "duration": data.get("duration") or 0,
            "views": data.get("view_count") or 0,
            "likes": data.get("like_count") or 0,
            "desc": (data.get("description") or "")[:1200],
        }
    return videos


def episode_number(title: str):
    import re
    match = re.match(r"\s*Ep(?:isode)?\s*(\d+)", title)
    return int(match.group(1)) if match else None


def main() -> int:
    stc_flat = yt_dlp(STC_PLAYLIST)
    stc_full = yt_dlp_full(STC_PLAYLIST)
    episodes = []
    for item in stc_flat:
        video_id = item["id"]
        full = stc_full.get(video_id, {})
        episodes.append({
            "id": video_id,
            "title": item.get("title") or full.get("title") or "",
            "date": full.get("date", ""),
            "duration": full.get("duration", item.get("duration") or 0),
            "views": full.get("views", item.get("view_count") or 0),
            "likes": full.get("likes", 0),
            "desc": full.get("desc", ""),
        })

    labs_flat = yt_dlp(LABS_PLAYLIST)
    labs_full = yt_dlp_full(LABS_PLAYLIST)
    labs = []
    for item in labs_flat:
        video_id = item["id"]
        full = labs_full.get(video_id, {})
        labs.append({
            "id": video_id,
            "title": full.get("title") or "",
            "date": full.get("date", ""),
            "duration": full.get("duration", 0),
            "views": full.get("views", 0),
            "likes": full.get("likes", 0),
            "desc": full.get("desc", ""),
            "available": bool(full),
            "private": not bool(full),
        })

    arcs = []
    for arc in STC_ARCS:
        members = []
        for episode in episodes:
            number = episode_number(episode["title"])
            if "Trailer" in episode["title"]:
                number = None
            if (number is not None and number in arc["numbers"]) or \
               any(episode["title"].startswith(prefix) for prefix in arc["extra"]):
                members.append(episode["id"])
        arcs.append({"id": arc["id"], "title": arc["title"], "note": arc["note"], "ids": members})

    covered = [vid for arc in arcs for vid in arc["ids"]]
    missing = [e["id"] for e in episodes if e["id"] not in covered]
    duplicated = {vid for vid in covered if covered.count(vid) > 1}
    if missing or duplicated:
        print(f"  !! unassigned: {[e['title'] for e in episodes if e['id'] in missing]}")
        print(f"  !! duplicated: {duplicated}")
        return 1

    labs_arcs = []
    for arc in LABS_ARCS:
        members = [e["id"] for e in labs if any(e["title"].startswith(t) for t in arc["titles"])]
        labs_arcs.append({"id": arc["id"], "title": arc["title"], "note": arc["note"], "ids": members})
    public_labs = [e for e in labs if e["title"]]
    labs_missing = [e["title"] for e in public_labs if e["id"] not in [v for a in labs_arcs for v in a["ids"]]]
    if labs_missing:
        print(f"  !! labs unassigned: {labs_missing}")
        return 1

    (ROOT / "data" / "episodes.json").write_text(json.dumps(episodes, indent=1, ensure_ascii=False) + "\n")
    (ROOT / "data" / "labs_episodes.json").write_text(json.dumps(labs, indent=1, ensure_ascii=False) + "\n")
    (ROOT / "data" / "arcs.json").write_text(json.dumps(
        {"stc": arcs, "labs": labs_arcs}, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote episodes.json — {len(episodes)} episodes in {len(arcs)} arcs")
    print(f"wrote labs_episodes.json — {len(labs)} episodes ({sum(1 for e in labs if e['available'])} public)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
