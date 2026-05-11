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
