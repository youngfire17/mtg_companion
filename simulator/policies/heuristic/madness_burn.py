from __future__ import annotations
from simulator.policies.base import Policy
from simulator.core.game_state import GameState
from simulator.core.actions import (
    Action, PlayLand, CastSpell, CastMadness, FlashbackSpell,
    AlternateCost, ActivateAbility, DeclareAttackers, PassPriority
)

_DISCARD_PRIORITY = [
    "Sneaky Snacker",   # discard first — sets up free GY return
    "Fiery Temper",     # madness {R} is great value
    "Guttersnipe",      # can be discarded if stuck
]


def _best_discard_action(spell_casts: list[CastSpell]) -> CastSpell | None:
    """Among CastSpell actions that require a discard, pick the one with best discard choice."""
    if not spell_casts:
        return None
    # Prefer actions that discard a madness card or Sneaky Snacker
    for name in _DISCARD_PRIORITY:
        for a in spell_casts:
            if a.discard_card and a.discard_card.name == name:
                return a
    return spell_casts[0]


class MadnessBurnHeuristic(Policy):
    """Plays Madness Burn optimally against a goldfish opponent."""

    def act(self, state: GameState, legal_actions: list[Action]) -> Action:
        # 1. Resolve pending madness first
        madness_casts = [a for a in legal_actions if isinstance(a, CastMadness)]
        if madness_casts:
            return madness_casts[0]

        # 2. Play a land
        land_plays = [a for a in legal_actions if isinstance(a, PlayLand)]
        if land_plays:
            return land_plays[0]

        # 3. Fireblast only if lethal this turn
        fb_actions = [a for a in legal_actions
                      if isinstance(a, AlternateCost) and a.card.name == "Fireblast"]
        if fb_actions and state.opponent_life <= 4:
            return fb_actions[0]

        spell_casts = [a for a in legal_actions if isinstance(a, CastSpell)]

        # 4. Kessig if not on battlefield
        if not state.has_creature("Kessig Flamebreather"):
            kessig = [a for a in spell_casts if a.card.name == "Kessig Flamebreather"]
            if kessig:
                return kessig[0]

        # 5. Discard-outlet spells — prefer if they can trigger madness
        discard_spells_with_madness = []
        for name in ("Grab the Prize", "Highway Robbery", "Faithless Looting"):
            candidates = [a for a in spell_casts
                          if a.card.name == name
                          and a.discard_card
                          and a.discard_card.has_madness]
            discard_spells_with_madness.extend(candidates)
        if discard_spells_with_madness:
            return discard_spells_with_madness[0]

        # 6. Guttersnipe if Kessig already in play
        if state.has_creature("Kessig Flamebreather"):
            gut = [a for a in spell_casts if a.card.name == "Guttersnipe"]
            if gut:
                return gut[0]

        # 7. Draw spells (Grab the Prize > Highway Robbery)
        for name in ("Grab the Prize", "Highway Robbery", "Faithless Looting"):
            found = [a for a in spell_casts if a.card.name == name]
            if found:
                # Prefer discarding Sneaky Snacker if available
                for a in found:
                    if a.discard_card and a.discard_card.name == "Sneaky Snacker":
                        return a
                return found[0]

        # 8. Burn spells at face (highest damage first)
        burn = sorted(
            [a for a in spell_casts if a.card.damage_on_cast > 0],
            key=lambda a: -a.card.damage_on_cast,
        )
        if burn:
            return burn[0]

        # 9. Flashback
        flashback = [a for a in legal_actions if isinstance(a, FlashbackSpell)]
        if flashback:
            return flashback[0]

        # 10. Declare attackers
        attack = [a for a in legal_actions if isinstance(a, DeclareAttackers)]
        if attack:
            return attack[0]

        return PassPriority()
