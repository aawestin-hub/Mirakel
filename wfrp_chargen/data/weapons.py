"""
WFRP 1st Edition weapon and armour data.

Sources: WFRP 1e Rulebook (1986), Appendix I.

Hand-to-hand weapon fields: i_mod, damage, parry, notes
Missile weapon fields: s_range, m_range, l_range, damage, reload
Armour fields: head, body, arms, legs
"""

# ── Hand-to-Hand weapons ──────────────────────────────────────────────────────
# damage: "S" = Strength, "S+1" etc., "S-1" etc.
# i_mod:  Initiative modifier (e.g. "+10", "-20", "-")
# parry:  "Yes" / "No"

HTH_WEAPONS = {
    "Hand Weapon":              {"i_mod": "-",   "ws_mod": "-",   "damage": "S",    "parry": "Yes"},
    "Sword":                    {"i_mod": "-",   "ws_mod": "-",   "damage": "S",    "parry": "Yes"},
    "Dagger":                   {"i_mod": "+10", "ws_mod": "-",   "damage": "S-2",  "parry": "No"},
    "Knife":                    {"i_mod": "+10", "ws_mod": "-",   "damage": "S-2",  "parry": "No"},
    "Axe":                      {"i_mod": "-",   "ws_mod": "-",   "damage": "S+1",  "parry": "No"},
    "Mace":                     {"i_mod": "-",   "ws_mod": "-",   "damage": "S+1",  "parry": "No"},
    "Club":                     {"i_mod": "-",   "ws_mod": "-",   "damage": "S",    "parry": "No"},
    "Spear":                    {"i_mod": "-10", "ws_mod": "-",   "damage": "S+1",  "parry": "Yes"},
    "Halberd":                  {"i_mod": "-20", "ws_mod": "-20", "damage": "S+2",  "parry": "No"},
    "Two-handed Sword":         {"i_mod": "-20", "ws_mod": "-20", "damage": "S+4",  "parry": "No"},
    "Two-handed Axe":           {"i_mod": "-20", "ws_mod": "-20", "damage": "S+3",  "parry": "No"},
    "Staff":                    {"i_mod": "-10", "ws_mod": "-",   "damage": "S",    "parry": "Yes"},
    "Pick":                     {"i_mod": "-10", "ws_mod": "-",   "damage": "S+2",  "parry": "No"},
    "Flail":                    {"i_mod": "-10", "ws_mod": "-10", "damage": "S+2",  "parry": "No"},
    "Foil":                     {"i_mod": "+20", "ws_mod": "+10", "damage": "S-2",  "parry": "Yes"},
    "Shield":                   {"i_mod": "-",   "ws_mod": "-",   "damage": "S-1",  "parry": "Yes"},
    "Buckler":                  {"i_mod": "-",   "ws_mod": "-",   "damage": "S-1",  "parry": "Yes"},
}

# Weapon name aliases (for "or" variants in trappings)
_HTH_ALIASES = {
    "hand weapon":              "Hand Weapon",
    "sword":                    "Sword",
    "dagger":                   "Dagger",
    "knife":                    "Knife",
    "axe":                      "Axe",
    "mace":                     "Mace",
    "club":                     "Club",
    "spear":                    "Spear",
    "halberd":                  "Halberd",
    "two-handed sword":         "Two-handed Sword",
    "two hand sword":           "Two-handed Sword",
    "two-handed axe":           "Two-handed Axe",
    "staff":                    "Staff",
    "pick":                     "Pick",
    "flail":                    "Flail",
    "foil":                     "Foil",
    "shield":                   "Shield",
    "buckler":                  "Buckler",
}

# ── Missile weapons ───────────────────────────────────────────────────────────
# ranges in metres; reload: "Half", "Full", "2 rounds", "3 rounds"

