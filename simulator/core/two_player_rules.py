from __future__ import annotations
import re
from simulator.core.card import Card, load_card
from simulator.core.game_state import CardState, Phase
from simulator.core.two_player_state import PlayerState, TwoPlayerGameState
from simulator.core.actions import (
    Action, PlayLand, CastSpell, CastMadness, FlashbackSpell,
    AlternateCost, ActivateAbility, DeclareAttackers, DeclareBlockers, PassPriority
)


def _parse_cmc(cost: str) -> int:
    pips = re.findall(r'\{([^}]+)\}', cost)
    total = 0
    for p in pips:
        if p.isdigit():
            total += int(p)
        elif p in ('R', 'G', 'U', 'B', 'W', 'C'):
            total += 1
    return total


def _tap_lands(ps: PlayerState, amount: int) -> None:
    tapped = 0
    for cs in ps.battlefield:
        if tapped >= amount:
            break
        if cs.card.is_land and not cs.tapped:
            cs.tapped = True
            tapped += 1


def _apply_pinger_triggers(state: TwoPlayerGameState, acting: int, spell: Card) -> None:
    is_noncreature = not spell.is_creature
    is_instant_sorcery = spell.is_instant or spell.is_sorcery
    opponent_idx = 1 - acting
    for cs in state.players[acting].battlefield:
        if cs.card.pings_per_noncreature_spell > 0 and is_noncreature:
            state.players[opponent_idx].life -= cs.card.pings_per_noncreature_spell
        if cs.card.pings_per_instant_sorcery > 0 and is_instant_sorcery:
            state.players[opponent_idx].life -= cs.card.pings_per_instant_sorcery


def _check_win(state: TwoPlayerGameState) -> None:
    if state.game_over:
        return
    p0_dead = state.players[0].life <= 0
    p1_dead = state.players[1].life <= 0
    if p0_dead and p1_dead:
        state.game_over = True
        state.winner = state.active_player  # active player wins ties
    elif p1_dead:
        state.game_over = True
        state.winner = 0
    elif p0_dead:
        state.game_over = True
        state.winner = 1


def draw_card_two_player(state: TwoPlayerGameState, player_idx: int) -> TwoPlayerGameState:
    state = state.copy()
    ps = state.players[player_idx]
    if not ps.library:
        return state
    card = ps.library.pop(0)
    ps.hand.append(card)
    ps.cards_drawn_this_turn += 1
    if ps.cards_drawn_this_turn >= 3:
        for grave_card in list(ps.graveyard):
            if grave_card.snacker_return:
                ps.graveyard.remove(grave_card)
                ps.battlefield.append(CardState(card=grave_card, tapped=True))
                break
    return state


def _resolve_spell(
    state: TwoPlayerGameState,
    acting: int,
    card: Card,
    targets: list,
    discard_card: Card | None,
    target_player_idx: int,
    target_card: Card | None,
) -> TwoPlayerGameState:
    target_ps = state.players[target_player_idx]
    acting_ps = state.players[acting]

    # Direct damage to face
    if card.damage_on_cast > 0 and "face" in targets and target_card is None:
        target_ps.life -= card.damage_on_cast

    # Damage to a specific creature (kills it if lethal)
    if card.damage_on_cast > 0 and target_card is not None and "creature" in targets:
        for cs in list(target_ps.battlefield):
            if cs.card.name == target_card.name:
                if card.damage_on_cast >= cs.card.toughness:
                    target_ps.battlefield.remove(cs)
                    target_ps.graveyard.append(cs.card)
                break

    # Grab the Prize bonus damage (nonland discard = 2 damage to each opponent)
    if card.grab_prize_damage > 0 and discard_card and not discard_card.is_land:
        target_ps.life -= card.grab_prize_damage

    # Area damage (End the Festivities)
    if card.damage_each_opponent > 0:
        target_ps.life -= card.damage_each_opponent
    if card.damage_each_opponent_creature > 0:
        dead = [cs for cs in target_ps.battlefield
                if cs.card.is_creature and card.damage_each_opponent_creature >= cs.card.toughness]
        for cs in dead:
            target_ps.battlefield.remove(cs)
            target_ps.graveyard.append(cs.card)

    # Draw effects (acting player draws)
    for _ in range(card.draw_on_cast):
        state = draw_card_two_player(state, acting)
        acting_ps = state.players[acting]

    # Discard effects
    if card.discard_on_cast > 0 and discard_card is not None:
        if discard_card in acting_ps.hand:
            acting_ps.hand.remove(discard_card)
        if discard_card.has_madness:
            acting_ps.madness_zone.append(discard_card)
        else:
            acting_ps.graveyard.append(discard_card)

    # ETB effects (creatures on battlefield)
    if card.damage_on_etb > 0:
        target_ps.life -= card.damage_on_etb
    if card.creates_blood_on_etb:
        acting_ps.blood_tokens += 1

    return state


