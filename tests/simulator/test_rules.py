import pytest
from simulator.core.card import load_card
from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.actions import CastSpell, PlayLand, PassPriority, AlternateCost, CastMadness
from simulator.core.rules import legal_actions, apply

def _state_with_hand(*card_names: str, lands_in_play: int = 2) -> GameState:
    gs = GameState()
    gs.phase = Phase.MAIN1
    gs.hand = [load_card(n) for n in card_names]
    for _ in range(lands_in_play):
        gs.battlefield.append(CardState(card=load_card("Mountain")))
    return gs

def test_can_play_land_from_hand():
    gs = _state_with_hand("Mountain", lands_in_play=0)
    actions = legal_actions(gs)
    play_land_actions = [a for a in actions if isinstance(a, PlayLand)]
    assert len(play_land_actions) == 1

def test_cannot_play_two_lands():
    gs = _state_with_hand("Mountain", lands_in_play=1)
    gs.lands_played = 1
    actions = legal_actions(gs)
    assert not any(isinstance(a, PlayLand) for a in actions)

def test_can_cast_lightning_bolt_with_mana():
    gs = _state_with_hand("Lightning Bolt", lands_in_play=1)
    actions = legal_actions(gs)
    bolt_casts = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Lightning Bolt"]
    assert len(bolt_casts) == 1

def test_cannot_cast_guttersnipe_without_enough_mana():
    gs = _state_with_hand("Guttersnipe", lands_in_play=2)
    actions = legal_actions(gs)
    casts = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Guttersnipe"]
    assert len(casts) == 0

def test_can_cast_guttersnipe_with_three_lands():
    gs = _state_with_hand("Guttersnipe", lands_in_play=3)
    actions = legal_actions(gs)
    casts = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Guttersnipe"]
    assert len(casts) == 1

def test_cast_lightning_bolt_deals_damage():
    gs = _state_with_hand("Lightning Bolt", lands_in_play=1)
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    new_gs = apply(gs, action)
    assert new_gs.opponent_life == 17

def test_kessig_pings_on_noncreature_spell():
    gs = _state_with_hand("Lightning Bolt", lands_in_play=1)
    gs.battlefield.append(CardState(card=load_card("Kessig Flamebreather")))
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    new_gs = apply(gs, action)
    assert new_gs.opponent_life == 16  # 3 from bolt + 1 from Kessig

def test_madness_discard_goes_to_madness_zone():
    gs = _state_with_hand("Faithless Looting", "Fiery Temper", lands_in_play=1)
    fl = load_card("Faithless Looting")
    temper = load_card("Fiery Temper")
    action = CastSpell(card=fl, cost={"R": 1}, targets=[], discard_card=temper)
    new_gs = apply(gs, action)
    assert temper in new_gs.madness_zone

def test_fireblast_alternate_cost_removes_mountains():
    gs = _state_with_hand("Fireblast", lands_in_play=3)
    gs.opponent_life = 4
    fb = load_card("Fireblast")
    action = AlternateCost(card=fb, targets=["face"])
    new_gs = apply(gs, action)
    assert new_gs.opponent_life == 0
    mountain_count = sum(1 for cs in new_gs.battlefield if cs.card.name == "Mountain")
    assert mountain_count == 1

def test_sneaky_snacker_returns_on_third_draw():
    from simulator.core.rules import draw_card
    snacker = load_card("Sneaky Snacker")
    gs = GameState()
    gs.phase = Phase.DRAW
    gs.graveyard = [snacker]
    gs.library = [load_card("Lightning Bolt")]
    gs.cards_drawn_this_turn = 2
    new_gs = draw_card(gs)
    assert any(cs.card.name == "Sneaky Snacker" for cs in new_gs.battlefield)
    assert snacker not in new_gs.graveyard

def test_game_over_when_opponent_at_zero():
    gs = _state_with_hand("Lightning Bolt", lands_in_play=1)
    gs.opponent_life = 3
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    new_gs = apply(gs, action)
    assert new_gs.game_over is True
    assert new_gs.winner == 0
