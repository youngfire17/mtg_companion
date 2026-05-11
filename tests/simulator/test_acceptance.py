import time
import pytest
from simulator.simulation.simulator import Simulator
from simulator.analysis.goldfish_analysis import analyze_goldfish
from simulator.analysis.hand_quality import (
    analyze_hand_quality, JUSTIN_RULE, STRICT_RULE
)
from simulator.core.deck import Deck
from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic

DECK_PATH = "decks/pauper-madness-burn.md"

def test_acceptance_10k_games_speed():
    """10,000 goldfish games must complete in under 10 seconds."""
    sim = Simulator()
    start = time.time()
    results = sim.run(DECK_PATH, MadnessBurnHeuristic(), n_games=10_000, seed=0, save_report=False)
    elapsed = time.time() - start
    assert elapsed < 10.0, f"10k games took {elapsed:.2f}s — too slow"
    assert results.n_games == 10_000

def test_acceptance_kill_curve_reasonable():
    """Kill curve must be in expected range for Madness Burn vs goldfish."""
    sim = Simulator()
    results = sim.run(DECK_PATH, MadnessBurnHeuristic(), n_games=5_000, seed=42, save_report=False)
    assert results.avg_kill_turn <= 8.0, f"avg kill turn {results.avg_kill_turn} too slow"
    assert results.avg_kill_turn >= 4.0, f"avg kill turn {results.avg_kill_turn} suspiciously fast"
    assert results.kill_by_turn(7) > 0.70, f"only {results.kill_by_turn(7):.1%} killed by T7"
    assert results.win_rate > 0.80, f"win rate {results.win_rate:.1%} too low for goldfish"

def test_acceptance_hand_quality():
    """Justin's rule must give higher keepable % than strict rule."""
    deck = Deck.from_file(DECK_PATH)
    justin = analyze_hand_quality(deck, JUSTIN_RULE, n_hands=10_000, seed=0)
    strict = analyze_hand_quality(deck, STRICT_RULE, n_hands=10_000, seed=0)
    assert justin.keepable_7 >= strict.keepable_7
    assert 0.30 <= strict.keepable_7 <= 0.99
    assert 0.40 <= justin.keepable_7 <= 0.99

def test_acceptance_analyze_outputs():
    """Analysis output strings are non-empty and contain expected content."""
    sim = Simulator()
    results = sim.run(DECK_PATH, MadnessBurnHeuristic(), n_games=500, seed=1, save_report=False)
    output = analyze_goldfish(results)
    assert len(output) > 100
    assert "Turn" in output
    assert "%" in output

    deck = Deck.from_file(DECK_PATH)
    hq = analyze_hand_quality(deck, JUSTIN_RULE, n_hands=500, seed=1)
    hq_text = hq.format()
    assert "keepable" in hq_text.lower()
    assert "%" in hq_text
