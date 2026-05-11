from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path

LOGS_DIR = Path(__file__).parents[2] / "library" / "logs"


@dataclass
class MetaEvResults:
    overall_ev: float
    contributions: dict[str, float]
    win_rates: dict[str, float]
    meta_shares: dict[str, float]

    def format(self) -> str:
        lines = [
            "Meta EV analysis",
            f"Overall EV: {self.overall_ev:.1%}",
            "",
            f"{'Matchup':<25} {'Meta%':>7} {'WR%':>7} {'Contribution':>12}",
            f"{'-' * 55}",
        ]
        for deck in sorted(self.contributions, key=lambda k: -self.contributions[k]):
            share = self.meta_shares.get(deck, 0.0)
            wr = self.win_rates.get(deck, 0.0)
            contrib = self.contributions[deck]
            lines.append(f"  {deck:<23} {share:>6.1%} {wr:>7.1%} {contrib:>+11.1%}")
        return "\n".join(lines)


def calculate_meta_ev(
    win_rates: dict[str, float],
    meta_shares: dict[str, float],
) -> MetaEvResults:
    """EV = Σ (normalized_meta_share[deck] × win_rate[deck])"""
    common = set(win_rates.keys()) & set(meta_shares.keys())
    total_share = sum(meta_shares[k] for k in common)

    contributions: dict[str, float] = {}
    for deck in common:
        normalized = meta_shares[deck] / total_share if total_share > 0 else 0.0
        contributions[deck] = normalized * win_rates[deck]

    return MetaEvResults(
        overall_ev=sum(contributions.values()),
        contributions=contributions,
        win_rates={k: win_rates[k] for k in common},
        meta_shares={k: meta_shares[k] for k in common},
    )


def load_win_rates_from_logs(min_matches: int = 2) -> dict[str, float]:
    """Load win rates from pauper-madness-batch-*.json files."""
    records: dict[str, list[int]] = {}

    for path in sorted(LOGS_DIR.glob("pauper-madness-batch-*.json")):
        matches = json.loads(path.read_text(encoding="utf-8")).get("matches", [])
        for m in matches:
            deck = m.get("opponent_deck", "Unknown")
            result = m.get("result", "?")
            if deck not in records:
                records[deck] = [0, 0]
            if result == "W":
                records[deck][0] += 1
                records[deck][1] += 1
            elif result == "L":
                records[deck][1] += 1

    return {
        deck: wins / total
        for deck, (wins, total) in records.items()
        if total >= min_matches
    }
