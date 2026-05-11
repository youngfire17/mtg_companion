from __future__ import annotations
import json
import random
from datetime import datetime
from pathlib import Path
from simulator.core.deck import Deck
from simulator.policies.base import Policy
from simulator.policies.goldfish import GoldfishPolicy
from simulator.simulation.game import Game
from simulator.simulation.results import SimulationResults

REPORTS_DIR = Path(__file__).parents[2] / "simulator" / "data" / "reports"


class Simulator:
    def run(
        self,
        deck_path: str,
        policy_a: Policy,
        opponent_policy: Policy | None = None,
        n_games: int = 10_000,
        seed: int | None = None,
        save_report: bool = True,
        description: str = "",
    ) -> SimulationResults:
        if opponent_policy is None:
            opponent_policy = GoldfishPolicy()

        rng = random.Random(seed)
        base_deck = Deck.from_file(deck_path)
        results = SimulationResults(n_games=n_games, wins=0, losses=0, timeouts=0)

        for _ in range(n_games):
            deck = base_deck.copy()
            deck.shuffle(seed=rng.randint(0, 2**31))
            result = Game(deck).run(policy_a, opponent_policy)
            results.game_results.append(result)
            if result.winner == 0:
                results.wins += 1
            elif result.winner == 1:
                results.losses += 1
            else:
                results.timeouts += 1

        if save_report:
            self._save_report(results, description)

        return results

    def _save_report(self, results: SimulationResults, description: str) -> None:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M")
        desc = description.replace(" ", "-") or "simulation"
        path = REPORTS_DIR / f"{ts}-{desc}.json"
        summary = {
            "n_games": results.n_games,
            "wins": results.wins,
            "losses": results.losses,
            "timeouts": results.timeouts,
            "win_rate": round(results.win_rate, 4),
            "avg_kill_turn": round(results.avg_kill_turn, 2),
            "median_kill_turn": results.median_kill_turn,
            "kill_by_turn_4": round(results.kill_by_turn(4), 4),
            "kill_by_turn_5": round(results.kill_by_turn(5), 4),
            "kill_by_turn_6": round(results.kill_by_turn(6), 4),
            "kill_turn_distribution": results.kill_turn_distribution(),
        }
        path.write_text(json.dumps(summary, indent=2))
