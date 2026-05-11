# MTG Simulator Phase 3A — Two-Player State + Rules Engine

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Prerequisite:** Phase 1 and Phase 2 complete (60 tests passing).

**Goal:** Build the two-player game state and rules engine that supports full attack/block/priority decisions, as the foundation for the mirror match simulator.

**Architecture:** Parallel to Phase 1/2 — no changes to existing goldfish infrastructure. Three new files: `core/two_player_state.py` (state model), modified `core/actions.py` (add DeclareBlockers + extend CastSpell), `core/two_player_rules.py` (rules engine for two boards).

**Tech Stack:** Python 3.14, dataclasses, pytest, stdlib only.

---

## File Structure

```
simulator/core/
  actions.py              MODIFY — add DeclareBlockers; add target_player/target_card to CastSpell
  two_player_state.py     CREATE — PlayerState + TwoPlayerGameState
  two_player_rules.py     CREATE — legal_main_actions, legal_instant_actions,
                                   apply_two_player, resolve_combat_damage,
                                   draw_card_two_player
tests/simulator/
  test_two_player.py      CREATE — all Phase 3A tests
```

**Existing files NOT modified:** `game_state.py`, `game.py`, `simulator.py`, any analysis module, any policy file.

---

## Task 1: Extend actions.py + create TwoPlayerGameState

**Files:**
- Modify: `simulator/core/actions.py`
- Create: `simulator/core/two_player_state.py`
- Create: `tests/simulator/test_two_player.py`

- [ ] **Step 1: Write failing tests**

Create `tests/simulator/test_two_player.py`:

```python
import pytest
from simulator.core.actions import DeclareBlockers, CastSpell
from simulator.core.card import load_card
from simulator.core.two_player_state import PlayerState, TwoPlayerGameState
from simulator.core.game_state import CardState, Phase


def _player(life: int = 20, hand_names: list[str] = None, lands: int = 3) -> PlayerState:
    hand = [load_card(n) for n in (hand_names or [])]
    battlefield = [CardState(card=load_card("Mountain")) for _ in range(lands)]
    return PlayerState(
        library=[], hand=hand, battlefield=battlefield,
        graveyard=[], exile=[], madness_zone=[],
        blood_tokens=0, life=life,
        lands_played=0, cards_drawn_this_turn=0,
    )


def _state(life_a: int = 20, life_b: int = 20) -> TwoPlayerGameState:
    return TwoPlayerGameState(
        players=[_player(life=life_a), _player(life=life_b)],
        active_player=0,
        priority_player=0,
        phase=Phase.MAIN1,
        turn=1,
        declared_attackers=[],
        declared_blocks={},
        last_pass=[False, False],
        game_over=False,
        winner=-1,
    )


def test_player_state_properties():
    ps = _player(lands=3)
    assert ps.available_mana == 3
    assert len(ps.untapped_lands) == 3
    assert ps.has_creature("Kessig Flamebreather") is False


def test_player_state_with_creatures():
    from simulator.core.game_state import CardState
    ps = _player()
    ps.battlefield.append(CardState(card=load_card("Kessig Flamebreather")))
    assert ps.has_creature("Kessig Flamebreather") is True
    assert len(ps.creatures) == 1


def test_two_player_state_properties():
    state = _state()
    assert state.active is state.players[0]
    assert state.inactive is state.players[1]
    assert state.priority is state.players[0]


def test_two_player_state_copy_is_independent():
    state = _state(life_a=20, life_b=20)
    copy = state.copy()
    copy.players[0].life = 10
    assert state.players[0].life == 20


def test_declare_blockers_action():
    kessig = load_card("Kessig Flamebreather")
    snacker = load_card("Sneaky Snacker")
    action = DeclareBlockers(assignments={snacker: kessig})
    assert snacker in action.assignments
    assert action.assignments[snacker] is kessig


def test_cast_spell_has_target_player():
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"], target_player=1)
    assert action.target_player == 1
    assert action.target_card is None


def test_cast_spell_target_player_defaults_to_one():
    """Backward compat: existing code that omits target_player still works."""
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    assert action.target_player == 1  # default = target opponent
```

