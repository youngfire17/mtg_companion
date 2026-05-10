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
