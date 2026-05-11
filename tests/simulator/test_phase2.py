import pytest
from simulator.analysis.deck_compare import compare_decks, DeckCompareResults
from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic

DECK_PATH = "decks/pauper-madness-burn.md"

def test_compare_returns_results():
    results = compare_decks(
        deck_path_a=DECK_PATH,
        label_a="Standard",
        deck_path_b=DECK_PATH,
        label_b="Same",
        policy=MadnessBurnHeuristic(),
        n_games=200,
        seed=42,
    )
    assert isinstance(results, DeckCompareResults)
    assert results.n_games == 200
    assert abs(results.avg_kill_a - results.avg_kill_b) < 1.0

def test_compare_formats_output():
    results = compare_decks(
        deck_path_a=DECK_PATH,
        label_a="Deck A",
        deck_path_b=DECK_PATH,
        label_b="Deck B",
        policy=MadnessBurnHeuristic(),
        n_games=200,
        seed=1,
    )
    output = results.format()
    assert "Deck A" in output
    assert "Deck B" in output
    assert "kill" in output.lower()
    assert "%" in output

def test_compare_statistical_fields():
    results = compare_decks(
        deck_path_a=DECK_PATH,
        label_a="A",
        deck_path_b=DECK_PATH,
        label_b="B",
        policy=MadnessBurnHeuristic(),
        n_games=300,
        seed=7,
    )
    assert hasattr(results, "p_value")
    assert 0.0 <= results.p_value <= 1.0
    assert hasattr(results, "significant")
    assert hasattr(results, "recommendation")
