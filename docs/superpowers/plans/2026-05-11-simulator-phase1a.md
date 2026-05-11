# MTG Simulator Phase 1A — Core + Policies

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the core rules engine and policy layer for the Madness Burn goldfish simulator.

**Architecture:** Card model loads from oracle.ndjson with hardcoded tag overrides for the Madness Burn 75. GameState is a copyable dataclass. Rules engine is `legal_actions(state) -> List[Action]` and `apply(state, action) -> GameState`. Policy interface is `act(state, legal_actions) -> Action`.

**Tech Stack:** Python 3.14, numpy, pytest, stdlib (json, dataclasses, random, pathlib)

---

## File Structure

```
simulator/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── card.py
│   ├── deck.py
│   ├── game_state.py
│   ├── actions.py
│   └── rules.py
├── policies/
│   ├── __init__.py
│   ├── base.py
│   ├── goldfish.py
│   └── heuristic/
│       ├── __init__.py
│       └── madness_burn.py
tests/simulator/
├── __init__.py
├── test_card.py
├── test_rules.py
└── test_policies.py
```

All paths relative to `C:\Desktop\CLAUDE Projects\MTG_Companion`.

---

## Task 1: Project scaffold + Card model

**Files:**
- Create: `simulator/__init__.py`, `simulator/core/__init__.py`, `simulator/policies/__init__.py`, `simulator/policies/heuristic/__init__.py`, `simulator/simulation/__init__.py`, `simulator/analysis/__init__.py`
- Create: `simulator/core/card.py`
- Create: `tests/simulator/__init__.py`, `tests/simulator/test_card.py`

- [ ] **Step 1: Create all __init__.py files**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion"
mkdir -p simulator/core simulator/policies/heuristic simulator/simulation simulator/analysis simulator/data/reports
mkdir -p tests/simulator
touch simulator/__init__.py simulator/core/__init__.py
touch simulator/policies/__init__.py simulator/policies/heuristic/__init__.py
touch simulator/simulation/__init__.py simulator/analysis/__init__.py
touch tests/simulator/__init__.py
```

- [ ] **Step 2: Write failing test for Card**

Create `tests/simulator/test_card.py`:

```python
import pytest
from simulator.core.card import Card, load_card, CARD_OVERRIDES

def test_card_loads_from_oracle():
    card = load_card("Lightning Bolt")
    assert card.name == "Lightning Bolt"
    assert card.mana_cost == "{R}"
    assert card.cmc == 1
    assert card.is_instant is True
    assert card.is_land is False
    assert card.damage_on_cast == 3

def test_card_madness_tag():
    card = load_card("Fiery Temper")
    assert card.has_madness is True
    assert card.madness_cost == "{R}"
    assert card.damage_on_cast == 3

def test_card_kessig_tag():
    card = load_card("Kessig Flamebreather")
    assert card.pings_per_noncreature_spell == 1
    assert card.is_creature is True

def test_card_fireblast_alternate_cost():
    card = load_card("Fireblast")
    assert card.has_alternate_cost is True
    assert card.alternate_cost == "sac_2_mountains"
    assert card.damage_on_cast == 4

def test_card_mountain_is_land():
    card = load_card("Mountain")
    assert card.is_land is True

def test_card_sneaky_snacker():
    card = load_card("Sneaky Snacker")
    assert card.snacker_return is True
    assert card.is_creature is True

def test_unknown_card_raises():
    with pytest.raises(KeyError):
        load_card("Nonexistent Card That Does Not Exist")
```

- [ ] **Step 3: Run test to confirm it fails**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion"
python -m pytest tests/simulator/test_card.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'simulator'`

- [ ] **Step 4: Implement Card model**

Create `simulator/core/card.py`:

