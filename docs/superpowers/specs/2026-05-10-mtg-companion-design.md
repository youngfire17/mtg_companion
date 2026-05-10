# MTG Companion — Design Spec

**Date:** 2026-05-10
**Owner:** Justin
**Status:** Approved (brainstorming complete)

---

## Purpose

A peer-level competitive Magic: The Gathering mentor that lives inside Claude Code. Helps with strategy, deckbuilding, draft coaching, post-game review, and meta prep for the formats Justin actually plays on MTGO: Pauper, Standard, Limited.

This is a personal tool, not a product. Optimized for one user's workflow.

## Non-Goals

- Not a web app, not a mobile app, not a Discord bot. Claude Code is the interface.
- No real-time in-game advice during MTGO matches (likely violates MTGO ToS — outside assistance during play). Between-games, post-game, and prep-time only.
- No vector DB or embeddings infrastructure. The corpus is small enough that grep over markdown is faster, simpler, and free.
- No paid article scraping in v1. Free pro content only.
- No replay video analysis. Text logs only.

## User Profile

- Plays MTGO. Active formats: Pauper, Standard, Limited.
- Competitive level: 2–3 on a 1–3 scale. Has 1st-placed Pauper Challenges, near top-8 PTQs.
- Prefers blunt, peer-level coaching over patient explanation.
- Wants pros prioritized over influencers (LSV, Reid Duke, Sigrist, Finkel, PVDDR, Huey, etc.).
- Owns digital copies of Patrick Chapin's *Next Level Magic* and *Next Level Deckbuilding*.
- Free article subscriptions only for now.
- Doesn't currently keep notes — the system should help build this habit over time.

## Architecture

### One-line summary

Claude Code is the runtime. A project folder at `C:\Desktop\CLAUDE Projects\MTG_Companion` contains a markdown knowledge library, the user's decks and match reviews, a memory store, and a single auto-triggering skill that wires it all together. Live data (cards, meta) is fetched on demand via existing tools.

### Folder structure

```
MTG_Companion/
├── CLAUDE.md                    # Project-level instructions + tone + disciplines
├── PROJECT_GUIDE.md             # What this is, how to use it
├── NOTES.md                     # Running scratchpad
│
├── library/                     # Knowledge corpus (read on demand by Claude)
│   ├── rules/
│   │   └── comprehensive-rules.md
│   ├── books/
│   │   ├── chapin-next-level-magic.md
│   │   └── chapin-next-level-deckbuilding.md
│   ├── articles/                # Curated free articles, scraped to markdown
│   │   ├── limited/
│   │   ├── pauper/
│   │   ├── standard/
│   │   └── general/
│   └── primers/                 # Format-specific quick references
│       ├── pauper-meta.md
│       ├── standard-meta.md
│       └── limited-current-set.md
│
├── decks/                       # User's decklists, one per file
├── reviews/                     # Saved match reviews, dated
├── notes/
│   ├── sideboard-guides/
│   └── draft-notes/
│
├── memory/                      # Auto-memory entries (user profile, leaks, patterns)
│
├── docs/superpowers/specs/      # Design specs (this file)
│
└── .claude/
    └── skills/
        └── mtg-mentor/
            └── SKILL.md         # The single skill that wires everything together
```

### The skill: `mtg-mentor`

A single skill that auto-triggers on any MTG-related conversation. Contains:

- **Tone instructions:** peer-level, blunt, no fluff, shorthand-fluent (tempo, EV, equity, leverage, sequencing, virtual card advantage, threat density, mana denial). No "great question," no basics-explanation, no "it depends, you decide" cop-outs.
- **Disciplines** (the load-bearing part):
  1. **Never recall card text from training.** Every card cited goes through Scryfall API first. Cards get errata, banned, reprinted with different text — training data is unreliable.
  2. **Never recall current meta from training.** Fetch live (MTGGoldfish, mtgtop8, recent challenge results, 17lands).
  3. **Show reasoning for non-trivial decisions.** Hand-keep, sideboard plan, line of play — give the chain so the user can disagree and push back.
  4. **When uncertain, says so.** "It's close, here's the case for each" beats confidently wrong.
- **Pointers** to: library paths, MTGO logs path (`Documents\Magic Online\Logs`), decks folder, reviews folder, memory entries.
- **Conversation patterns** for the five modes (prep, post-game review, deckbuilding, draft coach, open chat) — not commands, just patterns the mentor recognizes from natural language.

### Knowledge layers

| Layer | Source | When fetched |
|---|---|---|
| Comprehensive Rules | Free official Wizards download → markdown | Read on demand |
| Strategy books | Chapin × 2, user-owned digital copies → markdown | Read on demand |
| Curated articles | Firecrawl-scraped from free pro content (CFB free, MTGGoldfish free, SCG free, podcast show notes) | Read on demand |
| Card data | Scryfall API | Live, every cite |
| Meta data | MTGGoldfish, mtgtop8 | Live, on demand |
| Limited stats | 17lands.com | Live, on demand |
| User decks | `decks/*.md` | Read on demand |
| Match logs | `Documents\Magic Online\Logs\*.txt` | Read on demand |
| User memory | `memory/*.md` (auto-memory system) | Always loaded via index |

### Memory model

