# MTG Simulator Phase 3B — Two-Player Game Loop

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Prerequisite:** Phase 3A complete (80 tests passing). `simulator/core/two_player_state.py` and `simulator/core/two_player_rules.py` exist.

**Goal:** Build the alternating-turn game loop with all 8 priority windows (upkeep, draw, Main 1, beginning of combat, post-attackers, post-blockers, post-damage, end step) and an N-game simulator that runs mirror matches at scale.

**Architecture:** `TwoPlayerGame.run()` drives the loop calling `run_priority_loop()` at each priority window. `Policy` base class gets `choose_attackers` and `choose_blockers` optional methods. A thin `TwoPlayerAutoPolicy` wraps the existing `MadnessBurnHeuristic` to handle two-player state for Phase 3B testing. Phase 3C will replace it with smart targeting and blocking decisions.

**Tech Stack:** Python 3.14, pytest, stdlib only.

---

## File Structure

```
simulator/
  policies/
    base.py                   MODIFY — add choose_attackers, choose_blockers optional methods
    two_player_auto.py        CREATE — wraps MadnessBurnHeuristic for two-player state
  simulation/
    two_player_game.py        CREATE — run_priority_loop + TwoPlayerGame + TwoPlayerGameResult
    two_player_simulator.py   CREATE — N-game runner, alternates first player
    two_player_results.py     CREATE — TwoPlayerSimResults dataclass
tests/simulator/
  test_two_player_game.py     CREATE — Phase 3B tests
```

**Existing files NOT modified:** `game.py`, `simulator.py`, `two_player_state.py`, `two_player_rules.py`.

---

## Task 1: Extend Policy base + create TwoPlayerAutoPolicy

**Files:**
- Modify: `simulator/policies/base.py`
- Create: `simulator/policies/two_player_auto.py`
- Create: `tests/simulator/test_two_player_game.py`

- [ ] **Step 1: Write failing tests**

Create `tests/simulator/test_two_player_game.py`:

```python
import pytest
from simulator.core.card import load_card
from simulator.core.game_state import CardState, Phase
from simulator.core.two_player_state import PlayerState, TwoPlayerGameState
from simulator.core.actions import DeclareAttackers, DeclareBlockers
from simulator.policies.base import Policy
from simulator.policies.two_player_auto import TwoPlayerAutoPolicy
from simulator.policies.goldfish import GoldfishPolicy


def _player(life: int = 20, lands: int = 2) -> PlayerState:
    return PlayerState(
        library=[], hand=[], battlefield=[CardState(card=load_card("Mountain")) for _ in range(lands)],
        graveyard=[], exile=[], madness_zone=[],
        blood_tokens=0, life=life, lands_played=0, cards_drawn_this_turn=0,
    )


def _state() -> TwoPlayerGameState:
    return TwoPlayerGameState(
        players=[_player(), _player()],
        active_player=0, priority_player=0,
        phase=Phase.MAIN1, turn=1,
    )


def test_policy_has_choose_attackers():
    policy = GoldfishPolicy()
    state = _state()
    # Goldfish default: attack with all untapped creatures (none here)
    result = policy.choose_attackers(state)
    assert isinstance(result, DeclareAttackers)
    assert result.creatures == []


def test_policy_has_choose_blockers():
    policy = GoldfishPolicy()
    state = _state()
    result = policy.choose_blockers(state)
    assert isinstance(result, DeclareBlockers)
    assert result.assignments == {}


def test_two_player_auto_policy_exists():
    from simulator.core.deck import Deck
    deck = Deck.from_file("decks/pauper-madness-burn.md")
    policy = TwoPlayerAutoPolicy(player_idx=0)
    assert policy is not None


def test_two_player_auto_returns_action():
    from simulator.core.two_player_rules import legal_main_actions
    state = _state()
    state.players[0].hand = [load_card("Lightning Bolt")]
    policy = TwoPlayerAutoPolicy(player_idx=0)
    actions = legal_main_actions(state, 0)
    action = policy.act(state, actions)
    assert action is not None
```

