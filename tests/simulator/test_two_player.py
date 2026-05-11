import pytest
from simulator.core.actions import DeclareBlockers, CastSpell, PlayLand, CastMadness, AlternateCost, PassPriority
from simulator.core.card import load_card
from simulator.core.two_player_state import PlayerState, TwoPlayerGameState
from simulator.core.game_state import CardState, Phase
from simulator.core.two_player_rules import (
    legal_main_actions, legal_instant_actions,
    apply_two_player, draw_card_two_player,
    resolve_combat_damage,
)


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


# ---------------------------------------------------------------------------
# Task 2: Two-player rules engine tests
# ---------------------------------------------------------------------------

def test_legal_main_actions_includes_pass():
    state = _state()
    actions = legal_main_actions(state, 0)
    assert any(isinstance(a, PassPriority) for a in actions)


def test_legal_main_can_play_land():
    state = _state()
    state.players[0].hand = [load_card("Mountain")]
    state.players[0].battlefield = []
    actions = legal_main_actions(state, 0)
    assert any(isinstance(a, PlayLand) for a in actions)


def test_legal_main_can_cast_bolt_with_mana():
    state = _state()
    state.players[0].hand = [load_card("Lightning Bolt")]
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    actions = legal_main_actions(state, 0)
    bolt_actions = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Lightning Bolt"]
    assert len(bolt_actions) >= 1
    assert all(a.target_player == 1 for a in bolt_actions)


def test_legal_main_bolt_can_target_opponent_creature():
    state = _state()
    state.players[0].hand = [load_card("Lightning Bolt")]
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    state.players[1].battlefield = [CardState(card=load_card("Kessig Flamebreather"))]
    actions = legal_main_actions(state, 0)
    bolt_actions = [a for a in actions if isinstance(a, CastSpell) and a.card.name == "Lightning Bolt"]
    assert len(bolt_actions) == 2
    creature_targets = [a for a in bolt_actions if a.target_card is not None]
    assert len(creature_targets) == 1
    assert creature_targets[0].target_card.name == "Kessig Flamebreather"


def test_legal_instant_filters_sorceries():
    state = _state()
    state.players[0].hand = [load_card("Faithless Looting"), load_card("Lightning Bolt")]
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    instant_actions = legal_instant_actions(state, 0)
    fl_actions = [a for a in instant_actions if isinstance(a, CastSpell) and a.card.name == "Faithless Looting"]
    assert len(fl_actions) == 0
    bolt_actions = [a for a in instant_actions if isinstance(a, CastSpell) and a.card.name == "Lightning Bolt"]
    assert len(bolt_actions) >= 1


def test_apply_bolt_to_opponent_face():
    state = _state(life_b=20)
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    state.players[0].hand = [load_card("Lightning Bolt")]
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"], target_player=1)
    new_state = apply_two_player(state, action, acting_player=0)
    assert new_state.players[1].life == 17


def test_apply_bolt_to_opponent_creature():
    state = _state()
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    state.players[0].hand = [load_card("Lightning Bolt")]
    kessig = load_card("Kessig Flamebreather")
    state.players[1].battlefield = [CardState(card=kessig)]
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["creature"], target_player=1, target_card=kessig)
    new_state = apply_two_player(state, action, acting_player=0)
    assert not new_state.players[1].has_creature("Kessig Flamebreather")
    assert any(c.name == "Kessig Flamebreather" for c in new_state.players[1].graveyard)


def test_apply_kessig_pings_opponent_on_noncreature():
    state = _state()
    state.players[0].battlefield = [
        CardState(card=load_card("Mountain")),
        CardState(card=load_card("Kessig Flamebreather")),
    ]
    state.players[0].hand = [load_card("Lightning Bolt")]
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"], target_player=1)
    new_state = apply_two_player(state, action, acting_player=0)
    assert new_state.players[1].life == 16


def test_draw_card_two_player():
    state = _state()
    state.players[0].library = [load_card("Lightning Bolt"), load_card("Mountain")]
    new_state = draw_card_two_player(state, 0)
    assert len(new_state.players[0].hand) == 1
    assert new_state.players[0].hand[0].name == "Lightning Bolt"
    assert new_state.players[0].cards_drawn_this_turn == 1


def test_game_over_when_opponent_reaches_zero():
    state = _state(life_b=3)
    state.players[0].battlefield = [CardState(card=load_card("Mountain"))]
    state.players[0].hand = [load_card("Lightning Bolt")]
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"], target_player=1)
    new_state = apply_two_player(state, action, acting_player=0)
    assert new_state.game_over is True
    assert new_state.winner == 0


# ---------------------------------------------------------------------------
# Task 3: Integration tests for combat sequences
# ---------------------------------------------------------------------------

def test_full_attack_sequence():
    """Unblocked Kessig (1/3) attacks and deals 1 damage to opponent's life."""
    state = _state(life_a=20, life_b=20)
    kessig = load_card("Kessig Flamebreather")
    state.players[0].battlefield = [CardState(card=kessig)]
    state.declared_attackers = [kessig]
    state.declared_blocks = {}

    new_state = resolve_combat_damage(state)
    assert new_state.players[1].life == 19
    assert new_state.game_over is False


def test_blocking_kills_attacker():
    """Snacker (2/1) blocked by Kessig (1/3): Snacker dies, Kessig survives."""
    state = _state(life_a=20, life_b=20)
    kessig = load_card("Kessig Flamebreather")   # 1/3
    snacker = load_card("Sneaky Snacker")          # 2/1
    state.players[0].battlefield = [CardState(card=snacker)]
    state.declared_attackers = [snacker]
    state.players[1].battlefield = [CardState(card=kessig)]
    state.declared_blocks = {kessig: snacker}

    new_state = resolve_combat_damage(state)
    # Snacker (2/1) takes 1 damage from Kessig → dies (1 >= 1 toughness)
    assert not new_state.players[0].has_creature("Sneaky Snacker")
    # Kessig (1/3) takes 2 damage from Snacker → survives (2 < 3 toughness)
    assert new_state.players[1].has_creature("Kessig Flamebreather")
    assert new_state.players[1].life == 20  # no unblocked damage


def test_snacker_survives_blocking_epicure():
    """Sneaky Snacker (2/1) blocks Voldaren Epicure (1/1): Snacker survives, Epicure dies."""
    state = _state(life_a=20, life_b=20)
    epicure = load_card("Voldaren Epicure")   # 1/1
    snacker = load_card("Sneaky Snacker")     # 2/1
    state.players[0].battlefield = [CardState(card=epicure)]
    state.declared_attackers = [epicure]
    state.players[1].battlefield = [CardState(card=snacker)]
    state.declared_blocks = {snacker: epicure}

    new_state = resolve_combat_damage(state)
    # Epicure (1/1) takes 2 damage from Snacker → dies
    assert not new_state.players[0].has_creature("Voldaren Epicure")
    # Snacker (2/1) takes 1 damage from Epicure → both die (1 >= 1 toughness)
    assert not new_state.players[1].has_creature("Sneaky Snacker")
    assert new_state.players[1].life == 20
