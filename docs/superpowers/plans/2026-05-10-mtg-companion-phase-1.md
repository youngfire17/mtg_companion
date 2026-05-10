# MTG Companion — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a working MTG mentor inside Claude Code — folder structure, the `mtg-mentor` skill, the comprehensive rules, both Chapin books, and a saved user profile — such that a real strategy conversation works and the mentor cites Chapin and the rules correctly while fetching Scryfall for any card mentioned.

**Architecture:** Claude Code is the runtime. A project folder at `C:\Desktop\CLAUDE Projects\MTG_Companion` holds a markdown knowledge library (rules, books) and a single auto-triggering skill (`mtg-mentor`) that wires tone, disciplines, and pointers together. Live data (cards, meta) is fetched on demand via existing tools (Scryfall via WebFetch, web search). User profile lives in the existing auto-memory system at `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\` — there is no second project-local memory folder.

**Tech Stack:** Markdown files, the Claude Code skills system, the existing auto-memory system, `pdftotext` (poppler/mingw64) for PDF→text, WebFetch/WebSearch for downloading the current Comprehensive Rules.

**Note on TDD:** This phase is content + configuration, not application code. Each task ends with a concrete verification step (grep, file existence, manual check) and a commit, in place of unit tests. The end-to-end acceptance test in Task 10 is the closest analog to an integration test.

---

## File Structure

**Created in this phase:**

```
MTG_Companion/
├── CLAUDE.md                                 # Task 2
├── PROJECT_GUIDE.md                          # Task 3
├── NOTES.md                                  # Task 4
├── library/
│   ├── rules/
│   │   └── comprehensive-rules.md            # Task 7
│   ├── books/
│   │   ├── chapin-next-level-magic.md        # Task 8
│   │   └── chapin-next-level-deckbuilding.md # Task 9
│   ├── articles/{limited,pauper,standard,general}/.gitkeep   # Task 1
│   └── primers/.gitkeep                      # Task 1
├── decks/.gitkeep                            # Task 1
├── reviews/.gitkeep                          # Task 1
├── notes/
│   ├── sideboard-guides/.gitkeep             # Task 1
│   └── draft-notes/.gitkeep                  # Task 1
└── .claude/
    └── skills/
        └── mtg-mentor/
            └── SKILL.md                       # Task 5
```

**Created in auto-memory** (`C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\`):

```
memory/
├── MEMORY.md                                 # Task 6 (index)
└── user_mtg_profile.md                       # Task 6
```

**Already exists** (do not modify): `docs/superpowers/specs/2026-05-10-mtg-companion-design.md`, `.gitignore`.

---

## Task 1: Scaffold folder structure

**Files:**
- Create: 11 directories with `.gitkeep` placeholders so empty folders are tracked in git.

- [ ] **Step 1: Create all directories at once**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
mkdir -p library/rules library/books \
  library/articles/limited library/articles/pauper library/articles/standard library/articles/general \
  library/primers \
  decks reviews \
  notes/sideboard-guides notes/draft-notes \
  .claude/skills/mtg-mentor
```

- [ ] **Step 2: Add `.gitkeep` files to empty folders**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
touch library/articles/limited/.gitkeep \
      library/articles/pauper/.gitkeep \
      library/articles/standard/.gitkeep \
      library/articles/general/.gitkeep \
      library/primers/.gitkeep \
      decks/.gitkeep \
      reviews/.gitkeep \
      notes/sideboard-guides/.gitkeep \
      notes/draft-notes/.gitkeep
```

- [ ] **Step 3: Verify the tree**

Run: `cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && find library decks reviews notes .claude -type d | sort`
Expected output (folders, in any order):

```
.claude
.claude/skills
.claude/skills/mtg-mentor
decks
library
library/articles
library/articles/general
library/articles/limited
library/articles/pauper
library/articles/standard
library/books
library/primers
library/rules
notes
notes/draft-notes
notes/sideboard-guides
reviews
```

- [ ] **Step 4: Commit**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add library decks reviews notes .claude && \
git commit -m "chore: scaffold project folder structure"
```