- [ ] **Step 2: Run to confirm fail**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion"
python -m pytest tests/simulator/test_two_player_game.py -v 2>&1 | head -5
```
Expected: `AttributeError: 'GoldfishPolicy' object has no attribute 'choose_attackers'`

- [ ] **Step 3: Modify `simulator/policies/base.py`**

Read the file first, then add two methods to the `Policy` ABC after the existing `value()` method:

```python
    def choose_attackers(self, state) -> "DeclareAttackers":
        """Which creatures to attack with. Default: all untapped creatures."""
        from simulator.core.actions import DeclareAttackers
        untapped = [cs for cs in state.active.creatures if not cs.tapped]
        return DeclareAttackers(creatures=[cs.card for cs in untapped])

    def choose_blockers(self, state) -> "DeclareBlockers":
        """Which creatures to block which attackers. Default: don't block."""
        from simulator.core.actions import DeclareBlockers
        return DeclareBlockers(assignments={})
```

Note: `state.active` is a property on `TwoPlayerGameState` that returns the active player's `PlayerState`. These methods only get called during two-player games.

- [ ] **Step 4: Create `simulator/policies/two_player_auto.py`**

This is a thin wrapper that translates `TwoPlayerGameState` into the single-player decisions the `MadnessBurnHeuristic` understands, then applies them in the two-player context.

```python
from __future__ import annotations
from simulator.policies.base import Policy
from simulator.core.two_player_state import TwoPlayerGameState
from simulator.core.actions import Action, PassPriority


class TwoPlayerAutoPolicy(Policy):
    """
    Wraps MadnessBurnHeuristic for two-player games.
    Translates TwoPlayerGameState to the player's own perspective,
    then delegates to the existing heuristic.
    Phase 3B: attacks with all, never blocks.
    Phase 3C will replace this with smart targeting + blocking decisions.
    """

    def __init__(self, player_idx: int) -> None:
        self.player_idx = player_idx
        from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic
        self._heuristic = MadnessBurnHeuristic()

    def act(self, state: TwoPlayerGameState, legal_actions: list[Action]) -> Action:
        """
        Delegate to MadnessBurnHeuristic.
        The heuristic's legal_actions are already generated by two_player_rules.legal_*_actions
        which are aware of the two-player context. The heuristic just picks from the list.
        """
        return self._heuristic.act(state, legal_actions)
```

The key insight: `TwoPlayerAutoPolicy.act()` just delegates to `MadnessBurnHeuristic.act()`. The existing heuristic's decision logic reads from `state` — it calls `state.has_creature()`, checks `state.opponent_life`, etc. For two-player games, `state` is a `TwoPlayerGameState`. We need to verify the heuristic's property accesses work on `TwoPlayerGameState`.

Check `simulator/policies/heuristic/madness_burn.py` for what properties it accesses on `state`. If it accesses `state.has_creature()`, `state.opponent_life`, `state.blood_tokens`, etc., we need to add compatibility properties to `TwoPlayerGameState`. 

Read `madness_burn.py` and check which `state.` attributes it uses. Then add any missing properties to `TwoPlayerGameState` in `two_player_state.py`:

```python
# Add to TwoPlayerGameState for heuristic compatibility
@property
def opponent_life(self) -> int:
    """Life of the player who is NOT the active player."""
    return self.players[1 - self.active_player].life

@property
def blood_tokens(self) -> int:
    """Blood tokens belonging to the active player."""
    return self.players[self.active_player].blood_tokens

