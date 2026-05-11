import pytest
from simulator.core.deck import Deck

DECK_PATH = "decks/pauper-madness-burn.md"

def test_deck_loads_60_cards():
    deck = Deck.from_file(DECK_PATH)
    assert len(deck.cards) == 60

def test_deck_has_mountains():
    deck = Deck.from_file(DECK_PATH)
    mountains = [c for c in deck.cards if c.name == "Mountain"]
    assert len(mountains) == 18

def test_deck_has_4_lightning_bolts():
    deck = Deck.from_file(DECK_PATH)
    bolts = [c for c in deck.cards if c.name == "Lightning Bolt"]
    assert len(bolts) == 4

def test_deck_copy_is_independent():
    deck = Deck.from_file(DECK_PATH)
    copy = deck.copy()
    copy.cards.pop()
    assert len(deck.cards) == 60

def test_deck_draw_removes_from_library():
    deck = Deck.from_file(DECK_PATH)
    deck.shuffle(seed=42)
    top = deck.cards[0]
    drawn = deck.draw()
    assert drawn.name == top.name
    assert len(deck.cards) == 59
