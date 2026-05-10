# MTG Companion — Project Guide

A personal Magic: The Gathering mentor that lives inside Claude Code. No app, no server. Open Claude Code in this folder and start talking.

## What it does

Five conversation modes (no commands — just natural language):

1. **Prep & study** — *"I'm running mono-U Faeries in tonight's Pauper league, what should I be ready for?"*
2. **Post-game review** — *"Review my last match."* (Reads the most recent MTGO log.)
3. **Deckbuilding partner** — *"Here's my decklist, what's weak?"*
4. **Draft coach** — Paste a pack screenshot or list; the mentor picks with reasoning.
5. **Open chat** — *"Why did Reid keep this hand on camera last week?"*

## How to use it

- Start Claude Code in `C:\Desktop\CLAUDE Projects\MTG_Companion`.
- Talk normally. The `mtg-mentor` skill auto-triggers on Magic conversations.
- Add new decks to `decks/` (one markdown file per deck).
- Match reviews are saved to `reviews/` automatically when you say "review my last match."
- Sideboard guides live in `notes/sideboard-guides/`. Draft notes in `notes/draft-notes/`.

## Phase status

- **Phase 1 (current):** foundation — folder structure, skill, rules, both Chapin books, user profile.
- **Phase 2:** your decks added, first real match review tested end-to-end.
- **Phase 3:** curated free pro articles ingested into the library.
- **Phase 4:** documented live data fetch patterns (meta, 17lands).

## Setup checklist (Phase 1)

- [x] Folder structure scaffolded
- [x] `CLAUDE.md` with tone + disciplines
- [x] `PROJECT_GUIDE.md` (this file)
- [x] `mtg-mentor` skill written
- [x] Comprehensive Rules ingested
- [x] *Next Level Magic* ingested
- [x] *Next Level Deckbuilding* ingested
- [x] User profile saved to auto-memory
- [x] Acceptance: real strategy conversation works, cites Chapin and rules, fetches Scryfall for cards

## Source files (kept outside the repo)

- *Next Level Magic*: `C:\Desktop\MTG STUFF\MAGIC the GATHERING\Next Level Magic - Patrick Chapin.pdf`
- *Next Level Deckbuilding*: `C:\Desktop\MTG STUFF\MAGIC the GATHERING\Next Level Deck Building - Patrick Chapin.pdf`
- Comprehensive Rules: downloaded fresh from `https://magic.wizards.com/en/rules` each ingestion.