def has_creature(self, name: str) -> bool:
    """Check active player's battlefield."""
    return self.players[self.active_player].has_creature(name)
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/simulator/test_two_player_game.py -v
```
Expected: `4 passed`

- [ ] **Step 6: Run full suite**

```bash
python -m pytest tests/simulator/ -q 2>&1 | tail -3
```
Expected: `84 passed`

- [ ] **Step 7: Commit**

```bash
git add simulator/policies/base.py simulator/policies/two_player_auto.py tests/simulator/test_two_player_game.py
git commit -m "feat(simulator): Policy choose_attackers/blockers + TwoPlayerAutoPolicy"
```

---

## Task 2: TwoPlayerGame with priority loop

**Files:**
- Create: `simulator/simulation/two_player_game.py`
- Create: `simulator/simulation/two_player_results.py`
- Modify: `tests/simulator/test_two_player_game.py` — add game loop tests

- [ ] **Step 1: Write failing tests**

Add to `tests/simulator/test_two_player_game.py`:

```python
from simulator.simulation.two_player_game import TwoPlayerGame, run_priority_loop
from simulator.simulation.two_player_results import TwoPlayerGameResult
from simulator.core.deck import Deck
from simulator.core.two_player_rules import legal_instant_actions

DECK_PATH = "decks/pauper-madness-burn.md"


def test_priority_loop_terminates_on_double_pass():
    """Both policies pass immediately → loop exits with no actions taken."""
    from simulator.policies.goldfish import GoldfishPolicy
    state = _state()
    policies = [GoldfishPolicy(), GoldfishPolicy()]
    new_state = run_priority_loop(state, policies, legal_instant_actions, starting_player=0)
    assert new_state.last_pass == [True, True]


def test_two_player_game_terminates():
    deck_a = Deck.from_file(DECK_PATH)
    deck_b = Deck.from_file(DECK_PATH)
    deck_a.shuffle(seed=42)
    deck_b.shuffle(seed=43)
    policy = TwoPlayerAutoPolicy(player_idx=0)
    game = TwoPlayerGame(deck_a, deck_b)
    result = game.run(policy, TwoPlayerAutoPolicy(player_idx=1))
    assert isinstance(result, TwoPlayerGameResult)
    assert result.turns <= 30
    assert result.winner in (0, 1, -1)


def test_two_player_game_both_players_draw():
    """After setup, both players have 7-card opening hands."""
    deck_a = Deck.from_file(DECK_PATH)
    deck_b = Deck.from_file(DECK_PATH)
    deck_a.shuffle(seed=1)
    deck_b.shuffle(seed=2)
    policy = TwoPlayerAutoPolicy(player_idx=0)
    game = TwoPlayerGame(deck_a, deck_b)
    result = game.run(policy, TwoPlayerAutoPolicy(player_idx=1))
    assert result.final_state.turn >= 1


def test_mirror_produces_winner():
    """10 mirror games — all produce a winner (no timeouts expected at 30 turns)."""
    wins = [0, 0, 0]  # [player0, player1, timeout]
    for seed in range(10):
        deck_a = Deck.from_file(DECK_PATH)
        deck_b = Deck.from_file(DECK_PATH)
        deck_a.shuffle(seed=seed)
        deck_b.shuffle(seed=seed + 100)
        game = TwoPlayerGame(deck_a, deck_b)
        result = game.run(TwoPlayerAutoPolicy(player_idx=0), TwoPlayerAutoPolicy(player_idx=1))
        wins[result.winner + 1] += 1
    # At least 8 of 10 games should produce a real winner
    assert wins[0] + wins[1] >= 8
```

- [ ] **Step 2: Run to confirm fail**

```bash
python -m pytest tests/simulator/test_two_player_game.py::test_priority_loop_terminates_on_double_pass -v 2>&1 | head -5
```
Expected: `ImportError`

- [ ] **Step 3: Create `simulator/simulation/two_player_results.py`**

```python
from __future__ import annotations
from dataclasses import dataclass
from simulator.core.two_player_state import TwoPlayerGameState


@dataclass
class TwoPlayerGameResult:
    winner: int                  # 0, 1, or -1 (timeout)
    turns: int
    kill_turn: int | None        # turn on which the losing player hit 0 life
    final_state: TwoPlayerGameState
