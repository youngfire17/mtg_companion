# MTG Simulator — Design Spec

**Date:** 2026-05-11  
**Owner:** Justin  
**Status:** Approved (brainstorming complete)

---

## Purpose

A Magic: The Gathering game simulator living inside the MTG_Companion repo. Tier 1 is a goldfish/statistical simulator that answers deck construction and mulligan questions. Tier 2 adds heuristic opponent archetypes for matchup simulation. Tier 3 is reinforcement learning via self-play — the long-term goal where the AI discovers optimal lines through millions of games.

All three tiers share the same game engine. Only the policy changes. The architecture is designed so Tier 3 is an extension, not a rewrite.

## Interaction Model

Justin asks a natural language question in Claude Code. Claude calls the simulator inline via Bash, reads the output, and summarizes in chat. Detailed results are saved to `simulator/data/reports/` with timestamps.

Examples:
- *"What % of my opening hands are keepable?"* → hand quality analysis
- *"Is 4 Fireblast better than 3?"* → deck comparison, 10,000 games each
- *"Show me my kill curve"* → goldfish speed analysis
- *"What's my expected win rate in this meta?"* → meta EV with live meta fetch

No CLI, no UI. Just ask and get results.

---

## Architecture

Five layers, each independently testable, no circular dependencies:

```
simulator/
├── core/               # Card, Deck, GameState, Actions, Rules engine
├── policies/           # Player decision-making (heuristic → RL-ready)
│   └── archetypes/     # Per-opponent heuristics (Tier 2)
├── simulation/         # Game loop + N-game runner + results
├── analysis/           # Goldfish stats, hand quality, deck compare, meta EV
└── data/reports/       # Saved simulation outputs
```

**Design principle:** The game engine never knows what's making decisions. It presents legal actions; the policy picks one. Heuristic, MCTS, or neural net — same interface, same engine.

---

## Layer 1 — Core

### `core/card.py` — Card model

Loads from `library/cards/oracle.ndjson`. Immutable data object. Tags are parsed from oracle text via regex, with a hardcoded override dict for edge cases (Fireblast's mountain sacrifice cost, Sneaky Snacker's return trigger, etc.).

**Fields:**
```
name, mana_cost, cmc, type_line, oracle_text
colors, keywords, power, toughness

# Parsed tags
is_land, is_creature, is_instant, is_sorcery
has_madness, madness_cost          # "Madness {R}"
has_flashback, flashback_cost       # "Flashback {2}{R}"
has_alternate_cost, alternate_cost  # Fireblast "sac 2 Mountains"
pings_per_noncreature_spell: int    # Kessig (1), default 0
pings_per_instant_sorcery: int      # Guttersnipe (2), default 0
damage_on_etb: int                  # Epicure (1), Jagged Barrens (1)
creates_blood_on_etb: bool          # Epicure
snacker_return: bool                # Sneaky Snacker graveyard trigger
draw_on_cast: int                   # Highway Robbery (2), Grab the Prize (2)
grab_prize_damage: int              # 2 if nonland discarded (Grab the Prize)
```

Unknown cards raise a flag rather than silently doing nothing.

### `core/deck.py` — Deck

Loads from `decks/pauper-madness-burn.md` (or `.dek`). A list of Card objects with duplicates for 4-ofs. Supports shuffle, draw, copy, and loading by name from the decks directory.

### `core/game_state.py` — GameState

Dataclass representing complete game state. Designed to be:
- **Copyable** — for MCTS branching (`state.copy()`)
- **Serializable as a feature vector** — for neural net input (Tier 3)
- **Complete** — sufficient to determine all legal actions

```
library: List[Card]           # index 0 = top
hand: List[Card]
battlefield: List[CardState]  # card + tapped/untapped + counters
graveyard: List[Card]
exile: List[Card]
madness_zone: List[Card]      # discarded into exile, awaiting cast decision

mana_pool: Dict[str, int]     # {'R': 2}
lands_played: int
cards_drawn_this_turn: int    # Sneaky Snacker trigger counter
mountains_on_battlefield: int # fast lookup for Fireblast eligibility

turn: int
phase: Phase                  # DRAW, MAIN1, COMBAT, MAIN2, END
life: int
opponent_life: int
pending_triggers: List[Trigger]
active_player: int            # 0 or 1
```

### `core/actions.py` — Action types

```python
PlayLand(card)
CastSpell(card, cost, targets)
CastMadness(card, madness_cost, targets)      # from madness_zone
FlashbackSpell(card, cost, targets)            # from graveyard
AlternateCost(card, sacrifices, targets)       # Fireblast: sac 2 Mountains
ActivateAbility(card, ability_index, targets)  # Blood token, Relic
DeclareAttackers(creatures)
PassPriority
```

### `core/rules.py` — Rules engine

Two functions:

