"""
Career tables and definitions for WFRP 1st Edition.

The career system uses FOUR career classes: Warrior, Ranger, Rogue, Academic.
Each class has stat prerequisites that must be met to enter it.
After qualifying, the player rolls d100 within that class's race-specific table.

CAREER_CLASS_PREREQS  – per-race lambda checks on a stats dict
CAREER_CLASS_TABLES   – {class: {race: [(min, max, career_name), ...]}}
CAREERS               – {career_name: {advance_scheme, skills, trappings, note?}}

Advance scheme values are maximum advances available while in the career.
S and T advances are on the small D3 scale (0–4), not the percentile scale.

Sources: wfrp1e.fandom.com (via web.archive.org).
"""

# ---------------------------------------------------------------------------
# Career-class prerequisites (stats dict has keys matching Character fields)
# ---------------------------------------------------------------------------

CAREER_CLASS_PREREQS: dict[str, dict[str, object]] = {
    "Human": {
        "Warrior":  lambda s: s["WS"]  >= 30,
        "Ranger":   lambda s: s["BS"]  >= 30,
        "Rogue":    lambda s: s["I"]   >= 30,
        "Academic": lambda s: s["Int"] >= 30 and s["WP"] >= 30,
    },
    "Elf": {
        "Warrior":  lambda s: s["WS"]  >= 30,
        "Ranger":   lambda s: s["BS"]  >= 30,
        "Rogue":    lambda s: s["I"]   >= 65,   # Very high bar for Elves
        "Academic": lambda s: s["Int"] >= 30 and s["WP"] >= 30,
    },
    "Dwarf": {
        "Warrior":  lambda s: s["WS"]  >= 30,
        "Ranger":   lambda s: s["BS"]  >= 30,
        # No Rogue class for Dwarfs
        "Academic": lambda s: s["Int"] >= 30 and s["WP"] >= 30,
    },
    "Halfling": {
        "Warrior":  lambda s: s["WS"]  >= 30,
        "Ranger":   lambda s: s["BS"]  >= 30,
        "Rogue":    lambda s: s["I"]   >= 30,
        "Academic": lambda s: s["Int"] >= 30 and s["WP"] >= 30,
    },
}


# ---------------------------------------------------------------------------
# Career class d100 tables  (min_roll, max_roll are both inclusive; 1–100)
# ---------------------------------------------------------------------------

CAREER_CLASS_TABLES: dict[str, dict[str, list[tuple[int, int, str]]]] = {
    "Warrior": {
        "Human": [
            (1,  10, "Bodyguard"),
            (11, 20, "Labourer"),
            (21, 25, "Marine"),
            (26, 35, "Mercenary"),
            (36, 40, "Militiaman"),
            (41, 45, "Noble"),
            (46, 55, "Outlaw"),
            (56, 60, "Pit Fighter"),
            (61, 65, "Protagonist"),
            (66, 70, "Seaman"),
            (71, 80, "Servant"),
            (81, 90, "Soldier"),
            (91, 95, "Squire"),
            (96, 100, "Watchman"),
        ],
        "Elf": [
            (1,  15, "Bodyguard"),
            (16, 25, "Marine"),
            (26, 35, "Noble"),
            (36, 75, "Soldier"),
            (76, 85, "Seaman"),
            (86, 100, "Watchman"),
        ],
        "Dwarf": [
            (1,  10, "Bodyguard"),
            (11, 20, "Marine"),
            (21, 35, "Mercenary"),
            (36, 40, "Noble"),
            (41, 50, "Seaman"),
            (51, 70, "Soldier"),
            (71, 75, "Troll Slayer"),
            (76, 90, "Tunnel Fighter"),
            (91, 100, "Watchman"),
        ],
        "Halfling": [
            (1,  15, "Bodyguard"),
            (16, 20, "Labourer"),
            (21, 30, "Militiaman"),
            (31, 35, "Noble"),
            (36, 40, "Outlaw"),
            (41, 55, "Servant"),
            (56, 70, "Soldier"),
            (71, 80, "Squire"),
            (81, 100, "Watchman"),
        ],
    },

    "Ranger": {
        "Human": [
            (1,   5, "Boatman"),
            (6,  10, "Bounty Hunter"),
            (11, 15, "Coachman"),
            (16, 20, "Farmer"),
            (21, 30, "Fisherman"),
            (31, 40, "Gamekeeper"),
            (41, 45, "Herdsman"),
            (46, 50, "Hunter"),
            (51, 55, "Muleskinner"),
            (56, 60, "Outrider"),
            (61, 65, "Prospector"),
            (66, 70, "Rat Catcher"),
            (71, 75, "Roadwarden"),
            (76, 80, "Toll-Keeper"),
            (81, 90, "Trapper"),
            (91, 100, "Woodsman"),
        ],
        "Elf": [
            (1,   1, "Farmer"),
            (2,  11, "Herdsman"),
            (12, 25, "Hunter"),
            (26, 55, "Miner"),
            (56, 65, "Prospector"),
            (66, 70, "Rat Catcher"),
            (71, 80, "Roadwarden"),
            (81, 90, "Runner"),
            (91, 100, "Trapper"),
        ],
        "Dwarf": [
            (1,   5, "Boatman"),
            (6,   8, "Farmer"),
            (9,  10, "Fisherman"),
            (11, 20, "Herdsman"),
            (21, 35, "Hunter"),
            (36, 50, "Miner"),
            (51, 55, "Pilot"),
            (56, 65, "Prospector"),
            (66, 70, "Rat Catcher"),
            (71, 80, "Roadwarden"),
            (81, 90, "Runner"),
            (91, 100, "Trapper"),
        ],
        "Halfling": [
            (1,   5, "Coachman"),
            (6,  10, "Fisherman"),
            (11, 20, "Gamekeeper"),
            (21, 30, "Herdsman"),
            (31, 40, "Hunter"),
            (41, 50, "Muleskinner"),
            (51, 65, "Rat Catcher"),
            (66, 70, "Roadwarden"),
            (71, 75, "Toll-Keeper"),
            (76, 85, "Trapper"),
            (86, 100, "Woodsman"),
        ],
    },

    "Rogue": {
        # Dwarfs and Elves (practically) have no Rogue class
        "Human": [
            (1,   5, "Agitator"),
            (6,  15, "Bawd"),
            (16, 25, "Beggar"),
            (26, 35, "Entertainer"),
            (36, 45, "Footpad"),
            (46, 50, "Gambler"),
            (51, 55, "Grave Robber"),
            (56, 60, "Jailer"),
            (61, 65, "Pedlar"),
            (66, 70, "Raconteur"),
            (71, 75, "Rustler"),
            (76, 80, "Smuggler"),
            (81, 95, "Thief"),
            (96, 100, "Tomb Robber"),
        ],
        "Halfling": [
            (1,   5, "Agitator"),
            (6,  10, "Bawd"),
            (11, 15, "Beggar"),
            (16, 25, "Entertainer"),
            (26, 30, "Footpad"),
            (31, 35, "Gambler"),
            (36, 40, "Grave Robber"),
            (41, 45, "Jailer"),
            (46, 55, "Pedlar"),
            (56, 65, "Raconteur"),
            (66, 70, "Rustler"),
            (71, 80, "Smuggler"),
            (81, 95, "Thief"),
            (96, 100, "Tomb Robber"),
        ],
    },

    "Academic": {
        "Human": [
            (1,  10, "Alchemist's Apprentice"),
            (11, 20, "Artisan's Apprentice"),
            (21, 25, "Druid"),
            (26, 30, "Exciseman"),
            (31, 35, "Herbalist"),
            (36, 38, "Hedge-Wizard's Apprentice"),
            (39, 42, "Hypnotist"),
            (43, 52, "Initiate"),
            (53, 57, "Pharmacist"),
            (58, 62, "Physician's Student"),
            (63, 72, "Scribe"),
            (73, 77, "Seer"),
            (78, 82, "Student"),
            (83, 92, "Trader"),
            (93, 100, "Wizard's Apprentice"),
        ],
        "Elf": [
            (1,  10, "Alchemist's Apprentice"),
            (11, 15, "Artisan's Apprentice"),
            (16, 30, "Herbalist"),
            (31, 35, "Hypnotist"),
            (36, 40, "Initiate"),
            (41, 45, "Pharmacist"),
            (46, 50, "Physician's Student"),
            (51, 55, "Scribe"),
            (56, 65, "Seer"),
            (66, 70, "Student"),
            (71, 85, "Trader"),
            (86, 87, "Wizard's Apprentice"),
            (88, 100, "Wood Elf Mage's Apprentice"),
        ],
        "Dwarf": [
            (1,   5, "Alchemist's Apprentice"),
            (6,  28, "Artisan's Apprentice"),
            (29, 53, "Engineer"),
            (54, 58, "Herbalist"),
            (59, 63, "Initiate"),
            (64, 73, "Pharmacist"),
            (74, 78, "Physician's Student"),
            (79, 86, "Runescribe"),
            (87, 90, "Runesmith's Apprentice"),
            (91, 100, "Trader"),
        ],
        "Halfling": [
            (1,  10, "Alchemist's Apprentice"),
            (11, 25, "Artisan's Apprentice"),
            (26, 30, "Exciseman"),
            (31, 40, "Herbalist"),
            (41, 47, "Hedge-Wizard's Apprentice"),
            (48, 52, "Initiate"),
            (53, 62, "Pharmacist"),
            (63, 68, "Physician's Student"),
            (69, 78, "Scribe"),
            (79, 83, "Seer"),
            (84, 88, "Student"),
            (89, 98, "Trader"),
            (99, 100, "Wizard's Apprentice"),
        ],
    },
}


