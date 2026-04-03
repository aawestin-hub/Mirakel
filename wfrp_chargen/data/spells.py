"""
WFRP 1st Edition spell data.

Each spell dict has:
  sl          : Spell Level (0 = Petty Magic)
  mp          : Magic Points cost
  r           : Range
  d           : Duration
  ingredients : Ingredients required ("-" if none)
  effect      : Short effect description (fits in one column)
"""

SPELLS = {
    # ── Petty Magic ────────────────────────────────────────────────────────────
    "Magic Alarm":       {"sl": 0, "mp": 1, "r": "Tch",  "d": "1hr",   "ingredients": "Chalk",     "effect": "Alarm if crossed"},
    "Magic Flame":       {"sl": 0, "mp": 1, "r": "Self",  "d": "Con.",  "ingredients": "Flint",     "effect": "Lit flame in hand"},
    "Magic Dart":        {"sl": 0, "mp": 1, "r": "24m",   "d": "Ins.",  "ingredients": "-",         "effect": "S+2 dmg, no armour"},
    "Magic Light":       {"sl": 0, "mp": 1, "r": "Self",  "d": "1hr",   "ingredients": "-",         "effect": "Bright light 10m"},
    "Zone of Warmth":    {"sl": 0, "mp": 1, "r": "Self",  "d": "1hr",   "ingredients": "-",         "effect": "Immune cold effects"},
    "Cure Light Injury": {"sl": 0, "mp": 2, "r": "Tch",   "d": "Prm.",  "ingredients": "-",         "effect": "Heal 1 Wound"},
    "Sleep":             {"sl": 0, "mp": 2, "r": "12m",   "d": "2hr",   "ingredients": "-",         "effect": "Target sleeps"},

    # ── Battle Magic Level 1 (Arcane) ──────────────────────────────────────────
    "Aura of Protection":    {"sl": 1, "mp": 2, "r": "Self",  "d": "1hr",   "ingredients": "-",      "effect": "+10 to all saves"},
    "Zone of Steadfastness": {"sl": 1, "mp": 2, "r": "Self",  "d": "1hr",   "ingredients": "-",      "effect": "Immune fear/terror"},
    "Silver Spear":          {"sl": 1, "mp": 2, "r": "24m",   "d": "Ins.",  "ingredients": "Silver", "effect": "S+4 dmg bolt"},
    "Wind Blast":            {"sl": 1, "mp": 2, "r": "36m",   "d": "Ins.",  "ingredients": "-",      "effect": "Knock target back"},
    "Mystic Mist":           {"sl": 1, "mp": 2, "r": "36m",   "d": "1hr",   "ingredients": "-",      "effect": "Dense 10m mist"},

    # ── Divine Magic (Initiate/Cleric) ─────────────────────────────────────────
    "Bless":          {"sl": 1, "mp": 1, "r": "Tch",   "d": "1hr",   "ingredients": "Holy Symbol", "effect": "+10 to one test"},
    "Sanctuary":      {"sl": 1, "mp": 1, "r": "Self",  "d": "Spc.",  "ingredients": "Holy Symbol", "effect": "Undead cannot enter"},
    "Heal Wounds":    {"sl": 1, "mp": 2, "r": "Tch",   "d": "Prm.",  "ingredients": "-",           "effect": "Restore D3 Wounds"},
    "Consecrate":     {"sl": 1, "mp": 2, "r": "Tch",   "d": "Prm.",  "ingredients": "Holy Water",  "effect": "Sanctify object/area"},
}


def get_spell(name: str) -> dict | None:
    """Return spell data dict, or None if not found."""
    return SPELLS.get(name)
