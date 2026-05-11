#!/usr/bin/env python3
"""
Parse MTGO match logs for Youngfire17's Pauper Madness games.
"""

import os
import re
import json
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = r"C:\Users\young\AppData\Local\Apps\2.0\Data\7XH06GVZ.3OE\3XMBKRDE.BQ3\mtgo..tion_a7d96b15d2cce030_0003.0004_14d45b23a333357e\Data\AppFiles\C751E3EACD0590519323874A8E13D1A3"
OUTPUT_FILE = r"C:\Desktop\CLAUDE Projects\MTG_Companion\library\logs\pauper-madness-batch-01.json"
PLAYER = "Youngfire17"

# Madness deck identification cards
MADNESS_REQUIRED = ["Fiery Temper"]
MADNESS_SECONDARY = [
    "Faithless Looting", "Lightning Axe", "Alms of the Vein",
    "Thermo-Alchemist", "Highway Robbery", "Kessig Flamebreather"
]

# Opponent deck archetypes - (card_set, archetype_name, min_matches)
ARCHETYPE_RULES = [
    # Classic archetypes (explicit heuristics from spec)
    ({"Counterspell", "Snap", "Archaeomancer", "Ephemerate", "Sunscape Familiar"}, "Familiars", 3),
    ({"Gurmag Angler", "Counterspell", "Preordain"}, "Dimir Faeries/Terror", 2),
    ({"Galvanic Blast", "Atog", "Frogmite"}, "Affinity", 2),
    ({"Burning-Tree Emissary", "Goblin Bushwhacker"}, "Kuldotha/Goblins", 2),
    ({"Crypt Rats", "Stinkweed Imp", "Tortured Existence"}, "Tortured Existence", 2),
    ({"Elves of Deep Shadow", "Elvish Mystic", "Lys Alana Huntmaster"}, "Elves", 2),
    ({"Urza's Mine", "Urza's Tower", "Urza's Power Plant"}, "Tron", 2),

    # Extended heuristics based on observed card patterns
    # Orzhov Blink / White Weenie with artifacts
    ({"Glint Hawk", "Kor Skyfisher", "Thraben Inspector", "Vault of Whispers", "Ancient Den"}, "Orzhov/Boros Blink", 3),
    ({"Glint Hawk", "Kor Skyfisher", "Experimental Synthesizer", "Great Furnace"}, "Boros Blink/Synthesizer", 2),
    ({"Kor Skyfisher", "Thraben Inspector", "Novice Inspector", "Journey to Nowhere"}, "White-based Blink", 3),

    # MBC / Black Control
    ({"Crypt Rats", "Pestilence", "Defile"}, "Mono Black Control", 2),
    ({"Crypt Rats", "Defile", "Cast Down"}, "Mono Black Control", 2),
    ({"Thorn of the Black Rose", "Crypt Rats"}, "MBC/Monarch", 2),

    # Familiars (broader detection)
    ({"Sunscape Familiar", "Snap", "Counterspell"}, "Familiars", 2),
    ({"Thornscape Familiar", "Sunscape Familiar"}, "Familiars", 2),
    ({"Murmuring Mystic", "Arcane Denial", "Brainstorm"}, "Izzet/Blue Control", 2),

    # Bogles / Aura
    ({"Ethereal Armor", "Spirit Mantle", "Silhana Ledgewalker"}, "Bogles", 2),
    ({"Rancor", "Spirit Mantle", "Gladecover Scout"}, "Bogles", 2),

    # Stompy / Green Aggro
    ({"Burning-Tree Emissary", "Nest Invader"}, "Green Stompy/Eldrazi", 2),
    ({"Nest Invader", "Eldrazi Repurposer", "Writhing Chrysalis"}, "Eldrazi Green", 2),
    ({"Malevolent Rumble", "Writhing Chrysalis", "Eldrazi Repurposer"}, "Eldrazi Green", 2),
    ({"Boarding Party", "Eldrazi Repurposer", "Writhing Chrysalis"}, "Eldrazi/Big Red-Green", 2),

    # Infect
    ({"Glistener Elf", "Ichorclaw Myr", "Blight Mamba", "Groundswell"}, "Infect", 2),
    ({"Prologue to Phyresis", "Infectious Inquiry", "Pentad Prism"}, "Infect/Proliferate", 2),

    # Storm / Combo
    ({"Manamorphose", "Seething Song", "Goblin Anarchomancer"}, "Grapeshot Storm", 2),
    ({"Dark Ritual", "Songs of the Damned", "Cabal Ritual"}, "Black Storm/Reanimator", 2),
    ({"Lotus Petal", "Dark Ritual", "Songs of the Damned"}, "Storm/Cycle", 2),

    # Cycling
    ({"Horror of the Broken Lands", "Street Wraith", "Architects of Will"}, "Cycling", 2),

    # Flicker / Value loops
    ({"Ghostly Flicker", "Mnemonic Wall", "Mulldrifter"}, "Ghostly Flicker Combo", 2),
    ({"Ephemerate", "Kor Skyfisher", "Inspiring Overseer"}, "Ephemerate Flicker", 2),

    # Vampires
    ({"Vampire Sovereign", "Vampire Spawn", "Voldaren Epicure"}, "Vampires", 2),

    # Monowhite / Heroic
    ({"Ethereal Armor", "Cartouche of Solidarity", "Akroan Skyguard"}, "Heroic White", 2),

    # Goblins
    ({"Goblin Tomb Raider", "Impact Tremors", "Goblin Anarchomancer"}, "Goblins", 2),

    # Weather the Storm / Fog
    ({"Weather the Storm", "Fog", "Moment's Peace"}, "Turbo Fog/Combo", 2),

    # Esper / Azorius Control
    ({"Preordain", "Counterspell", "Brainstorm", "Mulldrifter"}, "Blue Control/Faeries", 3),

    # White Enchantments / Orzhov Sac / Saga
    ({"Okiba Reckoner Raid", "Era of Enlightenment", "Grim Guardian"}, "White Enchantments/Sagas", 2),
    ({"Okiba Reckoner Raid", "Slumbering Keepguard", "Journey to Nowhere"}, "White Enchantments/Sagas", 2),
    ({"Coalition Honor Guard", "Grim Guardian", "Journey to Nowhere"}, "White Enchantments", 2),
    ({"Trespasser's Curse", "Contaminated Ground", "Duress"}, "Orzhov Discard/Control", 2),
]

