"""
Race-appropriate name tables for WFRP 1st Edition.
Names are drawn from the Old World style of the 1986 rulebook.
"""

import random

# (forenames, surnames/epithets)
_NAMES: dict[str, dict] = {
    "Human": {
        "male": [
            "Aldric", "Burkhard", "Dietrich", "Ernst", "Franz", "Gerhard",
            "Heinrich", "Ingo", "Johann", "Karl", "Ludwig", "Manfred",
            "Niklas", "Otto", "Pieter", "Rolf", "Stefan", "Tobias",
            "Ulrich", "Werner", "Xaver", "Yannick", "Zigfried",
        ],
        "female": [
            "Adelheid", "Britta", "Catharina", "Dagmar", "Elke", "Frieda",
            "Greta", "Hilde", "Inge", "Johanna", "Klara", "Liesel",
            "Marta", "Nora", "Ottilie", "Petra", "Renate", "Sigrid",
            "Trude", "Ursula", "Walburga",
        ],
        "surname": [
            "Brauer", "Dreher", "Fischer", "Gerber", "Hammerer", "Jäger",
            "Kaufmann", "Leiner", "Müller", "Nagel", "Pfeiffer", "Richter",
            "Schneider", "Tischler", "Vogel", "Wagner", "Zimmermann",
            "von Stahl", "von Ratten", "zum Schwarzen Bären",
        ],
    },

    "Dwarf": {
        "male": [
            "Angrim", "Balin", "Brokk", "Dagni", "Dolgrin", "Draupnir",
            "Durgin", "Eitri", "Fjord", "Grimni", "Gunnar", "Haldor",
            "Kili", "Lodin", "Morin", "Nori", "Orik", "Ragnir",
            "Skaldi", "Thorek", "Ulfar", "Valgrim",
        ],
        "female": [
            "Bryn", "Dagny", "Edda", "Freyda", "Gudrun", "Helga",
            "Ingrid", "Katla", "Magna", "Ragnhild", "Sigrun", "Thyra",
        ],
        "surname": [
            "Copperback", "Dragonbrew", "Fireforge", "Goldmantle",
            "Hammerfall", "Ironbrow", "Longbeard", "Oathkeeper",
            "Runehand", "Silveraxe", "Stonehelm", "Strongarm",
            "Trollslayer", "Underhill",
        ],
    },

    "Elf": {
        "male": [
            "Aelarion", "Caladrel", "Darandir", "Elandrin", "Faelthas",
            "Galathil", "Ithilmar", "Laraniel", "Meliandir", "Naeris",
            "Orendil", "Palanir", "Quellas", "Ranaloth", "Silarith",
            "Thalion", "Uialdor", "Vaelindra", "Ylthari",
        ],
        "female": [
            "Aelindra", "Caralyn", "Elariel", "Faelindra", "Gilindra",
            "Ithiliel", "Laralindë", "Miriandel", "Naeris", "Orindel",
            "Quelindra", "Silindra", "Thalindra", "Yriel",
        ],
        "surname": [
            "Dawnweaver", "Farstrider", "Greenwarden", "Leafwhisper",
            "Moonbow", "Shadowstep", "Silverwind", "Starmantle",
            "Swiftarrow", "Treesinger", "Windwalker",
        ],
    },

    "Halfling": {
        "male": [
            "Bilbert", "Cob", "Dodinas", "Elias", "Ferdi", "Gorbadoc",
            "Hamfast", "Isumbras", "Jago", "Largo", "Meriadoc",
            "Nob", "Odo", "Peregrin", "Rufo", "Samkin", "Tobold",
            "Uffo", "Wilcome",
        ],
        "female": [
            "Amaranth", "Belba", "Camellia", "Daisy", "Eglantine",
            "Esmeralda", "Hilda", "Marigold", "Myrtle", "Pearl",
            "Poppy", "Primrose", "Rosie", "Ruby", "Tansy",
        ],
        "surname": [
            "Applebottom", "Barleycorn", "Brandyfoot", "Brownlock",
            "Cheesewright", "Fatbottom", "Goodbarrel", "Hayfoot",
            "Larder", "Mugwort", "Proudfoot", "Sackville",
            "Sandybanks", "Sweetbriar", "Thistlewood",
        ],
    },
}


def random_name(race: str) -> str:
    """Return a random full name appropriate for the given race."""
    data = _NAMES.get(race, _NAMES["Human"])
    gender = random.choice(["male", "female"])
    forename = random.choice(data[gender])
    surname = random.choice(data["surname"])
    return f"{forename} {surname}"