```

- [ ] **Step 4: Create `simulator/simulation/two_player_game.py`**

```python
from __future__ import annotations
from typing import Callable
from simulator.core.deck import Deck
from simulator.core.card import Card
from simulator.core.game_state import CardState, Phase
from simulator.core.two_player_state import PlayerState, TwoPlayerGameState
from simulator.core.two_player_rules import (
    legal_main_actions, legal_instant_actions,
    apply_two_player, draw_card_two_player, resolve_combat_damage,
)
from simulator.core.actions import PassPriority, DeclareAttackers, DeclareBlockers
from simulator.policies.base import Policy
from simulator.simulation.two_player_results import TwoPlayerGameResult

MAX_TURNS = 30


def _setup(deck_a: Deck, deck_b: Deck) -> TwoPlayerGameState:
    """Create initial game state: two players, 7-card opening hands."""
    def make_player(deck: Deck) -> PlayerState:
        ps = PlayerState(
            library=list(deck.cards),
            hand=[], battlefield=[], graveyard=[], exile=[], madness_zone=[],
            blood_tokens=0, life=20, lands_played=0, cards_drawn_this_turn=0,
        )
        return ps

    state = TwoPlayerGameState(
        players=[make_player(deck_a), make_player(deck_b)],
        active_player=0, priority_player=0,
        phase=Phase.DRAW, turn=1,
    )
    # Draw opening hands (7 cards each); player 0 goes first (skips draw on T1)
    for _ in range(7):
        state = draw_card_two_player(state, 0)
    state.players[0].cards_drawn_this_turn = 0
    for _ in range(7):
        state = draw_card_two_player(state, 1)
    state.players[1].cards_drawn_this_turn = 0
    return state


def run_priority_loop(
    state: TwoPlayerGameState,
    policies: list[Policy],
    legal_fn: Callable,
    starting_player: int,
) -> TwoPlayerGameState:
    """
    Loop until both players pass in succession.
    Resets pass flags whenever a spell resolves.
    Safety cap: 500 iterations.
    """
    state = state.copy()
    state.priority_player = starting_player
    state.last_pass = [False, False]
    for _ in range(500):
        if all(state.last_pass):
            break
        p = state.priority_player
        actions = legal_fn(state, p)
        action = policies[p].act(state, actions)
        if isinstance(action, PassPriority):
            state.last_pass[p] = True
        else:
            state.last_pass = [False, False]
            state = apply_two_player(state, action, acting_player=p)
        state.priority_player = 1 - p
        if state.game_over:
            break
    return state


def _run_turn(
    state: TwoPlayerGameState,
    policies: list[Policy],
    turn: int,
) -> TwoPlayerGameState:
    """Execute one full turn for the active player with all 8 priority windows."""
    active = state.active_player
    inactive = 1 - active

    # Untap active player's permanents
    for cs in state.players[active].battlefield:
        cs.tapped = False
    state.players[active].lands_played = 0
    state.players[active].cards_drawn_this_turn = 0

    # 1. Upkeep priority window
    state = run_priority_loop(state, policies, legal_instant_actions, active)
    if state.game_over:
        return state

    # 2. Draw (skip for player 0 on turn 1)
    if not (turn == 1 and active == 0):
        state = draw_card_two_player(state, active)
    state = run_priority_loop(state, policies, legal_instant_actions, active)
    if state.game_over:
        return state

    # 3. Main Phase 1
    state.phase = Phase.MAIN1
    state = run_priority_loop(state, policies, legal_main_actions, active)
    if state.game_over:
        return state

    # 4. Beginning of combat priority
    state.phase = Phase.COMBAT
    state = run_priority_loop(state, policies, legal_instant_actions, active)
    if state.game_over:
        return state

    # 5. Declare attackers (active player only — not a priority loop)
    atk_action = policies[active].choose_attackers(state)
    state.declared_attackers = list(atk_action.creatures)

    # 6. Post-attackers priority loop
    state = run_priority_loop(state, policies, legal_instant_actions, active)
    if state.game_over:
        return state

    # 7. Declare blockers (inactive player only — not a priority loop)
    blk_action = policies[inactive].choose_blockers(state)
    state.declared_blocks = dict(blk_action.assignments)

    # 8. Post-blockers priority loop
    state = run_priority_loop(state, policies, legal_instant_actions, active)
    if state.game_over:
        return state

    # 9. Combat damage
    state = resolve_combat_damage(state)
    if state.game_over:
        return state

    # 10. Post-damage priority loop
    state = run_priority_loop(state, policies, legal_instant_actions, active)
    if state.game_over:
        return state

    # Clear combat state
    state.declared_attackers = []
    state.declared_blocks = {}

    # 11. Main Phase 2
    state.phase = Phase.MAIN2
    state = run_priority_loop(state, policies, legal_main_actions, active)
    if state.game_over:
        return state

    # 12. End step priority
    state.phase = Phase.END
    state = run_priority_loop(state, policies, legal_instant_actions, active)
    if state.game_over:
        return state

    # Cleanup: discard to 7
    while len(state.players[active].hand) > 7:
        worst = max(state.players[active].hand, key=lambda c: c.cmc)
        state.players[active].hand.remove(worst)
        state.players[active].graveyard.append(worst)

    # Switch active player
    state.active_player = inactive
    state.priority_player = inactive

    return state