def legal_main_actions(state: TwoPlayerGameState, player_idx: int) -> list[Action]:
    ps = state.players[player_idx]
    opponent_idx = 1 - player_idx
    opponent = state.players[opponent_idx]
    actions: list[Action] = [PassPriority()]

    available_mana = ps.available_mana

    if ps.lands_played == 0:
        for card in ps.hand:
            if card.is_land:
                actions.append(PlayLand(card=card))

    for card in ps.hand:
        if card.is_land:
            continue
        cmc = _parse_cmc(card.mana_cost)

        # Alternate cost (Fireblast)
        if card.has_alternate_cost and card.alternate_cost == "sac_2_mountains":
            if len(ps.untapped_mountains) >= 2:
                actions.append(AlternateCost(card=card, targets=["face"]))

        if available_mana >= cmc:
            if card.discard_on_cast > 0:
                discard_options = [c for c in ps.hand if c is not card and not c.is_land]
                if not discard_options:
                    discard_options = [c for c in ps.hand if c is not card]
                for dc in discard_options:
                    actions.append(CastSpell(
                        card=card, cost={"R": cmc},
                        targets=["face"] if card.damage_on_cast > 0 else [],
                        discard_card=dc, target_player=opponent_idx,
                    ))
            elif not (card.has_alternate_cost and card.alternate_cost == "sac_2_mountains"):
                if card.damage_any_target and card.damage_on_cast > 0:
                    # Face target
                    actions.append(CastSpell(card=card, cost={"R": cmc},
                                             targets=["face"], target_player=opponent_idx))
                    # Creature targets
                    for cs in opponent.creatures:
                        actions.append(CastSpell(card=card, cost={"R": cmc},
                                                 targets=["creature"],
                                                 target_player=opponent_idx,
                                                 target_card=cs.card))
                else:
                    actions.append(CastSpell(card=card, cost={"R": cmc},
                                             targets=[], target_player=opponent_idx))

    # Madness zone
    for card in ps.madness_zone:
        actions.append(CastMadness(card=card, madness_cost=card.madness_cost,
                                   targets=["face"]))

    # Flashback
    for card in ps.graveyard:
        if not card.has_flashback:
            continue
        if card.flashback_cost == "sac_mountain":
            if len(ps.untapped_mountains) > 0:
                actions.append(FlashbackSpell(card=card, targets=["face"]))
        else:
            fc = _parse_cmc(card.flashback_cost)
            if available_mana >= fc:
                actions.append(FlashbackSpell(card=card, targets=["face"]))

    # Blood token
    if ps.blood_tokens > 0:
        for dc in ps.hand:
            actions.append(ActivateAbility(
                source=load_card("Voldaren Epicure"),
                ability_index=0, discard_card=dc,
            ))

    return actions


def legal_instant_actions(state: TwoPlayerGameState, player_idx: int) -> list[Action]:
    all_actions = legal_main_actions(state, player_idx)
    result = []
    for a in all_actions:
        if isinstance(a, PassPriority):
            result.append(a)
        elif isinstance(a, CastSpell) and (a.card.is_instant or a.card.has_madness):
            result.append(a)
        elif isinstance(a, (CastMadness, FlashbackSpell, ActivateAbility)):
            result.append(a)
        elif isinstance(a, AlternateCost) and a.card.is_instant:
            result.append(a)
    return result


