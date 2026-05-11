import pytest
from simulator.core.card import Card, load_card, CARD_OVERRIDES

def test_card_loads_from_oracle():
    card = load_card("Lightning Bolt")
    assert card.name == "Lightning Bolt"
    assert card.mana_cost == "{R}"
    assert card.cmc == 1
    assert card.is_instant is True
    assert card.is_land is False
    assert card.damage_on_cast == 3

def test_card_madness_tag():
    card = load_card("Fiery Temper")
    assert card.has_madness is True
    assert card.madness_cost == "{R}"
    assert card.damage_on_cast == 3

def test_card_kessig_tag():
    card = load_card("Kessig Flamebreather")
    assert card.pings_per_noncreature_spell == 1
    assert card.is_creature is True

def test_card_fireblast_alternate_cost():
    card = load_card("Fireblast")
    assert card.has_alternate_cost is True
    assert card.alternate_cost == "sac_2_mountains"
    assert card.damage_on_cast == 4

def test_card_mountain_is_land():
    card = load_card("Mountain")
    assert card.is_land is True

def test_card_sneaky_snacker():
    card = load_card("Sneaky Snacker")
    assert card.snacker_return is True
    assert card.is_creature is True

def test_unknown_card_raises():
    with pytest.raises(KeyError):
        load_card("Nonexistent Card That Does Not Exist XYZ")