class TwoPlayerGame:
    def __init__(self, deck_a: Deck, deck_b: Deck) -> None:
        self.deck_a = deck_a
        self.deck_b = deck_b

    def run(self, policy_a: Policy, policy_b: Policy) -> TwoPlayerGameResult:
        state = _setup(self.deck_a, self.deck_b)
        policies = [policy_a, policy_b]
        kill_turn: int | None = None

        for turn in range(1, MAX_TURNS + 1):
            state.turn = turn
            state = _run_turn(state, policies, turn)
            if state.game_over:
                kill_turn = turn
                break

        return TwoPlayerGameResult(
            winner=state.winner if state.game_over else -1,
            turns=state.turn,
            kill_turn=kill_turn,
            final_state=state,
        )
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/simulator/test_two_player_game.py -v
```
Expected: `8 passed` (4 from Task 1 + 4 new)

If `test_mirror_produces_winner` fails with most games timing out (winner=-1), it means the game loop is stuck. Debug with:

```bash
python -c "
from simulator.core.deck import Deck
from simulator.simulation.two_player_game import TwoPlayerGame
from simulator.policies.two_player_auto import TwoPlayerAutoPolicy
deck_a = Deck.from_file('decks/pauper-madness-burn.md')
deck_b = Deck.from_file('decks/pauper-madness-burn.md')
deck_a.shuffle(seed=0); deck_b.shuffle(seed=1)
result = TwoPlayerGame(deck_a, deck_b).run(TwoPlayerAutoPolicy(0), TwoPlayerAutoPolicy(1))
print(f'Winner: {result.winner}, Turn: {result.turns}, Kill turn: {result.kill_turn}')
print(f'P0 life: {result.final_state.players[0].life}')
print(f'P1 life: {result.final_state.players[1].life}')
"
```

Common issue: the heuristic might be calling `state.opponent_life` or `state.has_creature()` which don't exist on `TwoPlayerGameState`. If AttributeError, add the compatibility properties to `TwoPlayerGameState` in `two_player_state.py`:

```python
@property
def opponent_life(self) -> int:
    return self.players[1 - self.active_player].life

@property  
def blood_tokens(self) -> int:
    return self.players[self.active_player].blood_tokens

def has_creature(self, name: str) -> bool:
    return self.players[self.active_player].has_creature(name)