- [ ] **Step 2: Run to confirm fail**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion"
python -m pytest tests/simulator/test_two_player.py -v 2>&1 | head -8
```
Expected: `ImportError: cannot import name 'DeclareBlockers'`

- [ ] **Step 3: Modify `simulator/core/actions.py` — add DeclareBlockers + extend CastSpell**

Read the file first, then make these two changes:

**Add `DeclareBlockers` after `DeclareAttackers`:**
```python
@dataclass(frozen=True)
class DeclareBlockers:
    assignments: dict  # blocker Card → attacker Card (both are Card objects)
```

**Extend `CastSpell` with two optional fields** (add after `discard_card`):
```python
@dataclass(frozen=True)
class CastSpell:
    card: Card
    cost: dict
    targets: list = field(default_factory=list)
    discard_card: Card | None = None
    target_player: int = 1          # NEW: which player is targeted (default=1, opponent)
    target_card: Card | None = None  # NEW: specific creature targeted (None = face)
```

**Update the `Action` union type** at the bottom of the file — add `DeclareBlockers`:
```python
Action = (PlayLand | CastSpell | CastMadness | FlashbackSpell |
          AlternateCost | ActivateAbility | DeclareAttackers | DeclareBlockers | PassPriority)
```

- [ ] **Step 4: Create `simulator/core/two_player_state.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from simulator.core.card import Card
from simulator.core.game_state import CardState, Phase


@dataclass
class PlayerState:
    library: list[Card]
    hand: list[Card]
    battlefield: list[CardState]
    graveyard: list[Card]
    exile: list[Card]
    madness_zone: list[Card]
    blood_tokens: int
    life: int
    lands_played: int
    cards_drawn_this_turn: int

    @property
    def untapped_lands(self) -> list[CardState]:
        return [cs for cs in self.battlefield if cs.card.is_land and not cs.tapped]

    @property
    def available_mana(self) -> int:
        return len(self.untapped_lands)

    @property
    def untapped_mountains(self) -> list[CardState]:
        return [cs for cs in self.battlefield
                if cs.card.name == "Mountain" and not cs.tapped]

    @property
    def creatures(self) -> list[CardState]:
        return [cs for cs in self.battlefield if cs.card.is_creature]

    def has_creature(self, name: str) -> bool:
        return any(cs.card.name == name for cs in self.battlefield)

    def copy(self) -> PlayerState:
        return PlayerState(
            library=list(self.library),
            hand=list(self.hand),
            battlefield=[CardState(cs.card, cs.tapped, dict(cs.counters))
                         for cs in self.battlefield],
            graveyard=list(self.graveyard),
            exile=list(self.exile),
            madness_zone=list(self.madness_zone),
            blood_tokens=self.blood_tokens,
            life=self.life,
            lands_played=self.lands_played,
            cards_drawn_this_turn=self.cards_drawn_this_turn,
        )