def apply_two_player(
    state: TwoPlayerGameState,
    action: Action,
    acting_player: int,
) -> TwoPlayerGameState:
    state = state.copy()
    ps = state.players[acting_player]
    opponent_idx = 1 - acting_player

    match action:
        case PassPriority():
            pass

        case PlayLand(card=card):
            ps.hand.remove(card)
            ps.battlefield.append(CardState(card=card))
            ps.lands_played += 1

        case CastSpell(card=card, cost=cost, targets=targets, discard_card=dc,
                       target_player=tp, target_card=tc):
            ps.hand.remove(card)
            _tap_lands(ps, sum(cost.values()))
            _apply_pinger_triggers(state, acting_player, card)
            if not card.is_creature and not card.is_artifact and not card.is_enchantment:
                ps.graveyard.append(card)
            else:
                ps.battlefield.append(CardState(card=card))
            state = _resolve_spell(state, acting_player, card, targets, dc, tp, tc)
            _check_win(state)

        case CastMadness(card=card, madness_cost=cost, targets=targets):
            if card in ps.madness_zone:
                ps.madness_zone.remove(card)
            _tap_lands(ps, _parse_cmc(cost))
            _apply_pinger_triggers(state, acting_player, card)
            ps.graveyard.append(card)
            state = _resolve_spell(state, acting_player, card, targets, None, opponent_idx, None)
            _check_win(state)

        case FlashbackSpell(card=card, targets=targets):
            ps.graveyard.remove(card)
            if card.flashback_cost == "sac_mountain":
                for cs in ps.battlefield:
                    if cs.card.name == "Mountain":
                        ps.battlefield.remove(cs)
                        ps.graveyard.append(cs.card)
                        break
            else:
                _tap_lands(ps, _parse_cmc(card.flashback_cost))
            _apply_pinger_triggers(state, acting_player, card)
            ps.exile.append(card)
            state = _resolve_spell(state, acting_player, card, targets, None, opponent_idx, None)
            _check_win(state)

        case AlternateCost(card=card, targets=targets):
            ps.hand.remove(card)
            removed = 0
            for cs in list(ps.battlefield):
                if removed >= 2:
                    break
                if cs.card.name == "Mountain":
                    ps.battlefield.remove(cs)
                    ps.graveyard.append(cs.card)
                    removed += 1
            _apply_pinger_triggers(state, acting_player, card)
            ps.graveyard.append(card)
            state = _resolve_spell(state, acting_player, card, targets, None, opponent_idx, None)
            _check_win(state)

        case ActivateAbility(discard_card=dc):
            if dc and dc in ps.hand:
                ps.hand.remove(dc)
                if dc.has_madness:
                    ps.madness_zone.append(dc)
                else:
                    ps.graveyard.append(dc)
            ps.blood_tokens -= 1
            state = draw_card_two_player(state, acting_player)

    return state


def resolve_combat_damage(state: TwoPlayerGameState) -> TwoPlayerGameState:
    state = state.copy()
    active = state.active_player
    inactive = 1 - active
    active_ps = state.players[active]
    inactive_ps = state.players[inactive]

    blocked_attacker_names = {c.name for c in state.declared_blocks.values()}

    # Resolve blocks
    for blocker_card, attacker_card in list(state.declared_blocks.items()):
        blocker_cs = next((cs for cs in inactive_ps.battlefield
                           if cs.card.name == blocker_card.name), None)
        attacker_cs = next((cs for cs in active_ps.battlefield
                            if cs.card.name == attacker_card.name), None)
        if not blocker_cs or not attacker_cs:
            continue
        attacker_dies = blocker_cs.card.power >= attacker_cs.card.toughness
        blocker_dies = attacker_cs.card.power >= blocker_cs.card.toughness
        if attacker_dies:
            active_ps.battlefield.remove(attacker_cs)
            active_ps.graveyard.append(attacker_cs.card)
        if blocker_dies:
            inactive_ps.battlefield.remove(blocker_cs)
            inactive_ps.graveyard.append(blocker_cs.card)

    # Unblocked damage
    for attacker_card in state.declared_attackers:
        if attacker_card.name not in blocked_attacker_names:
            inactive_ps.life -= attacker_card.power

    _check_win(state)
    return state