NOISE_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]+')
CARD_RE = re.compile(r'@\[([^@]+)@:\d+,\d+:@\]')


def parse_dat_file(filepath):
    """Read and decode a .dat file, returning cleaned text lines."""
    with open(filepath, 'rb') as f:
        data = f.read()

    # Split on the binary timestamp separator
    parts = data.split(b'\x40\x50')

    lines = []
    for part in parts:
        try:
            text = part.decode('utf-8', errors='replace')
        except Exception:
            text = part.decode('latin-1', errors='replace')
        text = NOISE_RE.sub(' ', text).strip()
        if text:
            lines.append(text)
    return lines


def extract_cards(text):
    """Extract all card names from a text string."""
    return set(CARD_RE.findall(text))


def has_madness_deck(all_text):
    """Check if this file contains Youngfire17 playing Pauper Madness."""
    if MADNESS_REQUIRED[0] not in all_text:
        return False
    secondary_count = sum(1 for card in MADNESS_SECONDARY if card in all_text)
    return secondary_count >= 2


def identify_opponent_deck(opponent_cards, all_text):
    """Identify the opponent's deck archetype."""
    all_cards_text = all_text

    for card_set, archetype, min_match in ARCHETYPE_RULES:
        matches = sum(1 for card in card_set if card in all_cards_text)
        if matches >= min_match:
            matched = [c for c in card_set if c in all_cards_text]
            return archetype, matched

    # Fallback: return most distinctive cards seen from opponent
    cards_list = list(opponent_cards)[:6]
    return "Unknown", cards_list


def extract_opponent(lines, all_text):
    """Find the opponent's username."""
    # Look for "Turn N: PlayerName" patterns
    turn_re = re.compile(r'Turn \d+: ([^\s\n]+)')
    players_seen = set()
    for line in lines:
        for match in turn_re.finditer(line):
            name = match.group(1).strip()
            if name and name != PLAYER:
                players_seen.add(name)

    # Also look for "X wins the game" or "X has conceded"
    win_re = re.compile(r'([A-Za-z0-9_\-]+) wins the game')
    concede_re = re.compile(r'([A-Za-z0-9_\-]+) has conceded')

    for line in lines:
        for m in win_re.finditer(line):
            name = m.group(1)
            if name != PLAYER and len(name) > 2:
                players_seen.add(name)
        for m in concede_re.finditer(line):
            name = m.group(1)
            if name != PLAYER and len(name) > 2:
                players_seen.add(name)

    # Remove common false positives
    false_positives = {'Turn', 'Game', 'Match', 'Player', 'Round'}
    players_seen -= false_positives

    # Remove Youngfire17 variants
    players_seen = {p for p in players_seen if PLAYER.lower() not in p.lower()}

    if players_seen:
        return sorted(players_seen)[0]  # take first alphabetically if multiple
    return "Unknown"