```python
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from functools import lru_cache

ORACLE_PATH = Path(__file__).parents[2] / "library" / "cards" / "oracle.ndjson"

CARD_OVERRIDES: dict[str, dict] = {
    "Faithless Looting": {
        "has_flashback": True, "flashback_cost": "{2}{R}",
        "draw_on_cast": 2, "discard_on_cast": 2,
    },
    "Highway Robbery": {
        "draw_on_cast": 2, "discard_on_cast": 1,
        "can_sac_land_instead": True,
    },
    "Grab the Prize": {
        "draw_on_cast": 2, "discard_on_cast": 1,
        "grab_prize_damage": 2,
    },
    "Lava Dart": {
        "damage_on_cast": 1, "damage_any_target": True,
        "has_flashback": True, "flashback_cost": "sac_mountain",
    },
    "Lightning Bolt": {"damage_on_cast": 3, "damage_any_target": True},
    "Fiery Temper": {
        "damage_on_cast": 3, "damage_any_target": True,
        "has_madness": True, "madness_cost": "{R}",
    },
    "Fireblast": {
        "damage_on_cast": 4, "damage_any_target": True,
        "has_alternate_cost": True, "alternate_cost": "sac_2_mountains",
    },
    "Kessig Flamebreather": {"pings_per_noncreature_spell": 1},
    "Guttersnipe": {"pings_per_instant_sorcery": 2},
    "Voldaren Epicure": {"damage_on_etb": 1, "creates_blood_on_etb": True},
    "Sneaky Snacker": {"snacker_return": True},
    "Mountain": {},
    "Smash to Smithereens": {"damage_on_cast": 3, "destroys_artifact": True},
    "Relic of Progenitus": {},
    "Searing Blaze": {
        "damage_on_cast": 1, "damage_to_creature": 1, "has_landfall": True,
        "landfall_damage_on_cast": 3, "landfall_damage_to_creature": 3,
    },
    "End the Festivities": {
        "damage_each_opponent": 1, "damage_each_opponent_creature": 1,
    },
    "Flaring Pain": {
        "prevents_damage_prevention": True,
        "has_flashback": True, "flashback_cost": "{R}",
    },
}


@dataclass(frozen=True)
class Card:
    name: str
    mana_cost: str
    cmc: int
    type_line: str
    oracle_text: str
    # parsed types
    is_land: bool = False
    is_creature: bool = False
    is_instant: bool = False
    is_sorcery: bool = False
    is_artifact: bool = False
    is_enchantment: bool = False
    # combat
    power: int = 0
    toughness: int = 0
    # madness / flashback / alternate costs
    has_madness: bool = False
    madness_cost: str = ""
    has_flashback: bool = False
    flashback_cost: str = ""
    has_alternate_cost: bool = False
    alternate_cost: str = ""
    can_sac_land_instead: bool = False
    # damage tags
    damage_on_cast: int = 0
    damage_any_target: bool = False
    damage_on_etb: int = 0
    damage_each_opponent: int = 0
    damage_each_opponent_creature: int = 0
    damage_to_creature: int = 0
    has_landfall: bool = False
    landfall_damage_on_cast: int = 0
    landfall_damage_to_creature: int = 0
    # draw / discard
    draw_on_cast: int = 0
    discard_on_cast: int = 0
    grab_prize_damage: int = 0
    # trigger tags
    pings_per_noncreature_spell: int = 0
    pings_per_instant_sorcery: int = 0
    creates_blood_on_etb: bool = False
    snacker_return: bool = False
    # misc
    destroys_artifact: bool = False
    prevents_damage_prevention: bool = False


@lru_cache(maxsize=None)
def _load_oracle() -> dict[str, dict]:
    oracle: dict[str, dict] = {}
    with ORACLE_PATH.open(encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            oracle[data["name"]] = data
    return oracle


def load_card(name: str) -> Card:
    oracle = _load_oracle()
    if name not in oracle and name not in CARD_OVERRIDES:
        raise KeyError(f"Card not found in oracle or overrides: {name!r}")

    raw = oracle.get(name, {})
    overrides = CARD_OVERRIDES.get(name, {})

    type_line = raw.get("type_line", "")
    pt = raw.get("power", "0"), raw.get("toughness", "0")

    def safe_int(v: str) -> int:
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    return Card(
        name=name,
        mana_cost=raw.get("mana_cost", ""),
        cmc=int(raw.get("cmc", 0)),
        type_line=type_line,
        oracle_text=raw.get("oracle_text", ""),
        is_land="Land" in type_line,
        is_creature="Creature" in type_line,
        is_instant="Instant" in type_line,
        is_sorcery="Sorcery" in type_line,
        is_artifact="Artifact" in type_line,
        is_enchantment="Enchantment" in type_line,
        power=safe_int(pt[0]),
        toughness=safe_int(pt[1]),
        **overrides,
    )
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
cd "C:/Desktop/CLAUDE Projects/MTG_Companion"
python -m pytest tests/simulator/test_card.py -v
```

Expected: `7 passed`

- [ ] **Step 6: Commit**

```bash
git add simulator/ tests/simulator/
git commit -m "feat(simulator): scaffold + Card model with Madness Burn tag overrides"
```

---

## Task 2: Deck loading

**Files:**
- Create: `simulator/core/deck.py`
- Modify: `tests/simulator/test_card.py` → add deck tests (or create `tests/simulator/test_deck.py`)

- [ ] **Step 1: Write failing test**

Create `tests/simulator/test_deck.py`:

```python
import pytest
from simulator.core.deck import Deck

DECK_PATH = "decks/pauper-madness-burn.md"

def test_deck_loads_60_cards():
    deck = Deck.from_file(DECK_PATH)
    assert len(deck.cards) == 60

def test_deck_has_mountains():
    deck = Deck.from_file(DECK_PATH)
    mountains = [c for c in deck.cards if c.name == "Mountain"]
    assert len(mountains) == 18

def test_deck_has_4_lightning_bolts():
    deck = Deck.from_file(DECK_PATH)
    bolts = [c for c in deck.cards if c.name == "Lightning Bolt"]
    assert len(bolts) == 4

def test_deck_copy_is_independent():
    deck = Deck.from_file(DECK_PATH)
    copy = deck.copy()
    copy.cards.pop()
    assert len(deck.cards) == 60

def test_deck_draw_removes_from_library():
    deck = Deck.from_file(DECK_PATH)
    deck.shuffle(seed=42)
    top = deck.cards[0]
    drawn = deck.draw()
    assert drawn.name == top.name
    assert len(deck.cards) == 59
```

- [ ] **Step 2: Run to confirm fail**

```bash
python -m pytest tests/simulator/test_deck.py -v 2>&1 | head -5
```
Expected: `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Implement Deck**

Create `simulator/core/deck.py`:

```python
from __future__ import annotations
import re
import random
from dataclasses import dataclass, field
from pathlib import Path
from simulator.core.card import Card, load_card


