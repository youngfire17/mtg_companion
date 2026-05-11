import pytest
import time
from simulator.core.deck import Deck
from simulator.simulation.game import Game
from simulator.policies.goldfish import GoldfishPolicy
from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic
from simulator.simulation.simulator import Simulator

DECK_PATH = "decks/pauper-madness-burn.md"

def test_game_terminates():
    deck = Deck.from_file(DECK_PATH)
    deck.shuffle(seed=42)
    game = Game(deck)
    result = game.run(MadnessBurnHeuristic(), GoldfishPolicy())
    assert result.turns <= 30
    assert result.winner in (0, 1, -1)

def test_goldfish_game_player_wins():
    wins = 0
    for seed in range(20):
        deck = Deck.from_file(DECK_PATH)
        deck.shuffle(seed=seed)
        result = Game(deck).run(MadnessBurnHeuristic(), GoldfishPolicy())
        if result.winner == 0:
            wins += 1
    assert wins >= 15

def test_game_result_has_kill_turn():
    deck = Deck.from_file(DECK_PATH)
    deck.shuffle(seed=1)
    result = Game(deck).run(MadnessBurnHeuristic(), GoldfishPolicy())
    if result.winner == 0:
        assert result.kill_turn is not None
        assert 1 <= result.kill_turn <= 30

def test_game_draws_opening_hand():
    deck = Deck.from_file(DECK_PATH)
    deck.shuffle(seed=5)
    result = Game(deck).run(MadnessBurnHeuristic(), GoldfishPolicy())
    assert result.final_state.turn >= 1

def test_simulator_runs_n_games():
    sim = Simulator()
    results = sim.run("decks/pauper-madness-burn.md", MadnessBurnHeuristic(), n_games=100, seed=42, save_report=False)
    assert results.n_games == 100
    assert results.wins + results.losses + results.timeouts == 100

def test_simulator_speed():
    sim = Simulator()
    start = time.time()
    results = sim.run("decks/pauper-madness-burn.md", MadnessBurnHeuristic(), n_games=1000, seed=0, save_report=False)
    elapsed = time.time() - start
    assert elapsed < 15.0, f"1000 games took {elapsed:.2f}s"
    assert results.win_rate > 0.5

def test_simulator_reproducible_with_seed():
    sim = Simulator()
    r1 = sim.run("decks/pauper-madness-burn.md", MadnessBurnHeuristic(), n_games=50, seed=99, save_report=False)
    r2 = sim.run("decks/pauper-madness-burn.md", MadnessBurnHeuristic(), n_games=50, seed=99, save_report=False)
    assert r1.wins == r2.wins
