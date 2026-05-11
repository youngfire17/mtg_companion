import pytest
from simulator.analysis.deck_compare import compare_decks, DeckCompareResults
from simulator.analysis.meta_ev import (
    calculate_meta_ev, MetaEvResults, load_win_rates_from_logs
)
from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic

DECK_PATH = "decks/pauper-madness-burn.md"

SAMPLE_META = {
    "Mirror": 0.107,
    "Blue Terror": 0.097,
    "Elves": 0.069,
    "Affinity": 0.065,
    "Tron": 0.042,
    "Other": 0.620,
}

SAMPLE_WIN_RATES = {
    "Mirror": 0.667,
    "Blue Terror": 0.25,
    "Elves": 0.575,
    "Affinity": 0.75,
    "Tron": 0.667,
    "Other": 0.52,
}

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

def test_meta_ev_calculation():
    results = calculate_meta_ev(SAMPLE_WIN_RATES, SAMPLE_META)
    assert isinstance(results, MetaEvResults)
    assert 0.0 <= results.overall_ev <= 1.0
    assert abs(results.contributions["Mirror"] - 0.107 * 0.667) < 0.001

def test_meta_ev_formats_output():
    results = calculate_meta_ev(SAMPLE_WIN_RATES, SAMPLE_META)
    output = results.format()
    assert "EV" in output or "%" in output
    assert "Mirror" in output
    assert len(output) > 50

def test_meta_ev_sums_correctly():
    results = calculate_meta_ev(SAMPLE_WIN_RATES, SAMPLE_META)
    total = sum(results.contributions.values())
    assert abs(total - results.overall_ev) < 0.001

def test_load_win_rates_from_logs():
    win_rates = load_win_rates_from_logs()
    assert isinstance(win_rates, dict)
    assert len(win_rates) > 0
    for deck, rate in win_rates.items():
        assert 0.0 <= rate <= 1.0, f"{deck}: {rate} out of range"