@dataclass
class Deck:
    cards: list[Card]
    name: str = "unknown"

    @classmethod
    def from_file(cls, path: str | Path) -> Deck:
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        cards: list[Card] = []
        in_main = False
        for line in text.splitlines():
            if line.strip().startswith("```"):
                in_main = not in_main
                continue
            if not in_main:
                continue
            if line.startswith("---") or line.strip() == "":
                break
            m = re.match(r"^(\d+)\s+(.+)$", line.strip())
            if m:
                qty, name = int(m.group(1)), m.group(2).strip()
                card = load_card(name)
                cards.extend([card] * qty)
        return cls(cards=cards, name=path.stem)

    def shuffle(self, seed: int | None = None) -> None:
        rng = random.Random(seed)
        rng.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop(0)

    def copy(self) -> Deck:
        return Deck(cards=list(self.cards), name=self.name)

    def __len__(self) -> int:
        return len(self.cards)
```

- [ ] **Step 4: Check the actual deck file format**

```bash
head -30 "C:/Desktop/CLAUDE Projects/MTG_Companion/decks/pauper-madness-burn.md"
```

If the maindeck lines are NOT inside a code block (``` markers), adjust the parser: replace the `in_main` / code-block logic with a simpler approach that reads lines matching `^\d+\s+` until a `---` separator or end of maindeck section. Adjust until `test_deck_loads_60_cards` passes.

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/simulator/test_deck.py -v
```
Expected: `5 passed`

- [ ] **Step 6: Commit**

```bash
git add simulator/core/deck.py tests/simulator/test_deck.py
git commit -m "feat(simulator): Deck loading from markdown decklist"
```

---

## Task 3: GameState + Actions

**Files:**
- Create: `simulator/core/game_state.py`
- Create: `simulator/core/actions.py`

- [ ] **Step 1: Write failing test**

Add to `tests/simulator/test_card.py` or create `tests/simulator/test_game_state.py`:

```python
from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.actions import (
    PlayLand, CastSpell, CastMadness, FlashbackSpell,
    AlternateCost, ActivateAbility, DeclareAttackers, PassPriority
)
from simulator.core.card import load_card

def test_initial_game_state():
    gs = GameState.initial()
    assert gs.turn == 1
    assert gs.phase == Phase.DRAW
    assert gs.life == 20
    assert gs.opponent_life == 20
    assert gs.cards_drawn_this_turn == 0

def test_game_state_is_copyable():
    gs = GameState.initial()
    gs2 = gs.copy()
    gs2.opponent_life = 10
    assert gs.opponent_life == 20

def test_actions_are_comparable():
    a1 = PassPriority()
    a2 = PassPriority()
    assert a1 == a2

def test_cast_spell_action():
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    assert action.card.name == "Lightning Bolt"
```

- [ ] **Step 2: Run to confirm fail**

```bash
python -m pytest tests/simulator/test_game_state.py -v 2>&1 | head -5
```

- [ ] **Step 3: Implement GameState and Actions**

Create `simulator/core/actions.py`:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from simulator.core.card import Card


@dataclass(frozen=True)
class PlayLand:
    card: Card

@dataclass(frozen=True)
class CastSpell:
    card: Card
    cost: dict  # e.g. {"R": 1} or {"R": 2}
    targets: list = field(default_factory=list)
    discard_card: Card | None = None  # for Faithless Looting, Highway Robbery, etc.

@dataclass(frozen=True)
class CastMadness:
    card: Card
    madness_cost: str
    targets: list = field(default_factory=list)

@dataclass(frozen=True)
class FlashbackSpell:
    card: Card
    targets: list = field(default_factory=list)

@dataclass(frozen=True)
class AlternateCost:  # Fireblast
    card: Card
    targets: list = field(default_factory=list)

@dataclass(frozen=True)
class ActivateAbility:  # Blood token
    source: Card
    ability_index: int = 0
    discard_card: Card | None = None

@dataclass(frozen=True)
class DeclareAttackers:
    creatures: list = field(default_factory=list)

@dataclass(frozen=True)
class PassPriority:
    pass

Action = (PlayLand | CastSpell | CastMadness | FlashbackSpell |
          AlternateCost | ActivateAbility | DeclareAttackers | PassPriority)
```

Create `simulator/core/game_state.py`:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from simulator.core.card import Card


class Phase(Enum):
    UNTAP = auto()
    UPKEEP = auto()
    DRAW = auto()
    MAIN1 = auto()
    COMBAT = auto()
    MAIN2 = auto()
    END = auto()


@dataclass
class CardState:
    card: Card
    tapped: bool = False
    counters: dict = field(default_factory=dict)


