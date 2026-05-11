from __future__ import annotations
from simulator.simulation.results import SimulationResults


def analyze_goldfish(results: SimulationResults) -> str:
    """Format goldfish simulation results as a human-readable string."""
    dist = results.kill_turn_distribution()
    total = results.n_games
    lines = [
        f"Goldfish simulation: {total:,} games",
        f"Win rate: {results.win_rate:.1%}  |  Timeouts: {results.timeouts}",
        f"Average kill turn: {results.avg_kill_turn:.2f}  |  Median: {results.median_kill_turn}",
        "",
        "Kill turn distribution:",
    ]

    max_pct = max((c / total for c in dist.values()), default=1.0)
    bar_width = 30
    cumulative = 0

    for turn in sorted(dist.keys()):
        count = dist[turn]
        cumulative += count
        pct = count / total
        cum_pct = cumulative / total
        bar_len = int((pct / max_pct) * bar_width) if max_pct > 0 else 0
        bar = "█" * bar_len
        lines.append(
            f"  Turn {turn:2d}: {pct:5.1%} {bar:<{bar_width}}  (cumulative: {cum_pct:.1%})"
        )

    lines.extend([
        "",
        f"P(kill by turn 3): {results.kill_by_turn(3):.1%}",
        f"P(kill by turn 4): {results.kill_by_turn(4):.1%}",
        f"P(kill by turn 5): {results.kill_by_turn(5):.1%}",
        f"P(kill by turn 6): {results.kill_by_turn(6):.1%}",
        f"P(kill by turn 7): {results.kill_by_turn(7):.1%}",
    ])

    return "\n".join(lines)