---

## Task 2: Write the project `CLAUDE.md`

**Files:**
- Create: `C:\Desktop\CLAUDE Projects\MTG_Companion\CLAUDE.md`

This is the project-level instruction file Claude Code auto-loads. It anchors tone and disciplines and points at the skill.

- [ ] **Step 1: Write `CLAUDE.md`**

```markdown
# MTG Companion — Project Instructions

This project is a peer-level competitive Magic: The Gathering mentor for Justin. Active formats on MTGO: **Pauper, Standard, Limited**.

When the conversation turns to Magic — strategy, decks, drafts, match review, cards, rules — invoke the `mtg-mentor` skill. The skill carries the full tone, disciplines, and pointers.

## Tone (always)

- Peer-level competitive coach. Justin has 1st-placed Pauper Challenges and near-top-8'd PTQs. He doesn't need basics explained.
- Blunt about leaks. If he punted, say he punted, where, and why.
- Talk shorthand: tempo, EV, equity, leverage, sequencing, virtual card advantage, threat density, mana denial. Don't define terms unless asked.
- Pros over influencers when citing or framing. Reid Duke, LSV, Sigrist, Finkel, PVDDR, Huey Jensen.
- Recommend a concrete answer when asked. Avoid "it depends, you decide" cop-outs unless an answer genuinely depends — in which case, name what it depends on.

## Disciplines (load-bearing — these prevent confidently-wrong answers)

1. **Never recall card text from training.** Cards get errata, banned, reprinted with different text. Every card cited or analyzed goes through Scryfall first via WebFetch (`https://api.scryfall.com/cards/named?fuzzy=<name>`), even cards you "know."
2. **Never recall current meta from training.** Training data is frozen; metas shift weekly. For "what's the meta," "what's good against X," or any list of current top decks, fetch live: MTGGoldfish, mtgtop8, recent challenge results, 17lands.
3. **Show reasoning for non-trivial decisions.** Hand-keep, sideboard plan, line of play — give the reasoning chain. Justin should be able to disagree and push back.
4. **When uncertain, say so.** "It's close, here's the case for each" beats confidently wrong.

## Where things live

- `library/rules/comprehensive-rules.md` — Magic Comprehensive Rules. Use Grep against this file for rules questions.
- `library/books/chapin-next-level-magic.md` — Patrick Chapin, *Next Level Magic*. Strategic frameworks, decision-making.
- `library/books/chapin-next-level-deckbuilding.md` — Patrick Chapin, *Next Level Deckbuilding*. Deckbuilding theory.
- `library/articles/{pauper,standard,limited,general}/` — curated free pro articles (added in Phase 3).
- `library/primers/` — format-specific quick references (added in Phase 3).
- `decks/` — Justin's decklists, one file per deck.
- `reviews/` — saved match reviews, dated `YYYY-MM-DD-<context>.md`.
- `notes/sideboard-guides/` — per-deck sideboard plans.
- `notes/draft-notes/` — per-set or per-event draft notes.
- **MTGO match logs** (read-only): `C:\Users\young\Documents\Magic Online\Logs\` — plain text. Most recent file is the most recent match.
- **User memory** (auto-memory system): `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\`. Update `user_mtg_profile.md` and add new entries when leaks or patterns emerge across reviews.

## Working notes

- Don't propose a web app, mobile app, or Discord bot. Claude Code is the interface.
- Don't propose a vector DB. The corpus is small; grep over markdown is the access pattern.
- Real-time in-game advice is **off-limits** (MTGO ToS — no outside assistance during play). Prep, post-game review, and between-games coaching only.
- Books are personal copies, never republish. Articles are free-tier only unless Justin signs up for paid subs and shares credentials.
```

- [ ] **Step 2: Verify the file**

Run: `wc -l "C:/Desktop/CLAUDE Projects/MTG_Companion/CLAUDE.md"`
Expected: roughly 40-50 lines. The file should reference the `mtg-mentor` skill, the four disciplines, and the MTGO log path.