@dataclass
class GameState:
    # Zones
    library: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    battlefield: list[CardState] = field(default_factory=list)
    graveyard: list[Card] = field(default_factory=list)
    exile: list[Card] = field(default_factory=list)
    madness_zone: list[Card] = field(default_factory=list)
    blood_tokens: int = 0  # count of Blood tokens on battlefield

    # Mana
    mana_pool: dict = field(default_factory=lambda: {"R": 0, "C": 0})

    # Turn tracking
    lands_played: int = 0
    cards_drawn_this_turn: int = 0
    turn: int = 1
    phase: Phase = Phase.DRAW

    # Life
    life: int = 20
    opponent_life: int = 20

    # Status
    game_over: bool = False
    winner: int = -1  # -1 = no winner yet, 0 = us, 1 = opponent

    # Derived convenience
    @property
    def mountains_on_battlefield(self) -> int:
        return sum(1 for cs in self.battlefield
                   if cs.card.name == "Mountain" and not cs.tapped)

    @property
    def untapped_lands(self) -> list[CardState]:
        return [cs for cs in self.battlefield
                if cs.card.is_land and not cs.tapped]

    @property
    def creatures_on_battlefield(self) -> list[CardState]:
        return [cs for cs in self.battlefield if cs.card.is_creature]

    def has_creature(self, name: str) -> bool:
        return any(cs.card.name == name for cs in self.battlefield)

    def available_red_mana(self) -> int:
        return len(self.untapped_lands)  # all lands in this deck produce R

    @classmethod
    def initial(cls) -> GameState:
        return cls()

    def copy(self) -> GameState:
        import copy
        return copy.deepcopy(self)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/simulator/test_game_state.py -v
```
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add simulator/core/game_state.py simulator/core/actions.py tests/simulator/test_game_state.py
git commit -m "feat(simulator): GameState dataclass + Action types"
```

---

## Task 4: Rules engine

**Files:**
- Create: `simulator/core/rules.py`
- Create: `tests/simulator/test_rules.py`

- [ ] **Step 1: Write failing tests**

Create `tests/simulator/test_rules.py`:

```python
import pytest
from simulator.core.card import load_card
from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.actions import CastSpell, PlayLand, PassPriority, AlternateCost, CastMadness
from simulator.core.rules import legal_actions, apply

def _state_with_hand(*card_names: str, lands_in_play: int = 2) -> GameState:
    gs = GameState()
    gs.phase = Phase.MAIN1
    gs.hand = [load_card(n) for n in card_names]
    for _ in range(lands_in_play):
        gs.battlefield.append(CardState(card=load_card("Mountain")))
    return gs

def test_can_play_land_from_hand():
    gs = _state_with_hand("Mountain", lands_in_play=0)
    actions = legal_actions(gs)
    play_land_actions = [a for a in actions if isinstance(a, PlayLand)]
    assert len(play_land_actions) == 1

def test_cannot_play_two_lands():
    gs = _state_with_hand("Mountain", lands_in_play=1)
    gs.lands_played = 1
    actions = legal_actions(gs)
    assert not any(isinstance(a, PlayLand) for a in actions)

def test_can_cast_lightning_bolt_with_mana():
    gs = _state_with_hand("Lightning Bolt", lands_in_play=1)
    actions = legal_actions(gs)
    bolt_casts = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Lightning Bolt"]
    assert len(bolt_casts) == 1

def test_cannot_cast_guttersnipe_without_enough_mana():
    gs = _state_with_hand("Guttersnipe", lands_in_play=2)
    actions = legal_actions(gs)
    casts = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Guttersnipe"]
    assert len(casts) == 0  # needs 3 mana

def test_can_cast_guttersnipe_with_three_lands():
    gs = _state_with_hand("Guttersnipe", lands_in_play=3)
    actions = legal_actions(gs)
    casts = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Guttersnipe"]
    assert len(casts) == 1

def test_cast_lightning_bolt_deals_damage():
    gs = _state_with_hand("Lightning Bolt", lands_in_play=1)
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    new_gs = apply(gs, action)
    assert new_gs.opponent_life == 17  # 20 - 3

def test_kessig_pings_on_noncreature_spell():
    gs = _state_with_hand("Lightning Bolt", lands_in_play=1)
    gs.battlefield.append(CardState(card=load_card("Kessig Flamebreather")))
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    new_gs = apply(gs, action)
    assert new_gs.opponent_life == 16  # 3 from bolt + 1 from Kessig

def test_madness_discard_goes_to_madness_zone():
    gs = _state_with_hand("Faithless Looting", "Fiery Temper", lands_in_play=1)
    fl = load_card("Faithless Looting")
    temper = load_card("Fiery Temper")
    action = CastSpell(card=fl, cost={"R": 1}, targets=[], discard_card=temper)
    new_gs = apply(gs, action)
    assert temper in new_gs.madness_zone

def test_fireblast_alternate_cost_removes_mountains():
    gs = _state_with_hand("Fireblast", lands_in_play=3)
    gs.opponent_life = 4
    fb = load_card("Fireblast")
    action = AlternateCost(card=fb, targets=["face"])
    new_gs = apply(gs, action)
    assert new_gs.opponent_life == 0
    mountain_count = sum(1 for cs in new_gs.battlefield if cs.card.name == "Mountain")
    assert mountain_count == 1  # 3 - 2 = 1

def test_sneaky_snacker_returns_on_third_draw():
    snacker = load_card("Sneaky Snacker")
    gs = GameState()
    gs.phase = Phase.DRAW
    gs.graveyard = [snacker]
    gs.library = [load_card("Lightning Bolt")]
    gs.cards_drawn_this_turn = 2  # next draw is the 3rd
    from simulator.core.rules import draw_card
    new_gs = draw_card(gs)
    assert any(cs.card.name == "Sneaky Snacker" for cs in new_gs.battlefield)
    assert snacker not in new_gs.graveyard

def test_game_over_when_opponent_at_zero():
    gs = _state_with_hand("Lightning Bolt", lands_in_play=1)
    gs.opponent_life = 3
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    new_gs = apply(gs, action)
    assert new_gs.game_over is True
    assert new_gs.winner == 0
```