```python
def legal_actions(state: GameState) -> List[Action]:
    """Returns all valid actions in the current state."""

def apply(state: GameState, action: Action) -> GameState:
    """Applies action to state, returns new state. Fires triggered abilities."""
```

Rules implemented for Tier 1 (Madness Burn-specific, not the full comprehensive rules):
- Draw card (increment `cards_drawn_this_turn`, fire Sneaky Snacker at 3)
- Discard (check madness → madness_zone, or graveyard)
- Madness resolution window (cast or put to GY)
- Triggered ability queue (Kessig ping, Guttersnipe ping, Epicure ETB, Blood creation)
- Fireblast alternate cost (remove 2 Mountains from battlefield)
- Lava Dart flashback (remove 1 Mountain, cast from GY)
- Grab the Prize damage clause (2 damage if discarded card wasn't a land)
- Sneaky Snacker return (when `cards_drawn_this_turn` reaches 3, return from GY tapped)
- End of turn cleanup (discard to 7, clear mana pool)
- Win condition (opponent_life ≤ 0)

Extended in Tier 2 per-archetype as needed (Affinity's Metalcraft, Familiars' Snap loop, etc.).

---

## Layer 2 — Policies

### `policies/base.py` — The interface

```python
class Policy:
    def act(self, state: GameState, legal_actions: List[Action]) -> Action:
        """Given state and legal moves, return one action."""
        raise NotImplementedError

    def update(self, trajectory: List[Tuple[GameState, Action]], reward: float):
        """Called after game ends. Heuristics ignore. RL learns from it."""
        pass

    def value(self, state: GameState) -> float:
        """Estimate position quality. Used by MCTS and RL critics."""
        return 0.0
```

### Tier 1 policies

**`GoldfishPolicy`** — always passes. Do-nothing opponent for goldfish testing.

**`RandomPolicy`** — picks uniformly from legal actions. Sanity baseline. Also the starting point for RL self-play before any training.

**`MadnessBurnHeuristic`** — implements priority rules from the deck guide:
1. Play a land if possible
2. Cast Kessig Flamebreather if affordable and not already on battlefield
3. Trigger madness chains (discard outlet → madness card)
4. Cast Guttersnipe if affordable and Kessig is already in play
5. Cast draw spells (Grab the Prize > Highway Robbery when opponent ≤ 10 life)
6. Point burn at face
7. Fireblast if killing this turn (opponent_life ≤ 4 after other damage)
8. Pass

### Tier 2 policies

One file per archetype in `policies/archetypes/`. Each implements the same `Policy` interface. Testable independently against GoldfishPolicy to verify correct goldfish behavior before using in matchup simulation.

```
policies/archetypes/
  affinity.py       # Artifact lands → free creatures → Galvanic Blast
  familiars.py      # Sunscape Familiar → Snap/Archaeomancer loop T4
  elves.py          # Mana dorks → Priest → wide attack
  blue_terror.py    # Fill GY, drop Terror, hold counter mana
  ...
```

### Tier 3 policies (future)

**`MCTSPolicy`** — no training required. Runs N rollouts from current state using RandomPolicy, picks the action with best empirical win rate. Bridge between heuristic and neural.

**`NeuralPolicy`** — backed by a small neural net. Input: GameState serialized as feature vector (~100-200 floats: life totals, turn, cards in hand as one-hot over deck's unique card types, pingers on board, Snacker in GY, etc.). Output: probability distribution over legal actions + value estimate.

**Self-play training loop (~30 lines):**
```python
for iteration in range(n_iterations):
    trajectory, winner = game.run(policy_a, policy_b)
    policy_a.update(trajectory_a, reward=+1 if winner==0 else -1)
    policy_b.update(trajectory_b, reward=+1 if winner==1 else -1)
```

The neural net does not need to be large — Pauper card pools are small and specific matchup state spaces are tractable.

---

## Layer 3 — Simulation

### `simulation/game.py` — Game loop

Runs one game, returns a `GameResult` containing outcome, trajectory, and per-turn stats.

**Turn structure:**
1. Untap all permanents, refill mana
2. Upkeep — process upkeep triggers
3. Draw — draw 1 card (skip turn 1 on play), increment `cards_drawn_this_turn`
4. Main 1 — loop: `legal_actions(state)` → `policy.act()` → `rules.apply()` → process triggers; ends on `PassPriority`
5. Combat — declare attackers → opponent declares blockers → assign damage (goldfish: all attacks connect)
6. Main 2 — same loop as Main 1
7. End — discard to 7, clear mana pool, process end triggers
8. Win check — `opponent_life ≤ 0` → game over

**Priority (Tier 2):** After the active player acts, the inactive player gets a priority window. Policies expose `wants_priority(state) -> bool` (default: False). Only policies that explicitly want to respond get the window — keeps goldfish fast with no overhead.

**Turn limit:** 30 turns. Games exceeding this are logged as timeouts (not wins or losses). Prevents infinite loops in edge cases.

### `simulation/simulator.py` — N-game runner

```python
class Simulator:
    def run(
        self,
        deck_a: Deck,
        policy_a: Policy,
        deck_b: Deck = None,
        policy_b: Policy = None,          # None = GoldfishPolicy
        n_games: int = 10_000,
        collect_trajectories: bool = False, # True for RL training
        seed: int = None,
    ) -> SimulationResults:
```

**Speed target:** 10,000 goldfish games in under 3 seconds. Achieved by keeping game state as simple Python objects, avoiding unnecessary copies, and using `random.shuffle` for deck randomization.

### `simulation/results.py` — Results

```
SimulationResults:
  n_games, wins, losses, timeouts, win_rate

  # Kill speed
  kill_turn_distribution: Dict[int, int]
  avg_kill_turn: float
  kill_by_turn: Dict[int, float]       # cumulative P(kill by turn N)

  # Hand quality
  keepable_7, keepable_6, keepable_5: float

  # Comparison (when two variants run)
  variant_a_avg_kill, variant_b_avg_kill: float
  p_value: float

  # Optional: raw game logs for deep analysis
  game_logs: List[GameLog]
```

Results auto-save to `simulator/data/reports/YYYY-MM-DD-HH-MM-<description>.json`.

---

## Layer 4 — Analysis

### `analysis/hand_quality.py`

Evaluates N random 7-card draws against configurable keep criteria. Outputs P(keepable) at 7, 6, and 5 cards, with breakdown of failure modes (too few lands / no outlet / no action). Criteria are pluggable — test Justin's current threshold vs. stricter or more lenient versions.

### `analysis/goldfish.py`

Goldfish speed statistics with text-based kill curve visualization. Tracks card contribution breakdown (pingers vs. direct burn vs. creatures). Median and percentile kill turns.

### `analysis/deck_compare.py`

Runs two deck variants (same structure, different card counts) against the same opponent. Produces side-by-side kill turn comparison with statistical significance test. Answers "does this card swap actually matter?"

### `analysis/meta_ev.py`

```
EV = Σ (meta_share[deck] × win_rate[deck])
```

Takes win rates from simulation or from `library/logs/` batch data. Fetches live meta shares from MTGTop8 via WebFetch. Outputs current EV, per-matchup contribution, and EV delta for proposed changes ("adding 4x Pyroblast improves EV by +2.9 points").

---

## Build Phases

### Phase 1 — Core + Madness Burn goldfish (Tier 1)
- `core/` fully implemented (card tagging, game state, actions, rules for Madness Burn)
- `GoldfishPolicy` + `RandomPolicy` + `MadnessBurnHeuristic`
- `simulation/` game loop + runner + results
- `analysis/goldfish.py` + `analysis/hand_quality.py`
- **Acceptance:** 10,000 goldfish games run in < 3 seconds; kill curve output matches intuition (median kill turn ~5); hand quality numbers match manual probability calculation

### Phase 2 — Deck comparison + meta EV (Tier 1 complete)
- `analysis/deck_compare.py` + `analysis/meta_ev.py`
- **Acceptance:** can run "4x Fireblast vs 3x Fireblast" comparison and get statistically valid output; meta EV calculation matches hand-computed result for a known meta

### Phase 3 — First opponent archetype (Tier 2 begins)
- First archetype policy (likely Affinity — simplest decision tree)
- Extend rules engine with Affinity-specific rules (Metalcraft, artifact lands)
- **Acceptance:** Madness Burn Heuristic vs Affinity Heuristic runs 10,000 games; win rate is in the expected range (65-75%) based on our log data

### Phase 4 — MCTS + self-play infrastructure (Tier 3 foundation)
- `MCTSPolicy` (no training, just rollouts)
- Self-play training loop
- GameState serialization as feature vector
- **Acceptance:** MCTS policy beats RandomPolicy reliably; self-play loop runs without errors; feature vector captures all relevant state

### Phase 5 — Neural policy (Tier 3)
- `NeuralPolicy` with simple feedforward net (numpy or PyTorch)
- Train via self-play
- **Acceptance:** trained policy beats heuristic policy at > 55% win rate

---

## Open Questions (resolved before Phase 1 plan)

1. **Card tag parsing priority:** regex from oracle text or hardcoded dict first? Recommendation: hardcoded dict for the Madness Burn 75 (known, small), regex for unknown cards added later.
2. **Mana system depth:** does Phase 1 need to track colored mana specifically (R vs generic) or just total mana count? Recommendation: track colored mana — Madness Burn needs {R} for madness costs vs {1}{R} for spells.
3. **Dependencies:** stdlib + `random` only for Phase 1? Or allow `numpy` for speed? Recommendation: allow numpy — it's almost certainly already installed and the vectorized shuffle is faster.
