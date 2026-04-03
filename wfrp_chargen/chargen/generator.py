"""
Character generation logic for WFRP 1st Edition.

generate_character() is the main entry point.  It:
  1. Rolls all primary characteristics for the chosen race.
  2. Computes SB/TB and rolls W, M, and FP.
  3. Picks a career class (optionally guided by user preference) and
     rolls within that class's d100 table.
  4. Applies career skills, trappings, and advance scheme to the Character.

Career class prerequisites (source: wfrp1e.fandom.com):
  Warrior   – WS ≥ 30
  Ranger    – BS ≥ 30
  Rogue     – I ≥ 30 (Elves: I ≥ 65; Dwarfs: unavailable)
  Academic  – Int ≥ 30 AND WP ≥ 30
"""

import random
import re


_RACE_SKILL_RE = re.compile(
    r'\((Dwarfs? only|Elves? only|Halflings? only|Humans? only)\)',
    re.IGNORECASE,
)
_RACE_KEYWORD = {
    "Dwarf": "dwarf", "Elf": "elf", "Halfling": "halfling", "Human": "human",
}

_TRAP_PCT_RE = re.compile(r'^(\d+)%\s+chance\s+of\s+(.+)$', re.IGNORECASE)


def _resolve_or_trapping(text: str) -> str:
    """For 'A or B' trappings, randomly pick one alternative.
    Only splits on 'or' at the top level (not inside parentheses)."""
    depth = 0
    for i, c in enumerate(text):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0 and text[i:i+4] == " or ":
            a = text[:i].strip()
            b = text[i+4:].strip()
            return random.choice([a, b])
    return text


_COND_NO_RE = re.compile(
    r"^(.+?)\s+\(if character doesn[''`]t have (.+?)\)$", re.IGNORECASE
)


def _apply_career_trappings(career_trappings: list) -> list:
    """Process raw trapping entries:
    - Roll for probabilistic items ('X% chance of ...')
    - Randomly choose between 'A or B' alternatives
    - Resolve 'Item (if character doesn't have X)' conditionals
    """
    result = []
    for item in career_trappings:
        if item.lower() == "none listed":
            continue

        # Conditional: "Leather Jack (if character doesn't have Mail Shirt)"
        cm = _COND_NO_RE.match(item)
        if cm:
            trapping_name = cm.group(1).strip()
            required_absent = cm.group(2).strip().lower()
            if not any(required_absent in t.lower() for t in result):
                result.append(trapping_name)
            continue

        # Probabilistic: "X% chance of ITEM"
        m = _TRAP_PCT_RE.match(item)
        if m:
            pct = int(m.group(1))
            if random.randint(1, 100) <= pct:
                result.append(_resolve_or_trapping(m.group(2).strip()))
            # else: item not received — skip
            continue

        result.append(_resolve_or_trapping(item))
    return result

_OR_EQUAL_RE = re.compile(
    r'^(.+?)\s+or\s+(.+?)\s+\(equal chance of either\)$', re.IGNORECASE
)
_PCT_OR_RE = re.compile(
    r'^(\d+)%\s+chance\s+of\s+(.+?)\s+or\s+(.+)$', re.IGNORECASE
)
_PCT_RE = re.compile(r'^(\d+)%\s+chance\s+of\s+(.+)$', re.IGNORECASE)


def _pick_or(a: str, b: str) -> str:
    """Return one of two skill alternatives with equal probability.

    When the second alternative lacks a colon prefix but the first has one
    (e.g. "Secret Signs: Scout's or Woodsman's"), the shared category prefix
    is prepended to keep the skill name fully qualified.
    """
    a, b = a.strip(), b.strip()
    if ":" in a and ":" not in b:
        prefix = a[: a.index(":") + 1].strip()
        b = f"{prefix} {b}"
    return random.choice([a, b])