def determine_result(lines, opponent):
    """Determine W/L/T for Youngfire17."""
    all_text = '\n'.join(lines)

    # Check for explicit win/loss indicators
    youngfire_wins = len(re.findall(r'Youngfire17 wins the game', all_text, re.IGNORECASE))
    youngfire_loses = 0

    if opponent and opponent != "Unknown":
        opp_pattern = re.escape(opponent)
        opp_wins = len(re.findall(rf'{opp_pattern} wins the game', all_text, re.IGNORECASE))
        youngfire_loses = opp_wins

    # Concede checks
    youngfire_concedes = len(re.findall(r'Youngfire17 has conceded', all_text, re.IGNORECASE))
    if opponent and opponent != "Unknown":
        opp_concedes = len(re.findall(rf'{re.escape(opponent)} has conceded', all_text, re.IGNORECASE))
    else:
        opp_concedes = 0

    # Match result - look for "Match complete" style messages
    # Count game wins
    yf_game_wins = youngfire_wins + opp_concedes
    opp_game_wins = youngfire_loses + youngfire_concedes

    if yf_game_wins > opp_game_wins:
        return "W"
    elif opp_game_wins > yf_game_wins:
        return "L"
    else:
        # Check for match-level result
        if re.search(r'Youngfire17 wins the match', all_text, re.IGNORECASE):
            return "W"
        if opponent and re.search(rf'{re.escape(opponent)} wins the match', all_text, re.IGNORECASE):
            return "L"
        return "T"


def count_games_and_turns(lines):
    """Count number of games and total turns.

    MTGO logs show 'Turn 1: PlayerA' when PlayerA takes Turn 1.
    Each game has one Turn 1 per player, so 'Turn 1: Youngfire17' marks
    a new game when Youngfire17 goes first, and vice versa.
    We count unique game starts by looking for 'Game X' markers or
    'wins the game' / 'concedes' events.
    """
    all_text = '\n'.join(lines)

    # Count game-ending events: each "wins the game" or "has conceded" ends a game
    win_events = len(re.findall(r'wins the game', all_text, re.IGNORECASE))
    concede_events = len(re.findall(r'has conceded', all_text, re.IGNORECASE))
    total_endings = win_events + concede_events

    # Games = game endings (each game ends exactly once)
    # If we see "Game N" markers, use those
    game_markers = re.findall(r'\bGame \d+\b', all_text)
    if game_markers:
        games = max(int(re.search(r'\d+', g).group()) for g in game_markers)
    elif total_endings > 0:
        games = total_endings
    else:
        games = 1

    # Total turn count: count all "Turn N:" markers
    turn_markers = re.findall(r'\bTurn \d+:', all_text)
    total_turns = len(turn_markers)

    return games, total_turns


def extract_key_moments(lines, opponent):
    """Extract 1-2 notable moments from the log."""
    notes = []
    all_text = '\n'.join(lines)

    # Check for sideboard games (went to 3 games = full match)
    win_events = len(re.findall(r'wins the game', all_text, re.IGNORECASE))
    concede_events = len(re.findall(r'has conceded', all_text, re.IGNORECASE))
    total_game_endings = win_events + concede_events
    if total_game_endings >= 3:
        notes.append(f"Went to games (3-game match)")

    # Notable opponent interaction
    if "Counterspell" in all_text:
        notes.append("Opponent had Counterspell")
    elif "Daze" in all_text:
        notes.append("Opponent had Daze")

    # Board sweepers
    if "Pestilence" in all_text or "Crypt Rats" in all_text:
        notes.append("Opponent had board wipe (Pestilence/Crypt Rats)")

    # Fast clock
    if "Guttersnipe" in all_text:
        notes.append("Opponent had Guttersnipe")
    if "Thermo-Alchemist" in all_text:
        notes.append("Thermo-Alchemist engine used")

    # Stompy/fast opponent
    if "Boarding Party" in all_text:
        notes.append("Opponent had Boarding Party (Cascade)")

    return '; '.join(notes[:2]) if notes else None