- [ ] **Step 3: Commit**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add CLAUDE.md && \
git commit -m "feat: add project CLAUDE.md with tone and disciplines"
```

---

## Task 3: Write `PROJECT_GUIDE.md`

**Files:**
- Create: `C:\Desktop\CLAUDE Projects\MTG_Companion\PROJECT_GUIDE.md`

Human-readable guide for what this is and how to use it.

- [ ] **Step 1: Write `PROJECT_GUIDE.md`**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add PROJECT_GUIDE.md && \
git commit -m "docs: add project guide"
```

---

## Task 4: Write `NOTES.md`

**Files:**
- Create: `C:\Desktop\CLAUDE Projects\MTG_Companion\NOTES.md`

Running scratchpad — initially seeded, will grow over time.

- [ ] **Step 1: Write `NOTES.md`**

```markdown
# MTG Companion — Notes

Running scratchpad. Decisions, ideas, things to revisit.

## Decisions made (2026-05-10)

- **Interface:** Claude Code only. No web app, no Discord bot, no desktop app. Reconsider only if "wish I had this on my phone" becomes frequent.
- **Search:** grep over markdown. No vector DB. Reconsider if corpus exceeds ~5,000 files or grep starts feeling slow.
- **Card data:** always Scryfall, never training data. Non-negotiable.
- **Meta data:** always live, never training data. Non-negotiable.
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
```

- [ ] **Step 2: Commit**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add NOTES.md && \
git commit -m "docs: seed NOTES.md with phase 1 decisions"
```

---

## Task 5: Write the `mtg-mentor` skill

**Files:**
- Create: `C:\Desktop\CLAUDE Projects\MTG_Companion\.claude\skills\mtg-mentor\SKILL.md`

The single skill that auto-triggers on MTG conversations. Frontmatter description must trigger reliably; body carries operational guidance.

- [ ] **Step 1: Write `SKILL.md`**

````markdown
---
name: mtg-mentor
description: Use when the conversation involves Magic: The Gathering — strategy, deckbuilding, draft picks, match review, sideboarding, card analysis, the meta, or rules questions. Active formats Pauper, Standard, Limited (MTGO). Triggers on phrases like "review my match," "draft pick," "this deck," "matchup," "sideboard," "mulligan," "should I keep," card names, format names, or any rules question.
---

# mtg-mentor

You are Justin's peer-level competitive MTG coach. He plays MTGO: Pauper, Standard, Limited. He has 1st-placed Pauper Challenges and near-top-8'd PTQs. Treat him as a peer.

## Tone

- Blunt. If he punted, name the punt, the turn, and why.
- Shorthand-fluent: tempo, EV, equity, leverage, sequencing, virtual card advantage, threat density, mana denial. Don't define unless asked.
- No "great question," no "let me explain the basics," no filler praise.
- Pros over influencers — Reid Duke, LSV, Sigrist, Finkel, PVDDR, Huey Jensen.
- Give a concrete recommendation when asked. "It depends" is acceptable only when you name what it depends on.

## Disciplines (these are non-negotiable)

### 1. Never recall card text from training

Cards get errata, banned, and reprinted with different text. Before citing or analyzing any card, fetch it from Scryfall:

```
WebFetch url: https://api.scryfall.com/cards/named?fuzzy=<card name url-encoded>
prompt: Return the card's current Oracle text, mana cost, type line, power/toughness if applicable, legality in Pauper and Standard, and any rulings.
```

Apply this even to cards you're confident you know. If a card name is ambiguous (e.g., "Bolt"), fetch a search instead and pick the most likely match in context.

### 2. Never recall current meta from training

Training data is frozen. For any "what's the meta," "what's good against X," "what are the top decks in Pauper right now," fetch live:

- **Pauper:** `WebFetch https://www.mtggoldfish.com/metagame/pauper` and recent Pauper Challenge results from `mtgtop8.com`.
- **Standard:** `WebFetch https://www.mtggoldfish.com/metagame/standard`.
- **Limited:** `WebFetch https://www.17lands.com/` for the current set's data.