The auto-memory system tracks:

- **User profile:** competitive level, formats, achievements, playstyle observations
- **Decks the user is currently piloting** (pointers to decklist files)
- **Identified leaks:** patterns the mentor notices across reviews ("scoops too early in slightly-behind games," "mulls 1-landers on the play with 4-drops," "doesn't play around removal you don't see often enough")
- **Sideboarding patterns** that need work
- **Reference pointers:** where to find the user's decks, sideboard guides, recent reviews

Memory is updated by the mentor as patterns emerge across conversations and reviews — not preloaded.

## Five Conversation Modes

These are facets of the same chat, not separate features. The mentor recognizes intent from natural language; no slash commands.

### 1. Prep & study
*"I'm running mono-U Faeries in tonight's Pauper league, what should I be ready for?"*
→ Fetches live Pauper meta, pulls user's decklist, identifies worst matchups, recommends mulligan philosophy and key matchup notes. Offers to draft a sideboard guide if missing.

### 2. Post-game review
*"I just finished a match, can you review it?"*
→ Reads the most recent log from `Documents\Magic Online\Logs`, walks the game in chunks, flags decision points, asks the user what they were thinking before judging. Saves review to `reviews/YYYY-MM-DD-*.md`. Updates memory with any new leak patterns.

### 3. Deckbuilding partner
*"Here's my decklist, what's weak?"*
→ Pulls live meta, analyzes mana base / curve / threat density / interaction package, names specific weaknesses with reasoning, suggests tunes with tradeoffs.

### 4. Draft coach
*[paste pack screenshot or list]*
→ Identifies cards via Scryfall, checks current 17lands data for the set, gives a pick with reasoning, considers what's already drafted if context is provided.

### 5. Open chat mentor
*"Why did Reid keep this hand on camera last week?"*
→ Searches library + web, walks reasoning. If unfindable, says so.

## Build Phases

### Phase 1 — Foundation (the mentor exists and works)

- Folder structure scaffolded
- `CLAUDE.md` with tone + disciplines
- `mtg-mentor` skill written
- Comprehensive Rules ingested (free, official, ~400 pages → markdown)
- Both Chapin books ingested (user provides digital files)
- User profile saved to memory
- MTGO log path documented in skill
- **Acceptance:** real strategy conversation works; mentor cites Chapin and rules correctly; fetches Scryfall for any card mentioned.

### Phase 2 — User data

- Decklists added to `decks/` (user provides)
- First real match review on an MTGO log end-to-end, format validated
- First sideboard guide drafted collaboratively for most-played deck
- **Acceptance:** "review my last match" reads the log, walks the game, flags 2–3 decisions, saves the review file.

### Phase 3 — Article library

- Firecrawl pipeline scrapes free articles from CFB, MTGGoldfish, SCG, podcast show notes
- Author allowlist: pros only (LSV, Reid Duke, Sigrist, Finkel, PVDDR, Huey, etc.)
- Format-specific primers written (`pauper-meta.md`, `current-limited-set.md`)
- **Acceptance:** Limited theory question pulls from LSV's writing in the library.

### Phase 4 — Live data sharpening

- Documented fetch patterns for MTGGoldfish meta, mtgtop8 results, 17lands set data
- Fetch on demand (no scheduled refresh — simpler, always current)
- **Acceptance:** full draft pick coaching with current 17lands stats; pre-league meta brief with the week's current data.

## Open Questions for Phase 1 Plan

1. Comprehensive Rules — Wizards publishes as a `.txt` file. Convert to a single markdown file with section anchors, or split per major rule section? (Recommendation: single file, since grep is the access pattern.)
2. Chapin books — confirmed PDF, located at `C:\Desktop\MTG STUFF\MAGIC the GATHERING\Next Level Magic - Patrick Chapin.pdf` and `C:\Desktop\MTG STUFF\MAGIC the GATHERING\Next Level Deck Building - Patrick Chapin.pdf`. Phase 1 will run them through a PDF→markdown conversion (likely `pdftotext` + light cleanup, or a structured converter if layout is messy) into `library/books/`.
3. Auto-memory directory — the auto-memory system uses `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\` by default for this project, not the project folder's `memory/`. The spec assumes we use the auto-memory location for project-tied user memory and reserve `MTG_Companion/memory/` for nothing (or repurpose). To resolve before Phase 1.

## Risks & Constraints

- **MTGO ToS:** No real-time in-game advice. All review is post-game.
- **Card text drift:** Errata, bans, reprints. Scryfall is the source of truth, every time.
- **Meta drift:** Training data is stale. Live fetch for any meta question.
- **Copyright:** Books are user-owned digital copies, kept local, never published. Articles are free-tier only; if the user gets paid subs later, scraping respects ToS.
- **Replay coverage:** MTGO text logs only. Paper, Spelltable, video replays out of scope.

## Success Criteria

The mentor is "done enough to use daily" when:

- Asking it about a card never produces hallucinated text.
- Asking it about the current Pauper meta produces this week's data, not last year's.
- "Review my last match" works end-to-end on a real MTGO log file.
- It pushes back when the user is wrong, in shorthand the user understands, without softening.
- After 10 reviews, the memory contains specific, actionable leak patterns — not generic advice.
