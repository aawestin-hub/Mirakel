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
            "Adalbert", "Brendt", "Conrad", "Dieter", "Erich", "Friedrich",
            "Georg", "Helmut", "Igor", "Jan", "Klaus", "Leo",
            "Markus", "Nikolaus", "Oskar", "Paul", "Reinhold", "Sebold",
            "Theobald", "Udo", "Valentin", "Walther", "Zacharias",
            "Albrecht", "Baldric", "Christoph", "Diederick", "Emmerich",
            "Florian", "Gottfried", "Hans", "Josef", "Klemens",
            "Lorenz", "Matthias", "Norbert", "Philipp", "Rupert",
            "Sebastian", "Tilman", "Wolfram", "Benedikt", "Erasmus",
            "Gregor", "Hieronymus", "Konrad", "Sigmund", "Theodor",
            "Wilhelm", "Anton", "Claus", "Eugen", "Felix",
        ],
        "female": [
            "Adelheid", "Britta", "Catharina", "Dagmar", "Elke", "Frieda",
            "Greta", "Hilde", "Inge", "Johanna", "Klara", "Liesel",
            "Marta", "Nora", "Ottilie", "Petra", "Renate", "Sigrid",
            "Trude", "Ursula", "Walburga",
            "Agathe", "Berta", "Christiane", "Dorothea", "Edith",
            "Franziska", "Gertrude", "Hannelore", "Ilse", "Juliane",
            "Käthe", "Lotte", "Magda", "Natalie", "Pauline",
            "Rositta", "Sofie", "Thea", "Veronika", "Wilhelmine",
            "Angelika", "Barbara", "Christine", "Elisabeth", "Gerda",
            "Hermine", "Irma", "Josephine", "Konstanze", "Leonora",
            "Mechthild", "Rosemunde", "Sibilla", "Theresia", "Walpurga",
            "Anneliese", "Brunhilde", "Cordula", "Elfriede", "Hildegard",
        ],
        "surname": [
            "Brauer", "Dreher", "Fischer", "Gerber", "Hammerer", "Jäger",
            "Kaufmann", "Leiner", "Müller", "Nagel", "Pfeiffer", "Richter",
            "Schneider", "Tischler", "Vogel", "Wagner", "Zimmermann",
            "von Stahl", "von Ratten", "zum Schwarzen Bären",
            "Bauer", "Berg", "Fuchs", "Gross", "Haas", "Krug",
            "Lang", "Meier", "Metz", "Ritter", "Schwarz", "Sommer",
            "Stark", "Stein", "Weber", "Weiss", "Wolf",
            "zur Goldkrone", "zum Silbermond", "von Hammer",
            "Kleinhammer", "Rotbart", "Schwarzkopf", "Felsbrunn",
            "Graustein", "Eisenbach", "Holzmann", "Kreuzberg",
            "Langmann", "Rauber", "Silbermann", "Sturmwind",
            "Waldmann", "Eisenfaust", "Kupfermann", "Salzmann",
        ],
    },

    "Dwarf": {
        "male": [
            "Angrim", "Balin", "Brokk", "Dagni", "Dolgrin", "Draupnir",
            "Durgin", "Eitri", "Fjord", "Grimni", "Gunnar", "Haldor",
            "Kili", "Lodin", "Morin", "Nori", "Orik", "Ragnir",
            "Skaldi", "Thorek", "Ulfar", "Valgrim",
            "Aldrik", "Bofri", "Broddi", "Dori", "Dwalin", "Fafnir",
            "Galdr", "Gorm", "Grundi", "Hafni", "Hammir", "Hrokk",
            "Ingvar", "Kjeld", "Krondi", "Mogri", "Mundr", "Nagli",
            "Olfar", "Ragni", "Snorri", "Steinn", "Stormi", "Svaldi",
            "Thord", "Torvald", "Ulfrik", "Vargi", "Vigrid", "Yngvi",
            "Brokkr", "Darin", "Egil", "Fengri", "Helgi", "Hogni",
        ],
        "female": [
            "Bryn", "Dagny", "Edda", "Freyda", "Gudrun", "Helga",
            "Ingrid", "Katla", "Magna", "Ragnhild", "Sigrun", "Thyra",
            "Aldis", "Bergny", "Brynja", "Dagna", "Embla", "Freya",
            "Gunnhild", "Hagna", "Idunn", "Jorunn", "Kara", "Lovisa",
            "Marta", "Nanna", "Randi", "Sigga", "Solvei", "Thurid",
            "Tora", "Unn", "Valdis", "Vigdis",
        ],
        "surname": [
            "Copperback", "Dragonbrew", "Fireforge", "Goldmantle",
            "Hammerfall", "Ironbrow", "Longbeard", "Oathkeeper",
            "Runehand", "Silveraxe", "Stonehelm", "Strongarm",
            "Trollslayer", "Underhill",
            "Anvilarm", "Boulderback", "Coppershield", "Deepdelver",
            "Emberstrike", "Flintrock", "Gemcutter", "Graniteback",
            "Ironfist", "Kegbreaker", "Mithrilhelm", "Mountainborn",
            "Petrason", "Quarryman", "Rockgrip", "Runeblade",
            "Steelshield", "Strongfist", "Thunderaxe", "Warpick",
        ],
    },

    "Elf": {
        "male": [
            "Aelarion", "Caladrel", "Darandir", "Elandrin", "Faelthas",
            "Galathil", "Ithilmar", "Laraniel", "Meliandir", "Naeris",
            "Orendil", "Palanir", "Quellas", "Ranaloth", "Silarith",
            "Thalion", "Uialdor", "Vaelindra", "Ylthari",
            "Aerandel", "Carandil", "Celeborn", "Dirindel", "Elindor",
            "Faelon", "Gildorin", "Halindor", "Idralas", "Kaladrel",
            "Lanthiel", "Mirindor", "Naerdiel", "Olorath", "Peladril",
            "Quendel", "Raventhal", "Silvandor", "Threndil", "Ulindor",
            "Vardamir", "Windrel", "Xarindel", "Yilindor", "Zarathel",
            "Alandil", "Berendir", "Celorath", "Darthiel", "Eldamar",
        ],
        "female": [
            "Aelindra", "Caralyn", "Elariel", "Faelindra", "Gilindra",
            "Ithiliel", "Laralindë", "Miriandel", "Naeris", "Orindel",
            "Quelindra", "Silindra", "Thalindra", "Yriel",
            "Aerindel", "Caladwen", "Celebriel", "Diandel", "Eleniel",
            "Faerindel", "Galadriel", "Halindra", "Idrial", "Kaladrel",
            "Laurindel", "Miriel", "Narindra", "Olowen", "Peladrel",
            "Quildra", "Ravindra", "Silandel", "Tindrel", "Urindel",
            "Vaelindra", "Windra", "Xarindel", "Yaradel", "Zilindra",
        ],
        "surname": [
            "Dawnweaver", "Farstrider", "Greenwarden", "Leafwhisper",
            "Moonbow", "Shadowstep", "Silverwind", "Starmantle",
            "Swiftarrow", "Treesinger", "Windwalker",
            "Autumnveil", "Bladewhisper", "Crystalsong", "Duskmantle",
            "Embersoul", "Forestborn", "Glimmerpath", "Hollowwood",
            "Ironveil", "Jadeleaf", "Kindlewind", "Lightweave",
            "Morningstar", "Nightgrace", "Oakheart", "Petalweave",
            "Quickgale", "Riverborn", "Streamwalker", "Thornweave",
        ],
    },

    "Halfling": {
        "male": [
            "Bilbert", "Cob", "Dodinas", "Elias", "Ferdi", "Gorbadoc",
            "Hamfast", "Isumbras", "Jago", "Largo", "Meriadoc",
            "Nob", "Odo", "Peregrin", "Rufo", "Samkin", "Tobold",
            "Uffo", "Wilcome",
            "Adelbert", "Balbo", "Colman", "Drogo", "Everard",
            "Folco", "Griffo", "Halfast", "Isembold", "Jolly",
            "Longo", "Mosco", "Mungo", "Otto", "Polo",
            "Robin", "Sadoc", "Tolman", "Uvaldo", "Weldon",
            "Bungo", "Cosimo", "Dinodas", "Filibert", "Gorhendad",
            "Hildibrand", "Inigo", "Jasper", "Lotho", "Milo",
        ],
        "female": [
            "Amaranth", "Belba", "Camellia", "Daisy", "Eglantine",
            "Esmeralda", "Hilda", "Marigold", "Myrtle", "Pearl",
            "Poppy", "Primrose", "Rosie", "Ruby", "Tansy",
            "Angelica", "Begonia", "Clover", "Dora", "Estella",
            "Fern", "Goldie", "Heather", "Iris", "Jasmine",
            "Lavender", "Lobelia", "Mimosa", "Nasturtium", "Pansy",
            "Peony", "Petunia", "Salvia", "Sorrel", "Verbena",
            "Violet", "Wisteria",
        ],
        "surname": [
            "Applebottom", "Barleycorn", "Brandyfoot", "Brownlock",
            "Cheesewright", "Fatbottom", "Goodbarrel", "Hayfoot",
            "Larder", "Mugwort", "Proudfoot", "Sackville",
            "Sandybanks", "Sweetbriar", "Thistlewood",
            "Bolger", "Boffin", "Bracegirdle", "Bunce", "Burrows",
            "Cotton", "Chubb", "Diggle", "Gamgee", "Goodbody",
            "Greenhill", "Grubbs", "Hornblower", "Lightfoot", "Maggot",
            "Noakes", "Puddifoot", "Roper", "Smallburrow", "Took",
        ],
    },
}


def random_name(race: str, gender: str | None = None) -> str:
    """Return a random full name appropriate for the given race and gender."""
    data = _NAMES.get(race, _NAMES["Human"])
    if gender and gender.lower() in ("male", "female"):
        g = gender.lower()
    else:
        g = random.choice(["male", "female"])
    forename = random.choice(data[g])
    surname = random.choice(data["surname"])
    return f"{forename} {surname}"