def _apply_career_skills(career_skills: list, race: str = "") -> list:
    """Roll d100 for probabilistic skills and filter race-restricted ones."""
    result = []
    for skill in career_skills:
        # "Skill A or Skill B (equal chance of either)" — no percentage, 50/50
        m = _OR_EQUAL_RE.match(skill)
        if m:
            result.append(_pick_or(m.group(1), m.group(2)))
            continue

        # "X% chance of Skill A or Skill B" — roll then choose between alternatives
        m = _PCT_OR_RE.match(skill)
        if m:
            pct = int(m.group(1))
            if random.randint(1, 100) <= pct:
                result.append(_pick_or(m.group(2), m.group(3)))
            continue

        # "X% chance of Skill" — standard probabilistic skill
        m = _PCT_RE.match(skill)
        if m:
            pct = int(m.group(1))
            if random.randint(1, 100) <= pct:
                result.append(m.group(2).strip())
            continue

        # Plain skill — drop if restricted to a different race
        rm = _RACE_SKILL_RE.search(skill)
        if rm and race:
            allowed = rm.group(1).lower()
            if _RACE_KEYWORD.get(race, "").lower() not in allowed:
                continue
        result.append(skill)
    return result


from data.races import RACES
from data.careers import CAREERS, CAREER_CLASS_TABLES, CAREER_CLASS_PREREQS, ADVANCED_CAREER_CLASSES
from chargen.character import Character
from chargen.roller import roll_stat, roll_small_stat, roll_direct, roll_d100

# Stats rolled on the 2d10+base percentile scale
_PERCENTILE_STATS = ("WS", "BS", "I", "Dex", "Ld", "Int", "Cl", "WP", "Fel")

# ── Physical appearance tables (WFRP 1e rulebook, Table 2-8 / 2-9) ─────────────
# Each list is a d10 table: index 0 = roll 1, index 9 = roll 10.

_HAIR = {
    # Table 2-8: Hair Colour (d10)
    "Human":    ["Blond", "Red", "Copper", "Light Brown", "Light Brown",
                 "Brown", "Brown", "Dark Brown", "Dark Brown", "Black"],
    "Elf":      ["Silver", "Ash Blond", "Corn Yellow", "Yellow", "Copper",
                 "Light Brown", "Brown", "Dark Brown", "Black", "Black"],
    "Dwarf":    ["Ash Blond", "Ash Blond", "Ash Blond", "Yellow", "Yellow",
                 "Copper", "Light Brown", "Brown", "Dark Brown", "Black"],
    "Halfling": ["Ash Blond", "Ash Blond", "Corn Yellow", "Corn Yellow", "Copper",
                 "Light Brown", "Light Brown", "Brown", "Brown", "Black"],
}

_EYES = {
    # Table 2-9: Eye Colour (d10)
    "Human":    ["Blue", "Blue", "Hazel", "Hazel", "Green",
                 "Grey", "Grey", "Light Brown", "Brown", "Dark Brown"],
    "Elf":      ["Grey", "Blue", "Blue", "Blue", "Green",
                 "Light Brown", "Brown", "Brown", "Dark Brown", "Black"],
    "Dwarf":    ["Pale Grey", "Grey", "Blue", "Hazel", "Green",
                 "Light Brown", "Brown", "Dark Brown", "Black", "Purple"],
    "Halfling": ["Pale Grey", "Grey", "Blue", "Hazel", "Green",
                 "Light Brown", "Light Brown", "Brown", "Dark Brown", "Black"],
}


def _d10_table(table: list) -> str:
    return table[random.randint(1, 10) - 1]


# Age: book Table 2-13 (d100 lookup, 20 buckets of 5 rolls each)
# Each list has 20 values — roll d100, bucket = (roll-1)//5, return list[bucket]
_AGE_TABLE = {
    "Human":    list(range(16, 36)),                                      # 16–35
    "Dwarf":    list(range(20, 116, 5)),                                   # 20–115
    "Elf":      list(range(30, 126, 5)),                                   # 30–125
    "Halfling": [20,22,24,26,28,30,32,34,36,38,40,42,44,46,50,52,54,56,58,60],
}


def _roll_age(race: str) -> int:
    roll = random.randint(1, 100)
    bucket = (roll - 1) // 5   # 0–19
    return _AGE_TABLE[race][bucket]

# Height: (female_base_in, male_base_in) — book Table 2-6, both use +1d10"
_HEIGHT = {
    "Human":    (61, 64),   # Female 5'1"+1d10", Male 5'4"+1d10"
    "Elf":      (64, 66),   # Female 5'4"+1d10", Male 5'6"+1d10"
    "Dwarf":    (50, 52),   # Female 4'2"+1d10", Male 4'4"+1d10"
    "Halfling": (38, 40),   # Female 3'2"+1d10", Male 3'4"+1d10"
}

