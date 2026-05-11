from __future__ import annotations
from dataclasses import dataclass, field
from simulator.core.card import Card


@dataclass(frozen=True)
class PlayLand:
    card: Card

@dataclass(frozen=True)
class CastSpell:
    card: Card
    cost: dict
    targets: list = field(default_factory=list)
    discard_card: Card | None = None

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
class AlternateCost:
    card: Card
    targets: list = field(default_factory=list)

@dataclass(frozen=True)
class ActivateAbility:
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
