from simulator.simulation.simulator import Simulator
from simulator.analysis.goldfish_analysis import analyze_goldfish
from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic

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
