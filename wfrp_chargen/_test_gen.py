import random
from chargen.generator import generate_character
from sheet_image import save_character_spread
random.seed(42)
char = generate_character(None, "Aldric", None, "Wizard's Apprentice")
save_character_spread(char, "preview_latest.jpg")
print("Saved!")
