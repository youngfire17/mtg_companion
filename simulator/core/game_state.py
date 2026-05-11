from __future__ import annotations
import copy as _copy
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
    library: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    battlefield: list[CardState] = field(default_factory=list)
    graveyard: list[Card] = field(default_factory=list)
    exile: list[Card] = field(default_factory=list)
    madness_zone: list[Card] = field(default_factory=list)
    blood_tokens: int = 0

    mana_pool: dict = field(default_factory=lambda: {"R": 0, "C": 0})
    lands_played: int = 0
    cards_drawn_this_turn: int = 0
    turn: int = 1
    phase: Phase = field(default=Phase.DRAW)

    life: int = 20
    opponent_life: int = 20
    game_over: bool = False
    winner: int = -1

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
        return len(self.untapped_lands)

    @classmethod
    def initial(cls) -> GameState:
        return cls()

    def copy(self) -> GameState:
        gs = GameState.__new__(GameState)
        gs.library = list(self.library)
        gs.hand = list(self.hand)
        gs.battlefield = [CardState(cs.card, cs.tapped, dict(cs.counters))
                          for cs in self.battlefield]
        gs.graveyard = list(self.graveyard)
        gs.exile = list(self.exile)
        gs.madness_zone = list(self.madness_zone)
        gs.blood_tokens = self.blood_tokens
        gs.mana_pool = dict(self.mana_pool)
        gs.lands_played = self.lands_played
        gs.cards_drawn_this_turn = self.cards_drawn_this_turn
        gs.turn = self.turn
        gs.phase = self.phase
        gs.life = self.life
        gs.opponent_life = self.opponent_life
        gs.game_over = self.game_over
        gs.winner = self.winner
        return gs
