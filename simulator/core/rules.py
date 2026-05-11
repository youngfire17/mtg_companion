from __future__ import annotations
import copy
import re
from simulator.core.card import Card, load_card
from simulator.core.game_state import GameState, CardState, Phase
from simulator.core.actions import (
    Action, PlayLand, CastSpell, CastMadness, FlashbackSpell,
    AlternateCost, ActivateAbility, DeclareAttackers, PassPriority
)


def _parse_cmc(cost: str) -> int:
    """Parse '{1}{R}' style mana cost string into total mana count."""
    pips = re.findall(r'\{([^}]+)\}', cost)
    total = 0
    for p in pips:
        if p.isdigit():
            total += int(p)
        elif p in ('R', 'G', 'U', 'B', 'W', 'C'):
            total += 1
    return total


def draw_card(gs: GameState) -> GameState:
    """Draw top card from library. Fire Sneaky Snacker trigger at 3rd draw."""
    gs = gs.copy()
    if not gs.library:
        return gs
    card = gs.library.pop(0)
    gs.hand.append(card)
    gs.cards_drawn_this_turn += 1
    if gs.cards_drawn_this_turn >= 3:
        for grave_card in list(gs.graveyard):
            if grave_card.snacker_return:
                gs.graveyard.remove(grave_card)
                gs.battlefield.append(CardState(card=grave_card, tapped=True))
                break
    return gs


def _tap_lands_for_mana(gs: GameState, amount: int) -> GameState:
    """Tap `amount` untapped lands."""
    tapped = 0
    for cs in gs.battlefield:
        if tapped >= amount:
            break
        if cs.card.is_land and not cs.tapped:
            cs.tapped = True
            gs.mana_pool["R"] = gs.mana_pool.get("R", 0) + 1
            tapped += 1
    return gs


def _apply_pinger_triggers(gs: GameState, spell_card: Card) -> GameState:
    """Fire Kessig Flamebreather and Guttersnipe triggers."""
    is_noncreature = not spell_card.is_creature
    is_instant_sorcery = spell_card.is_instant or spell_card.is_sorcery
    for cs in gs.battlefield:
        if cs.card.pings_per_noncreature_spell > 0 and is_noncreature:
            gs.opponent_life -= cs.card.pings_per_noncreature_spell
        if cs.card.pings_per_instant_sorcery > 0 and is_instant_sorcery:
            gs.opponent_life -= cs.card.pings_per_instant_sorcery
    return gs


def _check_win(gs: GameState) -> GameState:
    if gs.opponent_life <= 0 and not gs.game_over:
        gs.game_over = True
        gs.winner = 0
    return gs


def _resolve_spell(
    gs: GameState,
    card: Card,
    targets: list,
    discard_card: Card | None = None,
) -> GameState:
    """Apply spell effects. Card is already in graveyard/battlefield."""
    if card.damage_on_cast > 0 and "face" in targets:
        gs.opponent_life -= card.damage_on_cast

    if card.grab_prize_damage > 0 and discard_card and not discard_card.is_land:
        gs.opponent_life -= card.grab_prize_damage

    if card.damage_each_opponent > 0:
        gs.opponent_life -= card.damage_each_opponent

    # Draw happens BEFORE discard (e.g. Faithless Looting draws 2 then discards 2)
    for _ in range(card.draw_on_cast):
        gs = draw_card(gs)

    if card.discard_on_cast > 0 and discard_card is not None:
        if discard_card in gs.hand:
            gs.hand.remove(discard_card)
        if discard_card.has_madness:
            gs.madness_zone.append(discard_card)
        else:
            gs.graveyard.append(discard_card)

    if card.damage_on_etb > 0:
        gs.opponent_life -= card.damage_on_etb

    if card.creates_blood_on_etb:
        gs.blood_tokens += 1

    return gs


