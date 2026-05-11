import pytest
from simulator.core.deck import Deck
from simulator.simulation.game import Game
from simulator.policies.goldfish import GoldfishPolicy
from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic

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