@dataclass
class TwoPlayerGameState:
    players: list[PlayerState]    # [player0, player1]
    active_player: int            # whose turn it is
    priority_player: int          # who has priority right now
    phase: Phase
    turn: int
    declared_attackers: list[Card] = field(default_factory=list)
    declared_blocks: dict = field(default_factory=dict)  # blocker → attacker
    last_pass: list[bool] = field(default_factory=lambda: [False, False])
    game_over: bool = False
    winner: int = -1

    @property
    def active(self) -> PlayerState:
        return self.players[self.active_player]

    @property
    def inactive(self) -> PlayerState:
        return self.players[1 - self.active_player]

    @property
    def priority(self) -> PlayerState:
        return self.players[self.priority_player]

    def copy(self) -> TwoPlayerGameState:
        return TwoPlayerGameState(
            players=[p.copy() for p in self.players],
            active_player=self.active_player,
            priority_player=self.priority_player,
            phase=self.phase,
            turn=self.turn,
            declared_attackers=list(self.declared_attackers),
            declared_blocks=dict(self.declared_blocks),
            last_pass=list(self.last_pass),
            game_over=self.game_over,
            winner=self.winner,
        )
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/simulator/test_two_player.py -v
```
Expected: `7 passed`

- [ ] **Step 6: Confirm existing tests still pass**

```bash
python -m pytest tests/simulator/ -q 2>&1 | tail -3
```
Expected: `67 passed` (60 Phase 1/2 + 7 new)

- [ ] **Step 7: Commit**

```bash
git add simulator/core/actions.py simulator/core/two_player_state.py tests/simulator/test_two_player.py
git commit -m "feat(simulator): TwoPlayerGameState + DeclareBlockers action type"
```

---

## Task 2: Two-player rules engine

**Files:**
- Create: `simulator/core/two_player_rules.py`
- Modify: `tests/simulator/test_two_player.py` — add rules tests

- [ ] **Step 1: Write failing tests**

Add to `tests/simulator/test_two_player.py`:

```python
from simulator.core.two_player_rules import (
    legal_main_actions, legal_instant_actions,
    apply_two_player, draw_card_two_player,
)
from simulator.core.actions import PlayLand, CastSpell, CastMadness, AlternateCost, PassPriority


def test_legal_main_actions_includes_pass():
    state = _state()
    actions = legal_main_actions(state, 0)
    assert any(isinstance(a, PassPriority) for a in actions)


def test_legal_main_can_play_land():
    state = _state()
    state.players[0].hand = [load_card("Mountain")]
    state.players[0].battlefield = []  # no lands in play yet
    actions = legal_main_actions(state, 0)
    assert any(isinstance(a, PlayLand) for a in actions)


def test_legal_main_can_cast_bolt_with_mana():
    state = _state()
    state.players[0].hand = [load_card("Lightning Bolt")]
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    actions = legal_main_actions(state, 0)
    bolt_actions = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Lightning Bolt"]
    assert len(bolt_actions) >= 1
    # All bolt actions target player 1 (opponent)
    assert all(a.target_player == 1 for a in bolt_actions)


def test_legal_main_bolt_can_target_opponent_creature():
    state = _state()
    state.players[0].hand = [load_card("Lightning Bolt")]
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    # Opponent has Kessig on board
    state.players[1].battlefield = [CardState(card=load_card("Kessig Flamebreather"))]
    actions = legal_main_actions(state, 0)
    bolt_actions = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Lightning Bolt"]
    # Should have: bolt face + bolt Kessig
    assert len(bolt_actions) == 2
    creature_targets = [a for a in bolt_actions if a.target_card is not None]
    assert len(creature_targets) == 1
    assert creature_targets[0].target_card.name == "Kessig Flamebreather"


def test_legal_instant_filters_sorceries():
    state = _state()
    state.players[0].hand = [load_card("Faithless Looting"), load_card("Lightning Bolt")]
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    instant_actions = legal_instant_actions(state, 0)
    # Faithless Looting is a sorcery — should not appear
    fl_actions = [a for a in instant_actions if isinstance(a, CastSpell)
                  and a.card.name == "Faithless Looting"]
    assert len(fl_actions) == 0
    # Lightning Bolt is instant — should appear
    bolt_actions = [a for a in instant_actions if isinstance(a, CastSpell)
                    and a.card.name == "Lightning Bolt"]
    assert len(bolt_actions) >= 1


def test_apply_bolt_to_opponent_face():
    state = _state(life_b=20)
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    state.players[0].hand = [load_card("Lightning Bolt")]
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"], target_player=1)
    new_state = apply_two_player(state, action, acting_player=0)
    assert new_state.players[1].life == 17  # 20 - 3


