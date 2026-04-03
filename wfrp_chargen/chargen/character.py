"""
Character dataclass for WFRP 1st Edition.
Holds all primary and secondary statistics, career data, skills and trappings.
"""

from dataclasses import dataclass, field


PRIMARY_STATS = ("WS", "BS", "S", "T", "I", "Dex", "Ld", "Int", "Cl", "WP", "Fel")

STAT_LABELS = {
    "WS":  "Weapon Skill",
    "BS":  "Ballistic Skill",
    "S":   "Strength",
    "T":   "Toughness",
    "I":   "Initiative",
    "Dex": "Dexterity",
    "Ld":  "Leadership",
    "Int": "Intelligence",
    "Cl":  "Cool",
    "WP":  "Will Power",
    "Fel": "Fellowship",
    "A":   "Attacks",
    "W":   "Wounds",
    "SB":  "Strength Bonus",
    "TB":  "Toughness Bonus",
    "M":   "Movement",
    "Mag": "Magic",
    "IP":  "Insanity Points",
    "FP":  "Fate Points",
}


@dataclass
class Character:
    # Identity
    name: str = ""
    race: str = ""
    career: str = ""
    career_class: str = ""   # Warrior / Ranger / Rogue / Academic
    character_type: str = "PC"   # "PC" or "NPC"

    # Primary stats
    WS:  int = 0   # Weapon Skill
    BS:  int = 0   # Ballistic Skill
    S:   int = 0   # Strength
    T:   int = 0   # Toughness
    I:   int = 0   # Initiative
    Dex: int = 0   # Dexterity
    Ld:  int = 0   # Leadership
    Int: int = 0   # Intelligence
    Cl:  int = 0   # Cool
    WP:  int = 0   # Will Power
    Fel: int = 0   # Fellowship

    # Secondary stats
    A:   int = 1   # Attacks
    W:   int = 0   # Wounds
    SB:  int = 0   # Strength Bonus
    TB:  int = 0   # Toughness Bonus
    M:   int = 4   # Movement
    Mag: int = 0   # Magic
    IP:  int = 0   # Insanity Points
    FP:  int = 0   # Fate Points

    # Identity extension
    alignment:   str = "Neutral"
    gender:      str = ""
    description: str = ""

    # Physical description (Row 2)
    age:         str = ""
    height:      str = ""
    weight:      str = ""
    hair_colour: str = ""
    eye_colour:  str = ""

    # Career info
    skills:          list  = field(default_factory=list)
    trappings:       list  = field(default_factory=list)
    spells:          list  = field(default_factory=list)
    advance_scheme:  dict  = field(default_factory=dict)
    career_exits:    list  = field(default_factory=list)
    career_note:     str   = ""

    # Equipment categories (parsed from trappings)
    hth_weapons:     list  = field(default_factory=list)
    missile_weapons: list  = field(default_factory=list)
    armour_items:    list  = field(default_factory=list)

    # Page 2 fields
    experience:          int   = 0
    languages:           list  = field(default_factory=list)
    place_of_birth:      str   = ""
    parents_occupation:  str   = ""
    family_members:      str   = ""
    star_sign:           str   = ""
    distinguishing_marks: str  = ""
    social_level:        str   = ""
    religion:            str   = ""
    psychology_notes:    str   = ""
    wealth_gc:           int   = 0   # Gold Crowns
    wealth_ss:           int   = 0   # Silver Shillings
    wealth_bp:           int   = 0   # Brass Pennies
    background_narrative: str = ""

    def compute_bonuses(self) -> None:
        """
        In 1st Edition, S and T are already on a small 1–9 scale,
        so SB = S and TB = T directly (no division by 10).
        """
        self.SB = self.S
        self.TB = self.T