# Weight: book Table 2-7, d100 lookup — (max_roll, [Dwarf, Elf, Halfling, Human])
_WEIGHT_TABLE = [
    (1,  [90,  80,  75,  105]),
    (3,  [95,  85,  75,  110]),
    (5,  [100, 90,  80,  115]),
    (8,  [105, 95,  80,  120]),
    (12, [110, 100, 85,  125]),
    (17, [115, 105, 85,  130]),
    (22, [120, 110, 90,  135]),
    (29, [125, 115, 90,  140]),
    (37, [130, 120, 95,  145]),
    (49, [135, 125, 100, 150]),
    (64, [140, 130, 100, 155]),
    (71, [145, 135, 105, 160]),
    (78, [150, 140, 110, 165]),
    (83, [155, 145, 115, 170]),
    (88, [160, 150, 120, 175]),
    (92, [165, 155, 125, 180]),
    (95, [170, 160, 130, 190]),
    (97, [175, 165, 135, 200]),
    (99, [180, 170, 140, 210]),
    (100,[185, 175, 145, 220]),
]
_WEIGHT_RACE_IDX = {"Dwarf": 0, "Elf": 1, "Halfling": 2, "Human": 3}


def _roll_weight(race: str) -> int:
    roll = random.randint(1, 100)
    idx  = _WEIGHT_RACE_IDX[race]
    for max_roll, weights in _WEIGHT_TABLE:
        if roll <= max_roll:
            return weights[idx]
    return _WEIGHT_TABLE[-1][1][idx]


def _d100_lookup(table: list, roll: int):
    for max_r, value in table:
        if roll <= max_r:
            return value
    return table[-1][1]


def _roll_d100_table(table: list):
    return _d100_lookup(table, random.randint(1, 100))


# ── Star Sign table (WFRP 1e rulebook, Table 2-12, d100) ──────────────────────
_STAR_SIGNS = [
    (5,  "Wymund the Anchorite"),
    (10, "The Big Cross"),
    (15, "The Limner's Line"),
    (25, "Gnuthus the Ox"),
    (30, "Dragomas the Drake"),
    (35, "The Gloaming"),
    (40, "Grungni's Baldric"),
    (45, "Mammit the Wise"),
    (50, "Mummit the Fool"),
    (55, "The Two Bullocks"),
    (60, "The Dancer"),
    (65, "The Drummer"),
    (70, "The Piper"),
    (75, "Vobist the Faint"),
    (80, "The Broken Cart"),
    (85, "The Greased Goat"),
    (90, "Rhya's Cauldron"),
    (95, "Cackelfax the Cockerel"),
    (98, "The Bonesaw"),
    (100, "The Witchling Star"),
]


# ── Distinguishing Marks table (WFRP 1e rulebook, Table 2-10, d100) ───────────
# Elves "seldom possess these marks" — they have a 10% chance only.
_DIST_MARKS = [
    (5,  "Pox Marks"),
    (10, "Ruddy Faced"),
    (15, "Broken Nose"),
    (20, "Missing Tooth"),
    (25, "Snaggle Teeth"),
    (29, "Huge Nose"),
    (35, "Large Mole"),
    (39, "Wart"),
    (45, "Scar"),
    (50, "Tattoo"),
    (55, "Earring"),
    (60, "Lazy Eye"),
    (65, "Ragged Ear"),
    (70, "Nose Ring"),
    (75, "Missing Nail"),
    (80, "Distinctive Gait"),
    (84, "Curious Smell"),
    (89, "Missing Eyebrow(s)"),
    (94, "Small Bald Patch"),
    (98, "Missing Digit"),
    (100, "Strange Coloured Eye(s)"),
]


def _roll_distinguishing_marks(race: str) -> str:
    if race == "Elf" and random.randint(1, 10) > 1:
        return ""   # 90% of Elves have no distinguishing mark
    return _roll_d100_table(_DIST_MARKS)


