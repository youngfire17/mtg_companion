from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from functools import lru_cache

ORACLE_PATH = Path(__file__).parents[2] / "library" / "cards" / "oracle.ndjson"

CARD_OVERRIDES: dict[str, dict[str, bool | int | str]] = {
    "Faithless Looting": {
        "has_flashback": True, "flashback_cost": "{2}{R}",
        "draw_on_cast": 2, "discard_on_cast": 2,
    },
    "Highway Robbery": {
        "draw_on_cast": 2, "discard_on_cast": 1,
        "can_sac_land_instead": True,
    },
    "Grab the Prize": {
        "draw_on_cast": 2, "discard_on_cast": 1,
        "grab_prize_damage": 2,
    },
    "Lava Dart": {
        "damage_on_cast": 1, "damage_any_target": True,
        "has_flashback": True, "flashback_cost": "sac_mountain",
    },
    "Lightning Bolt": {"damage_on_cast": 3, "damage_any_target": True},
    "Fiery Temper": {
        "damage_on_cast": 3, "damage_any_target": True,
        "has_madness": True, "madness_cost": "{R}",
    },
    "Fireblast": {
        "damage_on_cast": 4, "damage_any_target": True,
        "has_alternate_cost": True, "alternate_cost": "sac_2_mountains",
    },
    "Kessig Flamebreather": {"pings_per_noncreature_spell": 1},
    "Guttersnipe": {"pings_per_instant_sorcery": 2},
    "Voldaren Epicure": {"damage_on_etb": 1, "creates_blood_on_etb": True},
    "Sneaky Snacker": {"snacker_return": True},
    "Mountain": {},
    "Smash to Smithereens": {"damage_on_cast": 3, "destroys_artifact": True},
    "Relic of Progenitus": {},
    "Searing Blaze": {
        "damage_on_cast": 1, "damage_to_creature": 1, "has_landfall": True,
        "landfall_damage_on_cast": 3, "landfall_damage_to_creature": 3,
    },
    "End the Festivities": {
        "damage_each_opponent": 1, "damage_each_opponent_creature": 1,
    },
    "Flaring Pain": {
        "prevents_damage_prevention": True,
        "has_flashback": True, "flashback_cost": "{R}",
    },
}


@dataclass(frozen=True)
class Card:
    name: str
    mana_cost: str
    cmc: int
    type_line: str
    oracle_text: str
    # parsed types
    is_land: bool = False
    is_creature: bool = False
    is_instant: bool = False
    is_sorcery: bool = False
    is_artifact: bool = False
    is_enchantment: bool = False
    # combat
    power: int = 0
    toughness: int = 0
    # madness / flashback / alternate costs
    has_madness: bool = False
    madness_cost: str = ""
    has_flashback: bool = False
    flashback_cost: str = ""
    has_alternate_cost: bool = False
    alternate_cost: str = ""
    can_sac_land_instead: bool = False
    # damage tags
    damage_on_cast: int = 0
    damage_any_target: bool = False
    damage_on_etb: int = 0
    damage_each_opponent: int = 0
    damage_each_opponent_creature: int = 0
    damage_to_creature: int = 0
    has_landfall: bool = False
    landfall_damage_on_cast: int = 0
    landfall_damage_to_creature: int = 0
    # draw / discard
    draw_on_cast: int = 0
    discard_on_cast: int = 0
    grab_prize_damage: int = 0
    # trigger tags
    pings_per_noncreature_spell: int = 0
    pings_per_instant_sorcery: int = 0
    creates_blood_on_etb: bool = False
    snacker_return: bool = False
    # misc
    destroys_artifact: bool = False
    prevents_damage_prevention: bool = False


@lru_cache(maxsize=None)
def _load_oracle() -> dict[str, dict]:
    oracle: dict[str, dict] = {}
    with ORACLE_PATH.open(encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            oracle[data["name"]] = data
    return oracle


def load_card(name: str) -> Card:
    oracle = _load_oracle()
    if name not in oracle and name not in CARD_OVERRIDES:
        raise KeyError(f"Card not found in oracle or overrides: {name!r}")

    raw = oracle.get(name, {})
    overrides = CARD_OVERRIDES.get(name, {})

    type_line = raw.get("type_line", "")

    def safe_int(v: str | int | None) -> int:  # non-integer P/T (e.g. "*") returns 0
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    return Card(
        name=name,
        mana_cost=raw.get("mana_cost", ""),
        cmc=int(raw.get("cmc", 0)),
        type_line=type_line,
        oracle_text=raw.get("oracle_text", ""),
        is_land="Land" in type_line,
        is_creature="Creature" in type_line,
        is_instant="Instant" in type_line,
        is_sorcery="Sorcery" in type_line,
        is_artifact="Artifact" in type_line,
        is_enchantment="Enchantment" in type_line,
        power=safe_int(raw.get("power", 0)),
        toughness=safe_int(raw.get("toughness", 0)),
        **overrides,
    )
