"""
WFRP 1st Edition Character Generator
=====================================
Interactive CLI that generates a starting character step by step.

Run with:
    cd wfrp_chargen
    python main.py
"""

import sys
import re
import os
import random as _random

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from data.races import RACES
from data.names import random_name
from chargen.generator import generate_character, available_classes
from chargen.roller import roll_stat, roll_small_stat, roll_direct
from data.careers import CAREER_CLASS_TABLES
from display import print_character_sheet
from sheet_pdf import save_character_pdf
from sheet_html import save_character_html
from sheet_image import save_character_image, save_character_spread


RACES_LIST = list(RACES.keys())
CAREER_CLASSES = ["Warrior", "Ranger", "Rogue", "Academic"]

BANNER = r"""
__          __     _____  _    _          __  __ __  __ ______ _____
\ \        / /\   |  __ \| |  | |   /\   |  \/  |  \/  |  ____|  __ \
 \ \  /\  / /  \  | |__) | |__| |  /  \  | \  / | \  / | |__  | |__) |
  \ \/  \/ / /\ \ |  _  /|  __  | / /\ \ | |\/| | |\/| |  __| |  _  /
   \  /\  / ____ \| | \ \| |  | |/ ____ \| |  | | |  | | |____| | \ \
    \/  \/_/    \_\_|  \_\_|  |_/_/    \_\_|  |_|_|  |_|______|_|  \_\

  1st Edition Character Generator
"""


def _safe_input(prompt: str) -> str:
    """input() wrapper that returns '' on EOF (e.g. piped/non-interactive use)."""
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def prompt_character_type() -> str:
    """Ask the user whether they want to generate a PC or NPC."""
    print("What type of character do you want to generate?")
    print("  1. PC  – Player Character")
    print("  2. NPC – Non-Player Character")
    print()
    while True:
        raw = _safe_input("  > ").strip().lower()
        if raw in ("", "1", "pc", "player character", "player"):
            return "PC"
        if raw in ("2", "npc", "non-player character", "non-player", "nonplayer"):
            return "NPC"
        print("  Enter 1 (PC) or 2 (NPC).")


def prompt_race() -> str:
    """Ask the user to pick a race, or press Enter to roll randomly."""
    print("Choose a race (or press Enter to roll randomly):")
    for i, race in enumerate(RACES_LIST, 1):
        print(f"  {i}. {race}")
    print()

    while True:
        raw = _safe_input("  > ")
        if raw == "":
            import random
            # WFRP 1e d100 race table: Human 01-90, Elf 91-95, Dwarf 96-98, Halfling 99-00
            roll = random.randint(1, 100)
            if roll <= 90:
                choice = "Human"
            elif roll <= 95:
                choice = "Elf"
            elif roll <= 98:
                choice = "Dwarf"
            else:
                choice = "Halfling"
            print(f"  -> Rolled {roll:02d}: {choice}")
            return choice
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(RACES_LIST):
                return RACES_LIST[idx]
        # Accept the race name directly (case-insensitive)
        for race in RACES_LIST:
            if race.lower() == raw.lower():
                return race
        print(f"  Invalid choice. Enter a number 1–{len(RACES_LIST)} or a race name.")


def prompt_name(race: str) -> str:
    """Suggest a race-appropriate name; let the user accept or override."""
    suggestion = random_name(race)
    raw = _safe_input(f"Character name [Enter for '{suggestion}']: ")
    return raw if raw else suggestion


def prompt_gender() -> str:
    """Ask the user to pick a gender, or press Enter for random.
    Always returns a resolved value ('Male' or 'Female')."""
    print("Choose gender (or press Enter for random):")
    print("  1. Male")
    print("  2. Female")
    print()
    while True:
        raw = _safe_input("  > ").lower()
        if raw == "" or raw == "r":
            chosen = _random.choice(["Male", "Female"])
            print(f"  -> {chosen}")
            return chosen
        if raw in ("1", "male", "m"):
            return "Male"
        if raw in ("2", "female", "f"):
            return "Female"
        print("  Enter 1 (Male), 2 (Female), or press Enter for random.")



def prompt_career_class(race: str, stats: dict) -> str | None:
    """
    Show which career classes the character qualifies for and let the user
    choose one, or press Enter to pick randomly.
    Returns the chosen class name, or None to let the generator decide.
    """
    valid = available_classes(race, stats)
    if not valid:
        print("  (No career class prerequisites met – class will be assigned randomly.)")
        return None

    print("Career class prerequisites met:")
    for i, cls in enumerate(valid, 1):
        print(f"  {i}. {cls}")
    print()

    while True:
        raw = _safe_input("  Choose a career class (or Enter to roll randomly): ")
        if raw == "":
            choice = _random.choice(valid)
            print(f"  -> Randomly selected: {choice}")
            return choice
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(valid):
                return valid[idx]
        for cls in valid:
            if cls.lower() == raw.lower():
                return cls
        print(f"  Invalid choice. Enter a number 1–{len(valid)} or a class name.")


