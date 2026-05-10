"""
Refresh the local Scryfall card cache.

Downloads Scryfall's `oracle_cards` bulk file, slims it to the fields the
mentor actually uses, and writes `oracle.ndjson` (one card per line) plus a
sidecar `oracle.meta.json` with the refresh timestamp and source URL.

Usage:
    python library/cards/refresh.py

Run weekly, or when a new set drops, or before any session where you suspect
recent errata might matter. The mentor checks `oracle.meta.json` to know how
stale the cache is.
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.request
from datetime import datetime, timezone

USER_AGENT = "MTG-Companion/1.0 (personal study tool; youngfire17@gmail.com)"
BULK_INDEX_URL = "https://api.scryfall.com/bulk-data"

KEEP_FIELDS = {
    "name", "mana_cost", "cmc", "type_line", "oracle_text",
    "power", "toughness", "loyalty", "defense",
    "colors", "color_identity", "keywords",
    "layout", "set", "set_name", "rarity",
    "edhrec_rank", "penny_rank",
    "legalities",
}

SKIP_LAYOUTS = {"token", "double_faced_token", "emblem", "art_series"}

CARDS_DIR = pathlib.Path(__file__).parent
OUTPUT = CARDS_DIR / "oracle.ndjson"
META = CARDS_DIR / "oracle.meta.json"


def fetch_json(url: str) -> dict | list:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def slim_card(card: dict) -> dict:
    slim = {k: card[k] for k in KEEP_FIELDS if k in card}
    if "card_faces" in card:
        faces = []
        for face in card["card_faces"]:
            faces.append(face.get("name", ""))
            for k in ("mana_cost", "type_line", "oracle_text"):
                if face.get(k):
                    faces.append(face[k])
        slim["card_faces_text"] = " // ".join(t for t in faces if t)
    return slim


def main() -> int:
    print(f"Fetching bulk data index from {BULK_INDEX_URL}")
    index = fetch_json(BULK_INDEX_URL)
    oracle = next(d for d in index["data"] if d["type"] == "oracle_cards")
    print(f"Oracle cards bulk: {oracle['download_uri']} ({oracle['size']:,} bytes)")

    print("Downloading bulk file...")
    cards = fetch_json(oracle["download_uri"])
    print(f"Downloaded {len(cards):,} card entries")

    written = 0
    with OUTPUT.open("w", encoding="utf-8") as f:
        for card in cards:
            if card.get("layout") in SKIP_LAYOUTS:
                continue
            f.write(json.dumps(slim_card(card), separators=(",", ":")) + "\n")
            written += 1

    META.write_text(json.dumps({
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "source_url": oracle["download_uri"],
        "scryfall_updated_at": oracle.get("updated_at"),
        "cards_in_index": len(cards),
        "cards_written": written,
        "output_bytes": OUTPUT.stat().st_size,
    }, indent=2) + "\n", encoding="utf-8")

    size_mb = OUTPUT.stat().st_size / 1024 / 1024
    print(f"Wrote {written:,} cards to {OUTPUT.name} ({size_mb:.1f} MB)")
    print(f"Wrote refresh metadata to {META.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
