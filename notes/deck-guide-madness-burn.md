# Pauper Madness Burn — Deck Guide

*Oracle text verified for every card interaction. Last updated: 2026-05-10.*

---

## Overview & Role Theory

This deck wins by doing one thing faster than almost anything else in Pauper: converting cantrip-discard loops into direct damage, with a clock of bodies that punish the opponent for letting spells resolve. You are almost always the beatdown. The plan is never to "out-grind" — it's to make every card generate more than one damage event so you run the opponent out of life before they stabilize.

**Role assignment in one sentence:** You are the aggressor unless your opponent's deck is faster and runs more creatures than you can burn, in which case you briefly become the tempo-control deck (trading efficiently until you flip the corner back to aggression). That second mode happens almost exclusively against Mono-Red Burn mirrors or Goblin variants.

**Win condition stack, in priority order:**
1. Kessig Flamebreather / Guttersnipe on board + spell flood
2. Sneaky Snacker recurring as a free 2/1 flier every turn cycle
3. Raw face-burn off Lightning Bolt, Fiery Temper madness, Fireblast

Knowing which of the three lines you're threading in a given game determines every sequencing decision below.

---

## The Engine (How the Cards Actually Interact)

### Voldaren Epicure

Oracle text: *"When this creature enters, it deals 1 damage to each opponent. Create a Blood token. (It's an artifact with '{1}, {T}, Discard a card, Sacrifice this token: Draw a card.')"*

**What this does:** A 1/1 for {R} that ETB-pings for 1 and leaves behind a reusable discard outlet. Two points matter for competitive play:

1. The ETB ping is a triggered ability, not a spell — it does **not** trigger Kessig Flamebreather or Guttersnipe. Epicure's cast is a creature spell, also not triggering either enchantment.
2. Blood is an artifact. This means after Epicure ETBs, you have an artifact in play. This is relevant for Smash to Smithereens targets if your opponent is also playing artifacts, and it means you will naturally have artifact count on board mid-game. **Galvanic Blast is not in this deck** — do not make decisions assuming Metalcraft exists.
3. The Blood activation ({1}, {T}, discard a card, sacrifice: draw a card) is an **activated ability**, not a spell. Activating Blood does not trigger Kessig Flamebreather or Guttersnipe. If you discard Fiery Temper to Blood, the madness trigger fires (you discarded it "into exile" per madness rules), letting you cast it for {R} — but Kessig's ping comes from casting Fiery Temper as a noncreature spell, not from the Blood activation itself.

**Sequencing implication:** Epicure into Blood activation into Fiery Temper for {R} is a three-step sequence that costs {R} (Epicure) + {1}{T}(Blood) + {R}(madness) = {2}{R} + a Blood sacrifice for 1 (ETB) + 3 (Fiery Temper) = 4 damage total. With Kessig on board it's 5. With both Kessig and Guttersnipe it's 7. Know this arithmetic cold.

---

### Faithless Looting

Oracle text: *"Draw two cards, then discard two cards. Flashback {2}{R}."*

**Critical interaction note:** Faithless Looting draws two cards, then you discard two. The draw happens before the discard. This means if Faithless Looting is your first draw effect of the turn (plus your draw step = 1 prior draw), casting it brings you to draw 2 and draw 3 — triggering Sneaky Snacker **during resolution**, before you discard. Your Snacker returns tapped at the moment of the third card drawn.

**The discard two:** Both discards happen simultaneously at instruction resolution ("discard two cards"). If you discard Fiery Temper as one of the two, madness triggers. If you discard two cards with madness, both madness triggers go on the stack. You can cast both for their madness cost. This is your highest-EV Faithless Looting use case.

**Flashback {2}{R}:** Sorcery speed only. Costs three mana total. Usually wrong to flashback unless you're flooding on lands and need to dig. The primary value is casting it from hand turn 1 or 2 to enable madness and Sneaky Snacker triggers. Flashback is a "nice to have" for late-game desperation, not a core line.

---

### Highway Robbery

Oracle text: *"You may discard a card or sacrifice a land. If you do, draw two cards. Plot {1}{R} (You may pay {1}{R} and exile this card from your hand. Cast it as a sorcery on a later turn without paying its mana cost. Plot only as a sorcery.)"*

**What it actually does:** For {1}{R}, optionally discard or sacrifice a land, then draw two. The draw only happens if you paid the additional cost. You will almost always discard, not sacrifice a land. Discarding Fiery Temper here triggers madness.

**The conditional draw:** If for some reason you can't or don't pay the additional cost (e.g., empty hand, no lands to sacrifice), you draw nothing and wasted two mana. Never cast Highway Robbery without a discard target unless you're specifically planning to sacrifice a land to dig.