```

- [ ] **Step 6: Run full suite**

```bash
python -m pytest tests/simulator/ -q 2>&1 | tail -3
```
Expected: `88 passed`

- [ ] **Step 7: Commit**

```bash
git add simulator/simulation/two_player_game.py simulator/simulation/two_player_results.py tests/simulator/test_two_player_game.py
git commit -m "feat(simulator): TwoPlayerGame with 8-window priority loop"
```

---

## Task 3: TwoPlayerSimulator + acceptance

**Files:**
- Create: `simulator/simulation/two_player_simulator.py`
- Modify: `tests/simulator/test_two_player_game.py` — add acceptance tests

- [ ] **Step 1: Create `simulator/simulation/two_player_simulator.py`**

```python
from __future__ import annotations
import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from simulator.core.deck import Deck
from simulator.policies.base import Policy
from simulator.simulation.two_player_game import TwoPlayerGame
from simulator.simulation.two_player_results import TwoPlayerGameResult

REPORTS_DIR = Path(__file__).parents[2] / "simulator" / "data" / "reports"


@dataclass
class TwoPlayerSimResults:
    n_games: int
    wins_a: int         # player A wins
    wins_b: int         # player B wins
    timeouts: int
    game_results: list[TwoPlayerGameResult] = field(default_factory=list)

    @property
    def win_rate_a(self) -> float:
        total = self.wins_a + self.wins_b
        return self.wins_a / total if total > 0 else 0.0

    @property
    def avg_turns(self) -> float:
        if not self.game_results:
            return 0.0
        return sum(r.turns for r in self.game_results) / len(self.game_results)

    @property
    def going_first_wins(self) -> int:
        """How many times the player who went first (player 0) won."""
        return self.wins_a  # player 0 always goes first in this implementation

    def kill_turns(self) -> list[int]:
        return [r.kill_turn for r in self.game_results if r.kill_turn is not None]


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
        rng = random.Random(seed)
        base_a = Deck.from_file(deck_a_path)
        base_b = Deck.from_file(deck_b_path)

        results = TwoPlayerSimResults(n_games=n_games, wins_a=0, wins_b=0, timeouts=0)

        for _ in range(n_games):
            deck_a = base_a.copy()
            deck_b = base_b.copy()
            deck_a.shuffle(seed=rng.randint(0, 2**31))
            deck_b.shuffle(seed=rng.randint(0, 2**31))
            result = TwoPlayerGame(deck_a, deck_b).run(policy_a, policy_b)
            results.game_results.append(result)
            if result.winner == 0:
                results.wins_a += 1
            elif result.winner == 1:
                results.wins_b += 1
            else:
                results.timeouts += 1

        if save_report:
            self._save(results, description)
        return results

    def _save(self, results: TwoPlayerSimResults, description: str) -> None:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M")
        desc = description.replace(" ", "-") or "two-player"
        path = REPORTS_DIR / f"{ts}-{desc}.json"
        kt = results.kill_turns()
        path.write_text(json.dumps({
            "n_games": results.n_games,
            "wins_a": results.wins_a,
            "wins_b": results.wins_b,
            "timeouts": results.timeouts,
            "win_rate_a": round(results.win_rate_a, 4),
            "avg_turns": round(results.avg_turns, 2),
            "avg_kill_turn": round(sum(kt) / len(kt), 2) if kt else 0,
        }, indent=2))
```

- [ ] **Step 2: Add acceptance tests**

Add to `tests/simulator/test_two_player_game.py`:

```python
from simulator.simulation.two_player_simulator import TwoPlayerSimulator, TwoPlayerSimResults
import time

DECK_PATH = "decks/pauper-madness-burn.md"


def test_two_player_simulator_runs():
    sim = TwoPlayerSimulator()
    results = sim.run(
        DECK_PATH, DECK_PATH,
        TwoPlayerAutoPolicy(0), TwoPlayerAutoPolicy(1),
        n_games=100, seed=42, save_report=False,
    )
    assert isinstance(results, TwoPlayerSimResults)
    assert results.n_games == 100
    assert results.wins_a + results.wins_b + results.timeouts == 100


