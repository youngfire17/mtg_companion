from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Callable
from simulator.core.card import Card
from simulator.core.deck import Deck


@dataclass
class KeepCriteria:
    min_lands: int = 2
    requires_discard_outlet: bool = True
    requires_action: bool = True
    custom_keep: Callable[[list[Card]], bool] | None = None

    def evaluate(self, hand: list[Card]) -> bool:
        if self.custom_keep is not None:
            return self.custom_keep(hand)
        lands = sum(1 for c in hand if c.is_land)
        if lands < self.min_lands:
            return False
        if self.requires_discard_outlet:
            outlets = {"Faithless Looting", "Highway Robbery", "Grab the Prize"}
            has_outlet = any(c.name in outlets or c.creates_blood_on_etb for c in hand)
            if not has_outlet:
                return False
        if self.requires_action:
            has_action = any(c.cmc <= 2 and not c.is_land for c in hand)
            if not has_action:
                return False
        return True


def _justin_keep(hand: list[Card]) -> bool:
    lands = sum(1 for c in hand if c.is_land)
    has_fl = any(c.name == "Faithless Looting" for c in hand)
    if lands >= 1 and has_fl:
        return True
    if lands >= 2:
        return any(c.cmc <= 2 and not c.is_land for c in hand)
    return False


JUSTIN_RULE = KeepCriteria(custom_keep=_justin_keep)
STRICT_RULE = KeepCriteria(min_lands=2, requires_discard_outlet=True, requires_action=True)


@dataclass
class HandQualityResults:
    keepable_7: float
    keepable_6: float
    keepable_5: float
    n_hands: int
    criteria_name: str

    def format(self) -> str:
        return (
            f"Hand quality analysis ({self.n_hands:,} hands, criteria: {self.criteria_name})\n"
            f"  Keepable 7-card hand: {self.keepable_7:.1%}\n"
            f"  Keepable 6-card hand: {self.keepable_6:.1%}\n"
            f"  Keepable 5-card hand: {self.keepable_5:.1%}\n"
        )


def analyze_hand_quality(
    deck: Deck,
    criteria: KeepCriteria,
    n_hands: int = 50_000,
    seed: int | None = None,
) -> HandQualityResults:
    rng = random.Random(seed)
    cards = list(deck.cards)

    keep7 = keep6 = keep5 = 0
    for _ in range(n_hands):
        rng.shuffle(cards)
        keep7 += criteria.evaluate(cards[:7])
        keep6 += criteria.evaluate(cards[:6])
        keep5 += criteria.evaluate(cards[:5])

    if criteria is JUSTIN_RULE:
        name = "justin_rule"
    elif criteria is STRICT_RULE:
        name = "strict"
    else:
        name = "custom"

    return HandQualityResults(
        keepable_7=keep7 / n_hands,
        keepable_6=keep6 / n_hands,
        keepable_5=keep5 / n_hands,
        n_hands=n_hands,
        criteria_name=name,
    )
