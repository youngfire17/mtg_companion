# MTG Companion — Notes

Running scratchpad. Decisions, ideas, things to revisit.

## Decisions made (2026-05-10)

- **Interface:** Claude Code only. No web app, no Discord bot, no desktop app. Reconsider only if "wish I had this on my phone" becomes frequent.
- **Search:** grep over markdown. No vector DB. Reconsider if corpus exceeds ~5,000 files or grep starts feeling slow.
- **Card data:** local Scryfall cache (`library/cards/oracle.ndjson`, ~30 MB, ~34k cards), refreshed weekly via `python library/cards/refresh.py`. Bypass to live Firecrawl-Scryfall only for cards not in cache (newly printed) or suspected errata. **Never** training data. (Original plan was per-card live API hits — wasteful, and the Scryfall API 403s WebFetch anyway because of the User-Agent header.)
- **Meta data:** always live, never training data. Non-negotiable. mtgtop8 via WebFetch; MTGGoldfish must go through Firecrawl (403s WebFetch).
- **Memory:** existing auto-memory at `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\`. No second project-local memory folder.
- **Real-time advice:** off-limits (MTGO ToS).
- **Books:** Justin owns digital copies; kept local; never republished.
- **Articles:** free-tier only for now.

## Open ideas (later phases)

- Once 5+ match reviews exist, audit memory for leak patterns and write a "personal leaks" entry the mentor reads at the start of each review.
- For Limited, eventually script a 17lands fetch helper so the mentor pulls set data with one tool call instead of multiple.
- For Pauper, consider scraping the weekly Pauper Challenge top 32 into `library/primers/pauper-meta.md` on a schedule.
- If Justin starts paying for CFB Pro / SCG Premium / MTGGoldfish Premium, revisit article scraping with credentialed access (respect ToS).

## Things to revisit

- Whether Comprehensive Rules should be split per major rule section (currently one file). Revisit if grep gets noisy or the file gets unwieldy in context.
- Cache refresh cadence — weekly is the default, but if Justin starts feeling stale after big-event banlist changes mid-week, automate a refresh hook (e.g., on session start, check `oracle.meta.json` age and warn if >7 days).

## Phase 1 acceptance test (2026-05-10)

Ran the four probes from the implementation plan in a fresh session. Result: **3 of 4 passed strongly; the 4th passed substantively but exposed an architectural problem we fixed immediately (see Phase 1.5 below).**

- **Bolt vs Galvanic Blast probe:** PASS. Skill auto-loaded, peer-level tone, concrete recommendation (Galvanic Blast main, Bolt sideboard hedge against artifact hate), good reasoning chain. Caveat: Scryfall API 403'd, mentor scrambled to Firecrawl-scrape card pages — answered correctly but the path was ugly.
- **Humility / layer system probe:** PASS. Greped the comp rules, cited rule 613.1f (layer 6, ability removal) and 613.4b (layer 7b, P/T set), explained the split-layer interaction including the Tarmogoyf-CDA gotcha. Same Scryfall 403 issue for the Humility lookup.
- **Chapin who's-the-beatdown probe:** PASS. Greped *Next Level Magic*, surfaced the inevitability framing, the Tezzeret/Long.dec example, the symmetric-matchup tiebreakers in Chapin's priority order, and the practical "who loses if this goes to turn 15" heuristic. Strong synthesis.
- **Live Pauper meta probe:** SUBSTANTIVELY PASSED. Mentor was transparent that MTGGoldfish 403'd, fell back to mtgtop8, surfaced a real 2-week share table plus the May 8 / May 9 Challenge winners, and gave a real read (Affinity / Madness Burn / Combo as the three threats to plan for). But losing MTGGoldfish silently to a 403 is unacceptable when Firecrawl is right there.

## Phase 1.5 — local card cache + Firecrawl-routed meta (2026-05-10)

Justin's instinct after the acceptance test: per-card live Scryfall lookups are insane; cache locally and only check live for amendments. Correct call. Implemented:

- Added `library/cards/oracle.ndjson` (gitignored, ~30 MB, 34,153 cards) — slimmed from Scryfall's `oracle_cards` bulk dump. Each line is one card as JSON: name, mana_cost, cmc, type_line, oracle_text, P/T, colors, keywords, set, rarity, legalities. MDFCs/split cards include a `card_faces_text` field for grep coverage.
- Added `library/cards/refresh.py` — re-downloads and rebuilds the cache. Updates `oracle.meta.json` with timestamp and source URL. Run weekly or before sessions where new sets / errata might matter.
- Added `library/cards/README.md` — usage and refresh instructions.
- Updated `SKILL.md` and `CLAUDE.md` disciplines: card lookups go through the local cache by default; live Firecrawl-Scryfall only as fallback for cache misses.
- Updated `SKILL.md` meta sources: MTGGoldfish (and any 403-blocked source) routes through Firecrawl, not WebFetch.
