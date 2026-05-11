from __future__ import annotations
from abc import ABC, abstractmethod
from simulator.core.game_state import GameState
from simulator.core.actions import Action


class Policy(ABC):
    @abstractmethod
    def act(self, state: GameState, legal_actions: list[Action]) -> Action:
        ...

    def update(self, trajectory: list[tuple[GameState, Action]], reward: float) -> None:
        pass

    def value(self, state: GameState) -> float:
        return 0.0
