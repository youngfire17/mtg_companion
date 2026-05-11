from simulator.simulation.simulator import Simulator
from simulator.analysis.goldfish_analysis import analyze_goldfish
from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic
from simulator.analysis.hand_quality import (
    KeepCriteria, analyze_hand_quality, JUSTIN_RULE, STRICT_RULE
)
from simulator.core.deck import Deck

DECK_PATH = "decks/pauper-madness-burn.md"

def test_goldfish_analysis_returns_string():
    sim = Simulator()
    results = sim.run(DECK_PATH, MadnessBurnHeuristic(), n_games=500, seed=42, save_report=False)
    output = analyze_goldfish(results)
    assert isinstance(output, str)
    assert "kill turn" in output.lower() or "Turn" in output
    assert "%" in output

def test_goldfish_analysis_reasonable_numbers():
    sim = Simulator()
    results = sim.run(DECK_PATH, MadnessBurnHeuristic(), n_games=1000, seed=42, save_report=False)
    assert results.kill_by_turn(6) > 0.50
    assert 4.0 <= results.avg_kill_turn <= 8.0

def test_hand_quality_returns_results():
    deck = Deck.from_file(DECK_PATH)
    result = analyze_hand_quality(deck, STRICT_RULE, n_hands=1000, seed=42)
    assert 0.0 <= result.keepable_7 <= 1.0
    assert 0.0 <= result.keepable_6 <= 1.0
    assert result.keepable_6 <= result.keepable_7

def test_justin_rule_more_lenient_than_strict():
    deck = Deck.from_file(DECK_PATH)
    strict = analyze_hand_quality(deck, STRICT_RULE, n_hands=2000, seed=1)
    justin = analyze_hand_quality(deck, JUSTIN_RULE, n_hands=2000, seed=1)
    assert justin.keepable_7 >= strict.keepable_7

def test_hand_quality_formats_output():
    deck = Deck.from_file(DECK_PATH)
    result = analyze_hand_quality(deck, JUSTIN_RULE, n_hands=500, seed=7)
    text = result.format()
    assert "keepable" in text.lower()
    assert "%" in text