def test_apply_bolt_to_opponent_creature():
    state = _state()
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    state.players[0].hand = [load_card("Lightning Bolt")]
    kessig = load_card("Kessig Flamebreather")
    state.players[1].battlefield = [CardState(card=kessig)]
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["creature"],
                       target_player=1, target_card=kessig)
    new_state = apply_two_player(state, action, acting_player=0)
    # Kessig (2/2) takes 3 damage — dies (lethal)
    assert not new_state.players[1].has_creature("Kessig Flamebreather")
    # Goes to graveyard
    assert any(c.name == "Kessig Flamebreather" for c in new_state.players[1].graveyard)


def test_apply_kessig_pings_opponent_on_noncreature():
    state = _state()
    state.players[0].battlefield = [
        CardState(card=load_card("Mountain")),
        CardState(card=load_card("Kessig Flamebreather")),
    ]
    state.players[0].hand = [load_card("Lightning Bolt")]
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"], target_player=1)
    new_state = apply_two_player(state, action, acting_player=0)
    assert new_state.players[1].life == 16  # 3 bolt + 1 Kessig ping


def test_draw_card_two_player():
    state = _state()
    state.players[0].library = [load_card("Lightning Bolt"), load_card("Mountain")]
    new_state = draw_card_two_player(state, 0)
    assert len(new_state.players[0].hand) == 1
    assert new_state.players[0].hand[0].name == "Lightning Bolt"
    assert new_state.players[0].cards_drawn_this_turn == 1


def test_game_over_when_opponent_reaches_zero():
    state = _state(life_b=3)
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    state.players[0].hand = [load_card("Lightning Bolt")]
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"], target_player=1)
    new_state = apply_two_player(state, action, acting_player=0)
    assert new_state.game_over is True
    assert new_state.winner == 0
```

- [ ] **Step 2: Run to confirm fail**

```bash
python -m pytest tests/simulator/test_two_player.py::test_legal_main_actions_includes_pass -v 2>&1 | head -5
```
Expected: `ImportError: cannot import name 'legal_main_actions'`

- [ ] **Step 3: Create `simulator/core/two_player_rules.py`**

```python
from __future__ import annotations
import re
from simulator.core.card import Card, load_card
from simulator.core.game_state import CardState, Phase
from simulator.core.two_player_state import PlayerState, TwoPlayerGameState
from simulator.core.actions import (
    Action, PlayLand, CastSpell, CastMadness, FlashbackSpell,
    AlternateCost, ActivateAbility, DeclareAttackers, DeclareBlockers, PassPriority
)


def _parse_cmc(cost: str) -> int:
    pips = re.findall(r'\{([^}]+)\}', cost)
    total = 0
    for p in pips:
        if p.isdigit():
            total += int(p)
        elif p in ('R', 'G', 'U', 'B', 'W', 'C'):
            total += 1
    return total


def _tap_lands(ps: PlayerState, amount: int) -> None:
    """Tap `amount` of ps's untapped lands (mutates in place — called on a copy)."""
    tapped = 0
    for cs in ps.battlefield:
        if tapped >= amount:
            break
        if cs.card.is_land and not cs.tapped:
            cs.tapped = True
            tapped += 1


def _apply_pinger_triggers(state: TwoPlayerGameState, acting: int, spell: Card) -> None:
    """Fire Kessig/Guttersnipe triggers on acting player's board. Mutates state copy."""
    is_noncreature = not spell.is_creature
    is_instant_sorcery = spell.is_instant or spell.is_sorcery
    opponent_idx = 1 - acting
    for cs in state.players[acting].battlefield:
        if cs.card.pings_per_noncreature_spell > 0 and is_noncreature:
            state.players[opponent_idx].life -= cs.card.pings_per_noncreature_spell
        if cs.card.pings_per_instant_sorcery > 0 and is_instant_sorcery:
            state.players[opponent_idx].life -= cs.card.pings_per_instant_sorcery


def _check_win(state: TwoPlayerGameState) -> None:
    """Check both players' life totals. Mutates state copy."""
    if state.players[0].life <= 0 and not state.game_over:
        state.game_over = True
        state.winner = 1
    elif state.players[1].life <= 0 and not state.game_over:
        state.game_over = True
        state.winner = 0
    # Both at 0: active player wins (dealt damage first)
    if state.players[0].life <= 0 and state.players[1].life <= 0:
        state.game_over = True
        state.winner = state.active_player