def legal_actions(gs: GameState) -> list[Action]:
    actions: list[Action] = [PassPriority()]

    if gs.game_over:
        return actions

    if gs.phase in (Phase.MAIN1, Phase.MAIN2):
        available_mana = len(gs.untapped_lands)

        if gs.lands_played == 0:
            for card in gs.hand:
                if card.is_land:
                    actions.append(PlayLand(card=card))

        for card in gs.hand:
            if card.is_land:
                continue
            cmc = _parse_cmc(card.mana_cost)

            # Alternate cost option (e.g. Fireblast: sac 2 Mountains)
            if card.has_alternate_cost and card.alternate_cost == "sac_2_mountains":
                mountain_count = sum(
                    1 for cs in gs.battlefield
                    if cs.card.name == "Mountain" and not cs.tapped
                )
                if mountain_count >= 2:
                    actions.append(AlternateCost(card=card, targets=["face"]))

            # Normal mana cost cast — skip if this card only has alternate cost
            if available_mana >= cmc:
                if card.discard_on_cast > 0:
                    # Need a discard target (other card in hand)
                    discard_options = [c for c in gs.hand if c is not card and not c.is_land]
                    if not discard_options:
                        discard_options = [c for c in gs.hand if c is not card]
                    for dc in discard_options:
                        actions.append(CastSpell(
                            card=card,
                            cost={"R": cmc},
                            targets=["face"] if card.damage_on_cast > 0 else [],
                            discard_card=dc,
                        ))
                else:
                    # Don't add a normal-cost action if the card is alternate-cost-only
                    if not (card.has_alternate_cost and card.alternate_cost == "sac_2_mountains"):
                        actions.append(CastSpell(
                            card=card,
                            cost={"R": cmc},
                            targets=["face"] if card.damage_on_cast > 0 else [],
                        ))

        # Madness zone casts
        for card in gs.madness_zone:
            actions.append(CastMadness(
                card=card,
                madness_cost=card.madness_cost,
                targets=["face"] if card.damage_on_cast > 0 else [],
            ))

        # Flashback casts from graveyard
        for card in gs.graveyard:
            if not card.has_flashback:
                continue
            if card.flashback_cost == "sac_mountain":
                if gs.mountains_on_battlefield > 0:
                    actions.append(FlashbackSpell(card=card, targets=["face"]))
            else:
                fc = _parse_cmc(card.flashback_cost)
                if available_mana >= fc:
                    actions.append(FlashbackSpell(card=card, targets=["face"]))

        # Blood token activations
        if gs.blood_tokens > 0:
            for dc in gs.hand:
                actions.append(ActivateAbility(
                    source=load_card("Voldaren Epicure"),
                    ability_index=0,
                    discard_card=dc,
                ))

    if gs.phase == Phase.COMBAT:
        untapped_creatures = [cs for cs in gs.battlefield
                              if cs.card.is_creature and not cs.tapped]
        if untapped_creatures:
            actions.append(DeclareAttackers(
                creatures=[cs.card for cs in untapped_creatures]
            ))

    return actions


def apply(gs: GameState, action: Action) -> GameState:
    gs = gs.copy()

    match action:
        case PassPriority():
            pass

        case PlayLand(card=card):
            gs.hand.remove(card)
            gs.battlefield.append(CardState(card=card))
            gs.lands_played += 1

        case CastSpell(card=card, cost=cost, targets=targets, discard_card=dc):
            gs.hand.remove(card)
            cmc = sum(cost.values())
            gs = _tap_lands_for_mana(gs, cmc)
            gs = _apply_pinger_triggers(gs, card)
            # Permanents go to battlefield; instants/sorceries go to graveyard
            if not card.is_creature and not card.is_artifact and not card.is_enchantment:
                gs.graveyard.append(card)
            else:
                gs.battlefield.append(CardState(card=card))
            gs = _resolve_spell(gs, card, targets, dc)
            gs = _check_win(gs)

        case CastMadness(card=card, madness_cost=cost, targets=targets):
            if card in gs.madness_zone:
                gs.madness_zone.remove(card)
            mc = _parse_cmc(cost)
            gs = _tap_lands_for_mana(gs, mc)
            gs = _apply_pinger_triggers(gs, card)
            gs.graveyard.append(card)
            gs = _resolve_spell(gs, card, targets)
            gs = _check_win(gs)

        case FlashbackSpell(card=card, targets=targets):
            gs.graveyard.remove(card)
            if card.flashback_cost == "sac_mountain":
                for cs in gs.battlefield:
                    if cs.card.name == "Mountain":
                        gs.battlefield.remove(cs)
                        gs.graveyard.append(cs.card)
                        break
            else:
                fc = _parse_cmc(card.flashback_cost)
                gs = _tap_lands_for_mana(gs, fc)
            gs = _apply_pinger_triggers(gs, card)
            gs.exile.append(card)
            gs = _resolve_spell(gs, card, targets)
            gs = _check_win(gs)

        case AlternateCost(card=card, targets=targets):
            gs.hand.remove(card)
            removed = 0
            for cs in list(gs.battlefield):
                if removed >= 2:
                    break
                if cs.card.name == "Mountain":
                    gs.battlefield.remove(cs)
                    gs.graveyard.append(cs.card)
                    removed += 1
            gs = _apply_pinger_triggers(gs, card)
            gs.graveyard.append(card)
            gs = _resolve_spell(gs, card, targets)
            gs = _check_win(gs)

        case ActivateAbility(source=_, ability_index=_, discard_card=dc):
            if dc and dc in gs.hand:
                gs.hand.remove(dc)
                if dc.has_madness:
                    gs.madness_zone.append(dc)
                else:
                    gs.graveyard.append(dc)
            gs.blood_tokens -= 1
            gs = draw_card(gs)

        case DeclareAttackers(creatures=creatures):
            total_power = sum(c.power for c in creatures)
            gs.opponent_life -= total_power
            gs = _check_win(gs)

    return gs
