from __future__ import annotations
from dataclasses import dataclass, field
from simulator.core.game_state import GameState
from simulator.core.actions import Action


@dataclass
class GameResult:
    winner: int                     # 0 = player, 1 = opponent, -1 = timeout
    turns: int
    kill_turn: int | None
    damage_by_turn: dict[int, int]
    final_state: GameState
    trajectory: list[tuple[GameState, Action]] = field(default_factory=list)


@dataclass
class SimulationResults:
    n_games: int
    wins: int
    losses: int
    timeouts: int
    game_results: list[GameResult] = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        total = self.wins + self.losses
        return self.wins / total if total > 0 else 0.0

    @property
    def kill_turns(self) -> list[int]:
        return [r.kill_turn for r in self.game_results if r.kill_turn is not None]

    @property
    def avg_kill_turn(self) -> float:
        kt = self.kill_turns
        return sum(kt) / len(kt) if kt else 0.0

    @property
    def median_kill_turn(self) -> float:
        kt = sorted(self.kill_turns)
        if not kt:
            return 0.0
        mid = len(kt) // 2
        return kt[mid] if len(kt) % 2 else (kt[mid - 1] + kt[mid]) / 2

    def kill_by_turn(self, n: int) -> float:
        kt = self.kill_turns
        if not kt:
            return 0.0
        return sum(1 for t in kt if t <= n) / self.n_games

    def kill_turn_distribution(self) -> dict[int, int]:
        dist: dict[int, int] = {}
        for t in self.kill_turns:
            dist[t] = dist.get(t, 0) + 1
        return dict(sorted(dist.items()))