def prompt_career(career_class: str, race: str) -> str | None:
    """
    Show the careers available for the chosen class + race and let the user
    pick one, or press Enter to roll randomly on the d100 table.
    Returns the career name, or None to let the generator roll.
    """
    table = CAREER_CLASS_TABLES.get(career_class, {}).get(race, [])
    if not table:
        return None

    # Build unique, sorted career list from the d100 table
    careers = list(dict.fromkeys(name for _, _, name in table))

    print(f"Available {career_class} careers for {race}:")
    for i, career in enumerate(careers, 1):
        print(f"  {i:2}. {career}")
    print()

    while True:
        raw = _safe_input("  Choose a career (or Enter to roll randomly): ")
        if raw == "":
            return None   # let generator roll d100
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(careers):
                print(f"  -> Selected: {careers[idx]}")
                return careers[idx]
        for c in careers:
            if c.lower() == raw.lower():
                print(f"  -> Selected: {c}")
                return c
        print(f"  Invalid choice. Enter a number 1–{len(careers)} or a career name.")



def _generate_npc_auto(race: str | None = None) -> "Character":
    """Generate a fully random NPC with no user prompts."""
    import random as _rand
    from data.names import random_name as _rname
    from chargen.generator import generate_character as _gen

    # Roll race if not specified
    if race is None:
        roll = _rand.randint(1, 100)
        if roll <= 90:
            race = "Human"
        elif roll <= 95:
            race = "Elf"
        elif roll <= 98:
            race = "Dwarf"
        else:
            race = "Halfling"

    gender = _rand.choice(["Male", "Female"])
    name   = _rname(race)
    char   = _gen(race_name=race, char_name=name, gender=gender)
    char.character_type = "NPC"
    return char


def main() -> None:
    print(BANNER)

    while True:
        # ── PC or NPC? ───────────────────────────────────────────────────────
        char_type = prompt_character_type()
        print(f"  -> Generating {char_type}")
        print()

        if char_type == "NPC":
            # ── NPC: fully automatic ─────────────────────────────────────
            char = _generate_npc_auto()
            print(f"  Race    : {char.race}")
            print(f"  Gender  : {char.gender}")
            print(f"  Career  : {char.career}  ({char.career_class})")
            print(f"  Name    : {char.name}")
            print()

        else:
            # ── PC: guided character creation ────────────────────────────

            # ── Race selection ────────────────────────────────────────
            race = prompt_race()
            print()

            # ── Optional name ─────────────────────────────────────────
            name = prompt_name(race)
            print()

            # ── Gender selection ──────────────────────────────────────
            gender = prompt_gender()
            print()

            # ── Roll stats first so we can show prereqs ───────────────
            from data.races import RACES as _RACES
            rd = _RACES[race]
            _PSTATS = ("WS", "BS", "I", "Dex", "Ld", "Int", "Cl", "WP", "Fel")
            temp_stats = {s: roll_stat(rd["stat_bases"][s]) for s in _PSTATS}
            temp_stats["S"] = roll_small_stat(rd["s_mod"])
            temp_stats["T"] = roll_small_stat(rd["t_mod"])

            print("Rolled characteristics:")
            pairs = [f"{k}={v}" for k, v in temp_stats.items()]
            print("  " + "  ".join(pairs[:6]))
            print("  " + "  ".join(pairs[6:]))
            print()

            # ── Career class selection ────────────────────────────────
            career_cls = prompt_career_class(race, temp_stats)
            print()

            # ── Career selection ──────────────────────────────────────
            chosen_career = prompt_career(career_cls, race)
            if chosen_career is None:
                print(f"  -> Rolling randomly on the {career_cls} table...")
            print()

            # ── Generate using pre-rolled stats ──────────────────────
            char = generate_character(
                race_name=race,
                char_name=name,
                career_class=career_cls,
                career_name=chosen_career,
                gender=gender,
            )
            # Overwrite primary stats with the ones already shown to the user
            for k, v in temp_stats.items():
                setattr(char, k, v)
            char.SB = char.S
            char.TB = char.T
            char.character_type = char_type

        # ── Display ───────────────────────────────────────────────────────
        print_character_sheet(char)

        # ── Save PDF + HTML + image sheet ────────────────────────────────
        safe_name   = re.sub(r"[^\w\-]", "_", char.name or "character")
        out_dir     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(out_dir, exist_ok=True)
        pdf_path    = os.path.join(out_dir, f"{safe_name}_sheet.pdf")
        html_path   = os.path.join(out_dir, f"{safe_name}_sheet.html")
        spread_path = os.path.join(out_dir, f"{safe_name}_sheet.jpg")
        save_character_pdf(char, pdf_path)
        save_character_html(char, html_path)
        save_character_spread(char, spread_path, pc_mode=(char.character_type == "PC"))
        print(f"  [OK] PDF lagret  : {pdf_path}")
        print(f"  [OK] HTML lagret : {html_path}")
        print(f"  [OK] Ark lagret  : {spread_path}\n")

        # ── Play again? ───────────────────────────────────────────────────
        while True:
            again = _safe_input("Generate another character? [Y/n] ").lower()
            if again in ("", "y", "yes"):
                print()
                break
            if again in ("n", "no"):
                print("Farewell, and may Sigmar guide your dice!\n")
                sys.exit(0)
            if again == "":
                sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Farewell!\n")
        sys.exit(0)
