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
    players: list[PlayerState]
    active_player: int
    priority_player: int
    phase: Phase
    turn: int
    declared_attackers: list[Card] = field(default_factory=list)
    declared_blocks: dict = field(default_factory=dict)
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