- [ ] **Step 2: Run to confirm fail**

```bash
python -m pytest tests/simulator/test_rules.py -v 2>&1 | head -10
```
Expected: `ImportError: cannot import name 'legal_actions'`

- [ ] **Step 3: Implement rules engine**

Create `simulator/core/rules.py`:

```python
from __future__ import annotations
import copy
from simulator.core.card import Card, load_card
from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.actions import (
    Action, PlayLand, CastSpell, CastMadness, FlashbackSpell,
    AlternateCost, ActivateAbility, DeclareAttackers, PassPriority
)


def _parse_cmc(cost: str) -> int:
    """Parse a mana cost string like '{1}{R}' and return colored pip count."""
    import re
    pips = re.findall(r'\{([^}]+)\}', cost)
    total = 0
    for p in pips:
        if p.isdigit():
            total += int(p)
        elif p in ('R', 'G', 'U', 'B', 'W', 'C'):
            total += 1
    return total


def _has_enough_mana(gs: GameState, cmc: int) -> bool:
    return len(gs.untapped_lands) >= cmc


def draw_card(gs: GameState) -> GameState:
    """Draw the top card of library. Fire Sneaky Snacker trigger at 3rd draw."""
    gs = copy.deepcopy(gs)
    if not gs.library:
        return gs  # can't draw from empty library
    card = gs.library.pop(0)
    gs.hand.append(card)
    gs.cards_drawn_this_turn += 1
    if gs.cards_drawn_this_turn >= 3:
        for grave_card in list(gs.graveyard):
            if grave_card.snacker_return:
                gs.graveyard.remove(grave_card)
                gs.battlefield.append(CardState(card=grave_card, tapped=True))
                break
    return gs


def _tap_lands_for_mana(gs: GameState, amount: int) -> GameState:
    """Tap `amount` untapped lands to add R mana."""
    tapped = 0
    for cs in gs.battlefield:
        if tapped >= amount:
            break
        if cs.card.is_land and not cs.tapped:
            cs.tapped = True
            gs.mana_pool["R"] = gs.mana_pool.get("R", 0) + 1
            tapped += 1
    return gs


def _apply_pinger_triggers(gs: GameState, spell_card: Card) -> GameState:
    """Fire Kessig Flamebreather and Guttersnipe triggers for a cast spell."""
    is_noncreature = not spell_card.is_creature
    is_instant_sorcery = spell_card.is_instant or spell_card.is_sorcery
    for cs in gs.battlefield:
        if cs.card.pings_per_noncreature_spell > 0 and is_noncreature:
            gs.opponent_life -= cs.card.pings_per_noncreature_spell
        if cs.card.pings_per_instant_sorcery > 0 and is_instant_sorcery:
            gs.opponent_life -= cs.card.pings_per_instant_sorcery
    return gs


def _check_win(gs: GameState) -> GameState:
    if gs.opponent_life <= 0 and not gs.game_over:
        gs.game_over = True
        gs.winner = 0
    return gs


def _resolve_spell(gs: GameState, card: Card, targets: list, discard_card: Card | None = None) -> GameState:
    """Apply a spell's effects. Card is already off the stack (in graveyard)."""
    # Direct damage to face
    if card.damage_on_cast > 0 and "face" in targets:
        gs.opponent_life -= card.damage_on_cast

    # Grab the Prize bonus damage
    if card.grab_prize_damage > 0 and discard_card and not discard_card.is_land:
        gs.opponent_life -= card.grab_prize_damage

    # Draw effects
    for _ in range(card.draw_on_cast):
        gs = draw_card(gs)

    # Discard effects (after drawing)
    if card.discard_on_cast > 0 and discard_card:
        gs.hand.remove(discard_card) if discard_card in gs.hand else None
        if discard_card.has_madness:
            gs.madness_zone.append(discard_card)
        else:
            gs.graveyard.append(discard_card)

    # ETB damage (if this spell created a creature on ETB via sorcery, etc.)
    if card.damage_on_etb > 0:
        gs.opponent_life -= card.damage_on_etb

    # ETB Blood creation (Voldaren Epicure)
    if card.creates_blood_on_etb:
        gs.blood_tokens += 1

    return gs


def legal_actions(gs: GameState) -> list[Action]:
    actions: list[Action] = [PassPriority()]

    if gs.game_over:
        return actions

    if gs.phase in (Phase.MAIN1, Phase.MAIN2):
        # Play a land
        if gs.lands_played == 0:
            for card in gs.hand:
                if card.is_land:
                    actions.append(PlayLand(card=card))

        # Cast spells from hand
        available_mana = len(gs.untapped_lands)
        for card in gs.hand:
            if card.is_land:
                continue
            cmc = _parse_cmc(card.mana_cost)
            if available_mana >= cmc:
                # For cards that require discarding, add actions with each non-land discard option
                if card.discard_on_cast > 0:
                    discard_options = [c for c in gs.hand if c != card and not c.is_land]
                    if not discard_options:
                        discard_options = [c for c in gs.hand if c != card]
                    for dc in discard_options:
                        actions.append(CastSpell(
                            card=card,
                            cost={"R": cmc},
                            targets=["face"],
                            discard_card=dc
                        ))
                else:
                    # Alternate cost for Fireblast
                    if card.has_alternate_cost and card.alternate_cost == "sac_2_mountains":
                        mountain_count = sum(1 for cs in gs.battlefield
                                           if cs.card.name == "Mountain" and not cs.tapped)
                        if mountain_count >= 2:
                            actions.append(AlternateCost(card=card, targets=["face"]))
                    else:
                        actions.append(CastSpell(
                            card=card,
                            cost={"R": cmc},
                            targets=["face"] if card.damage_on_cast > 0 else []
                        ))

        # Cast madness cards from madness zone
        for card in gs.madness_zone:
            actions.append(CastMadness(
                card=card,
                madness_cost=card.madness_cost,
                targets=["face"] if card.damage_on_cast > 0 else []
            ))

        # Flashback from graveyard
        for card in gs.graveyard:
            if card.has_flashback:
                if card.flashback_cost == "sac_mountain":
                    if gs.mountains_on_battlefield > 0:
                        actions.append(FlashbackSpell(card=card, targets=["face"]))
                elif card.flashback_cost:
                    fc = _parse_cmc(card.flashback_cost)
                    if available_mana >= fc:
                        actions.append(FlashbackSpell(card=card, targets=["face"]))

        # Blood token activation
        if gs.blood_tokens > 0:
            discard_options = [c for c in gs.hand]
            for dc in discard_options:
                actions.append(ActivateAbility(
                    source=load_card("Voldaren Epicure"),
                    ability_index=0,
                    discard_card=dc
                ))

    if gs.phase == Phase.COMBAT:
        untapped_creatures = [cs for cs in gs.battlefield
                              if cs.card.is_creature and not cs.tapped]
        if untapped_creatures:
            actions.append(DeclareAttackers(
                creatures=[cs.card for cs in untapped_creatures]
            ))

    return actions


def apply(gs: GameState, action: Action) -> GameState:
    gs = copy.deepcopy(gs)

    match action:
        case PassPriority():
            pass

        case PlayLand(card=card):
            gs.hand.remove(card)
            gs.battlefield.append(CardState(card=card))
            gs.lands_played += 1

        case CastSpell(card=card, cost=cost, targets=targets, discard_card=dc):
            # Remove from hand
            gs.hand.remove(card)
            # Tap lands for mana
            cmc = sum(cost.values())
            gs = _tap_lands_for_mana(gs, cmc)
            # Fire pinger triggers BEFORE resolving
            gs = _apply_pinger_triggers(gs, card)
            # Move to graveyard (for non-permanent spells)
            if not card.is_creature and not card.is_artifact and not card.is_enchantment:
                gs.graveyard.append(card)
            else:
                gs.battlefield.append(CardState(card=card))
            # Resolve effects
            gs = _resolve_spell(gs, card, targets, dc)
            gs = _check_win(gs)

        case CastMadness(card=card, madness_cost=cost, targets=targets):
            gs.madness_zone.remove(card)
            mc = _parse_cmc(cost)
            gs = _tap_lands_for_mana(gs, mc)
            gs = _apply_pinger_triggers(gs, card)
            gs.graveyard.append(card)
            gs = _resolve_spell(gs, card, targets)
            gs = _check_win(gs)

        case FlashbackSpell(card=card, targets=targets):
            gs.graveyard.remove(card)
            if card.flashback_cost == "sac_mountain":
                # Sacrifice a Mountain
                for cs in gs.battlefield:
                    if cs.card.name == "Mountain":
                        gs.battlefield.remove(cs)
                        gs.graveyard.append(cs.card)
                        break
            else:
                fc = _parse_cmc(card.flashback_cost)
                gs = _tap_lands_for_mana(gs, fc)
            gs = _apply_pinger_triggers(gs, card)
            gs.exile.append(card)
            gs = _resolve_spell(gs, card, targets)
            gs = _check_win(gs)

        case AlternateCost(card=card, targets=targets):  # Fireblast
            gs.hand.remove(card)
            # Sacrifice 2 Mountains
            removed = 0
            for cs in list(gs.battlefield):
                if removed >= 2:
                    break
                if cs.card.name == "Mountain":
                    gs.battlefield.remove(cs)
                    gs.graveyard.append(cs.card)
                    removed += 1
            gs = _apply_pinger_triggers(gs, card)
            gs.graveyard.append(card)
            gs = _resolve_spell(gs, card, targets)
            gs = _check_win(gs)

        case ActivateAbility(source=_, ability_index=_, discard_card=dc):
            # Blood token: discard 1, draw 1
            if dc and dc in gs.hand:
                gs.hand.remove(dc)
                if dc.has_madness:
                    gs.madness_zone.append(dc)
                else:
                    gs.graveyard.append(dc)
            gs.blood_tokens -= 1
            gs = draw_card(gs)

        case DeclareAttackers(creatures=creatures):
            total_power = sum(c.power for c in creatures)
            gs.opponent_life -= total_power
            gs = _check_win(gs)

    return gs
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/simulator/test_rules.py -v
```
Expected: `11 passed`