# ── Siblings table (WFRP 1e rulebook, Table 2-11, d10) ────────────────────────
# Each tuple: (max_d10_roll, num_siblings)
_SIBLINGS_TABLE = {
    "Dwarf":    [(1, 0), (3, 0), (5, 1), (7, 1), (9, 2), (10, 3)],
    "Elf":      [(1, 0), (3, 1), (5, 1), (7, 2), (9, 2), (10, 3)],
    "Halfling": [(1, 1), (3, 2), (5, 3), (7, 4), (9, 5), (10, 6)],
    "Human":    [(1, 0), (3, 1), (5, 2), (7, 3), (9, 4), (10, 5)],
}


def _roll_siblings(race: str) -> int:
    roll = random.randint(1, 10)
    for max_r, count in _SIBLINGS_TABLE[race]:
        if roll <= max_r:
            return count
    return _SIBLINGS_TABLE[race][-1][1]


# ── Birthplace tables (WFRP 1e rulebook, Tables 2-14 to 2-17) ─────────────────
_HUMAN_PROVINCE   = ["Averland", "Hochland", "Middenland", "Nordland", "Ostermark",
                      "Ostland", "Reikland", "Stirland", "Talabecland", "Wissenland"]
_HUMAN_SETTLEMENT = ["City", "Prosperous Town", "Market Town", "Fortified Town",
                      "Farming Village", "Small Settlement", "Pig/Cattle Farm",
                      "Poor Village", "Arable Farm", "Hovel"]


def _roll_human_birthplace() -> str:
    province   = _HUMAN_PROVINCE[random.randint(0, 9)]
    settlement = _HUMAN_SETTLEMENT[random.randint(0, 9)]
    return f"{settlement}, {province}"


_DWARF_BIRTHPLACE = [
    (30,  None),                                       # roll on Human table
    (40,  "Karak Norn (Grey Mountains)"),
    (50,  "Karak Izor (the Vaults)"),
    (60,  "Karak Hirn (Black Mountains)"),
    (70,  "Karak Kadrin (World's Edge Mountains)"),
    (80,  "Karaz-A-Karak (World's Edge Mountains)"),
    (90,  "Zhufbar (World's Edge Mountains)"),
    (100, "Barak Varr (the Black Gulf)"),
]

_ELF_BIRTHPLACE = [
    (20,  "Altdorf"),
    (40,  "Marienburg"),
    (70,  "Laurelorn Forest"),
    (85,  "The Great Forest"),
    (100, "Reikwald Forest"),
]


def _roll_birthplace(race: str) -> str:
    if race == "Human":
        return _roll_human_birthplace()
    elif race == "Dwarf":
        result = _roll_d100_table(_DWARF_BIRTHPLACE)
        return _roll_human_birthplace() if result is None else result
    elif race == "Elf":
        return _roll_d100_table(_ELF_BIRTHPLACE)
    elif race == "Halfling":
        if random.randint(1, 100) <= 50:
            return "The Moot"
        return _roll_human_birthplace()
    return _roll_human_birthplace()


def _inches_to_cm(inches: int) -> str:
    return f"{round(inches * 2.54)} cm"


def _lbs_to_kg(lbs: int) -> str:
    return f"{round(lbs * 0.4536)} kg"


_DESCRIPTION_BUILDS = [
    "Athletic build", "Stocky build", "Slim build", "Broad-shouldered",
    "Wiry frame", "Heavy-set", "Lithe frame", "Muscular build",
]
_DESCRIPTION_FEATURES_NEUTRAL = [
    "sharp eyes", "a weathered face", "a stern gaze", "kind eyes",
    "a scarred cheek", "a crooked nose", "a strong jaw", "wild hair",
    "calloused hands", "a missing tooth", "bright eyes", "a furrowed brow",
    "a hawk-like nose", "piercing eyes", "high cheekbones",
]
_DESCRIPTION_FEATURES_MALE = [
    "a bushy beard", "a thick moustache", "a stubbly chin",
]
_DESCRIPTION_FEATURES_FEMALE = [
    "long lashes", "a graceful bearing", "a sharp tongue",
]


