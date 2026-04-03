"""
Character sheet display for WFRP 1st Edition.
Renders a Character object as a formatted terminal printout.
"""

from chargen.character import Character, STAT_LABELS

# Column widths for the stat table
_STAT_COL = 24   # label width
_VAL_COL  = 5    # value width
_ADV_COL  = 12   # advance scheme width


def _divider(char: str = "-", width: int = 64) -> str:
    return char * width


def _header(text: str, width: int = 64) -> str:
    pad = (width - len(text) - 2) // 2
    return "+" + "-" * (width - 2) + "+\n" \
           "|" + " " * pad + text + " " * (width - 2 - pad - len(text)) + "|\n" \
           "+" + "-" * (width - 2) + "+"


def _section(title: str, width: int = 64) -> str:
    line = f"--- {title} "
    return line + "-" * max(0, width - len(line))


def print_character_sheet(char: Character) -> None:
    W = 64

    print()
    print(_header("WARHAMMER FANTASY ROLEPLAY  -  CHARACTER SHEET", W))
    print()

    # Identity
    name_str = char.name if char.name else "(unnamed)"
    print(f"  Name          : {name_str}")
    print(f"  Race          : {char.race}")
    print(f"  Career Class  : {char.career_class}")
    print(f"  Career        : {char.career}")
    if char.career_note:
        print(f"  Note          : {char.career_note}")
    print()

    # ── Primary Characteristics ──────────────────────────────────────────────
    print(_section("PRIMARY CHARACTERISTICS", W))
    print()
    primary_stats = [
        ("WS", "BS", "S",   "T",  "I"),
        ("Dex", "Ld", "Int", "Cl", "WP", "Fel"),
    ]
    for row in primary_stats:
        labels = "  " + "  ".join(f"{s:<5}" for s in row)
        values = "  " + "  ".join(f"{getattr(char, s):<5}" for s in row)
        print(labels)
        print(values)
        print()

    # ── Secondary Characteristics ────────────────────────────────────────────
    print(_section("SECONDARY CHARACTERISTICS", W))
    print()
    secondary = [
        ("A", "W", "SB", "TB", "M", "Mag", "IP", "FP"),
    ]
    for row in secondary:
        labels = "  " + "  ".join(f"{s:<5}" for s in row)
        values = "  " + "  ".join(f"{getattr(char, s):<5}" for s in row)
        print(labels)
        print(values)
        print()

    # ── Advance Scheme ───────────────────────────────────────────────────────
    print(_section("ADVANCE SCHEME  (max advances per stat)", W))
    print()
    scheme = char.advance_scheme
    scheme_stats = [
        ("WS", "BS", "S", "T", "I", "Dex"),
        ("Ld", "Int", "Cl", "WP", "Fel", "A", "W"),
    ]
    for row in scheme_stats:
        labels = "  " + "  ".join(f"{s:<5}" for s in row if s in scheme)
        values = "  " + "  ".join(f"{scheme[s]:<5}" for s in row if s in scheme)
        print(labels)
        print(values)
        print()

    # ── Skills ───────────────────────────────────────────────────────────────
    print(_section("SKILLS", W))
    print()
    for i, skill in enumerate(char.skills, 1):
        print(f"  {i:>2}. {skill}")
    print()

    # ── Trappings ────────────────────────────────────────────────────────────
    print(_section("TRAPPINGS", W))
    print()
    for item in char.trappings:
        print(f"  * {item}")
    print()
    print(_divider(width=W))
    print()