- [ ] **Step 5: Commit**

```bash
git add simulator/core/rules.py tests/simulator/test_rules.py
git commit -m "feat(simulator): Rules engine with Madness Burn card interactions"
```

---

## Task 5: Policy interface + GoldfishPolicy + RandomPolicy

**Files:**
- Create: `simulator/policies/base.py`
- Create: `simulator/policies/goldfish.py`

- [ ] **Step 1: Write failing test**

Add to `tests/simulator/test_policies.py`:

```python
from simulator.policies.base import Policy
from simulator.policies.goldfish import GoldfishPolicy, RandomPolicy
from simulator.core.actions import PassPriority
from simulator.core.game_state import GameState

def test_goldfish_always_passes():
    policy = GoldfishPolicy()
    gs = GameState()
    actions = [PassPriority()]
    result = policy.act(gs, actions)
    assert isinstance(result, PassPriority)

def test_random_picks_from_legal():
    import random
    random.seed(42)
    policy = RandomPolicy(seed=42)
    gs = GameState()
    from simulator.core.actions import PlayLand
    from simulator.core.card import load_card
    actions = [PassPriority(), PlayLand(card=load_card("Mountain"))]
    results = {type(policy.act(gs, actions)).__name__ for _ in range(20)}
    assert len(results) > 1  # picked different actions

def test_policy_update_is_no_op():
    policy = GoldfishPolicy()
    policy.update([], 1.0)  # should not raise

def test_policy_value_is_zero():
    policy = GoldfishPolicy()
    gs = GameState()
    assert policy.value(gs) == 0.0
```

