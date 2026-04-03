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


def _apply_career_skills(career_skills: list) -> list:
    """Roll d100 for probabilistic skills (e.g. '75% chance of Drive Cart')."""
    result = []
    for skill in career_skills:
        m = re.match(r'^(\d+)%\s+chance\s+of\s+(.+)$', skill, re.IGNORECASE)
        if m:
            pct = int(m.group(1))
            if random.randint(1, 100) <= pct:
                result.append(m.group(2).strip())
        else:
            result.append(skill)
    return result


from data.races import RACES
from data.careers import CAREERS, CAREER_CLASS_TABLES, CAREER_CLASS_PREREQS, ADVANCED_CAREER_CLASSES
from chargen.character import Character
from chargen.roller import roll_stat, roll_small_stat, roll_direct, roll_d100

# Stats rolled on the 2d10+base percentile scale
_PERCENTILE_STATS = ("WS", "BS", "I", "Dex", "Ld", "Int", "Cl", "WP", "Fel")

# ── Physical appearance tables (WFRP 1e weighted) ────────────────────────────
# Weights reflect real-world frequency for immersion; roll D10 style

_HAIR = {
    "Human":    [("Brown", 3), ("Dark Brown", 2), ("Black", 2), ("Blonde", 1),
                 ("Chestnut", 1), ("Red", 1)],
    "Elf":      [("Golden", 3), ("Auburn", 2), ("Black", 2), ("Silver", 2), ("White", 1)],
    "Dwarf":    [("Brown", 2), ("Dark Brown", 2), ("Black", 2), ("Red", 2),
                 ("Ginger", 1), ("Grey", 1)],
    "Halfling": [("Brown", 3), ("Curly Brown", 2), ("Blonde", 2), ("Sandy", 2), ("Red", 1)],
}

_EYES = {
    "Human":    [("Brown", 3), ("Blue", 2), ("Grey", 2), ("Green", 2), ("Hazel", 1)],
    "Elf":      [("Blue", 2), ("Green", 2), ("Silver", 2), ("Grey", 2), ("Violet", 1), ("Gold", 1)],
    "Dwarf":    [("Brown", 3), ("Grey", 2), ("Dark Brown", 2), ("Blue", 2), ("Green", 1)],
    "Halfling": [("Brown", 3), ("Blue", 2), ("Green", 2), ("Hazel", 2), ("Grey", 1)],
}

def _weighted_choice(table):
    options, weights = zip(*table)
    return random.choices(options, weights=weights, k=1)[0]

_GENDER_WEIGHTS = {
    "Human":    [("Male", 50), ("Female", 50)],
    "Elf":      [("Male", 50), ("Female", 50)],
    "Dwarf":    [("Male", 65), ("Female", 35)],
    "Halfling": [("Male", 50), ("Female", 50)],
}

_DESCRIPTION_BUILDS = [
    "Athletic build", "Stocky build", "Slim build", "Broad-shouldered",
    "Wiry frame", "Heavy-set", "Lithe frame", "Muscular build",
]
_DESCRIPTION_FEATURES = [
    "sharp eyes", "a weathered face", "a stern gaze", "kind eyes",
    "a scarred cheek", "a crooked nose", "a strong jaw", "wild hair",
    "calloused hands", "a missing tooth", "a bushy beard", "bright eyes",
]

# Age ranges: (base, d_sides, d_count)
_AGE = {
    "Human":    (16, 10, 2),
    "Elf":      (60, 20, 5),
    "Dwarf":    (20, 20, 3),
    "Halfling": (16, 10, 2),
}

# Height in inches: (base_inches, d_sides, d_count)
_HEIGHT = {
    "Human":    (64, 6, 2),   # 5'4" + 2d6"
    "Elf":      (66, 6, 2),   # 5'6" + 2d6"
    "Dwarf":    (50, 6, 2),   # 4'2" + 2d6"
    "Halfling": (40, 6, 2),   # 3'4" + 2d6"
}

