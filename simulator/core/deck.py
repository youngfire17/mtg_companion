from __future__ import annotations
import re
import random
from dataclasses import dataclass
from pathlib import Path
from simulator.core.card import Card, load_card


@dataclass
class Deck:
    cards: list[Card]
    name: str = "unknown"

    @classmethod
    def from_file(cls, path: str | Path) -> Deck:
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        cards: list[Card] = []

        # Find the first ``` block after "## Maindeck"
        in_maindeck_section = False
        in_code_block = False
        for line in text.splitlines():
            if line.strip().startswith("## Maindeck"):
                in_maindeck_section = True
                continue
            if in_maindeck_section and line.strip().startswith("## "):
                break  # hit next section
            if in_maindeck_section and line.strip() == "```":
                if not in_code_block:
                    in_code_block = True
                    continue
                else:
                    break  # end of maindeck code block
            if in_code_block:
                # Strip inline comments (e.g., "4  Smash to Smithereens   (Affinity...)")
                clean = line.split("(")[0].strip()
                m = re.match(r"^(\d+)\s+(.+)$", clean)
                if m:
                    qty = int(m.group(1))
                    name = m.group(2).strip()
                    card = load_card(name)
                    cards.extend([card] * qty)

        return cls(cards=cards, name=path.stem)

    def shuffle(self, seed: int | None = None) -> None:
        rng = random.Random(seed)
        rng.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop(0)

    def copy(self) -> Deck:
        return Deck(cards=list(self.cards), name=self.name)

    def __len__(self) -> int:
        return len(self.cards)