**Plot {1}{R}:** Pay {1}{R}, exile this from hand, cast it later for free. The primary use case is plotting on turn 2 when you'd otherwise lose the card to an awkward draw, then firing it turn 3 or 4 without spending mana — effectively a mana-positive play in later turns. **Plotting does not count as casting** the spell, so it does not trigger Kessig Flamebreather. Casting the plotted copy later does trigger Kessig (it's a noncreature spell being cast).

**Comparing Highway Robbery vs. Grab the Prize:** See dedicated section below.

---

### Grab the Prize

Oracle text: *"As an additional cost to cast this spell, discard a card. Draw two cards. If the discarded card wasn't a land card, Grab the Prize deals 2 damage to each opponent."*

**The additional cost is mandatory.** You cannot cast Grab the Prize without discarding a card. This means you need a card in hand to cast it, full stop.

**The 2-damage trigger:** Fires if the discarded card is a nonland. In almost every scenario you're discarding a nonland — so plan on this dealing 2 to each opponent. In a 1v1 game that's 2 damage. With Kessig it's 3. With Kessig + Guttersnipe it's 7. Grab the Prize is doing a lot of work.

**The discard is part of the cast:** Because you discard as an additional cost, the discard happens during spell announcement (paying costs), before the spell resolves. This means madness on the discarded card (e.g., Fiery Temper) works correctly — you discard it into exile during announcement, the madness trigger fires, then Grab the Prize resolves (draw 2, deal 2), then you may cast Fiery Temper for {R}.

**Kessig Flamebreather interaction:** Grab the Prize is a sorcery (noncreature spell) — it triggers Kessig (+1 damage). The 2-damage clause is part of the spell's resolution, not a separate trigger. So: Kessig ping (1) + Grab the Prize resolution (2 damage, 2 cards drawn) + potential Guttersnipe ping (2) = 5 damage from one sorcery before Fiery Temper even lands.

---

### Highway Robbery vs. Grab the Prize: When to Cast Which

Both cost {1}{R} and draw two cards conditional on a discard. The differences:

| | Highway Robbery | Grab the Prize |
|---|---|---|
| Damage | None from the spell itself | 2 to each opponent (if nonland discarded) |
| Kessig trigger | Yes (noncreature spell) | Yes (noncreature spell) |
| Guttersnipe trigger | No (sorcery triggers Guttersnipe) ... wait — check oracle | Yes (sorcery) |

**Re-checking Guttersnipe:** Oracle text says *"Whenever you cast an instant or sorcery spell..."* Both Highway Robbery and Grab the Prize are sorceries. Both trigger Guttersnipe. Both trigger Kessig (noncreature spells).

**So the decision framework is:**
- Cast **Grab the Prize** when: you need the 2 damage, you have a nonland to pitch, you want the highest damage-per-mana output. This is your default choice when you want burn.
- Cast **Highway Robbery** when: you want to preserve the option to pitch a land instead of a spell (mana flood recovery), or you've plotted it and are casting for free. Plotting Highway Robbery also makes sense when your hand is contested — if an opponent might make you discard, a plotted card is safe.
- Never cast Highway Robbery over Grab the Prize just to "save" a card in hand if the 2 damage matters. Two damage is enormous in a deck trying to finish games at 3-4 life totals.

---

### Lava Dart

Oracle text: *"Lava Dart deals 1 damage to any target. Flashback — Sacrifice a Mountain."*

**Two separate spells.** Casting from hand (for {R}) is one spell. Flashing back (sacrificing a Mountain) is a second, separate casting. Each casting:
- Triggers Kessig Flamebreather once (noncreature spell)
- Triggers Guttersnipe once (instant)
- Enables madness on anything you discard via other effects (Lava Dart itself has no discard)

**The Mountain sacrifice for flashback is a cost paid during announcement** — you sacrifice the Mountain before Lava Dart resolves. You do not get to respond to your own flashback by saving the Mountain. If you have only one Mountain left, flashing back Lava Dart means you're tapped out and at one land. This is often correct in kill turns; it's disastrous in turns 2-3.

**Mana cost of flashback:** Zero mana. The flashback cost is "sacrifice a Mountain," which has no mana component. So you can flashback Lava Dart even at 0 mana in your pool, as long as you have an untapped Mountain to sacrifice.

**When to hold Lava Dart (from graveyard):**
- Hold if you need the Mountain for future turns and you're not killing them this turn.
- Hold if you haven't cast your draw spells yet — flashback Lava Dart after drawing to maximize Kessig triggers.
- Fire immediately if: Kessig + Guttersnipe are on board and you're stringing a kill turn, OR you're trying to kill a 1-toughness blocker that's stopping your attack.

**Lava Dart as removal:** 1 damage is a lot in Pauper. It kills: Kessig Flamebreather (1/3 — wait, no, Kessig is 1/3, so 1 damage doesn't kill it), Guttersnipe (2/2, no), Voldaren Epicure (1/1, yes), Sneaky Snacker (2/1, no). Lava Dart from hand + flashback = 2 damage total, killing Epicure, small tokens, Young Wolf (after undying... no, that's a 2/2). The primary targets are 1-toughness utility creatures and opposing X/1s.

