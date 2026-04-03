import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import random
from chargen.generator import generate_character
from sheet_image import save_character_spread
random.seed(42)
char = generate_character(None, "Aldric", None, "Wizard's Apprentice")
save_character_spread(char, "preview_latest.jpg")
print("Saved!")
