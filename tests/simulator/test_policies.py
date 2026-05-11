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
