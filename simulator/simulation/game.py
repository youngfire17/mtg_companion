from __future__ import annotations
import copy as _copy
from simulator.core.deck import Deck
from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.rules import legal_actions, apply, draw_card
from simulator.core.actions import PassPriority, DeclareAttackers
from simulator.policies.base import Policy
from simulator.simulation.results import GameResult

MAX_TURNS = 30


def _setup_game(deck: Deck) -> GameState:
    gs = GameState()
    gs.library = list(deck.cards)
    # Draw opening hand of 7
    for _ in range(7):
        gs = draw_card(gs)
    gs.cards_drawn_this_turn = 0  # reset — opening hand doesn't count
    gs.turn = 1
    gs.phase = Phase.MAIN1
    return gs


def _run_action_loop(
    gs: GameState,
    policy: Policy,
    trajectory: list,
    collect: bool,
) -> GameState:
    """Run the policy's action loop until PassPriority or game over."""
    for _ in range(200):  # safety limit prevents infinite loops
        if gs.game_over:
            break
        actions = legal_actions(gs)
        action = policy.act(gs, actions)
        if isinstance(action, PassPriority):
            break
        if collect:
            trajectory.append((_copy.copy(gs), action))
        gs = apply(gs, action)
    return gs


class Game:
    def __init__(self, deck: Deck) -> None:
        self.deck = deck

    def run(
        self,
        policy_a: Policy,
        policy_b: Policy | None = None,
        collect_trajectory: bool = False,
    ) -> GameResult:
        from simulator.policies.goldfish import GoldfishPolicy
        if policy_b is None:
            policy_b = GoldfishPolicy()

        gs = _setup_game(self.deck)
        damage_by_turn: dict[int, int] = {}
        trajectory: list = []
        kill_turn: int | None = None

        for turn in range(1, MAX_TURNS + 1):
            gs.turn = turn
            gs.lands_played = 0
            gs.cards_drawn_this_turn = 0

            # Untap all permanents
            for cs in gs.battlefield:
                cs.tapped = False

            # Draw (skip turn 1 on play)
            if turn > 1:
                gs = draw_card(gs)

            # Main Phase 1
            gs.phase = Phase.MAIN1
            gs = _run_action_loop(gs, policy_a, trajectory, collect_trajectory)
            if gs.game_over:
                kill_turn = turn
                break

            # Combat — simplified: all untapped creatures attack face
            gs.phase = Phase.COMBAT
            actions = legal_actions(gs)
            attack_actions = [a for a in actions if isinstance(a, DeclareAttackers)]
            if attack_actions:
                gs = apply(gs, attack_actions[0])
            if gs.game_over:
                kill_turn = turn
                break

            # Main Phase 2
            gs.phase = Phase.MAIN2
            gs = _run_action_loop(gs, policy_a, trajectory, collect_trajectory)
            if gs.game_over:
                kill_turn = turn
                break

            # End step: discard to 7
            while len(gs.hand) > 7:
                worst = max(gs.hand, key=lambda c: c.cmc)
                gs.hand.remove(worst)
                gs.graveyard.append(worst)

            damage_by_turn[turn] = 20 - gs.opponent_life

        winner = gs.winner if gs.game_over else -1

        return GameResult(
            winner=winner,
            turns=gs.turn,
            kill_turn=kill_turn,
            damage_by_turn=damage_by_turn,
            final_state=gs,
            trajectory=trajectory if collect_trajectory else [],
        )
