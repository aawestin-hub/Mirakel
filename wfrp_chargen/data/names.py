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
            "Adalger", "Berthold", "Cuno", "Detlef", "Engelbert",
            "Folkmar", "Goswin", "Hartmann", "Immo", "Jost",
            "Kunrad", "Luitpold", "Moritz", "Nico", "Ortwin",
            "Pankraz", "Reinmar", "Sigebrecht", "Timo", "Volkmar",
            "Wendelin", "Xandor", "Zeno", "Arndt", "Bertram",
            "Caius", "Diebold", "Edvard", "Friederich", "Gunter",
            "Hubertus", "Idolf", "Junker", "Kordian", "Lenz",
            # Extra variety
            "Aldhard", "Brennus", "Casimir", "Dietmar", "Eckhard",
            "Fabian", "Gebhard", "Hanno", "Ivo", "Joachim",
            "Kaspar", "Lambert", "Magnus", "Nepomuk", "Oswin",
            "Prosper", "Quirinus", "Raimund", "Sifrid", "Traugott",
            "Ulbert", "Veit", "Waldemar", "Xeno", "Yorick",
            "Zebulon", "Achard", "Borwin", "Cunrat", "Dankwart",
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
            "Adelgunde", "Bertrada", "Cäcilia", "Dietlinde", "Ermentrud",
            "Freiderike", "Gunhild", "Hedwig", "Irmgard", "Kriemhild",
            "Lieselotte", "Mathilde", "Notburga", "Otthild", "Richenza",
            "Sieglinde", "Trudel", "Uta", "Viviane", "Wibke",
            "Almut", "Brunilde", "Clotilde", "Dörte", "Elsbeth",
            "Felicitas", "Gisela", "Helene", "Isolde", "Jutta",
            # Extra variety
            "Adeltraud", "Berengaria", "Clementia", "Diemut", "Ermgard",
            "Friderun", "Gertrud", "Hadwig", "Ingeborg", "Kunigunde",
            "Liutgard", "Mechtild", "Nothild", "Ortrude", "Peregrina",
            "Radegund", "Swanhild", "Thecla", "Uda", "Waldburg",
            "Xenia", "Yrsa", "Zbigneva", "Aelheid", "Bennigna",
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
            "Ackermann", "Biermann", "Bauer", "Drechsler", "Ehrmann",
            "Fleischer", "Gärtner", "Hafner", "Imhoff", "Kissler",
            "Löffelmann", "Maurer", "Nagler", "Ostermann", "Pfister",
            "Quast", "Rademacher", "Schmied", "Tornow", "Uhlig",
            "von der Heide", "von Rauenstein", "zum Goldenen Anker",
            "Wildemann", "Ziegler", "Brunnmann", "Dorffmann", "Eichmann",
            # Extra surnames
            "Amberfeld", "Brunwald", "Carpenstock", "Dornbusch", "Edelmann",
            "Faustmann", "Glasemann", "Hartberg", "Immenbach", "Johannstock",
            "Kaltenburg", "Lichtenfeld", "Münsterwald", "Neidhardt", "Ochsenkopf",
            "Pfalzmann", "Querfeld", "Ritterbach", "Schönfeld", "Thalbach",
            "Uhlenhorst", "Vogelsberg", "Wachsmann", "Xylburg", "Zorndorf",
            "zum Roten Hahn", "zur Silbernen Eule", "von Wolfburg",
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
            "Asni", "Bivur", "Bopur", "Dafni", "Ekirn", "Funndin",
            "Gandalf", "Glamir", "Gondri", "Hanar", "Hlodvir", "Hreinn",
            "Jorunn", "Kori", "Litr", "Nali", "Nori", "Ori",
            "Rekk", "Sindri", "Skirfir", "Thorin", "Throri", "Virvir",
            # Extra
            "Aldur", "Boldur", "Corbrin", "Durgrim", "Embor",
            "Forgrim", "Grombold", "Holdir", "Ingor", "Kazrik",
            "Lorgrim", "Mordrin", "Norgin", "Orgrik", "Pergrim",
            "Ragdur", "Skolvir", "Torgin", "Ungrim", "Vordrin",
        ],
        "female": [
            "Bryn", "Dagny", "Edda", "Freyda", "Gudrun", "Helga",
            "Ingrid", "Katla", "Magna", "Ragnhild", "Sigrun", "Thyra",
            "Aldis", "Bergny", "Brynja", "Dagna", "Embla", "Freya",
            "Gunnhild", "Hagna", "Idunn", "Jorunn", "Kara", "Lovisa",
            "Marta", "Nanna", "Randi", "Sigga", "Solvei", "Thurid",
            "Tora", "Unn", "Valdis", "Vigdis",
            "Asdis", "Bjorg", "Borghild", "Dalla", "Erna", "Finna",
            "Gjertrud", "Halldis", "Hildur", "Isrid", "Jord", "Kolbrun",
            "Laug", "Magnhild", "Oddny", "Ragna", "Sigdis", "Solveig",
            "Thordis", "Unnur", "Vigdis", "Yrsa",
            # Extra
            "Agna", "Birna", "Disa", "Eldis", "Fjola",
            "Grima", "Hrafna", "Ingirid", "Kolfinna", "Ljot",
            "Mjoll", "Nidbjorg", "Olvora", "Pela", "Rangrid",
            "Signy", "Thorhild", "Ulvhild", "Vigrun", "Yngvild",
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
            "Ashbeard", "Brightforge", "Coalshaper", "Deepvein",
            "Dustmantle", "Flintspark", "Goldvein", "Hammerstone",
            "Ironclad", "Kettlehelm", "Loderunner", "Mastercroft",
            "Nailbiter", "Oreseeker", "Pickmaster", "Rundrik",
            "Stonefist", "Tinderhelm", "Underforge", "Vaultkeeper",
            # Extra
            "Axebreaker", "Boldgranite", "Coalshield", "Deepaxe",
            "Earthmantle", "Forgegrim", "Greystone", "Hardbrew",
            "Ironborn", "Kettlebrow", "Lodepick", "Mineborn",
            "Noblechest", "Oathforge", "Pitmaster", "Runeborn",
        ],
    },

    "Elf": {
        "male": [
            "Aelarion", "Caladrel", "Darandir", "Elandrin", "Faelthas",
            "Galathil", "Ithilmar", "Laraniel", "Meliandir", "Naeril",
            "Orendil", "Palanir", "Quellas", "Ranaloth", "Silarith",
            "Thalion", "Uialdor", "Vaelinor", "Ylthari",
            "Aerandel", "Carandil", "Celeborn", "Dirindel", "Elindor",
            "Faelon", "Gildorin", "Halindor", "Idralas", "Kaladir",
            "Lanthiel", "Mirindor", "Naerdiel", "Olorath", "Peladril",
            "Quendel", "Raventhal", "Silvandor", "Threndil", "Ulindor",
            "Vardamir", "Windrel", "Xarindel", "Yilindor", "Zarathel",
            "Alandil", "Berendir", "Celorath", "Darthiel", "Eldamar",
            "Amroth", "Borgil", "Ciryon", "Duilin", "Egalmoth",
            "Fingon", "Gelmir", "Haldor", "Ingoldo", "Lindir",
            "Maeglin", "Nellas", "Oropher", "Pengolodh", "Rumil",
            "Saeros", "Tuor", "Urion", "Voronwe", "Wiliwarin",
            # Extra
            "Aelthas", "Berindel", "Calindor", "Darethil", "Elarindel",
            "Farandil", "Galdoril", "Halathas", "Indorath", "Kaelthas",
            "Lorindel", "Melindor", "Naerindel", "Olindor", "Perindel",
            "Quelindor", "Randoril", "Seladon", "Thandoril", "Ulindorath",
        ],
        "female": [
            "Aelindra", "Caralyn", "Elariel", "Faelindra", "Gilindra",
            "Ithiliel", "Laralindë", "Miriandel", "Naeris", "Orindel",
            "Quelindra", "Silindra", "Thalindra", "Yriel",
            "Aerindel", "Caladwen", "Celebriel", "Diandel", "Eleniel",
            "Faerindel", "Galadwen", "Halindra", "Idrial", "Kaladwen",
            "Laurindel", "Miriel", "Narindra", "Olowen", "Peladriel",
            "Quildra", "Ravindra", "Silandel", "Tindrel", "Urindel",
            "Vaelindra", "Windra", "Xarindel", "Yaradel", "Zilindra",
            "Amarie", "Beriel", "Celebrian", "Findis", "Galadriel",
            "Haleth", "Indis", "Luthien", "Melian", "Nerdanel",
            "Nienor", "Olwe", "Riel", "Silmarien", "Tinuviel",
            # Extra
            "Aelindel", "Brindela", "Calindra", "Daelawen", "Elindra",
            "Faeldra", "Gaelindra", "Halindwen", "Ithindra", "Kaelindra",
            "Lorindel", "Melawen", "Naelindra", "Olindra", "Paelindra",
            "Quelindra", "Raelindra", "Saelindra", "Taelindra", "Vaelindra",
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
            "Ashbough", "Brightleaf", "Clovermist", "Dewdancer",
            "Evenstar", "Frostbloom", "Goldenwood", "Hazelthorn",
            "Ivymantle", "Juniperveil", "Lakeborn", "Mistweave",
            # Extra
            "Alderbough", "Birchsong", "Cedarwind", "Dawnrider",
            "Elderbloom", "Fernpath", "Galesong", "Heartwood",
            "Ivysong", "Jasperleaf", "Kinderwood", "Leafsong",
            "Moonweave", "Nightbloom", "Oakveil", "Pinecrest",
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
            "Andwise", "Bowman", "Cabbage", "Dinodas", "Erling",
            "Falco", "Gardener", "Hamson", "Ilbert", "Jedsmith",
            "Kembro", "Largo", "Munro", "Ninto", "Oakley",
            "Poddo", "Quimby", "Ruggo", "Sancho", "Tomba",
            # Extra (Moot-style halfling names)
            "Aldo", "Baldo", "Celdo", "Delmo", "Elmo",
            "Falko", "Galbo", "Halco", "Idelmo", "Jalco",
            "Kelmo", "Lalco", "Malco", "Nalbo", "Olmo",
            "Palco", "Ralbo", "Salco", "Talmo", "Ulco",
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
            "Acacia", "Bluebell", "Chrysanthemum", "Daffodil", "Edelweiss",
            "Foxglove", "Geranium", "Honeydew", "Idellia", "Juniper",
            "Larkspur", "Magnolia", "Narcissa", "Oleander", "Petal",
            "Queensfoil", "Rosemary", "Saffron", "Thyme", "Umbella",
            # Extra
            "Almond", "Barley", "Clover", "Dill", "Fennel",
            "Ginger", "Hazel", "Ivy", "Juniper", "Kale",
            "Lily", "Mint", "Nettle", "Olive", "Parsley",
            "Quince", "Rose", "Sage", "Tara", "Umber",
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
            "Applepie", "Barrelbottom", "Corkscrew", "Dustyfeet",
            "Elderberry", "Flapmoor", "Goodpipe", "Haybottom",
            "Jollyweed", "Kettlesworth", "Leafstep", "Mudfoot",
            "Nicewhistle", "Onionpatch", "Pipewort", "Roundbelly",
            # Extra
            "Appletree", "Bumblebee", "Cobblepot", "Daisyfoot",
            "Elderflower", "Fieldmouse", "Gooseberry", "Hobbithole",
            "Inkwell", "Jamsworth", "Kettledrum", "Lardefoot",
            "Mapleleaf", "Noodlecroft", "Oatfield", "Puddingbrook",
        ],
    },
}


def random_name(race: str, gender: str | None = None,
                exclude: set | None = None) -> str:
    """Return a random full name appropriate for the given race and gender.

    Parameters
    ----------
    race    : "Human", "Elf", "Dwarf", or "Halfling"
    gender  : "Male" / "Female" / None (random)
    exclude : set of full names already used — the function will try up to
              10 times to return a name not in this set before giving up.
    """
    data = _NAMES.get(race, _NAMES["Human"])
    if gender and gender.lower() in ("male", "female"):
        g = gender.lower()
    else:
        g = random.choice(["male", "female"])

    exclude = exclude or set()
    for _ in range(10):
        forename = random.choice(data[g])
        surname  = random.choice(data["surname"])
        name = f"{forename} {surname}"
        if name not in exclude:
            return name
    # Fallback: return whatever we get on the last try
    return name