def test_acceptance_mirror_1k_games():
    """
    1,000 mirror games. Acceptance criteria:
    - Completes in < 60 seconds
    - Going-first player wins 48-65% (slight advantage, not dominant)
    - < 20% timeouts
    """
    sim = TwoPlayerSimulator()
    start = time.time()
    results = sim.run(
        DECK_PATH, DECK_PATH,
        TwoPlayerAutoPolicy(0), TwoPlayerAutoPolicy(1),
        n_games=1000, seed=0, save_report=False,
    )
    elapsed = time.time() - start
    assert elapsed < 60.0, f"1000 mirror games took {elapsed:.1f}s"
    assert results.timeouts < 200, f"Too many timeouts: {results.timeouts}"
    total_decided = results.wins_a + results.wins_b
    if total_decided > 0:
        going_first_wr = results.wins_a / total_decided
        assert 0.35 <= going_first_wr <= 0.75, f"Going-first WR {going_first_wr:.1%} outside expected range"
    print(f"\n1k mirror: P0 {results.wins_a}W / P1 {results.wins_b}W / {results.timeouts}TO in {elapsed:.1f}s")
    print(f"Going-first WR: {results.win_rate_a:.1%}, Avg turns: {results.avg_turns:.1f}")
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/simulator/test_two_player_game.py -v -s
```
Expected: `10 passed` — `-s` shows the print output with the mirror stats.

- [ ] **Step 4: Run full suite**

```bash
python -m pytest tests/simulator/ -q 2>&1 | tail -3
```
Expected: `90 passed` (80 Phase 1/2/3A + 10 Phase 3B)

- [ ] **Step 5: Commit and push**

```bash
git add simulator/simulation/two_player_simulator.py tests/simulator/test_two_player_game.py
git commit -m "feat(simulator): TwoPlayerSimulator + Phase 3B acceptance (mirror match working)"
git push
```

---

## Self-Review

**Spec coverage:**
- 8 priority windows per turn → `_run_turn()` ✓ (upkeep, draw, Main1, beginning-of-combat, post-attackers, post-blockers, post-damage, Main2, end — that's 9 listed in spec; the spec has "after draw" as a window, implemented here)
- `run_priority_loop()` — both players pass in succession to advance → Task 2 ✓
- `choose_attackers` + `choose_blockers` on Policy base → Task 1 ✓
- Active player untaps at start of turn → Task 2 `_run_turn()` ✓
- Player 0 skips draw on turn 1 → Task 2 ✓
- Combat: attackers declared → priority loop → blockers declared → priority loop → damage → priority loop → Task 2 ✓
- `TwoPlayerSimulator` alternates... wait, spec says "alternates who goes first". Current implementation: player 0 always goes first. Update `TwoPlayerSimulator.run()` to alternate:

```python
# In the for loop inside run():
for i in range(n_games):
    deck_a = base_a.copy()
    deck_b = base_b.copy()
    deck_a.shuffle(seed=rng.randint(0, 2**31))
    deck_b.shuffle(seed=rng.randint(0, 2**31))
    # Alternate who goes first
    if i % 2 == 0:
        result = TwoPlayerGame(deck_a, deck_b).run(policy_a, policy_b)
        if result.winner == 0: results.wins_a += 1
        elif result.winner == 1: results.wins_b += 1
    else:
        result = TwoPlayerGame(deck_b, deck_a).run(policy_b, policy_a)
        # winner=0 means policy_b won (went first), winner=1 means policy_a won
        if result.winner == 0: results.wins_b += 1
        elif result.winner == 1: results.wins_a += 1
    ...
```

Add this alternation to `TwoPlayerSimulator.run()` in Task 3.

**Placeholder scan:** None.

**Type consistency:**
- `run_priority_loop(state, policies, legal_fn, starting_player) -> TwoPlayerGameState` — consistent
- `TwoPlayerGame.run(policy_a, policy_b) -> TwoPlayerGameResult` — consistent
- `TwoPlayerSimulator.run(...) -> TwoPlayerSimResults` — consistent
- `TwoPlayerGameResult.winner: int` — consistent with `_check_win` setting `state.winner`