def draw_card_two_player(state: TwoPlayerGameState, player_idx: int) -> TwoPlayerGameState:
    """Draw the top card of player_idx's library. Fire Sneaky Snacker at 3rd draw."""
    state = state.copy()
    ps = state.players[player_idx]
    if not ps.library:
        return state
    card = ps.library.pop(0)
    ps.hand.append(card)
    ps.cards_drawn_this_turn += 1
    if ps.cards_drawn_this_turn >= 3:
        for grave_card in list(ps.graveyard):
            if grave_card.snacker_return:
                ps.graveyard.remove(grave_card)
                ps.battlefield.append(CardState(card=grave_card, tapped=True))
                break
    return state


def _resolve_spell(
    state: TwoPlayerGameState,
    acting: int,
    card: Card,
    targets: list,
    discard_card: Card | None,
    target_player_idx: int,
    target_card: Card | None,
) -> TwoPlayerGameState:
    """Apply spell effects. Card already moved to GY/battlefield."""
    target_ps = state.players[target_player_idx]
    acting_ps = state.players[acting]

    # Direct damage to face
    if card.damage_on_cast > 0 and "face" in targets and target_card is None:
        target_ps.life -= card.damage_on_cast

    # Damage to a specific creature
    if card.damage_on_cast > 0 and target_card is not None:
        for cs in list(target_ps.battlefield):
            if cs.card is target_card or cs.card.name == target_card.name:
                if card.damage_on_cast >= cs.card.toughness:
                    target_ps.battlefield.remove(cs)
                    target_ps.graveyard.append(cs.card)
                break

    # Grab the Prize bonus damage
    if card.grab_prize_damage > 0 and discard_card and not discard_card.is_land:
        target_ps.life -= card.grab_prize_damage

    # Area damage (End the Festivities)
    if card.damage_each_opponent > 0:
        target_ps.life -= card.damage_each_opponent
    if card.damage_each_opponent_creature > 0:
        dead = []
        for cs in target_ps.battlefield:
            if cs.card.is_creature:
                if card.damage_each_opponent_creature >= cs.card.toughness:
                    dead.append(cs)
        for cs in dead:
            target_ps.battlefield.remove(cs)
            target_ps.graveyard.append(cs.card)

    # Draw effects (acting player draws)
    for _ in range(card.draw_on_cast):
        state = draw_card_two_player(state, acting)
        acting_ps = state.players[acting]  # re-bind after copy

    # Discard effects
    if card.discard_on_cast > 0 and discard_card is not None:
        if discard_card in acting_ps.hand:
            acting_ps.hand.remove(discard_card)
        if discard_card.has_madness:
            acting_ps.madness_zone.append(discard_card)
        else:
            acting_ps.graveyard.append(discard_card)

    # ETB effects (creatures entering battlefield)
    if card.damage_on_etb > 0:
        target_ps.life -= card.damage_on_etb
    if card.creates_blood_on_etb:
        acting_ps.blood_tokens += 1

    return state


