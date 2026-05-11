from simulator.policies.base import Policy
from simulator.policies.goldfish import GoldfishPolicy, RandomPolicy
from simulator.core.actions import PassPriority
from simulator.core.game_state import GameState

def test_goldfish_always_passes():
    policy = GoldfishPolicy()
    gs = GameState()
    actions = [PassPriority()]
    result = policy.act(gs, actions)
    assert isinstance(result, PassPriority)

def test_random_picks_from_legal():
    import random
    policy = RandomPolicy(seed=42)
    gs = GameState()
    from simulator.core.actions import PlayLand
    from simulator.core.card import load_card
    actions = [PassPriority(), PlayLand(card=load_card("Mountain"))]
    results = {type(policy.act(gs, actions)).__name__ for _ in range(20)}
    assert len(results) > 1

def test_policy_update_is_no_op():
    policy = GoldfishPolicy()
    policy.update([], 1.0)

def test_policy_value_is_zero():
    policy = GoldfishPolicy()
    gs = GameState()
    assert policy.value(gs) == 0.0

from simulator.policies.heuristic.madness_burn import MadnessBurnHeuristic
from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.card import load_card
from simulator.core.actions import CastSpell, PlayLand, PassPriority, AlternateCost
from simulator.core.rules import legal_actions

def _main1_state(*hand_names: str, lands: int = 2) -> GameState:
    gs = GameState()
    gs.phase = Phase.MAIN1
    gs.hand = [load_card(n) for n in hand_names]
    for _ in range(lands):
        gs.battlefield.append(CardState(card=load_card("Mountain")))
    return gs

def test_heuristic_plays_kessig_before_bolt():
    gs = _main1_state("Kessig Flamebreather", "Lightning Bolt", lands=2)
    policy = MadnessBurnHeuristic()
    actions = legal_actions(gs)
    chosen = policy.act(gs, actions)
    assert isinstance(chosen, CastSpell)
    assert chosen.card.name == "Kessig Flamebreather"

def test_heuristic_plays_land_when_available():
    gs = _main1_state("Mountain", "Lightning Bolt", lands=0)
    policy = MadnessBurnHeuristic()
    actions = legal_actions(gs)
    chosen = policy.act(gs, actions)
    assert isinstance(chosen, PlayLand)

def test_heuristic_fireblasts_at_4_life():
    gs = _main1_state("Fireblast", lands=3)
    gs.opponent_life = 4
    policy = MadnessBurnHeuristic()
    actions = legal_actions(gs)
    chosen = policy.act(gs, actions)
    assert isinstance(chosen, AlternateCost)
    assert chosen.card.name == "Fireblast"

def test_heuristic_does_not_fireblast_when_not_lethal():
    gs = _main1_state("Fireblast", lands=3)
    gs.opponent_life = 10
    policy = MadnessBurnHeuristic()
    actions = legal_actions(gs)
    chosen = policy.act(gs, actions)
    assert not (isinstance(chosen, AlternateCost) and chosen.card.name == "Fireblast")
