from __future__ import annotations
import math
import statistics
from dataclasses import dataclass
from simulator.policies.base import Policy
from simulator.policies.goldfish import GoldfishPolicy
from simulator.simulation.simulator import Simulator


def _z_test_two_means(
    mean_a: float, std_a: float, n_a: int,
    mean_b: float, std_b: float, n_b: int,
) -> float:
    """Two-sample Z-test for difference of means. Returns two-tailed p-value."""
    if n_a < 2 or n_b < 2:
        return 1.0
    se = math.sqrt((std_a ** 2) / n_a + (std_b ** 2) / n_b)
    if se == 0:
        return 1.0
    z = abs((mean_a - mean_b) / se)
    p = math.erfc(z / math.sqrt(2))
    return min(p, 1.0)


@dataclass
class DeckCompareResults:
    label_a: str
    label_b: str
    n_games: int
    avg_kill_a: float
    avg_kill_b: float
    std_kill_a: float
    std_kill_b: float
    win_rate_a: float
    win_rate_b: float
    kill_by_5_a: float
    kill_by_5_b: float
    kill_by_6_a: float
    kill_by_6_b: float
    p_value: float
    significant: bool
    recommendation: str

    def format(self) -> str:
        sig_marker = "significant (p<0.05)" if self.significant else "not significant"
        diff = self.avg_kill_a - self.avg_kill_b
        diff_str = f"{abs(diff):.2f} turns {'faster' if diff > 0 else 'slower'}"
        lines = [
            f"Deck comparison: {self.label_a} vs {self.label_b} ({self.n_games:,} games each)",
            "",
            f"{'Metric':<25} {self.label_a:<20} {self.label_b:<20}",
            f"{'-' * 65}",
            f"{'Avg kill turn':<25} {self.avg_kill_a:<20.2f} {self.avg_kill_b:<20.2f}",
            f"{'Win rate':<25} {self.win_rate_a:<20.1%} {self.win_rate_b:<20.1%}",
            f"{'P(kill by T5)':<25} {self.kill_by_5_a:<20.1%} {self.kill_by_5_b:<20.1%}",
            f"{'P(kill by T6)':<25} {self.kill_by_6_a:<20.1%} {self.kill_by_6_b:<20.1%}",
            "",
            f"Difference: {self.label_a} is {diff_str} on average",
            f"P-value: {self.p_value:.3f} ({sig_marker})",
            f"Recommendation: {self.recommendation}",
        ]
        return "\n".join(lines)


def compare_decks(
    deck_path_a: str,
    label_a: str,
    deck_path_b: str,
    label_b: str,
    policy: Policy | None = None,
    opponent_policy: Policy | None = None,
    n_games: int = 10_000,
    seed: int | None = None,
    save_report: bool = False,
) -> DeckCompareResults:
    if policy is None:
        from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic
        policy = MadnessBurnHeuristic()
    if opponent_policy is None:
        opponent_policy = GoldfishPolicy()

    sim = Simulator()
    ra = sim.run(deck_path_a, policy, opponent_policy, n_games=n_games, seed=seed,
                 save_report=save_report, description=f"compare-{label_a.replace(' ', '-')}")
    rb = sim.run(deck_path_b, policy, opponent_policy, n_games=n_games, seed=seed,
                 save_report=save_report, description=f"compare-{label_b.replace(' ', '-')}")

    kt_a, kt_b = ra.kill_turns, rb.kill_turns
    avg_a, avg_b = ra.avg_kill_turn, rb.avg_kill_turn
    std_a = statistics.stdev(kt_a) if len(kt_a) > 1 else 0.0
    std_b = statistics.stdev(kt_b) if len(kt_b) > 1 else 0.0

    p = _z_test_two_means(avg_a, std_a, len(kt_a), avg_b, std_b, len(kt_b))
    significant = p < 0.05

    if not significant:
        recommendation = "No meaningful difference"
    elif avg_a < avg_b:
        recommendation = label_a
    else:
        recommendation = label_b

    return DeckCompareResults(
        label_a=label_a, label_b=label_b, n_games=n_games,
        avg_kill_a=avg_a, avg_kill_b=avg_b,
        std_kill_a=std_a, std_kill_b=std_b,
        win_rate_a=ra.win_rate, win_rate_b=rb.win_rate,
        kill_by_5_a=ra.kill_by_turn(5), kill_by_5_b=rb.kill_by_turn(5),
        kill_by_6_a=ra.kill_by_turn(6), kill_by_6_b=rb.kill_by_turn(6),
        p_value=p, significant=significant, recommendation=recommendation,
    )