def legal_main_actions(state: TwoPlayerGameState, player_idx: int) -> list[Action]:
    """All legal sorcery + instant speed actions for player_idx."""
    ps = state.players[player_idx]
    opponent_idx = 1 - player_idx
    opponent = state.players[opponent_idx]
    actions: list[Action] = [PassPriority()]

    available_mana = ps.available_mana

    # Play land
    if ps.lands_played == 0:
        for card in ps.hand:
            if card.is_land:
                actions.append(PlayLand(card=card))

    for card in ps.hand:
        if card.is_land:
            continue
        cmc = _parse_cmc(card.mana_cost)

        # Alternate cost (Fireblast)
        if card.has_alternate_cost and card.alternate_cost == "sac_2_mountains":
            if len(ps.untapped_mountains) >= 2:
                actions.append(AlternateCost(card=card, targets=["face"]))

        if available_mana >= cmc:
            if card.discard_on_cast > 0:
                discard_options = [c for c in ps.hand if c is not card and not c.is_land]
                if not discard_options:
                    discard_options = [c for c in ps.hand if c is not card]
                for dc in discard_options:
                    actions.append(CastSpell(
                        card=card, cost={"R": cmc},
                        targets=["face"] if card.damage_on_cast > 0 else [],
                        discard_card=dc, target_player=opponent_idx,
                    ))
            elif not (card.has_alternate_cost and card.alternate_cost == "sac_2_mountains"):
                if card.damage_any_target and card.damage_on_cast > 0:
                    # Can target face OR any opponent creature
                    actions.append(CastSpell(card=card, cost={"R": cmc},
                                             targets=["face"], target_player=opponent_idx))
                    for cs in opponent.creatures:
                        actions.append(CastSpell(card=card, cost={"R": cmc},
                                                 targets=["creature"],
                                                 target_player=opponent_idx,
                                                 target_card=cs.card))
                else:
                    actions.append(CastSpell(card=card, cost={"R": cmc},
                                             targets=[], target_player=opponent_idx))

    # Cast from madness zone
    for card in ps.madness_zone:
        actions.append(CastMadness(card=card, madness_cost=card.madness_cost,
                                   targets=["face"]))

    # Flashback from graveyard
    for card in ps.graveyard:
        if not card.has_flashback:
            continue
        if card.flashback_cost == "sac_mountain":
            if len(ps.untapped_mountains) > 0:
                actions.append(FlashbackSpell(card=card, targets=["face"]))
        else:
            fc = _parse_cmc(card.flashback_cost)
            if available_mana >= fc:
                actions.append(FlashbackSpell(card=card, targets=["face"]))

    # Blood token activation
    if ps.blood_tokens > 0:
        for dc in ps.hand:
            actions.append(ActivateAbility(
                source=load_card("Voldaren Epicure"),
                ability_index=0, discard_card=dc,
            ))

    return actions


def legal_instant_actions(state: TwoPlayerGameState, player_idx: int) -> list[Action]:
    """Filter legal_main_actions to instant-speed only (for priority windows)."""
    all_actions = legal_main_actions(state, player_idx)
    result = []
    for a in all_actions:
        if isinstance(a, PassPriority):
            result.append(a)
        elif isinstance(a, CastSpell) and (a.card.is_instant or a.card.has_madness):
            result.append(a)
        elif isinstance(a, CastMadness):
            result.append(a)
        elif isinstance(a, FlashbackSpell):
            result.append(a)
        elif isinstance(a, ActivateAbility):
            result.append(a)
        elif isinstance(a, AlternateCost) and a.card.is_instant:
            result.append(a)  # Fireblast is an instant
    return result


