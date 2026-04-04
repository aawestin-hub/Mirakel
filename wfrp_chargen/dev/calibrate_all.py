"""Draw calibration markers on both templates to verify all coordinates."""
from PIL import Image, ImageDraw, ImageFont
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sheet_classic import (
    _C1_STAT_COLS, _C1_STARTER_Y, _C1_ADV_Y, _C1_CURR_Y,
    _C1_CAREER_X, _C1_CAREER_Y, _C1_CPATH_X,
    _C1_EXITS_X, _C1_EXITS_Y,
    _C1_HTH_START_Y, _C1_SKILL_START_Y, _C1_SKILL_L_X, _C1_SKILL_R_X,
    _C1_NAME_X, _C1_NAME_Y, _C1_RACE_X, _C1_RACE_Y,
    _C2_SPELL_NAME_X, _C2_SPELL_SL_X, _C2_SPELL_MP_X, _C2_SPELL_R_X,
    _C2_SPELL_D_X, _C2_SPELL_ING_X, _C2_SPELL_EFF_X, _C2_SPELL_START_Y, _C2_SPELL_SPACING,
    _C2_FP_X, _C2_FP_Y, _C2_MAG_X, _C2_MAG_Y, _C2_PL_X, _C2_PL_Y, _C2_XP_X, _C2_XP_Y,
    _C2_TRAP_NAME_X, _C2_TRAP_START_Y, _C2_TRAP_SPACING,
    _C2_MV_10_X, _C2_MV_MIN_X, _C2_MV_MPH_X, _C2_MV_CAUT_Y, _C2_MV_STD_Y, _C2_MV_RUN_Y,
    _C2_LANG_X, _C2_LANG_START_Y,
    _C2_BIRTH_X, _C2_BIRTH_Y, _C2_PARENT_X, _C2_PARENT_Y, _C2_FAMILY_X, _C2_FAMILY_Y,
    _C2_SOCIAL_X, _C2_SOCIAL_Y, _C2_RELIG_X, _C2_RELIG_Y,
    _C2_WGC_X, _C2_WGC_Y, _C2_WSS_X, _C2_WSS_Y, _C2_WBP_X, _C2_WBP_Y,
    _FRONT_TMPL, _BACK_TMPL,
)
_C1_CPATH_Y = _C1_CAREER_Y

RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 128, 0)

def dot(draw, x, y, color=RED, r=8):
    draw.ellipse([x-r, y-r, x+r, y+r], outline=color, width=2)

def label(draw, x, y, text, color=RED):
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    except Exception:
        font = None
    draw.text((x+10, y-8), text, fill=color, font=font)

# ── PAGE 1 ─────────────────────────────────────────────────────────────
p1 = Image.open(_FRONT_TMPL).copy().convert("RGB")
d1 = ImageDraw.Draw(p1)

# Stats columns – mark all 3 rows
for stat, x in _C1_STAT_COLS.items():
    for y, color in [(_C1_STARTER_Y, RED), (_C1_ADV_Y, BLUE), (_C1_CURR_Y, GREEN)]:
        dot(d1, x, y, color, r=5)
    label(d1, x-15, _C1_STARTER_Y - 20, stat, RED)

# Career row
dot(d1, _C1_CAREER_X, _C1_CAREER_Y, RED)
label(d1, _C1_CAREER_X, _C1_CAREER_Y, 'CAREER', RED)
dot(d1, _C1_CPATH_X, _C1_CPATH_Y, BLUE)
label(d1, _C1_CPATH_X, _C1_CPATH_Y, 'PATH', BLUE)
dot(d1, _C1_EXITS_X, _C1_EXITS_Y, GREEN)
label(d1, _C1_EXITS_X, _C1_EXITS_Y, 'EXITS', GREEN)

