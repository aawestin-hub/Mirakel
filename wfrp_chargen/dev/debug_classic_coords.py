"""Overlay coloured dots on the classic sheet templates to verify all coordinates."""
from PIL import Image, ImageDraw, ImageFont
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
front = Image.open(os.path.join(_HERE, "templates", "edited_front.png")).convert("RGB")
back  = Image.open(os.path.join(_HERE, "templates", "edited_back.png")).convert("RGB")
df = ImageDraw.Draw(front)
db = ImageDraw.Draw(back)
try:
    fnt = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
    fnt_s = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
except Exception:
    fnt = fnt_s = ImageFont.load_default()

RED  = (220,  20,  20)
BLUE = ( 20,  20, 220)
GRN  = ( 20, 180,  20)

def mark(draw, x, y, label, color=RED):
    draw.ellipse([x-7, y-7, x+7, y+7], fill=color, outline=(0,0,0))
    draw.text((x+10, y-11), label, fill=color, font=fnt_s)

# ── FRONT PAGE ──────────────────────────────────────────────────────────────
mark(df, 175, 335, "NAME")
mark(df, 533, 335, "RACE")
mark(df, 698, 335, "GENDER")
mark(df, 782, 335, "CC")
mark(df, 1205, 335, "ALIGN")

mark(df, 209, 465, "AGE")
mark(df, 309, 465, "HEIGHT")
mark(df, 420, 465, "WEIGHT")
mark(df, 485, 465, "HAIR")
mark(df, 703, 465, "EYES")
mark(df, 883, 465, "DESC")

mark(df, 175, 513, "CAREER(lt)", RED)
mark(df, 373, 513, "CPATH")
mark(df, 883, 513, "EXITS")

cols = {'M':343,'WS':439,'BS':535,'S':631,'T':727,'W':823,
        'I':919,'A':1015,'Dex':1111,'Ld':1207,'Int':1303,
        'Cl':1399,'WP':1495,'Fel':1591}
for stat, x in cols.items():
    mark(df, x, 757, stat, BLUE)
    mark(df, x, 812, stat, BLUE)
    mark(df, x, 867, stat, BLUE)
    df.line([(x, 730), (x, 885)], fill=BLUE, width=1)

mark(df, 175,  952, "HTH_1",  GRN)
mark(df, 505,  952, "SKL_L",  GRN)
mark(df, 800,  952, "SKL_R",  GRN)
mark(df, 175, 1227, "MSL_1",  GRN)
mark(df, 175, 1447, "ARM_1",  GRN)

out_dir = os.path.join(_HERE, "output")
os.makedirs(out_dir, exist_ok=True)
front.save(os.path.join(out_dir, "debug_classic_front.jpg"), quality=95)
print("Front debug saved →", os.path.join(out_dir, "debug_classic_front.jpg"))

# ── BACK PAGE ───────────────────────────────────────────────────────────────
for i in range(5):
    y = 201 + i * 67
    mark(db, 120, y, f"SPELL{i+1}")

mark(db, 315, 201, "SL",   BLUE)
mark(db, 355, 201, "MP",   BLUE)
mark(db, 375, 201, "R",    BLUE)
mark(db, 420, 201, "D",    BLUE)
mark(db, 465, 201, "ING",  BLUE)
mark(db, 750, 201, "EFF",  BLUE)

mark(db, 1520, 205, "FP",  RED)
mark(db, 1520, 299, "MAG", RED)
mark(db, 1520, 393, "PL",  RED)
mark(db, 1520, 483, "XP",  RED)

mark(db,  120, 487, "TRAP1", GRN)
mark(db,  527, 512, "MV_10", GRN)
mark(db,  574, 512, "MV_min",GRN)
mark(db,  614, 512, "MV_kph",GRN)
mark(db, 1165, 487, "LANG1", BLUE)
mark(db, 1175, 695, "IP",    RED)

mark(db,  600, 941,  "BIRTH",    RED)
mark(db,  640, 977,  "PARENT",   RED)
mark(db,  615, 1012, "FAMILY",   RED)
mark(db,  418, 1040, "BACK_TXT", RED)
mark(db,  580, 1140, "SOCIAL",   RED)
mark(db, 1000, 1140, "RELIG",    RED)

mark(db,  120, 1253, "GC",  GRN)
mark(db,  120, 1287, "SS",  GRN)
mark(db,  120, 1321, "BP",  GRN)

back.save(os.path.join(out_dir, "debug_classic_back.jpg"), quality=95)
print("Back debug saved  →", os.path.join(out_dir, "debug_classic_back.jpg"))