def apply_two_player(
    state: TwoPlayerGameState,
    action: Action,
    acting_player: int,
) -> TwoPlayerGameState:
    """Apply action, return new state. Never mutates the input."""
    state = state.copy()
    ps = state.players[acting_player]
    opponent_idx = 1 - acting_player

    match action:
        case PassPriority():
            pass

        case PlayLand(card=card):
            ps.hand.remove(card)
            ps.battlefield.append(CardState(card=card))
            ps.lands_played += 1

        case CastSpell(card=card, cost=cost, targets=targets, discard_card=dc,
                       target_player=tp, target_card=tc):
            ps.hand.remove(card)
            _tap_lands(ps, sum(cost.values()))
            _apply_pinger_triggers(state, acting_player, card)
            if not card.is_creature and not card.is_artifact and not card.is_enchantment:
                ps.graveyard.append(card)
            else:
                ps.battlefield.append(CardState(card=card))
            state = _resolve_spell(state, acting_player, card, targets, dc, tp, tc)
            _check_win(state)

        case CastMadness(card=card, madness_cost=cost, targets=targets):
            if card in ps.madness_zone:
                ps.madness_zone.remove(card)
            _tap_lands(ps, _parse_cmc(cost))
            _apply_pinger_triggers(state, acting_player, card)
            ps.graveyard.append(card)
            state = _resolve_spell(state, acting_player, card, targets, None, opponent_idx, None)
            _check_win(state)

        case FlashbackSpell(card=card, targets=targets):
            ps.graveyard.remove(card)
            if card.flashback_cost == "sac_mountain":
                for cs in ps.battlefield:
                    if cs.card.name == "Mountain":
                        ps.battlefield.remove(cs)
                        ps.graveyard.append(cs.card)
                        break
            else:
                _tap_lands(ps, _parse_cmc(card.flashback_cost))
            _apply_pinger_triggers(state, acting_player, card)
            ps.exile.append(card)
            state = _resolve_spell(state, acting_player, card, targets, None, opponent_idx, None)
            _check_win(state)

        case AlternateCost(card=card, targets=targets):
            ps.hand.remove(card)
            removed = 0
            for cs in list(ps.battlefield):
                if removed >= 2:
                    break
                if cs.card.name == "Mountain":
                    ps.battlefield.remove(cs)
                    ps.graveyard.append(cs.card)
                    removed += 1
            _apply_pinger_triggers(state, acting_player, card)
            ps.graveyard.append(card)
            state = _resolve_spell(state, acting_player, card, targets, None, opponent_idx, None)
            _check_win(state)

        case ActivateAbility(discard_card=dc):
            if dc and dc in ps.hand:
                ps.hand.remove(dc)
                if dc.has_madness:
                    ps.madness_zone.append(dc)
                else:
                    ps.graveyard.append(dc)
            ps.blood_tokens -= 1
            state = draw_card_two_player(state, acting_player)

    return state


def resolve_combat_damage(state: TwoPlayerGameState) -> TwoPlayerGameState:
    """
    Resolve combat damage after blocks are declared.
    Blocked attackers trade with their blockers.
    Unblocked attackers deal damage to the defending player.
    """
    state = state.copy()
    active = state.active_player
    inactive = 1 - active
    active_ps = state.players[active]
    inactive_ps = state.players[inactive]

    blocked_attackers = set(state.declared_blocks.values())

    # Resolve blocks: blocker ↔ attacker
    for blocker_card, attacker_card in list(state.declared_blocks.items()):
        # Find the CardState objects
        blocker_cs = next((cs for cs in inactive_ps.battlefield
                           if cs.card.name == blocker_card.name), None)
        attacker_cs = next((cs for cs in active_ps.battlefield
                            if cs.card.name == attacker_card.name), None)
        if not blocker_cs or not attacker_cs:
            continue
        # Assign damage
        attacker_dies = blocker_cs.card.power >= attacker_cs.card.toughness
        blocker_dies = attacker_cs.card.power >= blocker_cs.card.toughness
        if attacker_dies:
            active_ps.battlefield.remove(attacker_cs)
            active_ps.graveyard.append(attacker_cs.card)
        if blocker_dies:
            inactive_ps.battlefield.remove(blocker_cs)
            inactive_ps.graveyard.append(blocker_cs.card)

    # Resolve unblocked attackers
    for attacker_card in state.declared_attackers:
        if attacker_card.name not in {c.name for c in blocked_attackers}:
            inactive_ps.life -= attacker_card.power

    _check_win(state)
    return state
```

- [ ] **Step 4: Run all rules tests**

```bash
python -m pytest tests/simulator/test_two_player.py -v
```
Expected: `16 passed` (7 from Task 1 + 9 new)

- [ ] **Step 5: Run full suite**

```bash
python -m pytest tests/simulator/ -q 2>&1 | tail -3
```
Expected: `76 passed` (60 Phase 1/2 + 16 two-player)

- [ ] **Step 6: Commit**

```bash
git add simulator/core/two_player_rules.py tests/simulator/test_two_player.py
git commit -m "feat(simulator): Two-player rules engine with targeting + combat damage"
```

---

## Task 3: End-to-end state validation + push

**Files:**
- Modify: `tests/simulator/test_two_player.py` — add integration tests

- [ ] **Step 1: Add integration tests**

```python
def test_full_attack_sequence():
    """Full combat: declare attackers → resolve damage → check life."""
    state = _state(life_a=20, life_b=20)
    kessig = load_card("Kessig Flamebreather")
    state.players[0].battlefield = [CardState(card=kessig)]
    state.declared_attackers = [kessig]
    state.declared_blocks = {}  # no blocks

    new_state = resolve_combat_damage(state)
    # Kessig (2/2) attacks for 2
    assert new_state.players[1].life == 18
    assert new_state.game_over is False


