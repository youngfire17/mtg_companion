from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.actions import (
    PlayLand, CastSpell, CastMadness, FlashbackSpell,
    AlternateCost, ActivateAbility, DeclareAttackers, PassPriority
)
from simulator.core.card import load_card

def test_initial_game_state():
    gs = GameState.initial()
    assert gs.turn == 1
    assert gs.phase == Phase.DRAW
    assert gs.life == 20
    assert gs.opponent_life == 20
    assert gs.cards_drawn_this_turn == 0

def test_game_state_is_copyable():
    gs = GameState.initial()
    gs2 = gs.copy()
    gs2.opponent_life = 10
    assert gs.opponent_life == 20

def test_actions_are_comparable():
    a1 = PassPriority()
    a2 = PassPriority()
    assert a1 == a2

def test_cast_spell_action():
    bolt = load_card("Lightning Bolt")
    action = CastSpell(card=bolt, cost={"R": 1}, targets=["face"])
    assert action.card.name == "Lightning Bolt"