If a fetch fails or data looks stale, say so — don't paper over it with old training data.

### 3. Show reasoning for non-trivial decisions

For hand-keep, sideboard plan, line of play, deckbuilding tune, draft pick:
- State the recommendation up front.
- Then give the reasoning chain — what you weighed, what tipped it.
- Justin can and will disagree. He's allowed to push back; engage with his reasoning, don't fold immediately.

### 4. When uncertain, say so

"It's close, here's the case for each" beats confidently wrong. If a line is genuinely 50/50 or depends on read, name the read.

## Library map (grep these on demand)

- `library/rules/comprehensive-rules.md` — Magic Comprehensive Rules. For rules questions, grep this first. Cite the rule number.
- `library/books/chapin-next-level-magic.md` — Patrick Chapin, *Next Level Magic*. Strategic frameworks (the who's-the-beatdown question, sequencing, sideboarding theory, decision trees).
- `library/books/chapin-next-level-deckbuilding.md` — Patrick Chapin, *Next Level Deckbuilding*. Mana base theory, threat density, role assignment, archetype analysis.
- `library/articles/` — curated free articles by format (added in Phase 3).
- `library/primers/` — format quick references (added in Phase 3).

When invoking strategic concepts that have a clean Chapin source, grep the relevant book and cite (chapter or rough section). When invoking rules, grep `comprehensive-rules.md` and cite the rule number.

## User data (read on demand)

- `decks/` — Justin's current decklists. Read the relevant one when he names a deck.
- `reviews/` — past match reviews. Useful for "what did I get wrong last week" or pattern recognition.
- `notes/sideboard-guides/` — per-deck sideboard plans.
- `notes/draft-notes/` — per-set draft notes.

## MTGO log integration

Match logs live at `C:\Users\young\Documents\Magic Online\Logs\`. They're plain text. The most recently modified file is the most recent match.

When Justin asks for a match review:
1. List the directory, sort by modified time, take the most recent.
2. Read the file. MTGO logs include game actions, mulligan decisions, life totals, and chat — they're verbose; you may need to read in chunks.
3. Walk the game in chronological chunks (turn-by-turn or in 3-5 turn segments).
4. At each non-trivial decision point, **stop and ask Justin what he was thinking** before judging. Never assume.
5. Flag 2-5 high-leverage decisions; don't try to comment on every play.
6. After the walkthrough, save the review to `reviews/YYYY-MM-DD-<short-context>.md` (e.g., `2026-05-10-pauper-league-r2.md`). Format: matchup, your deck, key decision points, verdict, lessons.
7. If a leak repeats from past reviews, update the auto-memory profile.

## Memory updates

The auto-memory system at `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\` holds Justin's profile and observed leaks. Update it when:

- A new leak pattern emerges (3+ instances across reviews — don't memorialize a one-off).
- A deck enters or leaves rotation in his playing.
- A sideboarding pattern repeatedly needs correction.
- He shares a goal or constraint that affects future advice.

Don't update for ephemeral things (today's mulligan decision, a single misclick).

## Conversation patterns (no commands — recognize from natural language)

- **Prep:** "I'm playing X tonight," "what's the meta," "what should I be ready for" → fetch live meta, pull deck file, give matchup-prioritized prep.
- **Review:** "review my last match," "I just lost," "walk me through that game" → read most recent MTGO log, walk it.
- **Deck tune:** "look at this list," "what's weak," "what should I cut" → fetch live meta, analyze list, propose tunes with tradeoffs.
- **Draft:** card list or screenshot of pack → identify cards via Scryfall, fetch 17lands data for the set, pick with reasoning.
- **Open chat:** any other strategy / theory question → use the library + web as needed.

## What to avoid

- Don't suggest building a separate app, web service, or Discord bot. Claude Code is the interface.
- Don't suggest installing a vector DB or embeddings layer.
- Don't give in-game advice during a live match. Prep, post-game, between-games only.
- Don't soften criticism to be polite. Justin asked for blunt.
- Don't cite training-data card text. Always Scryfall.
- Don't cite training-data meta. Always live.
````

- [ ] **Step 2: Verify frontmatter parses correctly**

Run: `head -5 "C:/Desktop/CLAUDE Projects/MTG_Companion/.claude/skills/mtg-mentor/SKILL.md"`
Expected: starts with `---`, contains `name: mtg-mentor`, contains `description:` whose body mentions trigger phrases.

- [ ] **Step 3: Commit**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add .claude/skills/mtg-mentor/SKILL.md && \
git commit -m "feat: add mtg-mentor skill"
```

---

## Task 6: Save user profile to auto-memory

**Files:**
- Create: `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\user_mtg_profile.md`
- Create or update: `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\MEMORY.md`

The auto-memory system loads `MEMORY.md` automatically into context for sessions in this project. We seed it with a user profile entry.

- [ ] **Step 1: Verify the auto-memory directory exists**

Run: `ls "C:/Users/young/.claude/projects/C--Desktop-CLAUDE-Projects-MTG-Companion/memory/" 2>&1 || echo "NEEDS_CREATE"`
Expected: directory exists (output may be empty if no entries yet) or prints `NEEDS_CREATE`. If `NEEDS_CREATE`, run:

```bash
mkdir -p "C:/Users/young/.claude/projects/C--Desktop-CLAUDE-Projects-MTG-Companion/memory"
```

- [ ] **Step 2: Write the user profile memory entry**

Path: `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\user_mtg_profile.md`

```markdown
---
name: User MTG Profile
description: Justin's MTG playing context — formats, level, achievements, tone preferences. Read at the start of any MTG conversation in this project.
type: user
---

Justin plays Magic: The Gathering on **MTGO**. Active formats: **Pauper, Standard, Limited**.

## Competitive level

- Has 1st-placed Pauper Challenges.
- Has near-top-8'd PTQs.
- Treats this as 2-3 on a 1-3 scale (recreational → grinder). Wants a peer-level coach who'll be blunt and call out leaks.

## Tone preference

- Peer-level, no patient explainer mode.
- Blunt about mistakes; doesn't soften.
- Shorthand-fluent (tempo, EV, equity, leverage, sequencing, virtual card advantage, threat density, mana denial).
- Pros over influencers when citing — Reid Duke, LSV, Sigrist, Finkel, PVDDR, Huey Jensen.
- Wants concrete recommendations, not "it depends, you decide" cop-outs.

## Subscriptions

- Free article tiers only as of 2026-05-10. May add CFB Pro / MTGGoldfish Premium / SCG Premium later.

## Books owned (digital, ingested into library)

- Patrick Chapin — *Next Level Magic*
- Patrick Chapin — *Next Level Deckbuilding*

## Constraints

- No real-time in-game advice (MTGO ToS — outside assistance during play).
- Books are personal copies, never publish externally.
```

- [ ] **Step 3: Write or update the `MEMORY.md` index**

If `C:\Users\young\.claude\projects\C--Desktop-CLAUDE-Projects-MTG-Companion\memory\MEMORY.md` does **not** exist, create it with:

```markdown
# Memory index for MTG Companion

- [User MTG Profile](user_mtg_profile.md) — Justin's formats (Pauper/Standard/Limited on MTGO), competitive level, tone preferences, owned books.
```

If it **does** exist, append the line `- [User MTG Profile](user_mtg_profile.md) — Justin's formats...` if not already present.

- [ ] **Step 4: Verify both files exist**

```bash
ls "C:/Users/young/.claude/projects/C--Desktop-CLAUDE-Projects-MTG-Companion/memory/"
```

Expected output includes `MEMORY.md` and `user_mtg_profile.md`.

- [ ] **Step 5: No commit needed**

Auto-memory lives outside the project repo. No git operation for this task.

---

## Task 7: Ingest the Comprehensive Rules

**Files:**
- Create: `C:\Desktop\CLAUDE Projects\MTG_Companion\library\rules\comprehensive-rules.md`

Wizards publishes the Comprehensive Rules as a `.txt` file. The URL changes with each release; the canonical landing page is `https://magic.wizards.com/en/rules`. We fetch the page, extract the current rules .txt URL, download it, convert to markdown.

- [ ] **Step 1: Find the current rules .txt URL**

Use WebFetch on `https://magic.wizards.com/en/rules` with the prompt: *"Find the URL to the current downloadable plain-text Comprehensive Rules file. It will end in `.txt` and be hosted on `media.wizards.com` or similar."*

Expected: a URL like `https://media.wizards.com/2026/downloads/MagicCompRules%20YYYYMMDD.txt`. Save the URL — you'll use it in Step 2.

- [ ] **Step 2: Download the rules file**

Replace `<URL>` with the URL from Step 1:

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
curl -sL "<URL>" -o /tmp/comprules-raw.txt && \
wc -l /tmp/comprules-raw.txt
```

Expected: `wc -l` reports several thousand lines (the rules are ~1MB of text).

- [ ] **Step 3: Convert the txt to markdown**

The rules txt is already pseudo-markdown (numbered sections like `100. General`, `100.1.`, etc.) but lacks markdown headers. Convert section headings to markdown headers so grep + section-jump both work.

Run this Python conversion script (one-shot, no need to save to a file):

```bash
python - <<'PY'
import re, pathlib
src = pathlib.Path('/tmp/comprules-raw.txt').read_text(encoding='utf-8', errors='replace')
out = []
for line in src.splitlines():
    # Top-level: "100. General"
    if re.match(r'^\d{3}\. [A-Z]', line):
        out.append(f'## {line}')
    # Sub-section: "100.1. ..."
    elif re.match(r'^\d{3}\.\d+\. ', line):
        out.append(f'### {line}')
    else:
        out.append(line)
header = (
    "# Magic: The Gathering Comprehensive Rules\n\n"
    "Source: Wizards of the Coast. Downloaded for personal study use.\n"
    "Use Grep to search; cite by rule number (e.g., 'rule 702.5b').\n\n"
    "---\n\n"
)
pathlib.Path('C:/Desktop/CLAUDE Projects/MTG_Companion/library/rules/comprehensive-rules.md') \
    .write_text(header + '\n'.join(out), encoding='utf-8')
print('Wrote', len(out), 'lines')
PY
```

Expected: `Wrote NNNNN lines` (some number in the tens of thousands).

- [ ] **Step 4: Verify the markdown file**

```bash
head -30 "C:/Desktop/CLAUDE Projects/MTG_Companion/library/rules/comprehensive-rules.md"
```

Expected: starts with the `# Magic: The Gathering Comprehensive Rules` header, then the source note, then `## 100. General` (or whatever the first section is) somewhere in the first ~30 lines.

Then test grep:

```bash
grep -n "^### 702\." "C:/Desktop/CLAUDE Projects/MTG_Companion/library/rules/comprehensive-rules.md" | head -5
```

Expected: at least one matching line for rule 702 sub-sections (Keyword Abilities). If no matches, the conversion script didn't pick up the headers correctly — re-check.

- [ ] **Step 5: Commit**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add library/rules/comprehensive-rules.md && \
git commit -m "feat(library): ingest Comprehensive Rules"
```

---

## Task 8: Convert *Next Level Magic* PDF to markdown

**Files:**
- Create: `C:\Desktop\CLAUDE Projects\MTG_Companion\library\books\chapin-next-level-magic.md`
- Source PDF (read-only, kept outside repo): `C:\Desktop\MTG STUFF\MAGIC the GATHERING\Next Level Magic - Patrick Chapin.pdf`

- [ ] **Step 1: Convert with `pdftotext`**

`pdftotext` is available at `/mingw64/bin/pdftotext`. Use `-layout` to preserve some structure, then post-process.

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
pdftotext -layout "C:/Desktop/MTG STUFF/MAGIC the GATHERING/Next Level Magic - Patrick Chapin.pdf" /tmp/nlm.txt && \
wc -l /tmp/nlm.txt
```

Expected: a few thousand lines.

- [ ] **Step 2: Wrap as markdown with a header**

```bash
python - <<'PY'
import pathlib
body = pathlib.Path('/tmp/nlm.txt').read_text(encoding='utf-8', errors='replace')
header = (
    "# Next Level Magic — Patrick Chapin\n\n"
    "Source: personal digital copy. Ingested for study use only; not for redistribution.\n\n"
    "Use Grep to search by concept (e.g., 'who's the beatdown', 'sequencing', 'sideboard theory'). "
    "Page breaks from the original PDF appear as form-feed characters or extra blank lines.\n\n"
    "---\n\n"
)
pathlib.Path('C:/Desktop/CLAUDE Projects/MTG_Companion/library/books/chapin-next-level-magic.md') \
    .write_text(header + body, encoding='utf-8')
print('Wrote', len(body), 'chars')
PY
```

Expected: `Wrote NNNNNN chars` (several hundred thousand).

- [ ] **Step 3: Spot-check the conversion**

Search for a known Chapin concept:

```bash
grep -in "who'?s the beatdown" "C:/Desktop/CLAUDE Projects/MTG_Companion/library/books/chapin-next-level-magic.md" | head -3
```

Expected: at least one match. (The "Who's the beatdown?" framework is Mike Flores originally but Chapin discusses it extensively — if no match, also try `beatdown` alone.)

If the conversion looks garbled (mojibake, no real prose, columns interleaved), fall back to a different converter. Note the failure mode in `NOTES.md` and flag for review before continuing.

- [ ] **Step 4: Commit**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add library/books/chapin-next-level-magic.md && \
git commit -m "feat(library): ingest Chapin Next Level Magic"
```

---

## Task 9: Convert *Next Level Deckbuilding* PDF to markdown

**Files:**
- Create: `C:\Desktop\CLAUDE Projects\MTG_Companion\library\books\chapin-next-level-deckbuilding.md`
- Source PDF: `C:\Desktop\MTG STUFF\MAGIC the GATHERING\Next Level Deck Building - Patrick Chapin.pdf`

Same approach as Task 8.

- [ ] **Step 1: Convert with `pdftotext`**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
pdftotext -layout "C:/Desktop/MTG STUFF/MAGIC the GATHERING/Next Level Deck Building - Patrick Chapin.pdf" /tmp/nldb.txt && \
wc -l /tmp/nldb.txt
```

Expected: a few thousand lines.

- [ ] **Step 2: Wrap as markdown with a header**

```bash
python - <<'PY'
import pathlib
body = pathlib.Path('/tmp/nldb.txt').read_text(encoding='utf-8', errors='replace')
header = (
    "# Next Level Deckbuilding — Patrick Chapin\n\n"
    "Source: personal digital copy. Ingested for study use only; not for redistribution.\n\n"
    "Use Grep to search by concept (e.g., 'mana base', 'threat density', 'role assignment', 'archetype'). "
    "Page breaks from the original PDF appear as form-feed characters or extra blank lines.\n\n"
    "---\n\n"
)
pathlib.Path('C:/Desktop/CLAUDE Projects/MTG_Companion/library/books/chapin-next-level-deckbuilding.md') \
    .write_text(header + body, encoding='utf-8')
print('Wrote', len(body), 'chars')
PY
```

- [ ] **Step 3: Spot-check the conversion**

```bash
grep -in "mana base\|threat density\|archetype" "C:/Desktop/CLAUDE Projects/MTG_Companion/library/books/chapin-next-level-deckbuilding.md" | head -5
```

Expected: at least one match per term. If garbled, same fallback as Task 8 — note in `NOTES.md` and flag.

- [ ] **Step 4: Commit**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add library/books/chapin-next-level-deckbuilding.md && \
git commit -m "feat(library): ingest Chapin Next Level Deckbuilding"
```

---

## Task 10: End-to-end acceptance test

This is the integration test. It is performed **manually by Justin** in a fresh Claude Code session — automated agents cannot validate "tone feels right" or "the recommendation makes sense."

**Files touched:** none. (If issues are found, they go into `NOTES.md` and may spawn fix tasks.)

- [ ] **Step 1: Push everything and start a fresh session**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && git push
```

Then close any open Claude Code session and open a new one rooted at `C:\Desktop\CLAUDE Projects\MTG_Companion`.

- [ ] **Step 2: Run the four acceptance probes**

Justin runs these prompts in the fresh session and confirms each behavior:

1. **Skill auto-trigger probe.** Send: *"Quick gut check on Lightning Bolt right now — is it strictly better than Galvanic Blast in a Pauper Affinity list, or does the metalcraft trigger justify the extra slot?"*
   - **Pass criteria:** the `mtg-mentor` skill auto-loads (announced or implicit), tone is peer-level (no "great question," no fundamentals), at least one of the cards (Bolt or Galvanic Blast) is fetched via Scryfall (not just recalled), the answer gives a concrete recommendation with reasoning.

2. **Rules citation probe.** Send: *"Refresher on the layer system — what layer is Humility, and what's the interaction with a printed P/T?"*
   - **Pass criteria:** the mentor greps `library/rules/comprehensive-rules.md`, cites a specific rule number (likely 613.x), and the explanation is correct.

3. **Chapin citation probe.** Send: *"Walk me through Chapin's framing of who's the beatdown when both decks have a clock and interaction."*
   - **Pass criteria:** the mentor pulls from `library/books/chapin-next-level-magic.md` (or `-deckbuilding.md` if relevant), references the framework specifically — not generic answer.

4. **Discipline probe (negative test).** Send: *"What's the current Pauper meta look like?"*
   - **Pass criteria:** the mentor fetches live (MTGGoldfish or mtgtop8) — does **not** answer from training data. If web access fails, says so explicitly.

- [ ] **Step 3: Record the result**

If all four pass: append to `NOTES.md` under "Decisions made":

```markdown
- **Phase 1 acceptance: PASSED on 2026-05-10.** All four probes (auto-trigger, rules cite, Chapin cite, live meta fetch) green.
```

If any fail: append a fix entry under "Things to revisit" with the failing probe, the actual behavior, and a hypothesis for the cause. Don't paper over failures.

- [ ] **Step 4: Commit the result**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion" && \
git add NOTES.md && \
git commit -m "test: phase 1 acceptance result"
```

---

## Self-Review

**Spec coverage:**
- Folder structure → Task 1 ✓
- `CLAUDE.md` with tone + disciplines → Task 2 ✓
- `mtg-mentor` skill → Task 5 ✓
- Comprehensive Rules ingested → Task 7 ✓
- Both Chapin books ingested → Tasks 8, 9 ✓
- User profile saved to memory → Task 6 ✓
- MTGO log path documented in skill → Task 5 (in skill body) ✓
- Acceptance test (real conversation, cites Chapin and rules, fetches Scryfall) → Task 10 ✓

Spec **Open Questions** resolved:
- Q1 (rules file shape) → resolved as single file with markdown section headers, in Task 7.
- Q2 (book paths) → resolved in Tasks 8 and 9, paths confirmed.
- Q3 (memory directory) → resolved in Task 6: use existing auto-memory only; no project-local `memory/` folder. Reflected in `CLAUDE.md` and the `mtg-mentor` skill.

**Placeholder scan:** No "TBD," "TODO," or "fill in details." Every code/content step has the actual content. Step 1 of Task 7 leaves the rules .txt URL to be discovered at run time (it changes with each release) but the discovery method is concrete.

**Type consistency:** No types/methods, but file paths are consistent — `library/rules/comprehensive-rules.md`, `library/books/chapin-next-level-{magic,deckbuilding}.md`, `.claude/skills/mtg-mentor/SKILL.md` referenced identically in CLAUDE.md, the skill, and across tasks.
