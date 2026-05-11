import pytest
from simulator.core.actions import DeclareBlockers, CastSpell
from simulator.core.card import load_card
from simulator.core.two_player_state import PlayerState, TwoPlayerGameState
from simulator.core.game_state import CardState, Phase


def _player(life: int = 20, hand_names: list[str] = None, lands: int = 3) -> PlayerState:
    hand = [load_card(n) for n in (hand_names or [])]
    battlefield = [CardState(card=load_card("Mountain")) for _ in range(lands)]
    return PlayerState(
        library=[], hand=hand, battlefield=battlefield,
        graveyard=[], exile=[], madness_zone=[],
        blood_tokens=0, life=life,
        lands_played=0, cards_drawn_this_turn=0,
    )


def _state(life_a: int = 20, life_b: int = 20) -> TwoPlayerGameState:
    return TwoPlayerGameState(
        players=[_player(life=life_a), _player(life=life_b)],
        active_player=0,
        priority_player=0,
        phase=Phase.MAIN1,
        turn=1,
        declared_attackers=[],
        declared_blocks={},
        last_pass=[False, False],
        game_over=False,
        winner=-1,
    )


def test_player_state_properties():
    ps = _player(lands=3)
    assert ps.available_mana == 3
    assert len(ps.untapped_lands) == 3
    assert ps.has_creature("Kessig Flamebreather") is False


def test_player_state_with_creatures():
    ps = _player()
    ps.battlefield.append(CardState(card=load_card("Kessig Flamebreather")))
    assert ps.has_creature("Kessig Flamebreather") is True
    assert len(ps.creatures) == 1


def test_two_player_state_properties():
    state = _state()
    assert state.active is state.players[0]
    assert state.inactive is state.players[1]
    assert state.priority is state.players[0]


def test_two_player_state_copy_is_independent():
    state = _state(life_a=20, life_b=20)
    copy = state.copy()
    copy.players[0].life = 10
    assert state.players[0].life == 20


def test_declare_blockers_action():
    kessig = load_card("Kessig Flamebreather")
    snacker = load_card("Sneaky Snacker")
    action = DeclareBlockers(assignments={snacker: kessig})
    assert snacker in action.assignments
    assert action.assignments[snacker] is kessig


def test_cast_spell_has_target_player():
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"], target_player=1)
    assert action.target_player == 1
    assert action.target_card is None


def test_cast_spell_target_player_defaults_to_one():
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    assert action.target_player == 1
