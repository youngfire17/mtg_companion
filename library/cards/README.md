# library/cards — local Scryfall card cache

This directory holds a local cache of every Magic card's Oracle text, mana cost, type, P/T, and legalities. The mentor greps this file instead of hitting the Scryfall API on every card lookup.

## Files

- `oracle.ndjson` — one card per line, JSON-encoded. Slimmed from Scryfall's `oracle_cards` bulk file. **Not committed to git** — regenerate with the script below. ~30 MB, ~34,000 cards.
- `oracle.meta.json` — refresh timestamp, source URL, counts. Committed.
- `refresh.py` — downloads the latest bulk data and rebuilds `oracle.ndjson`.

## How to refresh

```bash
python library/cards/refresh.py
```

Run weekly, or when a new set drops, or before a session where recent errata or new cards matter. The script overwrites `oracle.ndjson` and updates `oracle.meta.json`.

## How the mentor uses it

```bash
# Single card lookup by exact name
grep '"name":"Lightning Bolt"' library/cards/oracle.ndjson

# Pauper-legal red instants (rough filter — combine with type_line)
grep '"pauper":"legal"' library/cards/oracle.ndjson | grep '"type_line":"Instant"' | grep '{R}'

# Search by Oracle text substring
grep '"oracle_text":"[^"]*lifelink' library/cards/oracle.ndjson | head -10
```

Each line is a self-contained JSON object — pipe to `python -c 'import sys,json; print(json.loads(sys.stdin.read())["oracle_text"])'` to extract individual fields.

## When to bypass the cache

The mentor should check Scryfall live (via Firecrawl, since the API rejects the WebFetch User-Agent) only when:

1. The card isn't in the cache (newly printed and the cache is older than the set release).
2. Errata is suspected after the cache was last refreshed.
3. Rulings or specific printings are needed (those aren't in the slim cache).

For the common case — "what does this card do, what's it cost, is it legal in Pauper" — the cache is authoritative.