# Weight in lbs: (base, d_sides, d_count)
_WEIGHT = {
    "Human":    (120, 10, 4),
    "Elf":      (100, 10, 3),
    "Dwarf":    (130, 10, 4),
    "Halfling": (60,  10, 3),
}


def _inches_to_cm(inches: int) -> str:
    return f"{round(inches * 2.54)} cm"


def _lbs_to_kg(lbs: int) -> str:
    return f"{round(lbs * 0.4536)} kg"


def _roll_appearance(race: str) -> dict:
    base_age, d_age, n_age = _AGE[race]
    age = base_age + sum(random.randint(1, d_age) for _ in range(n_age))

    base_h, d_h, n_h = _HEIGHT[race]
    height_in = base_h + sum(random.randint(1, d_h) for _ in range(n_h))

    base_w, d_w, n_w = _WEIGHT[race]
    weight = base_w + sum(random.randint(1, d_w) for _ in range(n_w))

    genders, weights = zip(*_GENDER_WEIGHTS[race])
    gender = random.choices(genders, weights=weights, k=1)[0]

    build   = random.choice(_DESCRIPTION_BUILDS)
    feature = random.choice(_DESCRIPTION_FEATURES)

    return {
        "age":         str(age),
        "height":      _inches_to_cm(height_in),
        "weight":      _lbs_to_kg(weight),
        "hair_colour": _weighted_choice(_HAIR[race]),
        "eye_colour":  _weighted_choice(_EYES[race]),
        "gender":      gender,
        "description": f"{build}, {feature}",
    }


# ── Alignment ─────────────────────────────────────────────────────────────────

_ALIGNMENT_TABLES = {
    "Warrior":  ["Lawful"] * 6 + ["Neutral"] * 3 + ["Chaotic"],
    "Ranger":   ["Neutral"] * 5 + ["Lawful"] * 3 + ["Chaotic"] * 2,
    "Rogue":    ["Neutral"] * 4 + ["Chaotic"] * 4 + ["Lawful"] * 2,
    "Academic": ["Lawful"] * 5 + ["Neutral"] * 4 + ["Chaotic"],
}


def _roll_alignment(career_class: str) -> str:
    return random.choice(_ALIGNMENT_TABLES.get(career_class, ["Neutral"] * 10))


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
    char.skills         = _apply_career_skills(career_data["skills"])
    char.trappings      = [t for t in career_data["trappings"] if t.lower() != "none listed"]
    char.advance_scheme = dict(career_data["advance_scheme"])
    char.career_exits   = list(career_data.get("exits", []))
    char.career_note    = career_data.get("note", "")

    # ── Alignment ─────────────────────────────────────────────────────────
    char.alignment = _roll_alignment(chosen_class)

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
    _BIRTH_BY_CLASS = {
        "Warrior":  ["Altdorf", "Nuln", "Talabheim", "Middenheim", "Averheim",
                     "Wolfenburg", "Hergig", "Bechafen"],
        "Ranger":   ["Wissenland", "Reikland", "Middenland", "Stirland",
                     "Hochland", "Nordland", "Ostland", "Ostermark"],
        "Rogue":    ["Marienburg", "Bögenhafen", "Kemperbad", "Altdorf",
                     "Nuln", "Wurtbad", "Ubersreik"],
        "Academic": ["Altdorf", "Middenheim", "Nuln", "Talabheim",
                     "Marienburg", "Averheim"],
    }
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
    char.place_of_birth     = random.choice(
        _BIRTH_BY_CLASS.get(chosen_class, ["Altdorf", "Middenheim", "Nuln"])
    )
    char.parents_occupation = random.choice(
        _PARENT_OCC_BY_CLASS.get(chosen_class, ["Farmer", "Merchant", "Soldier"])
    )
    brothers = random.randint(0, 3)
    sisters  = random.randint(0, 3)
    parts = []
    if brothers:
        parts.append(f"{brothers} brother{'s' if brothers > 1 else ''}")
    if sisters:
        parts.append(f"{sisters} sister{'s' if sisters > 1 else ''}")
    char.family_members   = ", ".join(parts) if parts else "No siblings"
    char.religion         = random.choice(
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