# Name row
dot(d1, _C1_NAME_X, _C1_NAME_Y, RED)
label(d1, _C1_NAME_X, _C1_NAME_Y, 'NAME', RED)
dot(d1, _C1_RACE_X, _C1_RACE_Y, BLUE)
label(d1, _C1_RACE_X, _C1_RACE_Y, 'RACE', BLUE)

# Skills
for i in range(6):
    y = _C1_SKILL_START_Y + i * 55
    dot(d1, _C1_SKILL_L_X, y, GREEN, r=4)
    dot(d1, _C1_SKILL_R_X, y, RED, r=4)

p1.save('dev/calibrate_p1.jpg', 'JPEG', quality=90)
print("Saved dev/calibrate_p1.jpg")

# ── PAGE 2 ─────────────────────────────────────────────────────────────
p2 = Image.open(_BACK_TMPL).copy().convert("RGB")
d2 = ImageDraw.Draw(p2)

# Spell rows
for i in range(5):
    y = _C2_SPELL_START_Y + i * _C2_SPELL_SPACING
    for x, name in [(_C2_SPELL_NAME_X, 'NAME'), (_C2_SPELL_SL_X, 'SL'),
                    (_C2_SPELL_MP_X, 'MP'), (_C2_SPELL_R_X, 'R'),
                    (_C2_SPELL_D_X, 'D'), (_C2_SPELL_ING_X, 'ING'),
                    (_C2_SPELL_EFF_X, 'EFF')]:
        dot(d2, x, y, RED if i == 0 else BLUE, r=5)
    if i == 0:
        for x, name in [(_C2_SPELL_SL_X, 'SL'), (_C2_SPELL_MP_X, 'MP'),
                        (_C2_SPELL_R_X, 'R'), (_C2_SPELL_D_X, 'D'),
                        (_C2_SPELL_ING_X, 'ING'), (_C2_SPELL_EFF_X, 'EFF')]:
            label(d2, x, y-20, name, RED)

# Right column boxes
for x, y, name, color in [
    (_C2_FP_X, _C2_FP_Y, 'FP', RED),
    (_C2_MAG_X, _C2_MAG_Y, 'MAG', BLUE),
    (_C2_PL_X, _C2_PL_Y, 'PL', GREEN),
    (_C2_XP_X, _C2_XP_Y, 'XP', RED),
]:
    dot(d2, x, y, color)
    label(d2, x+10, y, name, color)

# Trappings
for i in range(6):
    y = _C2_TRAP_START_Y + i * _C2_TRAP_SPACING
    dot(d2, _C2_TRAP_NAME_X, y, GREEN, r=4)

# Movement
for y, name in [(_C2_MV_CAUT_Y, 'CAUT'), (_C2_MV_STD_Y, 'STD'), (_C2_MV_RUN_Y, 'RUN')]:
    for x in [_C2_MV_10_X, _C2_MV_MIN_X, _C2_MV_MPH_X]:
        dot(d2, x, y, BLUE, r=5)

# Languages
for i in range(4):
    y = _C2_LANG_START_Y + i * 30
    dot(d2, _C2_LANG_X, y, RED, r=4)

# Background fields
for x, y, name in [(_C2_BIRTH_X, _C2_BIRTH_Y, 'BIRTH'), (_C2_PARENT_X, _C2_PARENT_Y, 'PARENT'),
                   (_C2_FAMILY_X, _C2_FAMILY_Y, 'FAMILY')]:
    dot(d2, x, y, GREEN)
    label(d2, x, y, name, GREEN)

# Wealth
for x, y, name in [(_C2_WGC_X, _C2_WGC_Y, 'GC'), (_C2_WSS_X, _C2_WSS_Y, 'SS'),
                   (_C2_WBP_X, _C2_WBP_Y, 'BP')]:
    dot(d2, x, y, RED, r=6)
    label(d2, x, y, name, RED)

p2.save('dev/calibrate_p2.jpg', 'JPEG', quality=90)
print("Saved dev/calibrate_p2.jpg")