# ---------------------------------------------------------------------------
# Advanced careers not in CAREER_CLASS_TABLES (accessible only via exits)
# ---------------------------------------------------------------------------
ADVANCED_CAREER_CLASSES: dict[str, str] = {
    "Scholar":  "Academic",
    "Minstrel": "Rogue",
}


# ---------------------------------------------------------------------------
# Career definitions
# advance_scheme: max advances available while in this career
# S and T advances are on the small D3 scale (0–4), not percentile.
# ---------------------------------------------------------------------------

CAREERS: dict[str, dict] = {

    # ── WARRIOR CAREERS ──────────────────────────────────────────────────────

    "Bodyguard": {
        "advance_scheme": {"WS": 20, "S": 1, "W": 2, "I": 10, "A": 1},
        "skills": [
            "Disarm", "Specialist Weapon - Fist Weapon", "Street Fighting",
            "Strike Mighty Blow", "Strike To Stun",
            "50% chance of Very Strong",
        ],
        "trappings": ["Knuckle-Dusters", "Leather Jack", "50% chance of Shield"],
        "exits": ["Bounty Hunter", "Footpad", "Mercenary", "Outlaw Chief"],
    },

    "Labourer": {
        "advance_scheme": {"S": 1, "T": 1, "W": 2},
        "skills": [
            "Scale Sheer Surface",
            "75% chance of Consume Alcohol", "75% chance of Sing",
            "50% chance of Carpentry", "50% chance of Drive Cart",
            "25% chance of Engineering", "25% chance of Very Resilient",
            "25% chance of Very Strong",
        ],
        "trappings": [
            "Sling bag containing packed lunch", "Flask of herbal tea", "Leather Jack",
        ],
        "exits": [
            "Artillerist (only for characters with Carpentry and/or Engineering)",
            "Bodyguard", "Footpad", "Miner",
        ],
    },

    "Marine": {
        "advance_scheme": {"WS": 10, "BS": 10, "S": 1, "W": 2, "I": 10, "A": 1, "Cl": 10},
        "skills": [
            "Consume Alcohol", "Disarm", "Dodge Blow", "Row",
            "Secret Language: Battle Tongue", "Strike Mighty Blow", "Strike To Stun",
            "25% chance of Swim",
        ],
        "trappings": [
            "Bow or Crossbow and ammunition", "Grappling hook and 10 yards of rope",
            "Mail Shirt", "Shield",
        ],
        "exits": [
            "Artillerist", "Bounty Hunter", "Footpad", "Mercenary Captain",
            "Sea Captain", "Slaver",
        ],
    },

    "Mercenary": {
        "advance_scheme": {"WS": 10, "BS": 10, "S": 1, "W": 2, "I": 10, "A": 1, "Ld": 10, "Cl": 10},
        "skills": [
            "Disarm", "Dodge Blow", "Secret Language: Battle Tongue",
            "Strike Mighty Blow", "Strike To Stun",
            "75% chance of Drive Cart", "50% chance of Animal Care", "25% chance of Ride",
        ],
        "trappings": ["Hand Weapon", "Bow or Crossbow and ammunition", "Mail Shirt or Metal Breastplate", "Shield"],
        "exits": [
            "Artillerist", "Gunner", "Mercenary Captain", "Outlaw Chief",
            "Sapper (Dwarfs only)", "Slaver", "Tunnel Fighter",
        ],
    },

    "Militiaman": {
        "advance_scheme": {"WS": 10, "BS": 10, "W": 2, "I": 10, "A": 1},
        "skills": [
            "Dodge Blow", "Strike Mighty Blow",
            "50% chance of Drive Cart", "25% chance of Animal Care", "25% chance of Ride",
        ],
        "trappings": ["Bow or Crossbow and ammunition", "Mail Shirt", "Shield", "Spear"],
        "exits": ["Footpad", "Mercenary", "Outlaw"],
    },

    "Noble": {
        "advance_scheme": {"Ld": 10, "Int": 10, "Cl": 10, "WP": 10, "Fel": 20, "W": 1},
        "skills": [
            "Blather", "Charm", "Etiquette", "Heraldry", "Luck", "Read/Write",
            "Ride", "Wit",
            "50% chance of Gamble", "50% chance of Public Speaking",
            "25% chance of Consume Alcohol",
            "25% chance of Specialist Weapon: Fencing Sword",
            "10% chance of Musicianship",
        ],
        "trappings": [
            "Horse", "Expensive clothes", "2D6 Gold Crowns",
            "Jewellery worth 10D6 Gold Crowns", "D4 hangers-on",
        ],
        "exits": ["Knight Errant", "Politician", "Lawyer"],
    },

    "Outlaw": {
        "advance_scheme": {"BS": 10, "I": 10, "Dex": 10, "WP": 10, "W": 2},
        "skills": [
            "Concealment: Rural", "Disarm", "Dodge Blow", "Scale Sheer Surface",
            "Secret Language: Battle Tongue or Thieves' (equal chance of either)",
            "Set Trap", "Silent Move: Rural", "Spot Trap",
            "Strike Mighty Blow", "Strike To Stun",
            "75% chance of Drive Cart", "75% chance of Ride: Horse",
            "50% chance of Animal Care", "25% chance of Marksmanship",
            "25% chance of Secret Signs: Woodsman's",
        ],
        "trappings": ["Bow and ammunition", "Shield", "50% chance of Leather Jerkin"],
        "exits": ["Gamekeeper", "Highwayman", "Outlaw Chief", "Rustler", "Targeteer"],
    },

    "Pit Fighter": {
        "advance_scheme": {"WS": 20, "S": 2, "W": 4, "I": 10, "A": 1, "Cl": 20},
        "skills": [
            "Disarm", "Dodge Blow",
            "Specialist Weapon: Fist Weapons", "Specialist Weapon: Flail Weapons",
            "Specialist Weapon: Parrying Weapons", "Specialist Weapon: Two-Handed Weapons",
            "Strike Mighty Blow", "Strike To Injure",
            "50% chance of Very Resilient", "50% chance of Very Strong",
        ],
        "trappings": [
            "Shield", "Mail Shirt", "Knuckle-Dusters", "Flail",
            "20% chance of Two-Handed Weapon",
        ],
        "exits": [
            "Bounty Hunter", "Footpad", "Judicial Champion", "Outlaw Chief", "Tunnel Fighter",
        ],
    },

    "Protagonist": {
        "advance_scheme": {"WS": 10, "W": 2, "I": 10, "A": 1},
        "skills": [
            "Disarm", "Dodge Blow", "Ride: Horse", "Street Fighting",
            "Strike Mighty Blow", "Strike To Injure", "Strike To Stun",
        ],
        "trappings": ["Horse with saddle and harness", "Mail Shirt or Metal Breastplate", "Shield"],
        "exits": ["Bounty Hunter", "Duellist", "Footpad", "Judicial Champion"],
    },

    "Seaman": {
        "advance_scheme": {"WS": 10, "BS": 10, "Dex": 10, "W": 2, "I": 10, "Cl": 10},
        "skills": [
            "Dodge Blow", "Row", "Sailing", "Scale Sheer Surface",
            "Speak Additional Language", "Street Fighting", "Strike Mighty Blow", "Swim",
            "75% chance of Consume Alcohol",
        ],
        "trappings": ["Bottle of cheap spirit"],
        "exits": ["Boatman", "Pilot", "Raconteur", "Sea Captain", "Slaver", "Smuggler"],
    },

    "Servant": {
        "advance_scheme": {"I": 10, "Fel": 10, "W": 1},
        "skills": ["Cook", "Drive Cart", "Evaluate", "Gossip", "Pub Talk", "Ride"],
        "trappings": ["Uniform or Livery", "1D6 Silver Shillings"],
        "exits": ["Bodyguard", "Entertainer", "Valet"],
    },

    "Soldier": {
        "advance_scheme": {"WS": 10, "BS": 10, "W": 2, "I": 10, "A": 1, "Cl": 10},
        "skills": [
            "Disarm", "Dodge Blow", "Secret Language: Battle Tongue",
            "Street Fighting", "Strike Mighty Blow",
            "50% chance of Animal Care", "25% chance of Ride: Horse",
        ],
        "trappings": ["Bow or Crossbow and ammunition", "Mail Shirt", "Shield"],
        "exits": [
            "Artillerist", "Bounty Hunter", "Footpad", "Gunner",
            "Mercenary Captain", "Slaver", "Sapper (Dwarfs only)",
        ],
    },

    "Squire": {
        "advance_scheme": {"WS": 10, "I": 10, "Dex": 10, "Ld": 10, "Fel": 10, "W": 2},
        "skills": [
            "Charm", "Drive Cart", "Evaluate", "Read/Write",
            "Ride", "Speak Additional Language",
        ],
        "trappings": ["Sword", "Horse", "Good Clothing", "3D6 Silver Shillings"],
        "exits": ["Knight Errant", "Mercenary", "Soldier"],
    },

    "Troll Slayer": {
        "advance_scheme": {"WS": 20, "S": 2, "W": 2, "I": 10, "A": 1, "Cl": 20, "WP": 20},
        "skills": [
            "Disarm", "Dodge Blow", "Specialist Weapon: Two-Handed Weapon",
            "Street Fighting", "Strike Mighty Blow",
        ],
        "trappings": ["Two-Handed Axe"],
        "note": "Dwarf only. Character has sworn the Slayer Oath.",
        "exits": ["Giant Slayer"],
    },

    "Tunnel Fighter": {
        "advance_scheme": {"WS": 10, "S": 1, "W": 2, "I": 10, "A": 1},
        "skills": [
            "Dodge Blow", "Orientation (underground only)", "Scale Sheer Surface",
            "Strike Mighty Blow", "Strike To Injure", "Strike To Stun",
        ],
        "trappings": [
            "Crossbow and ammunition", "Grappling hook and 10 yards of rope",
            "Mail Coat", "Shield", "Water flask",
        ],
        "exits": ["Sapper (Dwarfs only)", "Smuggler", "Tomb Robber"],
    },

    "Watchman": {
        "advance_scheme": {"WS": 10, "W": 2, "I": 10, "A": 1},
        "skills": ["Strike Mighty Blow", "Strike To Stun"],
        "trappings": [
            "Club", "Lantern and pole",
            "25% chance of Mail Shirt",
            "Leather Jack (if character doesn't have Mail Shirt)",
        ],
        "exits": [
            "Bounty Hunter", "Judicial Champion", "Mercenary Captain",
            "Racketeer", "Roadwarden",
        ],
    },

    # ── RANGER CAREERS ───────────────────────────────────────────────────────

    "Boatman": {
        "advance_scheme": {"Dex": 10, "I": 10, "W": 2},
        "skills": [
            "Fish", "Orientation", "River Lore", "Row",
            "50% chance of Very Strong", "25% chance of Boat Building",
            "25% chance of Consume Alcohol",
        ],
        "trappings": ["Hand Weapon", "Leather Jack", "Rowing Boat (moored on nearest water)"],
        "exits": ["Outlaw", "Seaman", "Smuggler"],
    },

    "Bounty Hunter": {
        "advance_scheme": {"BS": 10, "I": 10, "Dex": 10, "Cl": 10, "W": 2},
        "skills": [
            "Follow Trail", "Shadowing", "Silent Move: Rural", "Silent Move: Urban",
            "Specialist Weapon: Lasso", "Specialist Weapon: Net",
            "Strike Mighty Blow", "50% chance of Marksmanship",
        ],
        "trappings": [
            "Bow or Crossbow and ammunition", "Hand Weapon", "Mail Shirt",
            "Rope", "Net", "D4 pairs of Manacles",
        ],
        "exits": [
            "Assassin", "Footpad", "Mercenary", "Protagonist", "Slaver", "Targeteer",
        ],
    },

    "Coachman": {
        "advance_scheme": {"BS": 10, "Dex": 10, "I": 10, "W": 1},
        "skills": [
            "Animal Care", "Drive Cart", "Musicianship - Coach-Horn",
            "Ride: Horse", "Specialist Weapon - Firearms",
        ],
        "trappings": [
            "Coach-Horn",
            "Blunderbuss and D6 shots of powder and ammunition",
            "Hand Weapon", "Mail Shirt",
        ],
        "exits": ["Highwayman", "Scout"],
    },

    "Farmer": {
        "advance_scheme": {"S": 1, "T": 1, "W": 2},
        "skills": [
            "Agriculture", "Animal Care", "Carpentry", "Drive Cart",
            "Herb Lore", "Identify Plants",
        ],
        "trappings": ["Leather Jack", "Plough", "Spade"],
        "exits": ["Militiaman", "Scout", "Soldier", "Trader"],
    },

    "Fisherman": {
        "advance_scheme": {"Dex": 10, "I": 10, "W": 2},
        "skills": [
            "Fish", "Sailing", "Swim",
            "50% chance of River Lore", "25% chance of Boat Building",
            "5% chance of Cartography",
        ],
        "trappings": ["Leather Jack", "25% chance of Boat (moored or hidden at nearest water)"],
        "exits": ["Pilot", "Seaman", "Smuggler", "Trader"],
    },

    "Gamekeeper": {
        "advance_scheme": {"BS": 10, "I": 10, "Dex": 10, "W": 2},
        "skills": [
            "Concealment: Rural", "Marksmanship",
            "Secret Signs: Poacher (Poachers only)",
            "Set Trap", "Silent Move: Rural", "Spot Trap",
            "50% chance of Secret Language: Ranger",
            "10% chance of Animal Training: Hawk",
        ],
        "trappings": [
            "Bow or Crossbow and ammunition", "Hand Weapon", "Leather Jack", "Man Trap",
        ],
        "exits": ["Druid", "Outlaw", "Scout", "Targeteer"],
    },

    "Herdsman": {
        "advance_scheme": {"T": 1, "I": 10, "W": 2},
        "skills": [
            "Animal Care", "Charm Animal", "Musicianship: Wind Instruments",
            "Specialist Weapon: Sling",
            "75% chance of Herb Lore", "75% chance of Very Resilient",
            "50% chance of Animal Training",
        ],
        "trappings": ["Hand Weapon", "Pan-pipes", "Sling and ammunition", "Staff"],
        "exits": ["Druid", "Militiaman", "Outlaw", "Rustler", "Scout"],
    },

    "Hunter": {
        "advance_scheme": {"BS": 10, "I": 10, "Dex": 10, "W": 2},
        "skills": [
            "Concealment: Rural", "Follow Trail", "Game Hunting",
            "Secret Language: Ranger", "Secret Signs: Woodsman's",
            "Silent Move: Rural", "25% chance of Immunity To Poison",
        ],
        "trappings": ["Bow or Crossbow and ammunition", "Hand Weapon"],
        "exits": ["Druid", "Outlaw", "Scout"],
    },

    "Miner": {
        "advance_scheme": {"S": 2, "T": 1, "W": 3, "WP": 10},
        "skills": ["Consume Alcohol", "Mining", "Night Vision", "Pub Talk", "Tunnel Rat"],
        "trappings": ["Pick", "Lantern", "Sturdy Clothing", "2D6 Silver Shillings"],
        "note": "Primarily available to Dwarfs.",
        "exits": ["Engineer", "Scout", "Tunnel Fighter"],
    },

    "Muleskinner": {
        "advance_scheme": {"Dex": 10, "I": 10, "W": 1},
        "skills": [
            "Animal Care", "Specialist Weapon: Flail Weapons",
            "75% chance of Drive Cart", "25% chance of Animal Training",
        ],
        "trappings": ["Weatherproof coat", "Broad-brimmed hat", "Hand Weapon", "Whip"],
        "exits": ["Outlaw", "Scout", "Smuggler"],
    },

    "Outrider": {
        "advance_scheme": {"BS": 10, "I": 10, "Dex": 10, "Cl": 10, "W": 2},
        "skills": [
            "Animal Care", "Follow Trail", "Orientation", "Ride: Horse",
            "Silent Move: Rural", "Specialist Weapon: Lasso",
            "75% chance of Secret Signs: Scout's or Woodsman's",
        ],
        "trappings": [
            "Horse, saddle, and harness", "Bow or Crossbow and ammunition",
            "Mail Shirt", "Rope (10 yards)", "Shield",
        ],
        "exits": ["Highwayman", "Mercenary", "Scout"],
    },

    "Pilot": {
        "advance_scheme": {"Dex": 10, "I": 10, "W": 2},
        "skills": [
            "Orientation", "Row", "Sailing", "Swim",
            "20% chance of Consume Alcohol",
        ],
        "trappings": [
            "Leather Jerkin", "Rope (10 yards)",
            "Rowing boat (moored on nearest water)", "2 lanterns",
        ],
        "exits": ["Navigator", "Raconteur", "Sea Captain", "Smuggler"],
    },

    "Prospector": {
        "advance_scheme": {"I": 10, "Int": 10, "W": 2},
        "skills": [
            "Animal Care", "Carpentry", "Metallurgy", "Orientation", "River Lore",
            "50% chance of Fish", "50% chance of Game Hunting", "50% chance of Luck",
            "20% chance of Cartography",
        ],
        "trappings": [
            "Pack", "One-man tent", "Pick", "Shovel", "Pan", "25% chance of Mule",
        ],
        "exits": [
            "Lodefinder (Dwarfs only)", "Miner", "Scout", "Soldier",
            "Tomb Robber", "Tunnel Fighter (Dwarfs only)",
        ],
    },

    "Rat Catcher": {
        "advance_scheme": {"I": 10, "W": 1},
        "skills": [
            "Animal Training: Dog", "Concealment: Urban", "Immunity To Disease",
            "Immunity To Poison", "Set Trap", "Silent Move: Urban",
            "Specialist Weapon: Sling", "Spot Trap",
        ],
        "trappings": [
            "Ratter's pole with D6 dead rats", "Sling and ammunition",
            "Small but vicious dog", "D6 animal traps",
        ],
        "exits": ["Bodyguard", "Footpad", "Grave Robber", "Jailer"],
    },

    "Roadwarden": {
        "advance_scheme": {"WS": 10, "BS": 10, "I": 10, "W": 2, "A": 1},
        "skills": ["Ride: Horse"],
        "trappings": [
            "Bow or Crossbow and ammunition", "Horse with saddle and harness",
            "Mail Shirt", "Rope (10 yards)", "Shield",
        ],
        "exits": ["Highwayman", "Militiaman", "Outlaw"],
    },

    "Runner": {
        "advance_scheme": {"I": 10, "Dex": 10, "W": 1},
        "skills": [
            "Flee!", "Fleet Footed", "Orientation", "Spot Trap",
            "75% chance of Silent Move: Urban", "50% chance of Sixth Sense",
            "25% chance of Follow Trail",
        ],
        "trappings": ["Running shoes", "Specially made loose-fitting clothes", "Headband"],
        "exits": ["Mountaineer", "Scout", "Tunnel Fighter"],
    },

    "Toll-Keeper": {
        "advance_scheme": {"I": 10, "Int": 10, "W": 1},
        "skills": ["Evaluate", "Haggle"],
        "trappings": ["Bow or Crossbow and ammunition", "Mail Shirt", "Shield"],
        "exits": ["Highwayman", "Militiaman", "Outlaw"],
    },

    "Trapper": {
        "advance_scheme": {"BS": 10, "I": 10, "Dex": 10, "W": 2},
        "skills": [
            "Concealment: Rural", "Orientation", "Row",
            "Secret Language: Ranger", "Secret Signs: Woodsman's",
            "Set Trap", "Silent Move: Rural", "Spot Trap",
        ],
        "trappings": [
            "Bow or Crossbow and ammunition", "Fur hat and buckskins",
            "Leather Jerkin", "Rope (10 yards)",
            "Rowing boat or canoe (moored on nearest water)", "D4 animal traps",
        ],
        "exits": ["Druid", "Outlaw", "Scout"],
    },

    "Woodsman": {
        "advance_scheme": {"BS": 10, "S": 1, "I": 10, "Dex": 10, "W": 2},
        "skills": [
            "Concealment: Rural", "Follow Trail", "Identify Plant",
            "Secret Language: Ranger", "Set Trap", "Silent Move: Rural",
            "Specialist Weapon: Two-Handed Weapon", "Spot Trap",
            "75% chance of Secret Signs: Woodsman's",
        ],
        "trappings": ["Leather Jack", "Two-Handed Woodsman's Axe"],
        "exits": ["Druid", "Hedge-Wizard's Apprentice", "Outlaw", "Scout"],
    },

    # ── ROGUE CAREERS ────────────────────────────────────────────────────────

    "Agitator": {
        "advance_scheme": {"I": 10, "Ld": 10, "Int": 10, "WP": 10, "Fel": 10, "W": 1},
        "skills": ["Public Speaking", "Read/Write"],
        "trappings": ["Hand Weapon", "Leather Jack", "2D10 leaflets for various causes"],
        "exits": ["Charlatan", "Demagogue", "Outlaw"],
    },

    "Bawd": {
        "advance_scheme": {"I": 10, "Cl": 10, "Fel": 10, "W": 1},
        "skills": [
            "Bribery", "Secret Language: Thieves' Tongue", "Street Fighting",
            "25% chance of Wit",
        ],
        "trappings": ["Hand Weapon", "Leather Jack", "D6 Gold Crowns"],
        "exits": ["Bodyguard", "Fence", "Informer"],
    },

    "Beggar": {
        "advance_scheme": {"I": 10, "W": 1},
        "skills": [
            "Begging", "Concealment: Urban", "Secret Language: Thieves' Tongue",
            "Secret Signs: Thieves' Signs", "Silent Move: Urban",
            "25% chance of Consume Alcohol",
        ],
        "trappings": [
            "Begging bowl", "Tattered clothes", "Heavy stick", "Bottle of rotgut spirit",
        ],
        "exits": ["Bodyguard", "Informer", "Racketeer", "Rat Catcher"],
    },

    "Entertainer": {
        "advance_scheme": {"I": 10, "Dex": 10, "Cl": 10, "Fel": 10, "W": 2},
        "skills": [
            "Act", "Acrobatics", "Charm", "Dance", "Juggle",
            "Mime", "Musicianship", "Sing", "Tale Teller",
        ],
        "trappings": ["Musical Instrument or Costume", "2D6 Silver Shillings"],
        "exits": ["Bard", "Jongleur", "Minstrel"],
    },

    "Footpad": {
        "advance_scheme": {"I": 10, "Dex": 10, "W": 1},
        "skills": [
            "Concealment Urban", "Dodge Blow", "Gamble",
            "Palm Object", "Pick Pocket", "Scale Sheer Surface",
            "Secret Language (Thieves' Tongue)", "Secret Signs (Thief)",
            "Silent Move Urban", "Sleight of Hand",
        ],
        "trappings": ["Dagger", "2D6 Silver Shillings"],
        "exits": ["Outlaw", "Rogue", "Thief"],
    },

    "Gambler": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "Cl": 10, "W": 1},
        "skills": ["Gamble", "Luck", "Palm Object"],
        "trappings": [
            "Hand Weapon", "Leather Jack",
            "Pack of cards (including spare aces)",
            "Pair of dice", "Pair of loaded dice (always roll sixes)",
        ],
        "exits": ["Charlatan"],
    },

    "Grave Robber": {
        "advance_scheme": {"I": 10, "Dex": 10, "W": 1},
        "skills": [
            "Silent Move: Rural", "Silent Move: Urban",
            "25% chance of Spot Trap",
        ],
        "trappings": ["Black cloak", "Hand Weapon", "Lantern", "Large sack", "Spade"],
        "exits": ["Bodyguard", "Physician's Student", "Rat Catcher"],
    },

    "Jailer": {
        "advance_scheme": {"WS": 10, "S": 1, "W": 2, "Cl": 10, "A": 1},
        "skills": [
            "Immunity To Disease", "Immunity To Poison", "Palm Object",
            "Silent Move: Urban",
            "50% chance of Very Resilient", "25% chance of Consume Alcohol",
            "25% chance of Very Strong",
        ],
        "trappings": ["Club", "Ring of heavy keys", "Bottle of rough wine", "Fleas"],
        "exits": ["Bodyguard", "Rat Catcher", "Slaver", "Torturer"],
    },

    "Minstrel": {
        "advance_scheme": {"I": 10, "Dex": 10, "Ld": 10, "Cl": 10, "Fel": 10, "W": 1},
        "skills": ["Charm", "Etiquette", "Musicianship", "Public Speaking", "Sing"],
        "trappings": ["Lute or mandolin", "Sheet music", "Colourful clothes"],
        "exits": ["Charlatan", "Jester"],
    },

    "Pedlar": {
        "advance_scheme": {"I": 10, "Dex": 10, "Cl": 10, "Fel": 10, "W": 2},
        "skills": [
            "Animal Care", "Blather", "Drive Cart", "Evaluate", "Haggle",
            "Herb Lore", "Secret Signs: Pedlar", "Specialist Weapon: Fist Weapon",
            "10% chance of Astronomy",
        ],
        "trappings": [
            "Wagon and Horse", "Mattress and D4 blankets (in wagon)",
            "D4 sacks of assorted trade goods", "3D6 small knives",
            "D6 reels of coloured ribbon",
        ],
        "exits": ["Bodyguard", "Fence", "Outlaw", "Trader", "Trapper"],
    },

    "Raconteur": {
        "advance_scheme": {"I": 10, "Int": 10, "Ld": 10, "Cl": 10, "Fel": 10, "W": 1},
        "skills": [
            "Blather", "Charm", "Public Speaking", "Seduction", "Story Telling", "Wit",
            "25% chance of Etiquette",
        ],
        "trappings": ["Fine quality clothes", "Outrageous hat", "3D6 Gold Crowns"],
        "exits": ["Charlatan", "Demagogue"],
    },

    "Rustler": {
        "advance_scheme": {"BS": 10, "I": 10, "Dex": 10, "W": 1},
        "skills": [
            "Drive Cart", "Silent Move: Rural", "Specialist Weapon: Lasso",
            "50% chance of Secret Language: Ranger", "20% chance of Animal Care",
        ],
        "trappings": ["Horse and cart", "Hand Weapon", "Lantern", "Rope (10 yards)"],
        "exits": ["Outlaw", "Slaver"],
    },

    "Smuggler": {
        "advance_scheme": {"I": 10, "Dex": 10, "W": 1},
        "skills": [
            "Drive Cart", "Row", "Silent Move: Rural", "Silent Move: Urban",
            "50% chance of Consume Alcohol",
            "50% chance of Secret Language: Thieves' Tongue",
            "25% chance of Speak Additional Language",
        ],
        "trappings": [
            "Horse and cart", "Rowing boat (moored or hidden on nearest water)",
            "Hand Weapon", "Leather Jack",
        ],
        "exits": ["Fence", "Pilot", "Seaman"],
    },

    "Thief": {
        "advance_scheme": {"WS": 10, "BS": 10, "W": 2, "I": 10, "Dex": 10, "Fel": 10},
        "skills": [
            "Concealment: Urban", "Secret Language: Thieves' Tongue",
            "Secret Signs: Thieves' Signs", "Silent Move: Rural", "Silent Move: Urban",
            "25% chance of Evaluate",
        ],
        "trappings": [
            "Knife", "Dark Clothing", "Grappling Hook", "10m Rope", "Lock Picks",
        ],
        "exits": ["Bodyguard", "Charlatan", "Informer", "Outlaw", "Racketeer"],
    },

    "Tomb Robber": {
        "advance_scheme": {"I": 10, "Dex": 10, "W": 2},
        "skills": [
            "Concealment: Rural", "Concealment: Urban",
            "Silent Move: Rural", "Silent Move: Urban", "Spot Trap",
            "75% chance of Secret Signs: Thieves'",
            "50% chance of Evaluate",
            "50% chance of Secret Language: Thieves' Tongue",
        ],
        "trappings": [
            "Crowbar", "Hand Weapon", "Lantern", "Leather Jack",
            "Rope (10 yards)", "D4 sacks",
        ],
        "exits": ["Bodyguard", "Fence", "Rat Catcher", "Tunnel Fighter"],
    },

    # ── ACADEMIC CAREERS ─────────────────────────────────────────────────────

    "Alchemist's Apprentice": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "WP": 10, "W": 1},
        "skills": [
            "Brewing", "Evaluate", "Read/Write",
            "50% chance of Chemistry",
        ],
        "trappings": ["None listed"],
        "exits": [
            "Alchemist - level 1", "Astrologer", "Bawd", "Charlatan",
            "Counterfeiter", "Grave Robber", "Prospector",
        ],
    },

    "Artisan's Apprentice": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "W": 2},
        "skills": [
            "Drive Cart",
            "25% chance of Very Resilient", "25% chance of Very Strong",
        ],
        "trappings": ["Hand Weapon", "Tools appropriate to trade skill"],
        "exits": ["Artisan", "Astrologer", "Bodyguard", "Diviner", "Footpad"],
    },

    "Druid": {
        "advance_scheme": {"T": 1, "Ld": 10, "Int": 10, "Cl": 10, "WP": 10, "Fel": 10, "W": 2},
        "skills": [
            "Animal Care", "Dowsing", "Follow Trail", "Identify Plants",
            "Secret Signs: Druid",
        ],
        "trappings": [
            "Bag or sack", "Religious token - a small silver sickle-knife",
            "Staff", "Dowsing rods",
        ],
        "note": "Human Expatriate only.",
        "exits": [
            "Druidic Priest - level 1", "Gamekeeper", "Hedge-Wizard's Apprentice",
            "Hunter", "Outlaw", "Trapper", "Woodsman",
        ],
    },

    "Engineer": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "W": 1},
        "skills": [
            "Carpentry", "Drive Cart", "Engineering", "Read/Write",
            "Secret Signs: Dwarven Engineer's Guild",
            "Set Trap", "Smithing", "Spot Trap",
            "50% chance of Metallurgy",
        ],
        "trappings": ["Hand Weapon", "Leather Jack", "Tool bag", "Hand Axe"],
        "note": "Primarily available to Dwarfs.",
        "exits": [
            "Artillerist", "Artisan", "Gunner", "Master Engineer (Dwarfs only)",
            "Sapper", "Tunnel Fighter",
        ],
    },

    "Exciseman": {
        "advance_scheme": {"I": 10, "Ld": 10, "Int": 10, "Fel": 10, "W": 2},
        "skills": [
            "Blather", "Numismatics", "Read/Write", "Super Numerate",
            "50% chance of Law", "20% chance of Embezzling",
        ],
        "trappings": [
            "Leather Jack", "Hand Weapon", "Writing kit", "Abacus", "D6 Gold Crowns",
        ],
        "exits": [
            "Agitator", "Lawyer", "Merchant", "Militiaman", "Outlaw", "Roadwarden",
        ],
    },

    "Herbalist": {
        "advance_scheme": {"T": 1, "I": 10, "Dex": 10, "Int": 10, "W": 1},
        "skills": [
            "Arcane Language: Druidic", "Cure Disease", "Heal Wounds",
            "Herb Lore", "Identify Plants", "Read/Write",
            "Secret Language: Classical", "Secret Language: Guilder",
            "20% chance of Prepare Poisons",
        ],
        "trappings": ["Pestle and mortar", "Sling bag with dried herbs"],
        "exits": ["Druid", "Physician's Student", "Wise Woman"],
    },

    "Hedge-Wizard's Apprentice": {
        "advance_scheme": {"I": 10, "Int": 10, "WP": 10, "W": 1},
        "skills": [
            "Animal Care", "Cast Spells: Petty Magic", "Flee!",
            "Identify Plants", "Palm Object",
            "50% chance of Silent Move: Rural",
        ],
        "trappings": ["None listed"],
        "exits": [
            "Alchemist's Apprentice", "Beggar", "Charlatan",
            "Hedge-Wizard - level 1", "Herbalist", "Pharmacist",
            "Wizard's Apprentice",
        ],
    },

    "Hypnotist": {
        "advance_scheme": {"I": 10, "Ld": 10, "Int": 10, "WP": 10, "Fel": 10, "W": 1},
        "skills": ["Hypnotise", "Magical Awareness"],
        "trappings": ["Silver charm on chain"],
        "exits": ["Charlatan", "Entertainer", "Scholar"],
    },

    "Initiate": {
        "advance_scheme": {"W": 1, "Int": 10, "Cl": 10, "WP": 10, "Fel": 10},
        "skills": [
            "Read/Write", "Scroll Lore", "Secret Language: Classical",
            "Theology", "Read/Write: Khazalid (Dwarfs only)",
        ],
        "trappings": ["Robes", "Religious symbol"],
        "exits": ["Agitator", "Astrologer", "Augur", "Cleric - level 1", "Diviner", "Exorcist"],
    },

    "Pharmacist": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "W": 1},
        "skills": [
            "Chemistry", "Cure Disease", "Heal Wounds", "Immunity To Poison",
            "Manufacture Drugs", "Prepare Poisons", "Secret Language: Guilder",
        ],
        "trappings": [
            "Pestle and mortar", "D6 small glass jars of various powders and solutions",
        ],
        "exits": ["Alchemist's Apprentice", "Charlatan", "Physician", "Prospector"],
    },

    "Physician's Student": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "W": 1},
        "skills": [
            "Read/Write", "Scroll Lore", "Secret Language: Classical",
            "50% chance of Cure Disease", "50% chance of Heal Wounds",
            "50% chance of Manufacture Drugs", "50% chance of Prepare Poisons",
        ],
        "trappings": [
            "Hand Weapon", "Medical instruments (battered) in case",
            "Pottery jar containing D6 leeches",
        ],
        "exits": [
            "Bawd", "Charlatan", "Grave Robber",
            "Hedge-Wizard's Apprentice", "Physician",
        ],
    },

    "Runescribe": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "WP": 10, "W": 1},
        "skills": [
            "Arcane Language: Dwarf", "Arcane Language: Magick",
            "Read/Write: Khazalid", "Rune Lore",
            "75% chance of Speak Additional Language",
        ],
        "trappings": ["Writing equipment", "Sheets of thin metal foil"],
        "note": "Primarily available to Dwarfs and Norse Humans.",
        "exits": [
            "Alchemist's Apprentice", "Loremaster", "Runesmith's Apprentice", "Scholar",
        ],
    },

    "Runesmith's Apprentice": {
        "advance_scheme": {"WS": 10, "S": 1, "Dex": 10, "Int": 10, "Cl": 10, "W": 2},
        "skills": [
            "Animal Care", "Art", "Carpentry", "Engineering",
            "Magical Sense", "Metallurgy", "Read/Write: Khazalid",
            "Rune Lore", "Smithing",
        ],
        "trappings": [
            "Hand Weapon", "Tools", "Staff",
            "Horse and cart (to carry master's anvil)",
        ],
        "note": "Dwarf only.",
        "exits": ["Artisan", "Engineer", "Loremaster", "Runesmith"],
    },

    "Scholar": {
        "advance_scheme": {"I": 10, "Int": 20, "Cl": 10, "WP": 10, "Fel": 10, "W": 2},
        "skills": [
            "Astronomy", "Cartography", "History", "Identify Plant",
            "Linguistics", "Magical Sense", "Numismatics",
            "Rune Lore", "Speak Additional Language",
        ],
        "trappings": ["Hand Weapon", "Writing equipment", "5D6 Gold Crowns"],
        "exits": ["Explorer", "Loremaster (Dwarfs only)", "Merchant"],
    },

    "Scribe": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "W": 1},
        "skills": [
            "Arcane Language: Magick", "Read/Write", "Secret Language: Classical",
            "50% chance of Speak Additional Language",
        ],
        "trappings": ["Writing equipment"],
        "exits": [
            "Astrologer", "Diviner", "Forger", "Informer", "Lawyer", "Merchant", "Scholar",
        ],
    },

    "Seer": {
        "advance_scheme": {"I": 10, "Int": 10, "WP": 10, "Fel": 10, "W": 1},
        "skills": [
            "Arcane Language: Magick", "Divining", "Magical Sense",
            "50% chance of Blather", "50% chance of Charm Animal",
            "50% chance of Public Speaking",
        ],
        "trappings": ["Divination equipment (bones, sand-tray, dice, etc.)"],
        "exits": ["Agitator", "Astrologer", "Charlatan", "Diviner", "Wise Woman"],
    },

    "Student": {
        "advance_scheme": {"I": 10, "Int": 10, "W": 1},
        "skills": [
            "Arcane Language: Magick", "Read/Write", "Secret Language: Classical",
            "25% chance of Consume Alcohol", "20% chance of History",
            "10% chance of Astronomy", "10% chance of Cartography",
            "10% chance of Identify Plant", "10% chance of Numismatics",
            "10% chance of Speak Additional Language",
        ],
        "trappings": ["Hand Weapon", "D3 textbooks", "Writing kit"],
        "exits": [
            "Agitator", "Astrologer", "Bawd", "Lawyer",
            "Navigator", "Scholar", "Thief",
        ],
    },

    "Trader": {
        "advance_scheme": {"I": 10, "Ld": 10, "Int": 10, "Cl": 10, "Fel": 10, "W": 2},
        "skills": [
            "Evaluate", "Haggle", "Numismatics",
            "25% chance of Blather", "25% chance of Law",
        ],
        "trappings": ["Leather Jerkin", "2D6 Gold Crowns"],
        "exits": ["Fence", "Merchant", "Thief (Clipper)"],
    },

    "Wizard's Apprentice": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 20, "WP": 20},
        "skills": [
            "Arcane Language: Magick", "Cast Spells: Petty Magic only",
            "Read/Write", "Secret Language: Classical",
            "50% chance of Scroll Lore",
        ],
        "trappings": [
            "Grimoire (containing spells of Petty Magic)",
            "D3 doses of magical ingredient",
            "Robe",
        ],
        "exits": [
            "Astrologer", "Bawd", "Charlatan", "Diviner", "Gambler",
            "Grave Robber", "Grey Wizard - level 1", "Tomb Robber", "Wizard - level 1",
        ],
    },

    "Wood Elf Mage's Apprentice": {
        "advance_scheme": {"I": 10, "Dex": 10, "Int": 10, "WP": 20, "W": 2},
        "skills": [
            "Arcane Language: Magick", "Cast Spells: Petty Magic",
            "Follow Trail", "Identify Plants",
            "Secret Language: Malla-room-na-larin", "Sing", "Silent Move: Rural",
        ],
        "trappings": ["None listed"],
        "note": "Wood Elf only.",
        "exits": ["Wizard's Apprentice", "Wood Elf Mage - level 1", "Woodsman"],
    },
}