def parse_match(filepath):
    """Parse a single match log file and return structured data."""
    filename = os.path.basename(filepath)
    modified_time = os.path.getmtime(filepath)
    date_str = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d')

    lines = parse_dat_file(filepath)
    all_text = '\n'.join(lines)

    # Extract cards from entire file
    all_cards = extract_cards(all_text)

    # Find opponent
    opponent = extract_opponent(lines, all_text)

    # Get opponent-specific cards (heuristic: all cards not in madness deck)
    madness_deck_cards = {
        "Fiery Temper", "Faithless Looting", "Lightning Axe", "Alms of the Vein",
        "Thermo-Alchemist", "Highway Robbery", "Kessig Flamebreather",
        "Burning Inquiry", "Insolent Neonate", "Rakdos Charm",
        "Mountain", "Swamp", "Bloodstained Mire", "Polluted Delta",
        "Rakdos Carnarium", "Dragonskull Summit", "Bog Witch",
        "Stitcher's Supplier", "Grimdancer", "Deadly Dispute", "Grixis Panorama",
        "Galvanic Blast", "Great Furnace", "Vault of Whispers", "Drossforge Bridge",
        "Jagged Barrens"
        # Note: do NOT exclude cards like Kitchen Imp, Sneaky Snacker, Voldaren Epicure,
        # Blood Token, Lightning Bolt — those show up in opponent lists and help identify decks
    }
    opponent_cards = all_cards - madness_deck_cards

    # Identify deck
    opponent_deck, opponent_key_cards = identify_opponent_deck(opponent_cards, all_text)

    # Result
    result = determine_result(lines, opponent)

    # Games and turns
    games, turns_total = count_games_and_turns(lines)

    # Key moments
    key_moments = extract_key_moments(lines, opponent)

    record = {
        "file": filename,
        "date": date_str,
        "opponent": opponent,
        "result": result,
        "games": games,
        "turns_total": turns_total,
        "opponent_deck": opponent_deck,
        "opponent_key_cards": opponent_key_cards[:6] if opponent_key_cards else [],
        "notes": key_moments
    }
    return record


def find_madness_files(log_dir, top_n=20):
    """Find and return the top N largest GameLog files containing Pauper Madness."""
    dat_files = list(Path(log_dir).glob("Match_GameLog_*.dat"))
    print(f"Scanning {len(dat_files)} GameLog files for Pauper Madness content...")

    qualifying = []
    scanned = 0

    for fpath in dat_files:
        scanned += 1
        if scanned % 100 == 0:
            print(f"  Scanned {scanned}/{len(dat_files)}, found {len(qualifying)} qualifying so far...")

        try:
            # Quick text scan first (faster than full parse)
            with open(fpath, 'rb') as f:
                raw = f.read()

            # Decode for quick check
            try:
                text = raw.decode('utf-8', errors='replace')
            except Exception:
                text = raw.decode('latin-1', errors='replace')

            text = NOISE_RE.sub(' ', text)

            # Check madness criteria
            if has_madness_deck(text):
                qualifying.append(fpath)

        except Exception as e:
            pass  # Skip unreadable files

    print(f"Found {len(qualifying)} files with Pauper Madness content")

    # Sort by file size (largest first = most game content)
    qualifying.sort(key=lambda p: p.stat().st_size, reverse=True)

    return qualifying[:top_n]


def main():
    print("=" * 60)
    print("MTGO Pauper Madness Log Parser")
    print(f"Player: {PLAYER}")
    print("=" * 60)

    # Find qualifying files
    madness_files = find_madness_files(LOG_DIR, top_n=20)

    if not madness_files:
        print("ERROR: No qualifying files found!")
        sys.exit(1)

    print(f"\nParsing top {len(madness_files)} largest qualifying files...\n")

    results = []
    parse_errors = []

    for fpath in madness_files:
        filename = fpath.name
        try:
            record = parse_match(str(fpath))
            results.append(record)
            print(f"  OK: {filename} | {record['date']} | opp={record['opponent']} | {record['result']} | deck={record['opponent_deck']}")
        except Exception as e:
            print(f"  ERR: {filename} -> {e}")
            parse_errors.append({"file": filename, "error": str(e)})

    # Build output
    output = {
        "matches": results,
        "parse_errors": parse_errors,
        "generated": datetime.now().isoformat(),
        "total_matches": len(results),
        "player": PLAYER
    }

    # Write JSON
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(results)} match records to: {OUTPUT_FILE}")

    # Summary table
    print("\n" + "=" * 100)
    print(f"{'Date':<12} {'Opponent':<22} {'R':<3} {'Deck':<22} {'G':<4} {'Turns':<7} {'Notes'}")
    print("-" * 100)
    wins = losses = ties = 0
    for r in results:
        result_char = r['result']
        if result_char == 'W': wins += 1
        elif result_char == 'L': losses += 1
        else: ties += 1
        notes = (r['notes'] or '')[:30]
        print(f"{r['date']:<12} {r['opponent']:<22} {result_char:<3} {r['opponent_deck']:<22} {r['games']:<4} {r['turns_total']:<7} {notes}")

    print("=" * 100)
    print(f"Record: {wins}W - {losses}L - {ties}T  |  Total matches: {len(results)}")
    if parse_errors:
        print(f"Parse errors: {len(parse_errors)} files skipped")


if __name__ == '__main__':
    main()