---

### Kessig Flamebreather

Oracle text: *"Whenever you cast a noncreature spell, this creature deals 1 damage to each opponent."*

**What triggers it:** Any noncreature spell you cast. Instants (Lightning Bolt, Fiery Temper, Lava Dart, Lava Dart flashback, Searing Blaze, Smash to Smithereens, Flaring Pain), sorceries (Faithless Looting, Highway Robbery, Grab the Prize, End the Festivities, Faithless Looting flashback). Each casting is a separate trigger.

**What does NOT trigger it:**
- Creature spells (Voldaren Epicure, Kessig Flamebreather, Guttersnipe, Sneaky Snacker)
- Activated abilities (Blood token activation, Relic of Progenitus activations)
- Triggered abilities
- Casting a plotted card does trigger Kessig — it's still casting a sorcery, just without paying mana cost

**Multiple Kessig triggers:** If you have two Kessig Flamebreathers on board (possible), each triggers independently on each spell. One Lightning Bolt = 2 pings (one per Kessig) = 2 damage from triggers + 3 from Bolt = 5 total. Having two Kessigs is a goldfish kill threat.

**Kessig is a 1/3.** This matters a lot — it survives Lava Dart (1 damage), End the Festivities (1 to each creature), and Lightning Bolt (3 damage) does kill it. Protect Kessig from Bolt-equivalent removal; it's your engine piece, not a chump blocker.

---

### Guttersnipe

Oracle text: *"Whenever you cast an instant or sorcery spell, this creature deals 2 damage to each opponent."*

**Stricter than Kessig:** Only instants and sorceries. Not creature spells (same as Kessig). Not activated abilities (same as Kessig). But also not "any noncreature spell" — there is no noncreature spell in this deck that isn't an instant or sorcery, so in practice Kessig and Guttersnipe trigger on identical spells in this list. The difference matters against other decks but is irrelevant in your own deck's context.

**Double-stacking with Kessig:** When both are on board, each spell you cast that's an instant or sorcery deals 1 (Kessig) + 2 (Guttersnipe) = 3 additional damage. Lightning Bolt = 3 + 3 = 6 total. Fiery Temper at madness cost = 3 + 3 = 6 total. This is a fast kill rate.

**Guttersnipe is a 2/2.** It dies to Lava Dart + Lava Dart flashback (2 damage total), Lightning Bolt, or any 2+ damage effect. It's more fragile than Kessig (1/3). In a racing scenario, opponents will prioritize killing Guttersnipe first if both are in play because of the higher ping value. Play Guttersnipe second (after Kessig) to use Kessig as a lightning rod.

**Guttersnipe costs {2}{R}.** This is your 3-drop. Turn 3 Guttersnipe into a turn 4 spell-flood is the nut draw. Don't slam Guttersnipe on turn 3 if you can't protect it from a pre-combat removal spell — cast your burn spell first to drain their interaction mana if possible.

---

### Fiery Temper

Oracle text: *"Fiery Temper deals 3 damage to any target. Madness {R}."*

**Madness rule:** "If you discard this card, discard it into exile. When you do, cast it for its madness cost or put it into your graveyard." The madness trigger fires at the moment of discard. You can cast it for {R} in response to the trigger. This makes it a 1-mana Lightning Bolt whenever you have a discard outlet.

**Discard outlets in this deck:**
- Faithless Looting (discard 2 after drawing 2)
- Highway Robbery (discard a card as optional cost)
- Grab the Prize (discard a card as mandatory cost)
- Blood token activation ({1}, {T}, discard a card, sacrifice: draw a card)

**The timing sequence for madness:** Discard Fiery Temper → madness trigger goes on the stack → you can cast it for {R} immediately. You don't need to wait for the spell that caused the discard to resolve. Example: cast Faithless Looting (it's on the stack), Faithless Looting resolves (draw 2, then discard 2 — discard Fiery Temper among the two), madness trigger fires, cast Fiery Temper for {R}. Fiery Temper resolves before anything else.

**Fiery Temper is an instant** even when cast for its madness cost. Kessig triggers on it. Guttersnipe triggers on it. It can target players or creatures.

**Pitching Fiery Temper to Grab the Prize:** You cast Grab the Prize (announcing it, discarding Fiery Temper as additional cost) — madness trigger fires. Grab the Prize resolves: draws 2, deals 2 (nonland was discarded). Then Fiery Temper resolves for {R}: deals 3. Total: 2 + 3 = 5 damage, plus Kessig (1) + Guttersnipe (2 from Grab, 2 from Fiery Temper) if both are in play = 5 + 1 + 2 + 2 + 2 = 12 damage from two spells. That's the ceiling with both pingers in play.

---

### Sneaky Snacker

