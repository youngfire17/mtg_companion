# MTG Simulator Phase 3 — Two-Player Mirror Match Design

**Date:** 2026-05-11  
**Owner:** Justin  
**Status:** Approved (brainstorming complete)

---

## Purpose

Build a full two-player game engine for the Pauper Madness Burn mirror match. The goal is discovering **optimal lines of play** in real matchups — when to race vs. kill creatures, when to hold mana for instants, when to trade vs. attack face. The priority system enables real resource management decisions: tapping out has a cost, holding up mana has a value, and the AI learns which is correct from evidence rather than intuition.

This is the foundation for Tier 3 (RL self-play): heuristic first, MCTS next, neural policy after. The priority windows built here are the decision points the RL agent will learn to optimize.

---

## Non-Goals (Phase 3)

- No instant-speed responses to spells on the stack (responding to opponent's Lightning Bolt with your own — too complex for Phase 3, deferred to Tier 3)
- No first strike, trample, protection, or other keyword interactions
- No multi-blocker damage assignment ordering (each attacker can only be blocked by one creature in Phase 3 for simplicity)
- No milling or alternate win conditions
- No sideboarding between games

---

## Architecture: Parallel System

**Phase 1/2 infrastructure is untouched.** All 60 existing tests keep passing. Two-player infrastructure is built alongside the goldfish system, not replacing it.

```
simulator/core/
  two_player_state.py      # NEW — TwoPlayerGameState + PlayerState
  two_player_rules.py      # NEW — rules engine for two-player games
simulator/simulation/
  two_player_game.py       # NEW — game loop with full priority system
  two_player_simulator.py  # NEW — N-game runner for 2-player matches
simulator/policies/
  heuristic/
    mirror_madness.py      # NEW — MirrorMadnessHeuristic (extends heuristic base)
tests/simulator/
  test_two_player.py       # NEW — Phase 3 tests
```

**Shared, unchanged:** `Card`, `Deck`, `CardState`, `Phase`, all Action types, `Policy` base class.

---

## Data Model

### `PlayerState` (`core/two_player_state.py`)

Complete game state for one player's side of the board.

```python
@dataclass
class PlayerState:
    library: list[Card]
    hand: list[Card]
    battlefield: list[CardState]      # CardState has card + tapped + counters
    graveyard: list[Card]
    exile: list[Card]
    madness_zone: list[Card]
    blood_tokens: int
    life: int
    lands_played: int
    cards_drawn_this_turn: int

    @property
    def untapped_lands(self) -> list[CardState]: ...
    @property
    def available_mana(self) -> int: ...           # count of untapped lands
    @property
    def mountains(self) -> list[CardState]: ...    # untapped Mountains
    @property
    def creatures(self) -> list[CardState]: ...
    def has_creature(self, name: str) -> bool: ...
    def copy(self) -> PlayerState: ...
```

### `TwoPlayerGameState` (`core/two_player_state.py`)

Unified game state that both players' policies can read.

```python
@dataclass
class TwoPlayerGameState:
    players: list[PlayerState]        # [player0, player1]
    active_player: int                # whose turn it is (0 or 1)
    priority_player: int              # who currently holds priority
    phase: Phase
    turn: int
    declared_attackers: list[Card]    # set during combat
    declared_blocks: dict[Card, Card] # blocker → attacker
    last_pass: list[bool]             # [p0_passed, p1_passed]
    game_over: bool
    winner: int                       # 0, 1, or -1 (timeout)

    @property
    def active(self) -> PlayerState: ...    # player whose turn it is
    @property
    def inactive(self) -> PlayerState: ...  # the other player
    @property
    def priority(self) -> PlayerState: ...  # who has priority now

    def copy(self) -> TwoPlayerGameState: ...
```

---

## Priority System (`simulation/two_player_game.py`)

One function drives all eight priority windows:

```python
def run_priority_loop(
    state: TwoPlayerGameState,
    policies: list[Policy],
    legal_fn: Callable[[TwoPlayerGameState, int], list[Action]],
) -> TwoPlayerGameState:
    """
    Loop until both players pass in succession.
    When a spell resolves, reset pass flags so both players get priority again.
    """
    state.last_pass = [False, False]
    for _ in range(500):  # safety cap
        if all(state.last_pass):
            break
        p = state.priority_player
        actions = legal_fn(state, p)
        action = policies[p].act(state, actions)
        if isinstance(action, PassPriority):
            state.last_pass[p] = True
            state.priority_player = 1 - p
        else:
            state.last_pass = [False, False]  # reset — other player can respond
            state = apply_two_player(state, action, acting_player=p)
            state.priority_player = 1 - p
        if state.game_over:
            break
    return state
```

### Eight priority windows per turn

| Step | Active first? | Sorceries allowed? |
|---|---|---|
| Upkeep | Yes | No |
| After draw | Yes | No |
| Main Phase 1 | Yes | Yes |
| Beginning of combat | Yes | No |
| After attackers declared | Active first | No |
| After blockers declared | Active first | No |
| After combat damage | Active first | No |
| Main Phase 2 | Yes | Yes |
| End step | Active first | No |

**Mana consequence:** A player can only cast instants during a priority window if they have untapped lands. Tapping out in Main 1 means no Bolt in the opponent's end step. This makes "hold up mana vs. play a spell" a real, consequential decision.

---

## Turn Structure (`simulation/two_player_game.py`)

```python
for turn in range(1, MAX_TURNS + 1):
    active = state.active_player
    inactive = 1 - active

    # Untap
    for cs in state.players[active].battlefield:
        cs.tapped = False

    # Upkeep — resolve triggers, then priority loop
    state = resolve_upkeep_triggers(state, active)
    state = run_priority_loop(state, policies, legal_instant_actions)
    if state.game_over: break

    # Draw (skip turn 1 on play)
    if not (turn == 1 and active == 0):
        state = draw_card_two_player(state, active)
    state = run_priority_loop(state, policies, legal_instant_actions)
    if state.game_over: break

    # Main Phase 1 (sorceries + instants)
    state.phase = Phase.MAIN1
    state.priority_player = active
    state = run_priority_loop(state, policies, legal_main_actions)
    if state.game_over: break

    # Combat
    state.phase = Phase.COMBAT

    # Beginning of combat priority (active first)
    state.priority_player = active
    state = run_priority_loop(state, policies, legal_instant_actions)
    if state.game_over: break

    # Declare attackers (active player only — not a priority loop)
    attackers_action = policies[active].choose_attackers(state)
    state.declared_attackers = attackers_action.creatures

    # Post-declare-attackers priority loop
    state.priority_player = active
    state = run_priority_loop(state, policies, legal_instant_actions)
    if state.game_over: break

    # Declare blockers (inactive player only — not a priority loop)
    blocks_action = policies[inactive].choose_blockers(state)
    state.declared_blocks = blocks_action.assignments

    # Post-declare-blockers priority loop
    state.priority_player = active
    state = run_priority_loop(state, policies, legal_instant_actions)
    if state.game_over: break

    # Assign combat damage
    state = resolve_combat_damage(state)
    if state.game_over: break

    # Post-damage priority loop
    state.priority_player = active
    state = run_priority_loop(state, policies, legal_instant_actions)
    if state.game_over: break

    # Clear combat state
    state.declared_attackers = []
    state.declared_blocks = {}

    # Main Phase 2 (sorceries + instants)
    state.phase = Phase.MAIN2
    state.priority_player = active
    state = run_priority_loop(state, policies, legal_main_actions)
    if state.game_over: break

    # End step priority
    state.phase = Phase.END
    state.priority_player = active
    state = run_priority_loop(state, policies, legal_instant_actions)
    if state.game_over: break

    # Cleanup: discard to 7, clear mana, switch active player
    while len(state.active.hand) > 7:
        worst = max(state.active.hand, key=lambda c: c.cmc)
        state.active.hand.remove(worst)
        state.active.graveyard.append(worst)

    state.active_player = inactive
    state.priority_player = inactive
    state.players[inactive].lands_played = 0
    state.players[inactive].cards_drawn_this_turn = 0
```

---

## Rules Engine (`core/two_player_rules.py`)

Two primary functions:

### `legal_main_actions(state, player_idx) -> list[Action]`

Generates all legal sorcery + instant speed actions for the given player. Same logic as Phase 1's `legal_actions()` but:
- Reads from `state.players[player_idx]` instead of a single GameState
- Adds targeting options for the OPPONENT's board (bolt their creatures)
- `CastSpell` now includes `target_player: int` and `target_card: Card | None`

### `legal_instant_actions(state, player_idx) -> list[Action]`

Generates only instant-speed actions (+ PassPriority). Filters legal_main_actions to instants only: Lightning Bolt, Lava Dart (+ flashback), Fiery Temper (from madness zone), Smash to Smithereens, Searing Blaze.

### `apply_two_player(state, action, acting_player) -> TwoPlayerGameState`

Applies an action and resolves effects against both players' states. Key additions over Phase 1:
- Damage from spells decrements the TARGET player's life (which may be the opponent)
- Pinger triggers (Kessig, Guttersnipe) deal to the opponent when acting player casts
- Sneaky Snacker trigger checks acting player's draw count
- Win condition: check both `state.players[0].life <= 0` and `state.players[1].life <= 0`

### `resolve_combat_damage(state) -> TwoPlayerGameState`

```
For each (blocker → attacker) pair in declared_blocks:
    attacker takes blocker.power damage
    blocker takes attacker.power damage
    if lethal damage: creature goes to graveyard

For each unblocked attacker:
    inactive_player.life -= attacker.power

Check win condition.
```

Lethal = damage >= toughness. No first strike, no trample in Phase 3.

---

## Policy Interface Extension

The existing `Policy.act(state, legal_actions) -> Action` remains unchanged for backward compatibility. Two new optional methods for two-player games:

```python
class Policy(ABC):
    def act(self, state, legal_actions: list[Action]) -> Action: ...
    def update(self, trajectory, reward): pass
    def value(self, state) -> float: return 0.0

    # NEW — optional, for two-player only
    def choose_attackers(self, state: TwoPlayerGameState) -> DeclareAttackers:
        """Which creatures to attack with. Default: attack with all."""
        untapped = [cs for cs in state.active.creatures if not cs.tapped]
        return DeclareAttackers(creatures=[cs.card for cs in untapped])

    def choose_blockers(self, state: TwoPlayerGameState) -> DeclareBlockers:
        """Which creatures to block which attackers. Default: don't block."""
        return DeclareBlockers(assignments={})
```

`GoldfishPolicy` uses the defaults (all attack, no blocks). `MirrorMadnessHeuristic` overrides both.

---

## MirrorMadnessHeuristic (`policies/heuristic/mirror_madness.py`)

Extends `MadnessBurnHeuristic` with three new decision domains:

### Targeting decisions (in `act()`)

When generating burn spell actions against an opponent with creatures on board, evaluate each target:

**Kill their Guttersnipe first** (2 damage/spell, multiplies all their future spells)  
**Kill their Kessig if:** we're behind on life AND they have active discard outlets (Kessig will fire 3+ times before they tap out)  
**Otherwise:** target face — racing is almost always correct if we're ahead or even

Rule: `kill_creature = pings_remaining > bolt_damage / 2` where `pings_remaining = len(opponent.hand)` (rough estimate: each card in hand is a potential future trigger). This overestimates but errs toward killing pingers, which is generally correct.

### Attack decisions (in `choose_attackers()`)

- Always attack with Sneaky Snacker (flying, difficult to block effectively)
- Attack with Kessig/Guttersnipe if: opponent has no untapped creatures that trade favorably, OR we're racing and willing to trade
- Hold back Kessig if: opponent is attacking with a creature we need to block, AND Kessig blocking prevents lethal
- Attack with Voldaren Epicure if: opponent has nothing to profitably block it

### Block decisions (in `choose_blockers()`)

- **Never block with Kessig Flamebreather** — future ping value exceeds damage prevented
- **Block with Sneaky Snacker** if: unblocked damage + opponent's remaining burn puts us in lethal range before our next turn, AND the trade is neutral or better
- **Block with Voldaren Epicure** only if: we die to the attack and have no other option, Blood token already activated

### Mana holding decision (in `act()`)

When the heuristic is considering the last spell it can cast in Main 1:
- Hold the final Mountain if: opponent has Kessig or Guttersnipe on board AND we have a Bolt/Lava Dart in hand (the instant window to kill it on their turn is worth more than the sorcery we'd cast now)
- Otherwise: tap out, trust the race

---

## Two-Player Simulator (`simulation/two_player_simulator.py`)

```python
class TwoPlayerSimulator:
    def run(
        self,
        deck_a_path: str,
        deck_b_path: str,
        policy_a: Policy,
        policy_b: Policy,
        n_games: int = 10_000,
        seed: int | None = None,
        save_report: bool = True,
        description: str = "",
    ) -> TwoPlayerSimResults:
        """Alternates who goes first (game 0: A first, game 1: B first, ...)."""
```

Results include:
- Overall win rate for player A
- Win rate when going first vs. going second (critical mirror stat)
- Average game length in turns
- Kill distribution by source (burn vs. creature damage vs. pinger damage)
- Most common winning board states

---

## Build Phases

### Phase 3A — Core data model + rules engine
- `core/two_player_state.py`: `PlayerState` + `TwoPlayerGameState`
- `core/two_player_rules.py`: `legal_main_actions`, `legal_instant_actions`, `apply_two_player`, `resolve_combat_damage`
- Tests: state construction, copyability, basic action generation and application

### Phase 3B — Game loop
- `simulation/two_player_game.py`: full turn structure with all eight priority windows
- Tests: games terminate, both players draw and play, combat damage resolves correctly, Sneaky Snacker returns, Kessig fires, Fireblast works with alt cost

### Phase 3C — MirrorMadnessHeuristic
- `policies/heuristic/mirror_madness.py`: targeting, attacking, blocking, mana holding
- Tests: heuristic kills Guttersnipe before Kessig, holds mana with Bolt against their pinger, correct blocking decisions

### Phase 3D — Two-player simulator + acceptance
- `simulation/two_player_simulator.py`
- Run 10,000 mirror games, verify win rate for going-first player is 52-58% (slight advantage, not overwhelming)
- Verify game length is reasonable (6-15 turns for the mirror)

---

## Open Questions (resolved before Phase 3A plan)

1. **Madness timing in two-player**: when acting player discards to a discard outlet during their main phase, madness triggers fire immediately (same as Phase 1). The inactive player does NOT get priority to respond before madness resolution — madness cost replaces the discard, it's not a spell being cast onto the stack. **Resolved: madness works identically to Phase 1.**

2. **Sneaky Snacker draw count**: in two-player, the acting player's `cards_drawn_this_turn` counter still tracks their own draws. The inactive player's draws happen on their own turn. Same trigger logic as Phase 1. **Resolved: no changes needed.**

4. **`DeclareBlockers` action type**: Phase 3A must add `DeclareBlockers(assignments: dict[Card, Card])` to `core/actions.py`. This is the only new action type Phase 3 requires. **Resolved: add in Phase 3A alongside `TwoPlayerGameState`.**

5. **Both players die simultaneously**: if combat damage kills both players (mutual unblocked lethal), the active player wins (they dealt damage first, same as MTG rules). **Resolved: active player wins ties.**