MISSILE_WEAPONS = {
    "Bow":          {"s_range": "22m",  "m_range": "44m",  "l_range": "66m",
                     "damage": "S",    "reload": "Half"},
    "Crossbow":     {"s_range": "27m",  "m_range": "55m",  "l_range": "82m",
                     "damage": "S+3",  "reload": "Full"},
    "Pistol":       {"s_range": "7m",   "m_range": "18m",  "l_range": "29m",
                     "damage": "S+3",  "reload": "3 rnds"},
    "Handgun":      {"s_range": "15m",  "m_range": "29m",  "l_range": "46m",
                     "damage": "S+4",  "reload": "3 rnds"},
    "Blunderbuss":  {"s_range": "7m",   "m_range": "15m",  "l_range": "22m",
                     "damage": "S+4",  "reload": "3 rnds"},
    "Sling":        {"s_range": "14m",  "m_range": "27m",  "l_range": "41m",
                     "damage": "S",    "reload": "Half"},
    "Throwing Axe": {"s_range": "5m",   "m_range": "11m",  "l_range": "16m",
                     "damage": "S+1",  "reload": "-"},
}

_MISSILE_ALIASES = {
    "bow":          "Bow",
    "crossbow":     "Crossbow",
    "pistol":       "Pistol",
    "handgun":      "Handgun",
    "blunderbuss":  "Blunderbuss",
    "sling":        "Sling",
    "throwing axe": "Throwing Axe",
}

# ── Armour ────────────────────────────────────────────────────────────────────
# location: where it covers (text for table)
# enc: Encumbrance value
# AP per location (for avatar boxes): head, body, arms, legs

ARMOUR = {
    "Leather Jack":     {"location": "Body & Arms",       "enc": 40,
                         "head": 0, "body": 1, "arms": 1, "legs": 0},
    "Light Armour":     {"location": "Body",              "enc": 30,
                         "head": 0, "body": 1, "arms": 0, "legs": 0},
    "Leather Armour":   {"location": "Body, Arms & Legs", "enc": 50,
                         "head": 0, "body": 1, "arms": 1, "legs": 1},
    "Mail Shirt":       {"location": "Body & Arms",       "enc": 80,
                         "head": 0, "body": 2, "arms": 2, "legs": 0},
    "Mail Coat":        {"location": "Body, Arms & Legs", "enc": 100,
                         "head": 0, "body": 2, "arms": 2, "legs": 1},
    "Sleeved Mail":     {"location": "Body & Arms",       "enc": 80,
                         "head": 0, "body": 2, "arms": 2, "legs": 0},
    "Full Mail":        {"location": "Full",              "enc": 120,
                         "head": 1, "body": 2, "arms": 2, "legs": 2},
    "Plate Armour":     {"location": "Full",              "enc": 160,
                         "head": 2, "body": 3, "arms": 2, "legs": 2},
    "Full Plate":       {"location": "Full",              "enc": 200,
                         "head": 3, "body": 4, "arms": 3, "legs": 3},
    "Shield":           {"location": "Shield arm",        "enc": 30,
                         "head": 0, "body": 0, "arms": 0, "legs": 0},
}

_ARMOUR_ALIASES = {
    "leather jack":   "Leather Jack",
    "light armour":   "Light Armour",
    "leather armour": "Leather Armour",
    "mail shirt":     "Mail Shirt",
    "mail coat":      "Mail Coat",
    "sleeved mail":   "Sleeved Mail",
    "full mail":      "Full Mail",
    "plate armour":   "Plate Armour",
    "full plate":     "Full Plate",
    "shield":         "Shield",
}

# ── Lookup helpers ────────────────────────────────────────────────────────────

def _fuzzy_match(name: str, aliases: dict, db: dict):
    low = name.lower().strip()
    # Exact alias
    if low in aliases:
        return db.get(aliases[low])
    # Partial match
    for alias, canonical in aliases.items():
        if alias in low or low in alias:
            return db.get(canonical)
    return None


def get_hth_stats(name: str) -> dict | None:
    return _fuzzy_match(name, _HTH_ALIASES, HTH_WEAPONS)


def get_missile_stats(name: str) -> dict | None:
    return _fuzzy_match(name, _MISSILE_ALIASES, MISSILE_WEAPONS)


def get_armour_stats(name: str) -> dict | None:
    return _fuzzy_match(name, _ARMOUR_ALIASES, ARMOUR)