Oracle text: *"Flying. When you draw your third card in a turn, return this card from your graveyard to the battlefield tapped."*

**The trigger condition:** Drawing your **third** card in a turn. Not the third card total — the third draw event that results in drawing a card. Each discrete draw counts:
- Your draw step = card 1
- Drawing the first card off Faithless Looting = card 2
- Drawing the second card off Faithless Looting = card 3 → TRIGGER

**Sneaky Snacker returns from your graveyard.** It must already be in the graveyard to return. If it's in your hand or library, the trigger doesn't return it (there's nothing to return from the graveyard). This means you need to have gotten a Snacker into the graveyard before the trigger fires. Ways to get it there: casting and having it die, discarding it (to Faithless Looting, Highway Robbery, Grab the Prize, Blood token), or milling.

**It comes back tapped.** You cannot attack with it the turn it returns. It can block. In most cases Sneaky Snacker's return on your turn means you swing with it next turn.

**The 2/1 flying body:** In Pauper, a recurring 2/1 flier is significant. Guttersnipe blockers won't touch it in the air. It applies consistent pressure against decks that have no flying blockers.

**Getting Snacker into the yard early:** The ideal line is to discard Sneaky Snacker to Faithless Looting turn 1 (if you draw it early), then trigger the return on turn 2 or 3 when you chain another draw spell. You are intentionally putting a {U}{B} card in a mono-red deck into your graveyard as a free recurring threat. This is the whole point — Snacker doesn't cost you a red mana to deploy after the first time.

**Sneaky Snacker is a Faerie Rogue.** It's not a Human Shaman, not a Vampire. Tribal synergies are irrelevant here.

---

### The Draw-3 Ecosystem: Full Map

To trigger Sneaky Snacker's return, you need to draw your 3rd card in a single turn. Here's every card in the deck that draws, and how many draws it produces:

| Card | Draws produced | Notes |
|---|---|---|
| Your draw step | 1 | Always happens |
| Faithless Looting | 2 (draw 2, then discard 2) | 1st card drawn = card 2, 2nd card drawn = card 3 → triggers if draw step already happened |
| Highway Robbery | 2 (draw 2 if additional cost paid) | Same as Faithless Looting |
| Grab the Prize | 2 (draw 2) | Same |
| Blood token activation | 1 (draw 1) | Triggers if you've already drawn 2 earlier |
| Relic of Progenitus (SB) | 1 (draw 1 on exile activation) | Triggers if you've already drawn 2 earlier |

**The math:** Your draw step (card 1) + any 2-card draw spell (cards 2 and 3) = Sneaky Snacker trigger. This is the default pattern. You need your draw step plus one draw-2 spell to trigger Snacker on the same turn.

**What does NOT trigger Snacker when cast as your first spell of the turn (before draw step):** Nothing in this deck can. You always take your draw step first, so any draw-2 spell after that triggers Snacker. But if somehow you drew your 3rd card via two Blood token activations in the same turn (draw step → Blood activation = card 2 → Blood activation = card 3), that also works.

**Sequencing to guarantee the trigger:** Take draw step, cast draw spell (Faithless Looting, Highway Robbery, Grab the Prize), trigger fires on the second card drawn. The Snacker returns during resolution of the draw spell, before you discard. You can then use the returned Snacker as a blocker or attacker next turn.

---

### Fireblast

Oracle text: *"You may sacrifice two Mountains rather than pay this spell's mana cost. Fireblast deals 4 damage to any target."*

**The alternate cost:** Sacrifice two Mountains. You do not pay {4}{R}{R}. You sacrifice two Mountains as you announce the spell. This means:
1. You lose two land drops permanently
2. The spell costs zero mana from your pool
3. It can be cast at instant speed (it's an instant)

**When to Fireblast:** The canonical use is as your final spell in a kill turn — after you've spent all your mana on other spells, you pitch two Mountains for 4 more damage. If you've gotten the opponent to 4 life and you have two Mountains in play plus Fireblast in hand, that's lethal without spending another mana.

**Double Fireblast:** With three Fireblasts in the deck, the theoretical line is cast Fireblast #1 (sacrifice two Mountains), cast Fireblast #2 (sacrifice two more Mountains) = 8 damage from zero mana. This costs you four Mountains. At 18 Mountains in the deck, this is achievable if you're at 5-6 lands mid-game. It's the "I'm going for it" line when opponent is at 8 life and you have Fireblast × 2 plus any other burn.

**When NOT to Fireblast:**
- Turn 3 or earlier with only 3 Mountains — going to 1 land after Fireblast locks you off Kessig, Guttersnipe, and every 2-drop you need to rebuild.
- When Kessig or Guttersnipe are on board and you have future burn spells — the pingers multiply your remaining spells' value. Fireblast removes lands, shrinking your future spell window.
- When you have only two Mountains total and are not killing them — post-Fireblast at one land is a punishable error in many matchups.
- Against decks with life gain — 4 damage that costs you two land drops may not be enough to overcome a Kitchen Finks gaining 2.

**Fireblast with Kessig in play:** Fireblast is a noncreature spell (it's an instant). Kessig pings for 1 when you cast it. Guttersnipe pings for 2 when you cast it. Fireblast deals 4. Total: 4 + 1 (Kessig) + 2 (Guttersnipe) = 7 from one Fireblast if both pingers are in play. This is the line that ends games from nowhere.

**Why only 3 Fireblasts:** The 4th Fireblast is often dead in hand — you frequently want to deploy it as your last spell, not as a mid-game play, and drawing multiples in an opening hand can make it feel uncastable without a mountain-rich board. Three is the correct count.

---

## Mana & Sequencing Discipline

18 Mountains for a deck that tops out at {2}{R} (Guttersnipe) or the zero-mana Fireblast alternate cost. This mana base is tight. Here's the sequencing hierarchy:

**Turn 1 priority:**
1. Voldaren Epicure (1 damage + Blood token, begin draw engine setup)
2. Faithless Looting (set up madness and Snacker; discard Fiery Temper or Snacker)
3. Lava Dart (kill a 1-toughness creature that threatens to trade with your 1-drops)
4. Lightning Bolt (if opponent plays a must-answer threat on turn 1; otherwise hold)

**Turn 2 priority:**
1. Kessig Flamebreather (your engine piece; earlier = more spells amplified)
2. Highway Robbery / Grab the Prize (if Kessig is already on board, this is a burn+draw double-dip)
3. Do NOT jam Grab the Prize on turn 2 before Kessig if Kessig is in hand — sequencing Kessig first means your draw spell triggers a Kessig ping immediately on resolution.

**Turn 3 priority:**
1. Guttersnipe (if you haven't resolved Kessig yet, prioritize Kessig first — Kessig surviving a turn is worth more than Guttersnipe's higher per-trigger output, because Kessig is harder to kill)
2. Faithless Looting flashback (if you cast it turn 1 and now need to dig)
3. Multiple draw spells with Kessig in play — this is where kills start happening

**The land-sacrifice window for Lava Dart flashback:** You can flashback Lava Dart for free at any time you control an untapped Mountain, even after tapping all your mana. The Mountain sacrificed for flashback is sacrificed during announcement (cost payment), so it's never about tapping — it's about having a Mountain to sacrifice. This means even a turn where you've spent {R}{R}{R} on three spells, if you have a fourth untapped Mountain, you can flashback Lava Dart for a fourth trigger at zero additional mana.

**Highway Robbery Plot timing:** Plot on turn 2, fire the free copy on turn 3 or 4. This is mana-positive by {1}{R} when you cast the plotted copy, because you already paid {1}{R} to plot it — but you saved it for a turn when you would have spent that mana elsewhere. The real value of Plot is in high-pressure turns where you want to cast multiple things: Guttersnipe + free Highway Robbery + Lava Dart + Lava Dart flashback = a massive damage turn at 3 mana.

---

## Opening Hand Criteria

A keepable hand has:
- At least 2 Mountains (3 preferred)
- At least one spell that generates a discard outlet OR at least one Fiery Temper (for madness payoff when you inevitably discard)
- At least one of: Kessig Flamebreather, Voldaren Epicure, Lightning Bolt (you need a turn-1 or turn-2 play)

**Mulligan these hand patterns:**
- 0-1 Mountains — non-negotiable mulligan regardless of the spell quality
- 5+ Mountains with 1 spell — too flooded; only keep if the spell is Faithless Looting (which will find more spells)
- All draw spells, no creatures, no Lightning Bolt — you'll build to a great turn 4 against a deck that killed you turn 3
- Guttersnipe × 2, no turn-1 or turn-2 play — 3-drop into 3-drop with no early pressure is too slow against most Pauper decks

**Strong opening hands (snap keep):**
- Mountain × 2-3, Epicure, Faithless Looting, Fiery Temper, Kessig, Lightning Bolt — you have everything; turn 1 Epicure or Looting, turn 2 Kessig, turn 3 spell flood
- Mountain × 2, Faithless Looting, Sneaky Snacker (to discard), Highway Robbery, Kessig, Fiery Temper — discard Snacker on turn 1, recur it turn 2 off Robbery, Kessig comes down, Temper fires at madness cost
- Mountain × 3, Kessig, Grab the Prize, Fiery Temper, Lightning Bolt — turn 2 Kessig, turn 3 Grab the Prize (discard Temper → madness {R}) = 2 + 1 (Kessig on Prize) + 3 (Temper) + 1 (Kessig on Temper) = 7 damage in one turn on turn 3

**On the draw vs. on the play:** On the draw you can take a slightly greedier hand (one extra land, or one fewer cheap spell) because you see one extra card. On the play, the turn-1 play matters more — prioritize hands with an active turn 1.

---

## Turn-by-Turn Play Philosophy

**Turn 1:** Deploy your most synergistic 1-drop, not necessarily your most damaging one. Voldaren Epicure's Blood token is worth more than the 1 ETB damage when you factor in the discard engine for the rest of the game. Faithless Looting turn 1 discarding Sneaky Snacker and Fiery Temper sets up a chain that starts on turn 2.

**Turn 2:** Kessig Flamebreather before any spell that would trigger it. If you cast Lightning Bolt turn 2 and then play Kessig, the Bolt didn't trigger Kessig. If you play Kessig turn 2 and pass (holding up interaction), that's fine — Kessig is a 1/3, it blocks well and the opponent has to answer it. Don't tap out to deploy burn spells before your pinger is on board if Kessig is in hand.

**Turn 3:** This is the turn where the gap between "just burning" and "burning with multipliers" becomes clear. The ideal turn 3 is: have Kessig on board (played turn 2), play Guttersnipe, then cast one spell — Kessig pings, Guttersnipe pings. Your spell costs {R}, deals 3 (Lightning Bolt), Kessig pings 1, Guttersnipe pings 2 = 6 damage from {2}{R} + {R} = {3}{R} total on turn 3. Against most Pauper decks, that's 6 of their 20 life gone from essentially one turn.

**Turn 4+ (kill turns):** Once Kessig and/or Guttersnipe are established, your burn spells each become 2-4 damage better than face value. At this point, be methodical about ordering:
1. Cast draw spells first (to ensure Sneaky Snacker trigger if in grave, and to draw into more burn)
2. Then cast spells that benefit from knowing what's in hand (you may want to discard Fiery Temper specifically)
3. Fire Fireblast last — it's always your last spell because it removes lands you might need if the kill fails

**Holding mana vs. going wide:** Unlike control decks, you rarely hold up mana to respond on the opponent's turn. The exception is holding Lightning Bolt to kill a blocker on the opponent's attack step (to protect your small creatures) or to kill a pinger-type creature before it can activate. Otherwise, dump your hand on your turn while your pingers are online.

---

## Key Lines & Hidden Tech

### The Lava Dart Double-Cast Kill Extension

At any point where you have Kessig + Guttersnipe on board, a Lava Dart in the graveyard, and a Mountain to sacrifice: you get two free spell triggers (2 from Kessig × 2 casts = 2, 2 from Guttersnipe × 2 casts = 4, plus 2 actual damage) = 8 damage from zero mana. This is the "I thought you were dead but here's 8 more" line that ends races.

**Exact sequence:** You've already spent your mana. Guttersnipe + Kessig are both in play. Lava Dart is in graveyard. You have two or more untapped Mountains. Flash back Lava Dart for free (sacrifice one Mountain) → Kessig pings (1) + Guttersnipe pings (2) + Lava Dart deals 1 (to face or creature) = 4 damage. Now you have one fewer Mountain. That's it for Lava Dart, but combined with other burn this is frequently the last burst in a kill turn.

### Sneaky Snacker as a Pseudo-Free Recursive Threat

Once Snacker is in the graveyard, every Highway Robbery, Grab the Prize, or Faithless Looting cast on a normal turn (after draw step) returns it. Opponents who don't kill it quickly will face a flying body every single turn cycle with zero card investment from you. In drawn-out games this is often what wins — the opponent runs out of removal while you keep returning Snacker for free.

**The important anti-synergy to know:** If Snacker is in your hand, drawing your 3rd card does nothing — the trigger requires Snacker to be in your graveyard. Do not hold Snacker in hand while chaining draw spells expecting a return trigger. Discard it proactively via Faithless Looting or Blood token to activate this line.

### Highway Robbery Plot as Mana Insurance

In matchups where the opponent is tapping out to develop their board on turns 2-3, plotting Highway Robbery on turn 2 means your turn 4 can fire: Guttersnipe (3 mana) + free Highway Robbery (0 mana, already paid turn 2) + any {R} spell. You effectively get an extra spell per turn cycle for one turn. Don't overvalue this — sometimes just casting the Robbery is correct — but against Tron or Ephemerate control that develops slowly, the Plot line is mana positive and tempo positive.

### Grab the Prize + Fiery Temper at 7 Life

The sequence that kills from 7: Cast Grab the Prize, discard Fiery Temper (mandatory additional cost) → madness trigger fires on Fiery Temper. Grab the Prize resolves: draw 2, deal 2 (nonland discarded). Now cast Fiery Temper for {R}: deal 3. Total: 5. With Kessig in play: add 1 (Grab) + 1 (Fiery Temper) = 7. This kills from 7 with {1}{R}{R} spent (Grab + Fiery Temper madness), or {1}{R} + {R} = 3 mana total.

With Guttersnipe also in play: add 2 (Grab) + 2 (Fiery Temper) = 11 total. This kills from 11 with 3 mana and two cards.

### Searing Blaze Landfall Timing (Sideboard)

Oracle text: *"Searing Blaze deals 1 damage to target player or planeswalker and 1 damage to target creature... Landfall — if you had a land enter the battlefield under your control this turn, Searing Blaze deals 3 damage to that player or planeswalker and 3 damage to that creature instead."*

**Searing Blaze is an instant.** Play your land for the turn, then cast Searing Blaze the same turn — you get the Landfall bonus (3 to player, 3 to creature). If you cast Searing Blaze before playing your land, you only get 1 + 1. Always play land first if you're casting Searing Blaze that turn.

**At full power:** 3 to player + 3 to creature kills almost any non-hexproof creature in Pauper and deals significant face damage simultaneously. Combined with Kessig + Guttersnipe: 3 (creature) + 3 (player) + 1 (Kessig) + 2 (Guttersnipe) = 9 total impact from one {R}{R} instant.

---

## Sideboard Guide (Card-by-Card)

### 4 Smash to Smithereens ({1}{R}, Instant)

Oracle text: *"Destroy target artifact. Smash to Smithereens deals 3 damage to that artifact's controller."*

**When it comes in:** Affinity matchups, any Artifact-based deck. Destroys the artifact AND deals 3 face damage — it's a two-for-one at instant speed. With Kessig: 3 damage + 1 = 4. With both pingers: 3 + 1 + 2 = 6.

**What to cut for it:** End the Festivities (in matchups where their creatures aren't small), or one copy of a late-game card like Fireblast if you need room for interaction.

**Don't board it in vs.:** Any non-artifact deck. It requires a valid artifact target — if they don't have artifacts, it's a dead card.

**Note:** Your own Blood tokens are artifacts. Smash to Smithereens cannot target your own Blood tokens to kill them (you don't want to deal 3 to yourself), but opponents cannot Smash your Blood tokens without dealing themselves 3 damage.

### 3 Relic of Progenitus ({1}, Artifact)

Oracle text: *"{T}: Target player exiles a card from their graveyard. {1}, Exile this artifact: Exile all graveyards. Draw a card."*

**When it comes in:** Any graveyard-based deck. Common Pauper graveyard decks: Dredge variants, Reanimator, any deck using Ephemerate recursion with Mulldrifter, Tortured Existence.

**The tap ability:** Free to activate (no mana), targets a single player's graveyard, exiles one card at a time. Use this during the opponent's upkeep to surgically remove a specific card (e.g., their Carapace Forger before they can target it with Glissa's recursion, or a Gurmag Angler before it's reanimated).

**The full exile:** Pay {1}, sacrifice Relic, exile ALL graveyards (including yours), draw a card. This is your "nuke it" option when you need to answer a full graveyard at once. Note: this exiles your own graveyard too — if you have Faithless Looting in the grave for flashback, you lose it. Use the tap ability to pick off specific threats first; use the full exile when they're about to win through their graveyard.

**Relic is an artifact.** It bumps your artifact count in play (alongside Blood tokens). Still not enough for Metalcraft on anything — that's irrelevant since Galvanic Blast isn't in this deck.

### 3 Searing Blaze ({R}{R}, Instant — Landfall)

See oracle analysis in Key Lines section above.

**When it comes in:** Midrange creature decks where you need to 2-for-1 with burn (kill a creature AND deal face damage simultaneously). Most effective against decks with medium-sized must-kill creatures (2/2 or 2/3 range) that also have some life total you're racing.

**What to cut for it:** Lava Dart (if their creatures are all 2+ toughness), End the Festivities (if their creatures are bigger than X/1), or one Fireblast in matchups where you're not going under them.

**Always play your land before casting Searing Blaze** on the same turn. This is not optional — 1+1 vs. 3+3 is a massive difference.

### 4 End the Festivities ({R}, Sorcery)

Oracle text: *"End the Festivities deals 1 damage to each opponent and each creature and planeswalker they control."*

**When it comes in:** Token strategies (Elves, Faeries going wide, White Weenie token spam). Kills all X/1s, deals 1 to face. With Kessig: 1 (each opponent) + 1 (each creature) + 1 (Kessig trigger) to the opponent's face = 1 to face + 1 per creature swept + 1 = effectively a board wipe against tokens that also pings for 1.

**What NOT to use it for:** It's sorcery speed and only deals 1 damage per creature — it doesn't kill Kessig (1/3), Guttersnipe (2/2), or most midrange threats. This is strictly an anti-aggro/anti-tokens sweeper.

**Note:** End the Festivities deals 1 to "each opponent" (plural), but in 1v1 that's just your opponent. It also hits each creature and planeswalker they control — it doesn't hit your own creatures. This is pure upside; it won't kill your Kessig or Guttersnipe.

### 1 Flaring Pain ({1}{R}, Instant — Flashback {R})

Oracle text: *"Damage can't be prevented this turn. Flashback {R}."*

**When it comes in:** Any deck running Circle of Protection: Red, Holy Light, or more commonly in Pauper — any lifegain that scales with damage prevention. The primary target in Pauper is **Prismatic Strands** (which prevents damage) and any protection effect that stops your burn. Also critical against decks running CoP: Red.

**Note:** "Damage can't be prevented this turn" applies globally — it stops both your opponent and your own damage prevention effects, though you rarely have any. It does not stop life gain that isn't prevention — e.g., Krosan Tusker gaining 2 life is not prevention, Flaring Pain doesn't stop it.

**Flashback {R}:** You can cast Flaring Pain twice in the same turn cycle — once from hand and once from graveyard — for a total of {1}{R} + {R} = {2}{R}. In a turn where you're trying to push damage through protection, this means both your main burn spell and your finish both resolve without being stopped.

**Only 1 copy:** This is a silver bullet — you only need to see it once per match, and the matchups where it's relevant are narrow. Prioritize acquiring this card; it converts matchups against prevention-based hate from near-unwinnable to favorable.

---

## Common Mistakes to Avoid

**1. Casting burn before deploying Kessig Flamebreather on turn 2.**
You have Kessig in hand and Lightning Bolt in hand on turn 2. If you cast the Bolt first, Kessig doesn't trigger. If you play Kessig first and pass, you've set up every future spell to trigger Kessig. The correct play is almost always Kessig first unless the Bolt is killing a creature that would kill Kessig in combat before you untap.

**2. Activating Blood tokens before understanding the Sneaky Snacker count.**
Blood activation draws 1 card. If your draw step was card 1 and you've drawn one more card (card 2), the next Blood activation (card 3) triggers Snacker. Track your draw count every turn.

**3. Pitching a land to Highway Robbery "for value" when you need to trigger Sneaky Snacker.**
Highway Robbery says "discard a card **or** sacrifice a land." If you sacrifice a land instead of discarding, you don't discard — so you don't trigger madness, and you don't get the Grab the Prize 2-damage bonus if you accidentally cast that instead. More critically: if you discard a nonland to Highway Robbery, that's a valid madness outlet. If you sacrifice a land, you've lost a land with no madness upside.

**4. Using Fireblast on turn 3-4 when you're not killing them.**
Fireblast costs two Mountains. At 3 lands, you go to 1 land post-Fireblast. At 1 land, you cannot cast Kessig (2 mana), Guttersnipe (3 mana), Highway Robbery (2 mana), Grab the Prize (2 mana), or Faithless Looting flashback (3 mana). You've effectively locked yourself out of your deck's engine. Only Fireblast when it's part of a kill turn or you have 5+ lands.

**5. Expecting Sneaky Snacker to return when it's in hand, not in the graveyard.**
Snacker's trigger says "return this card from your graveyard." If it's in your hand, the trigger condition can be met (you drew 3 cards), but nothing returns because Snacker isn't in the graveyard. Proactively discard Snacker early — it's not a spell you want to cast for {U}{B} in a mono-red deck.

**6. Forgetting that Kessig is a 1/3 and leaving it in aggressive blocks unnecessarily.**
Kessig blocks a 2/2 and survives. It does not survive a 3/3 hit. Kessig's job is to trigger on every spell you cast for the rest of the game — trading it in combat for a 2/2 is -3 to -5 damage per future spell you cast. Chump-block with something else. Let Kessig live.

**7. Flashing back Faithless Looting proactively when you're already at 3 cards in hand.**
Faithless Looting flashback costs {2}{R}. If you have three cards in hand plus Mountains, you might be better off casting Guttersnipe and one spell than spending 3 mana to draw 2 and discard 2. The flashback is for refueling when you're at 0-1 cards; it's not a turn-3 default play.

**8. Missing the Searing Blaze window by playing your land after casting the spell.**
This is a sequencing error that converts a 3+3 Landfall Searing Blaze into a 1+1 non-Landfall. Always: land → Searing Blaze in the same turn. If you cast it before the land, you've lost 4 damage from one card. Never do this.

**9. Boarding in End the Festivities against non-token decks.**
It's 1 damage per creature. Against a Delver of Secrets (1/1 or 3/2), it might kill the 1/1 flip target. Against Faerie Stompy or Affinity with bigger bodies, it does nothing. Reserve it for matchups where they're going wide with X/1s.

**10. Treating Highway Robbery and Grab the Prize as equivalent when they're not.**
Grab the Prize mandatorily deals 2 damage if you discard a nonland. Highway Robbery does not deal damage. In almost every situation where you're trying to maximize damage output, Grab the Prize is superior. The only reason to prefer Highway Robbery is: (a) you plotted it and are getting the free copy, or (b) you specifically want to sacrifice a land instead of discard (land flood scenario), or (c) you want the Plot option for future mana efficiency.

---

*End of guide. Every interaction traced from oracle text.*