- [ ] **Step 2: Run to confirm fail**

```bash
python -m pytest tests/simulator/test_policies.py -v 2>&1 | head -5
```

- [ ] **Step 3: Implement**

Create `simulator/policies/base.py`:

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from simulator.core.game_state import GameState
from simulator.core.actions import Action


class Policy(ABC):
    @abstractmethod
    def act(self, state: GameState, legal_actions: list[Action]) -> Action:
        ...

    def update(self, trajectory: list[tuple[GameState, Action]], reward: float) -> None:
        pass  # heuristics ignore — RL overrides

    def value(self, state: GameState) -> float:
        return 0.0  # heuristics return 0 — RL overrides
```

Create `simulator/policies/goldfish.py`:

```python
from __future__ import annotations
import random
from simulator.policies.base import Policy
from simulator.core.game_state import GameState
from simulator.core.actions import Action, PassPriority


class GoldfishPolicy(Policy):
    """Do-nothing opponent. Always passes priority."""
    def act(self, state: GameState, legal_actions: list[Action]) -> Action:
        return PassPriority()


class RandomPolicy(Policy):
    """Picks uniformly at random from legal actions. Sanity baseline."""
    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def act(self, state: GameState, legal_actions: list[Action]) -> Action:
        return self._rng.choice(legal_actions)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/simulator/test_policies.py -v
```
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add simulator/policies/base.py simulator/policies/goldfish.py tests/simulator/test_policies.py
git commit -m "feat(simulator): Policy interface + GoldfishPolicy + RandomPolicy"
```

---

## Task 6: MadnessBurnHeuristic

**Files:**
- Create: `simulator/policies/heuristic/madness_burn.py`

- [ ] **Step 1: Write failing test**

Add to `tests/simulator/test_policies.py`:

```python
from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic
from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.card import load_card
from simulator.core.actions import CastSpell, PlayLand, PassPriority, AlternateCost
from simulator.core.rules import legal_actions

def _main1_state(*hand_names: str, lands: int = 2) -> GameState:
    gs = GameState()
    gs.phase = Phase.MAIN1
    gs.hand = [load_card(n) for n in hand_names]
    for _ in range(lands):
        gs.battlefield.append(CardState(card=load_card("Mountain")))
    return gs

def test_heuristic_plays_kessig_before_bolt():
    gs = _main1_state("Kessig Flamebreather", "Lightning Bolt", lands=2)
    policy = MadnessBurnHeuristic()
    actions = legal_actions(gs)
    chosen = policy.act(gs, actions)
    assert isinstance(chosen, CastSpell)
    assert chosen.card.name == "Kessig Flamebreather"

def test_heuristic_plays_land_when_available():
    gs = _main1_state("Mountain", "Lightning Bolt", lands=0)
    policy = MadnessBurnHeuristic()
    actions = legal_actions(gs)
    chosen = policy.act(gs, actions)
    assert isinstance(chosen, PlayLand)

def test_heuristic_fireblasts_at_4_life():
    gs = _main1_state("Fireblast", lands=3)
    gs.opponent_life = 4
    policy = MadnessBurnHeuristic()
    actions = legal_actions(gs)
    chosen = policy.act(gs, actions)
    assert isinstance(chosen, AlternateCost)
    assert chosen.card.name == "Fireblast"

def test_heuristic_does_not_fireblast_when_not_lethal():
    gs = _main1_state("Fireblast", lands=3)
    gs.opponent_life = 10
    policy = MadnessBurnHeuristic()
    actions = legal_actions(gs)
    chosen = policy.act(gs, actions)
    # Should not Fireblast when not killing
    assert not (isinstance(chosen, AlternateCost) and chosen.card.name == "Fireblast")
```

- [ ] **Step 2: Run to confirm fail**

```bash
python -m pytest tests/simulator/test_policies.py::test_heuristic_plays_kessig_before_bolt -v 2>&1 | head -5
```

- [ ] **Step 3: Implement MadnessBurnHeuristic**

Create `simulator/policies/heuristic/madness_burn.py`:

```python
from __future__ import annotations
from simulator.policies.base import Policy
from simulator.core.game_state import GameState
from simulator.core.actions import (
    Action, PlayLand, CastSpell, CastMadness, FlashbackSpell,
    AlternateCost, ActivateAbility, DeclareAttackers, PassPriority
)

_PRIORITY = {
    # Lower number = higher priority
    "Kessig Flamebreather": 10,
    "Voldaren Epicure": 15,
    "Guttersnipe": 20,
    "Faithless Looting": 25,
    "Grab the Prize": 26,
    "Highway Robbery": 27,
    "Lightning Bolt": 30,
    "Lava Dart": 31,
    "Fiery Temper": 32,
}

_DISCARD_PRIORITY = [
    "Sneaky Snacker",   # discard first — sets up free GY return
    "Fiery Temper",     # discard second — madness {R} is great
    "Guttersnipe",      # discard if stuck with it
]


def _best_discard(hand: list, exclude: object) -> object | None:
    """Pick the best card to discard from hand (excluding the card being cast)."""
    candidates = [c for c in hand if c is not exclude]
    if not candidates:
        return None
    for name in _DISCARD_PRIORITY:
        for c in candidates:
            if c.name == name:
                return c
    # Default: highest CMC (least immediately useful)
    return max(candidates, key=lambda c: c.cmc)


class MadnessBurnHeuristic(Policy):
    """Plays Madness Burn optimally against a goldfish opponent."""

    def act(self, state: GameState, legal_actions: list[Action]) -> Action:
        # 1. Resolve pending madness first
        madness_casts = [a for a in legal_actions if isinstance(a, CastMadness)]
        if madness_casts:
            return madness_casts[0]

        # 2. Play a land
        land_plays = [a for a in legal_actions if isinstance(a, PlayLand)]
        if land_plays:
            return land_plays[0]

        # 3. Fireblast only if lethal this turn
        fb_actions = [a for a in legal_actions
                      if isinstance(a, AlternateCost) and a.card.name == "Fireblast"]
        if fb_actions and state.opponent_life <= 4:
            return fb_actions[0]

        # 4. Cast creatures/spells by priority
        spell_casts = [a for a in legal_actions if isinstance(a, CastSpell)]

        # 4a. Kessig if not on battlefield
        if not state.has_creature("Kessig Flamebreather"):
            kessig = [a for a in spell_casts if a.card.name == "Kessig Flamebreather"]
            if kessig:
                return kessig[0]

        # 4b. Discard-outlet spells (trigger madness chain)
        discard_spells = [a for a in spell_casts if a.card.discard_on_cast > 0]
        for a in discard_spells:
            best_dc = _best_discard(state.hand, a.card)
            if best_dc and best_dc.has_madness:
                # Re-find the action with this discard
                matching = [x for x in spell_casts
                            if x.card.name == a.card.name
                            and x.discard_card and x.discard_card.name == best_dc.name]
                if matching:
                    return matching[0]

        # 4c. Guttersnipe if Kessig is already on battlefield
        if state.has_creature("Kessig Flamebreather"):
            gut = [a for a in spell_casts if a.card.name == "Guttersnipe"]
            if gut:
                return gut[0]

        # 4d. Grab the Prize preferred over Highway Robbery
        for name in ("Grab the Prize", "Highway Robbery", "Faithless Looting"):
            found = [a for a in spell_casts if a.card.name == name]
            if found:
                # Pick discard that maximizes value
                best = found[0]
                for a in found:
                    if a.discard_card and a.discard_card.has_madness:
                        best = a
                        break
                    elif a.discard_card and a.discard_card.name == "Sneaky Snacker":
                        best = a
                return best

        # 4e. Burn spells at face
        burn = sorted(
            [a for a in spell_casts if a.card.damage_on_cast > 0],
            key=lambda a: -a.card.damage_on_cast
        )
        if burn:
            return burn[0]

        # 4f. Flashback
        flashback = [a for a in legal_actions if isinstance(a, FlashbackSpell)]
        if flashback:
            return flashback[0]

        # 5. Declare attackers
        attack = [a for a in legal_actions if isinstance(a, DeclareAttackers)]
        if attack:
            return attack[0]

        return PassPriority()
```

- [ ] **Step 4: Run all policy tests**

```bash
python -m pytest tests/simulator/test_policies.py -v
```
Expected: `8 passed`

- [ ] **Step 5: Commit**

```bash
git add simulator/policies/heuristic/madness_burn.py tests/simulator/test_policies.py
git commit -m "feat(simulator): MadnessBurnHeuristic with priority-ordered decision tree"
```

---

## Self-Review

**Spec coverage (Phase 1A):**
- Card model with oracle.ndjson loading + CARD_OVERRIDES → Task 1 ✓
- Deck loading from markdown → Task 2 ✓  
- GameState copyable dataclass + Action types → Task 3 ✓
- Rules engine legal_actions + apply → Task 4 ✓
- Policy interface act/update/value → Task 5 ✓
- GoldfishPolicy + RandomPolicy → Task 5 ✓
- MadnessBurnHeuristic with priority rules → Task 6 ✓

**Placeholder scan:** None found.

**Type consistency:** `load_card(name: str) -> Card` used consistently. `GameState.copy()` uses `deepcopy`. `legal_actions(gs: GameState) -> list[Action]` and `apply(gs: GameState, action: Action) -> GameState` match across all tasks. `Policy.act(state, legal_actions) -> Action` consistent.

**Open:** Task 2 Step 4 notes that the deck file format must be verified and parser adjusted if needed. This is intentional — the actual file format is known but the parser should be validated against it.