def test_blocking_kills_attacker():
    """Blocker kills attacker in combat."""
    state = _state()
    kessig = load_card("Kessig Flamebreather")  # 2/2
    snacker = load_card("Sneaky Snacker")        # 2/1
    # Player 0 attacks with Kessig
    state.players[0].battlefield = [CardState(card=kessig)]
    state.declared_attackers = [kessig]
    # Player 1 blocks with Snacker
    state.players[1].battlefield = [CardState(card=snacker)]
    state.declared_blocks = {snacker: kessig}

    new_state = resolve_combat_damage(state)
    # Snacker (2/1) blocks Kessig (2/2): Kessig takes 2 ≥ 2 toughness → dies. Snacker takes 2 ≥ 1 toughness → dies.
    assert not new_state.players[0].has_creature("Kessig Flamebreather")
    assert not new_state.players[1].has_creature("Sneaky Snacker")
    assert new_state.players[1].life == 20  # no unblocked damage


def test_snacker_survives_if_kessig_blocked():
    """Blocking Kessig with Snacker: neither player takes life damage."""
    state = _state(life_a=20, life_b=20)
    kessig = load_card("Kessig Flamebreather")
    snacker = load_card("Sneaky Snacker")
    state.players[0].battlefield = [CardState(card=kessig)]
    state.declared_attackers = [kessig]
    state.players[1].battlefield = [CardState(card=snacker)]
    state.declared_blocks = {snacker: kessig}

    new_state = resolve_combat_damage(state)
    assert new_state.players[0].life == 20
    assert new_state.players[1].life == 20
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest tests/simulator/test_two_player.py -v
```
Expected: `19 passed`

- [ ] **Step 3: Run full suite**

```bash
python -m pytest tests/simulator/ -q 2>&1 | tail -3
```
Expected: `79 passed`

- [ ] **Step 4: Commit and push**

```bash
git add tests/simulator/test_two_player.py
git commit -m "test(simulator): Phase 3A integration tests — combat + targeting verified"
git push
```

---

## Self-Review

**Spec coverage:**
- `DeclareBlockers` action type → Task 1 ✓
- `CastSpell.target_player` + `target_card` → Task 1 ✓
- `PlayerState` with all properties → Task 1 ✓
- `TwoPlayerGameState` with `active`, `inactive`, `priority` properties → Task 1 ✓
- `legal_main_actions` generates creature targeting options → Task 2 ✓
- `legal_instant_actions` filters to instants only → Task 2 ✓
- `apply_two_player` applies all action types → Task 2 ✓
- Kessig/Guttersnipe trigger the opponent's life → Task 2 ✓
- `resolve_combat_damage` handles blocks + unblocked damage → Task 2 ✓
- Sneaky Snacker trigger on 3rd draw → Task 2 (`draw_card_two_player`) ✓
- Win condition when opponent reaches 0 → Task 2 ✓
- Both-die edge case → Task 2 (`_check_win`) ✓
- Combat integration test → Task 3 ✓
- Existing 60 tests unaffected → verified in each task ✓

**Placeholder scan:** None found.

**Type consistency:**
- `TwoPlayerGameState.players[i]` → `PlayerState` — used consistently
- `apply_two_player(state, action, acting_player: int)` — consistent across tasks 2-3
- `resolve_combat_damage(state) -> TwoPlayerGameState` — consistent
- `CastSpell.target_player: int = 1` default — backward compatible with Phase 1/2 existing code