def _roll_appearance(race: str) -> dict:
    age = _roll_age(race)

    gender = random.choice(["Male", "Female"])

    female_base, male_base = _HEIGHT[race]
    base_h = male_base if gender == "Male" else female_base
    height_in = base_h + random.randint(1, 10)   # +1d10" per book

    weight_lbs = _roll_weight(race)

    build = random.choice(_DESCRIPTION_BUILDS)
    gender_features = _DESCRIPTION_FEATURES_MALE if gender == "Male" else _DESCRIPTION_FEATURES_FEMALE
    feature_pool = _DESCRIPTION_FEATURES_NEUTRAL + gender_features
    feature = random.choice(feature_pool)

    return {
        "age":         str(age),
        "height":      _inches_to_cm(height_in),
        "weight":      _lbs_to_kg(weight_lbs),
        "hair_colour": _d10_table(_HAIR[race]),
        "eye_colour":  _d10_table(_EYES[race]),
        "gender":      gender,
        "description": f"{build}, {feature}",
    }


# ── Alignment ─────────────────────────────────────────────────────────────────

_ALIGNMENT_TABLES = {
    # Human and Dwarf: all five alignments, weighted by career class
    # Elf: Law or Good only
    # Halfling: Neutral only
    # Terms per wiki: Law / Good / Neutral / Evil / Chaos
    "Warrior": {
        "Human":    ["Law"] * 4 + ["Good"] * 2 + ["Neutral"] * 2 + ["Evil"] + ["Chaos"],
        "Dwarf":    ["Law"] * 5 + ["Good"] * 2 + ["Neutral"] * 2 + ["Evil"],
        "Elf":      ["Law"] * 6 + ["Good"] * 4,
        "Halfling": ["Neutral"] * 10,
    },
    "Ranger": {
        "Human":    ["Neutral"] * 4 + ["Law"] * 2 + ["Good"] * 2 + ["Evil"] + ["Chaos"],
        "Dwarf":    ["Neutral"] * 4 + ["Law"] * 3 + ["Good"] * 2 + ["Evil"],
        "Elf":      ["Good"] * 6 + ["Law"] * 4,
        "Halfling": ["Neutral"] * 10,
    },
    "Rogue": {
        "Human":    ["Neutral"] * 3 + ["Evil"] * 3 + ["Chaos"] * 2 + ["Law"] + ["Good"],
        "Dwarf":    ["Neutral"] * 4 + ["Evil"] * 3 + ["Law"] * 2 + ["Chaos"],
        "Elf":      ["Good"] * 7 + ["Law"] * 3,
        "Halfling": ["Neutral"] * 10,
    },
    "Academic": {
        "Human":    ["Good"] * 3 + ["Neutral"] * 3 + ["Law"] * 3 + ["Evil"],
        "Dwarf":    ["Good"] * 3 + ["Neutral"] * 3 + ["Law"] * 3 + ["Evil"],
        "Elf":      ["Good"] * 7 + ["Law"] * 3,
        "Halfling": ["Neutral"] * 10,
    },
}


def _roll_alignment(career_class: str, race: str = "Human") -> str:
    table = _ALIGNMENT_TABLES.get(career_class, {})
    options = table.get(race, ["Neutral"] * 10)
    return random.choice(options)


# ── Trapping parser ───────────────────────────────────────────────────────────

_HTH_KEYWORDS    = {"hand weapon", "sword", "dagger", "spear", "halberd", "axe",
                    "mace", "flail", "staff", "club", "blade",
                    "hammer", "knife", "foil", "truncheon", "cudgel", "scythe",
                    "two-handed", "morning star", "whip"}
_MISSILE_KEYWORDS = {"bow", "crossbow", "pistol", "handgun", "sling",
                     "blunderbuss", "musket"}
_ARMOUR_KEYWORDS  = {"armour", "armor", "jack", "mail", "helm", "helmet",
                     "coif", "shield", "buckler", "breastplate", "coat"}


def _resolve_alternatives(trappings: list) -> list:
    """Resolve 'X or Y' entries by picking one at random."""
    resolved = []
    for item in trappings:
        if " or " in item.lower():
            choices = [c.strip() for c in item.split(" or ")]
            resolved.append(random.choice(choices))
        else:
            resolved.append(item)
    return resolved


def _categorise_trappings(trappings: list) -> dict:
    hth, missile, armour, other = [], [], [], []
    for item in trappings:
        low = item.lower()
        if any(k in low for k in _MISSILE_KEYWORDS):
            missile.append(item)
        elif any(k in low for k in _HTH_KEYWORDS):
            hth.append(item)
        elif any(k in low for k in _ARMOUR_KEYWORDS):
            armour.append(item)
        else:
            other.append(item)
    return {"hth": hth, "missile": missile, "armour": armour, "other": other}


def available_classes(race_name: str, stats: dict[str, int]) -> list[str]:
    """Return which career classes this character qualifies for."""
    prereqs = CAREER_CLASS_PREREQS.get(race_name, {})
    return [cls for cls, check in prereqs.items() if check(stats)]


def _roll_career(career_class: str, race_name: str) -> str:
    """Roll d100 in the given career class table for the race."""
    table = CAREER_CLASS_TABLES[career_class][race_name]
    roll = roll_d100()
    for min_r, max_r, career_name in table:
        if min_r <= roll <= max_r:
            return career_name
    # Fallback: last entry
    return table[-1][2]


def generate_character(
    race_name: str,
    char_name: str = "",
    career_class: str | None = None,
    career_name: str | None = None,
    gender: str | None = None,
) -> Character:
    """
    Generate a complete starting character.

    Parameters
    ----------
    race_name    : one of "Human", "Elf", "Dwarf", "Halfling"
    char_name    : optional character name
    career_class : "Warrior", "Ranger", "Rogue", or "Academic".
                   If None, one is chosen randomly from those available.
    career_name  : specific career name (e.g. "Mercenary").
                   If provided, overrides career_class roll.
    Returns
    -------
    A fully populated Character instance.
    """
    if race_name is None:
        # WFRP 1e d100 race table: Human 01-90, Elf 91-95, Dwarf 96-98, Halfling 99-00
        _roll = random.randint(1, 100)
        if _roll <= 90:
            race_name = "Human"
        elif _roll <= 95:
            race_name = "Elf"
        elif _roll <= 98:
            race_name = "Dwarf"
        else:
            race_name = "Halfling"

    if race_name not in RACES:
        raise ValueError(
            f"Unknown race '{race_name}'. Choose from: {', '.join(RACES)}"
        )

    race_data = RACES[race_name]

    # ── Primary characteristics ───────────────────────────────────────────
    stat_bases = race_data["stat_bases"]
    rolled: dict[str, int] = {
        stat: roll_stat(stat_bases[stat]) for stat in _PERCENTILE_STATS
    }
    # S and T: D3 + racial modifier (small scale; result IS the bonus)
    rolled["S"] = roll_small_stat(race_data["s_mod"])
    rolled["T"] = roll_small_stat(race_data["t_mod"])

    char = Character(name=char_name, race=race_name, **rolled)
    char.compute_bonuses()   # SB = S, TB = T

    # ── Secondary: W, M, FP ───────────────────────────────────────────────
    char.W  = roll_direct(3, race_data["w_mod"])           # D3 + w_mod
    char.M  = roll_direct(race_data["m_die"], race_data["m_mod"])  # D2/D3 + m_mod
    char.FP = roll_direct(
        race_data["fate_die"], race_data["fate_mod"]
    )

    # Mag and IP are always 0 at character creation (magic careers get Mag=1)
    char.Mag = 0
    char.IP  = 0
    char.A   = 1

    # ── Career class selection ────────────────────────────────────────────
    stats_dict = {
        "WS": char.WS, "BS": char.BS, "S": char.S, "T": char.T,
        "I": char.I, "Dex": char.Dex, "Ld": char.Ld, "Int": char.Int,
        "Cl": char.Cl, "WP": char.WP, "Fel": char.Fel,
    }
    # Only include classes where this race has a career table
    valid_classes = [
        cls for cls in available_classes(race_name, stats_dict)
        if race_name in CAREER_CLASS_TABLES.get(cls, {})
    ]

    # Check requested class is valid and available for this race
    if career_class and career_class in valid_classes:
        chosen_class = career_class
    elif valid_classes:
        chosen_class = random.choice(valid_classes)
    else:
        # Extremely unlikely: no prereqs met – pick any available class
        all_classes = list(CAREER_CLASS_TABLES.keys())
        race_classes = [
            c for c in all_classes
            if race_name in CAREER_CLASS_TABLES[c]
        ]
        chosen_class = random.choice(race_classes)

    # ── Career roll ───────────────────────────────────────────────────────
    if career_name and career_name in CAREERS:
        # Use the explicitly chosen career; infer class from tables if needed
        resolved_career = career_name
        if career_name not in [
            c for tbl in CAREER_CLASS_TABLES.get(chosen_class, {}).values()
            for _, _, c in tbl
        ]:
            # Find the actual class this career belongs to
            for cls, race_tables in CAREER_CLASS_TABLES.items():
                for r_tbl in race_tables.values():
                    if any(c == career_name for _, _, c in r_tbl):
                        chosen_class = cls
                        break
            else:
                # Not a starting career; look up in advanced career class map
                if career_name in ADVANCED_CAREER_CLASSES:
                    chosen_class = ADVANCED_CAREER_CLASSES[career_name]
    else:
        resolved_career = _roll_career(chosen_class, race_name)
    career_data = CAREERS[resolved_career]

    char.career         = resolved_career
    char.career_class   = chosen_class
    char.skills         = _apply_career_skills(career_data["skills"], race_name)
    char.trappings      = _apply_career_trappings(career_data["trappings"])
    char.advance_scheme = dict(career_data["advance_scheme"])
    char.career_exits   = list(career_data.get("exits", []))
    char.career_note    = career_data.get("note", "")

    # ── Alignment ─────────────────────────────────────────────────────────
    char.alignment = _roll_alignment(chosen_class, race_name)

    # ── Physical appearance ───────────────────────────────────────────────
    appearance = _roll_appearance(race_name)
    char.age         = appearance["age"]
    char.height      = appearance["height"]
    char.weight      = appearance["weight"]
    char.hair_colour = appearance["hair_colour"]
    char.eye_colour  = appearance["eye_colour"]
    char.gender      = gender if gender else appearance["gender"]
    char.description = appearance["description"]

    # ── Resolve "X or Y" trapping alternatives ────────────────────────────
    char.trappings = _resolve_alternatives(char.trappings)

    # ── Categorise trappings ──────────────────────────────────────────────
    cats = _categorise_trappings(char.trappings)
    char.hth_weapons     = cats["hth"]
    char.missile_weapons = cats["missile"]
    char.armour_items    = cats["armour"]

    # ── Languages ─────────────────────────────────────────────────────────
    _RACE_LANGUAGES = {
        "Human":    ["Reikspiel"],
        "Elf":      ["Reikspiel", "Eltharin"],
        "Dwarf":    ["Reikspiel", "Khazalid"],
        "Halfling": ["Reikspiel", "Mootlandish"],
    }
    langs = list(_RACE_LANGUAGES.get(race_name, ["Reikspiel"]))
    if chosen_class == "Academic":
        langs.append("Classical")
    char.languages = langs

    # ── Social level ──────────────────────────────────────────────────────
    _SOCIAL_LEVEL = {
        "Warrior":  "3",
        "Ranger":   "2",
        "Rogue":    "2",
        "Academic": "3",
    }
    char.social_level = _SOCIAL_LEVEL.get(chosen_class, "2")

    # ── Background fields ─────────────────────────────────────────────────────
    _PARENT_OCC_BY_CLASS = {
        "Warrior":  ["Soldier", "Blacksmith", "Guard", "Watchman", "Militiaman",
                     "Mercenary", "Armourer"],
        "Ranger":   ["Farmer", "Hunter", "Woodsman", "Shepherd", "Trapper",
                     "Fisherman", "Miller"],
        "Rogue":    ["Peddler", "Innkeeper", "Merchant", "Dockworker",
                     "Smuggler", "Fence", "Beggar"],
        "Academic": ["Scholar", "Priest", "Physician", "Scribe",
                     "Merchant", "Lawyer", "Alchemist"],
    }
    char.place_of_birth     = _roll_birthplace(race_name)
    char.parents_occupation = random.choice(
        _PARENT_OCC_BY_CLASS.get(chosen_class, ["Farmer", "Merchant", "Soldier"])
    )

    # Siblings: book Table 2-11 (d10), each sibling 50/50 male/female
    num_siblings = _roll_siblings(race_name)
    brothers = sum(1 for _ in range(num_siblings) if random.random() < 0.5)
    sisters  = num_siblings - brothers
    parts = []
    if brothers:
        parts.append(f"{brothers} brother{'s' if brothers > 1 else ''}")
    if sisters:
        parts.append(f"{sisters} sister{'s' if sisters > 1 else ''}")
    char.family_members = ", ".join(parts) if parts else "No siblings"

    # Star sign: book Table 2-12 (d100)
    char.star_sign = _roll_d100_table(_STAR_SIGNS)

    # Distinguishing marks: book Table 2-10 (d100; Elves seldom have marks)
    char.distinguishing_marks = _roll_distinguishing_marks(race_name)

    char.religion = random.choice(
        {"Human":    ["Sigmar", "Ulric", "Morr", "Shallya", "Taal", "Ranald", "Verena", "Myrmidia"],
         "Dwarf":    ["Grungni", "Grimnir", "Valaya"],
         "Elf":      ["Isha", "Lileath", "Loec", "Khaine"],
         "Halfling": ["Esmeralda", "Ranald", "Shallya"],
        }.get(race_name, ["Sigmar"])
    )
    char.psychology_notes = ""

    # ── Starting wealth — parsed from trappings ───────────────────────────────
    # Handles "2D6 Gold Crowns", "D6 Silver Shillings", "1D6 Brass Pennies" etc.
    import re as _re
    _MONEY_PAT = _re.compile(
        r'^(\d*)D(\d+)\s+(Gold Crowns?|Silver Shillings?|Brass Pennies?)',
        _re.IGNORECASE
    )
    remaining = []
    for item in char.trappings:
        m = _MONEY_PAT.match(item.strip())
        if m:
            num_dice = int(m.group(1)) if m.group(1) else 1
            sides, currency = int(m.group(2)), m.group(3).lower()
            rolled = sum(random.randint(1, sides) for _ in range(num_dice))
            if "gold" in currency:
                char.wealth_gc += rolled
            elif "silver" in currency:
                char.wealth_ss += rolled
            else:
                char.wealth_bp += rolled
        else:
            remaining.append(item)
    char.trappings = remaining

    # Resolve remaining dice quantities in trapping descriptions
    # e.g. "D4 pairs of Manacles" → "2 pairs of Manacles"
    #      "Jewellery worth 10D6 Gold Crowns" → "Jewellery worth 37 Gold Crowns"
    def _roll_dice_in_text(text: str) -> str:
        def _sub(m):
            n = int(m.group(1)) if m.group(1) else 1
            sides = int(m.group(2))
            return str(sum(random.randint(1, sides) for _ in range(n)))
        return _re.sub(r'(\d*)D(\d+)', _sub, text, flags=_re.IGNORECASE)

    char.trappings = [_roll_dice_in_text(t) for t in char.trappings]

    # Recategorise after removing money items
    cats2 = _categorise_trappings(char.trappings)
    char.hth_weapons     = cats2["hth"]
    char.missile_weapons = cats2["missile"]
    char.armour_items    = cats2["armour"]

    # ── Starting spells (magic careers only) ─────────────────────────────────
    _PETTY_MAGIC = [
        "Magic Alarm", "Magic Flame", "Magic Dart", "Magic Light",
        "Zone of Warmth", "Cure Light Injury", "Sleep",
    ]
    _DIVINE_SPELLS = [
        "Bless", "Sanctuary", "Heal Wounds", "Zone of Warmth", "Consecrate",
    ]
    _ARCANE_L1 = [
        "Aura of Protection", "Zone of Steadfastness", "Silver Spear",
        "Wind Blast", "Mystic Mist",
    ]
    if resolved_career == "Wizard's Apprentice":
        char.spells = random.sample(_PETTY_MAGIC, min(3, len(_PETTY_MAGIC)))
        char.Mag = 1
    elif resolved_career == "Hedge-Wizard's Apprentice":
        char.spells = random.sample(_PETTY_MAGIC, min(2, len(_PETTY_MAGIC)))
        char.Mag = 1
    elif resolved_career == "Initiate":
        char.spells = random.sample(_DIVINE_SPELLS, min(2, len(_DIVINE_SPELLS)))
        char.Mag = 1
    elif resolved_career == "Wood Elf Mage's Apprentice":
        char.spells = random.sample(_PETTY_MAGIC + _ARCANE_L1, min(3, 7))
        char.Mag = 1

    return char
