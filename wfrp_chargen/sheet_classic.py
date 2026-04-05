"""
Fills character data onto the Classic WFRP 1st Edition character sheet
(WFRP_Character_Sheet_Edited front/back, rendered at 200 DPI → 1700×2200 px).

Coordinates are calibrated for the 1700×2200 image.
Run `python dev/calibrate_classic.py` to fine-tune positions.
"""

from PIL import Image, ImageDraw
import os

from chargen.character import Character
from data.weapons import get_hth_stats, get_missile_stats, get_armour_stats
from data.spells import get_spell

# Re-use shared drawing utilities from the main sheet module
from sheet_image import (
    _get_font, _draw_text, _draw_text_fit, _draw_text_wrap, _draw_paragraph,
    _INK,
)

_HERE       = os.path.dirname(os.path.abspath(__file__))
_FRONT_TMPL = os.path.join(_HERE, "templates", "edited_front.png")
_BACK_TMPL  = os.path.join(_HERE, "templates", "edited_back.png")

_PAGE_GAP = 14  # px gap between pages in the spread image

# ── Font sizes (scaled for 1700×2200 px) ─────────────────────────────────────
_CFS_FIELD = 24
_CFS_STAT  = 22
_CFS_SKILL = 19
_CFS_SMALL = 17

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1  (Frontside)  –  1700×2200 coordinate grid
# ─────────────────────────────────────────────────────────────────────────────

# Row 1: Name / Race / Gender / Career Class / Alignment  (data row center y≈335)
_C1_NAME_X,   _C1_NAME_Y   = 175,  335
_C1_RACE_X,   _C1_RACE_Y   = 533,  335
_C1_GENDER_X, _C1_GENDER_Y = 698,  335
_C1_CC_X,     _C1_CC_Y     = 782,  335   # Career Class (anchor lm at left edge)
_C1_ALIGN_X,  _C1_ALIGN_Y  = 1205, 335   # Alignment (anchor lm)

# Row 2: Age / Height / Weight / Hair / Eyes / Description  (center y≈465)
_C1_AGE_X,    _C1_AGE_Y    = 209,  465
_C1_HEIGHT_X, _C1_HEIGHT_Y = 309,  465
_C1_WEIGHT_X, _C1_WEIGHT_Y = 420,  465
_C1_HAIR_X,   _C1_HAIR_Y   = 495,  465
_C1_EYES_X,   _C1_EYES_Y   = 703,  465
_C1_DESC_X,   _C1_DESC_Y   = 883,  465

# Row 3: Current Career / Career Path / Career Exits
# Header band at y=473-560 (x=200 pixel scan); data cell y=560-653, center≈607
_C1_CAREER_X, _C1_CAREER_Y = 175,  563   # PC: lt anchor (top of cell, just below header)
_C1_CPATH_X,  _C1_CPATH_Y  = 373,  563
_C1_EXITS_X,  _C1_EXITS_Y  = 883,  563

# Stats grid  (14 columns; pixel-scan confirmed dividers at y=730:
#   right borders: M=522, WS=598, BS=677, S=755, T=833, W=907, I=986, A=1063,
#   Dex=1139, Ld=1213, Int=1293, Cl=1367, WP=1447, Fel=1520)
_C1_STAT_COLS = {
    'M':   484, 'WS':  560, 'BS':  638, 'S':   716,
    'T':   794, 'W':   870, 'I':   947, 'A':  1025,
    'Dex':1101, 'Ld': 1176, 'Int':1253, 'Cl': 1330,
    'WP': 1407, 'Fel':1484,
}
# Row centers: content y=707-763 (starter), 779-839 (advance), 855-916 (current)
_C1_STARTER_Y = 735
_C1_ADV_Y     = 809
_C1_CURR_Y    = 885

# Hand-to-hand weapons  (pixel-scanned at y=1000)
# Name: x=198-508 (center=353), stats: I=543, WS=612, D=685, PY=757
_C1_HTH_NAME_X  = 202   # lm; left edge + 4px padding (col starts x=198)
_C1_HTH_NAME_W  = 295   # max width of HTH weapon name (col is 310px)
_C1_HTH_I_X     = 543   # center of I column  (x=512-574)
_C1_HTH_WS_X    = 612   # center of WS column (x=578-646)
_C1_HTH_D_X     = 685   # center of D column  (x=650-720)
_C1_HTH_PY_X    = 757   # center of PY column (x=724-790)
_C1_HTH_START_Y = 975   # header band y=851-971; content starts y=971
_C1_HTH_SPACING = 55

# Missile weapons  (same column layout as HTH at y=1250)
# Name: x=196-506 (center=351), stats: S=540, L=610, E=684, ES=755
_C1_MSL_NAME_X  = 200   # lm; left edge + 4px padding
_C1_MSL_NAME_W  = 290   # max width of missile weapon name
_C1_MSL_S_X     = 540   # center of S column  (x=510-570)
_C1_MSL_L_X     = 610   # center of L column  (x=576-644)
_C1_MSL_E_X     = 684   # center of E column  (x=648-720)
_C1_MSL_ES_X    = 755   # center of ES column (x=724-786)
# Load has no separate column; no 5th stat col in this template
_C1_MSL_START_Y = 1227
_C1_MSL_SPACING = 53

# Armour table  (pixel-scanned at y=1480)
# Name: x=192-440 (center=316), Loc: x=444-506 (center=475), ENC: x=510-574 (center=542)
_C1_ARM_NAME_X  = 196   # lm; left edge of name column
_C1_ARM_NAME_W  = 235   # max width (col is 248px)
_C1_ARM_LOC_X   = 475   # mm; center of Loc column
_C1_ARM_ENC_X   = 542   # mm; center of ENC column
_C1_ARM_START_Y = 1447
_C1_ARM_SPACING = 55

# Armour Points – body-location boxes around the figure diagram
_C1_AP_HEAD_X,  _C1_AP_HEAD_Y  = 565, 1600
_C1_AP_RARM_X,  _C1_AP_RARM_Y  = 510, 1720
_C1_AP_LARM_X,  _C1_AP_LARM_Y  = 1065, 1685
_C1_AP_BODY_X,  _C1_AP_BODY_Y  = 1100, 1790
_C1_AP_RLEG_X,  _C1_AP_RLEG_Y  = 565, 1910
_C1_AP_LLEG_X,  _C1_AP_LLEG_Y  = 1100, 1950

# Skills – two columns (pixel-scanned at y=1000)
# Left skills: x=806-1160 (w=354, center=983)
# Right skills: x=1176-1518 (w=342, center=1347)
_C1_SKILL_L_X     = 810   # lm; left edge of left skills column
_C1_SKILL_L_W     = 340   # max width of skill text in left column
_C1_SKILL_R_X     = 1180  # lm; left edge of right skills column
_C1_SKILL_R_W     = 330   # max width of skill text in right column
_C1_SKILL_START_Y = 975   # same start as HTH weapons
_C1_SKILL_SPACING = 55
_C1_SKILL_ROWS    = 11    # rows per column  →  22 skills max


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2  (Backside)  –  1701×2200 coordinate grid
# ─────────────────────────────────────────────────────────────────────────────

# Spells table  (name / SL / MP / R / D / Ingredients / Effect)
# Column dividers at y=210: x=196(left), 474(name/SL), 541(SL/MP), 612(MP/R),
#                           680(R/D), 752(D/Ing), 1012(Ing/Eff), 1298(Eff/right)
_C2_SPELL_NAME_X  = 206   # lm; 10px inside left border at x=196
_C2_SPELL_SL_X    = 508   # mm center  (474+541)/2
_C2_SPELL_MP_X    = 577   # mm center  (541+612)/2
_C2_SPELL_R_X     = 646   # mm center  (612+680)/2
_C2_SPELL_D_X     = 716   # mm center  (680+752)/2
_C2_SPELL_ING_X   = 755   # lm start at col left edge
_C2_SPELL_EFF_X   = 1015  # lm start at col left edge
_C2_SPELL_START_Y = 236   # center of first spell row (y=193+43)
_C2_SPELL_SPACING = 87    # 5 rows spanning y=193-630

# Right-column stat boxes (FATE POINTS / MAGIC POINTS / POWER LEVEL / EXPERIENCE)
# Left border of right column: x=1300-1315; label/value divider: x=1515; right edge: x=1700
# Value box (where we write numbers): x=1516 to 1700, center=1608
# Row centers: FP y=193-256 center=225; MP y=315-376 center=346; PL y=432-499 center=466; XP y=520-640 center=580
_C2_FP_X,  _C2_FP_Y  = 1608, 225
_C2_MAG_X, _C2_MAG_Y = 1608, 346
_C2_PL_X,  _C2_PL_Y  = 1608, 466
_C2_XP_X,  _C2_XP_Y  = 1608, 580

# Equipment / Trappings  (name / Loc / ENC)
# Section header band y=642-695; content starts y≈710
_C2_TRAP_NAME_X  = 120
_C2_TRAP_LOC_X   = 437
_C2_TRAP_ENC_X   = 500
_C2_TRAP_START_Y = 710
_C2_TRAP_SPACING = 34
_C2_TRAP_MAX_Y   = 878   # stop before PSYCHOLOGY header at y≈880

# Movement rate (columns: 10 SECS / Min. / M.P.H.)
# Confirmed by pixel scan: col dividers at x=873/943/1009/1080; row centers at y=721/781/845
_C2_MV_10_X   = 908
_C2_MV_MIN_X  = 976
_C2_MV_MPH_X  = 1045
_C2_MV_CAUT_Y = 721
_C2_MV_STD_Y  = 781
_C2_MV_RUN_Y  = 845

# Insanity Points  (box is below PSYCHOLOGY & HEALTH header, right side)
# INSANITY POINTS: label dark band x=1100-1293, value cell x=1304-1504, y=877-932
_C2_IP_X, _C2_IP_Y = 1404, 905

# Languages
# Section header shares y=642-695 band; content starts y≈710
_C2_LANG_X       = 1165
_C2_LANG_START_Y = 710
_C2_LANG_SPACING = 30

# Background fields  (labels "Place of Birth:" etc. are pre-printed in the BACKGROUND box)
# BACKGROUND header band: y=1140-1190.  Row centres confirmed by pixel scan.
_C2_BIRTH_X,  _C2_BIRTH_Y  = 940, 1212   # after "Place of Birth:" label (ends ~x=925)
_C2_PARENT_X, _C2_PARENT_Y = 950, 1255   # after "Parents Occupation:" label (ends ~x=933)
_C2_FAMILY_X, _C2_FAMILY_Y = 920, 1291   # after "Family Members:" label (ends ~x=901)

# Narrative / extra lines in the large open area below the three labelled rows
# Box boundary: y≈1290 (after Family Members) to y≈1425 (dividing line before Social Level)
_C2_BACK_X,     _C2_BACK_Y     = 665, 1318
_C2_BACK_END_Y  = 1418          # dividing line; narrative must not exceed this

# Social Level  /  Religion  (row below the BACKGROUND box, y≈1445)
_C2_SOCIAL_X, _C2_SOCIAL_Y = 860, 1445
_C2_RELIG_X,  _C2_RELIG_Y  = 1120, 1445

# Wealth  (rows below the WEALTH header band at y=1520-1575)
_C2_WGC_X, _C2_WGC_Y = 220, 1600
_C2_WSS_X, _C2_WSS_Y = 220, 1635
_C2_WBP_X, _C2_WBP_Y = 220, 1670

# Companions & Animals  (open grid to the right of WEALTH, header y=1516-1570,
#   data area y=1570-2056.  Column borders pixel-scanned at y=1590.)
# Name column: x=695-876 → center 786; stat cells ~43-48px wide
_C2_COMP_NAME_X    = 786   # mm center of companion name column
_C2_COMP_NAME_MAX  = 170   # max px for name text
_C2_COMP_STAT_XS   = [898, 942, 987, 1031, 1078, 1123, 1168, 1213,
                       1260, 1304, 1347, 1395, 1442, 1485]
_C2_COMP_STATS     = ["M","WS","BS","S","T","W","I","A","Dex","Ld","Int","Cl","WP","Fel"]
_C2_COMP_ROW1_Y    = 1640  # y center of first companion row
_C2_COMP_ROW_H     = 140   # px between companion rows


# ─────────────────────────────────────────────────────────────────────────────
# Fill functions
# ─────────────────────────────────────────────────────────────────────────────

def _fill_classic_page1(img: Image.Image, char: Character, pc_mode: bool) -> None:
    """Draw character data onto the classic frontside template."""
    draw = ImageDraw.Draw(img)
    f_field = _get_font(_CFS_FIELD)
    f_stat  = _get_font(_CFS_STAT)
    f_skill = _get_font(_CFS_SKILL)
    f_small = _get_font(_CFS_SMALL)

    # ── Identity ──────────────────────────────────────────────────────────────
    _draw_text_fit(draw, _C1_NAME_X, _C1_NAME_Y, char.name, _CFS_FIELD,
                   max_width=370, anchor="lm")
    _draw_text(draw, _C1_RACE_X,   _C1_RACE_Y,   char.race,   f_field, "mm")
    _draw_text(draw, _C1_GENDER_X, _C1_GENDER_Y, char.gender, f_field, "mm")
    _draw_text_fit(draw, _C1_CC_X, _C1_CC_Y, char.career_class,
                   _CFS_FIELD, max_width=390, anchor="lm")
    if char.alignment:
        _draw_text_fit(draw, _C1_ALIGN_X, _C1_ALIGN_Y, char.alignment,
                       _CFS_FIELD, max_width=420, anchor="lm")

    _draw_text(draw, _C1_AGE_X,    _C1_AGE_Y,    str(char.age),  f_field, "mm")
    _draw_text(draw, _C1_HEIGHT_X, _C1_HEIGHT_Y, char.height,    f_field, "mm")
    _draw_text(draw, _C1_WEIGHT_X, _C1_WEIGHT_Y, char.weight,    f_field, "mm")
    _draw_text_fit(draw, _C1_HAIR_X, _C1_HAIR_Y, char.hair_colour,
                   _CFS_FIELD, max_width=210, anchor="lm")
    _draw_text_fit(draw, _C1_EYES_X, _C1_EYES_Y, char.eye_colour,
                   _CFS_FIELD, max_width=175, anchor="lm")
    desc_parts = [p for p in [char.description, char.distinguishing_marks] if p]
    _draw_text_fit(draw, _C1_DESC_X, _C1_DESC_Y, ", ".join(desc_parts) if desc_parts else "",
                   _CFS_FIELD, max_width=730, anchor="lm")

    # ── Career ────────────────────────────────────────────────────────────────
    # Career cell spans y≈563-653, center≈607
    _career_center_y = _C1_CAREER_Y + 44   # center of cell for lm anchor
    if pc_mode:
        # Place at top of cell so player can strike out & write new career
        _draw_text_fit(draw, _C1_CAREER_X, _C1_CAREER_Y, char.career,
                       _CFS_FIELD, max_width=185, anchor="lt")
        # Career path: also at top so player can track career progression
        if hasattr(char, 'career_path') and char.career_path:
            _draw_text_fit(draw, _C1_CPATH_X, _C1_CPATH_Y, char.career_path,
                           _CFS_SMALL, max_width=480, anchor="lt")
        # Career exits: show for PC too
        if char.career_exits:
            exits = ", ".join(char.career_exits[:4])
            _draw_text_fit(draw, _C1_EXITS_X, _C1_EXITS_Y, exits,
                           _CFS_SMALL, max_width=620, anchor="lt")
    else:
        _draw_text_fit(draw, _C1_CAREER_X, _career_center_y, char.career,
                       _CFS_FIELD, max_width=185, anchor="lm")
        # NPC: show career class in the career path field for reference
        if getattr(char, 'career_class', None):
            _draw_text_fit(draw, _C1_CPATH_X, _career_center_y,
                           f"[{char.career_class}]", _CFS_SMALL,
                           max_width=470, anchor="lm")
        if char.career_exits:
            exits = ", ".join(char.career_exits[:4])
            _draw_text_fit(draw, _C1_EXITS_X, _career_center_y, exits,
                           _CFS_SMALL, max_width=620, anchor="lm")

    # ── Stats ─────────────────────────────────────────────────────────────────
    STAT_ORDER = ['M','WS','BS','S','T','W','I','A','Dex','Ld','Int','Cl','WP','Fel']
    starter = getattr(char, "starter_profile", {})
    for stat in STAT_ORDER:
        x = _C1_STAT_COLS[stat]
        curr_val = getattr(char, stat, None)
        start_val = starter.get(stat) if starter else None
        if start_val is None:
            start_val = curr_val
        if start_val is not None:
            _draw_text(draw, x, _C1_STARTER_Y, start_val, f_stat, "mm")
            if not pc_mode and curr_val is not None:
                _draw_text(draw, x, _C1_CURR_Y, curr_val, f_stat, "mm")
        # Advance scheme
        if stat in char.advance_scheme:
            raw = char.advance_scheme[stat]
            try:
                n = int(raw)
                label = f"+{n}" if n >= 0 else str(n)
            except (TypeError, ValueError):
                label = str(raw)
            _draw_text(draw, x, _C1_ADV_Y, label, f_stat, "mm")

    # ── Hand-to-Hand Weapons ──────────────────────────────────────────────────
    for i, name in enumerate(char.hth_weapons[:4]):
        ws = get_hth_stats(name)
        if not ws:
            continue
        y = _C1_HTH_START_Y + i * _C1_HTH_SPACING
        _draw_text_fit(draw, _C1_HTH_NAME_X, y, name, _CFS_SKILL,
                       max_width=_C1_HTH_NAME_W, anchor="lm", min_size=_CFS_SKILL)
        _draw_text(draw, _C1_HTH_I_X,  y, ws.get('i_mod',  '–'), f_small, "mm")
        _draw_text(draw, _C1_HTH_WS_X, y, ws.get('ws_mod', '–'), f_small, "mm")
        _draw_text(draw, _C1_HTH_D_X,  y, ws.get('damage', '–'), f_small, "mm")
        # PY (Parry): show Yes/No from data
        py_val = ws.get('parry', '–')
        _draw_text(draw, _C1_HTH_PY_X, y, py_val, f_small, "mm")

    # ── Missile Weapons ───────────────────────────────────────────────────────
    for i, name in enumerate(char.missile_weapons[:4]):
        ms = get_missile_stats(name)
        if not ms:
            continue
        y = _C1_MSL_START_Y + i * _C1_MSL_SPACING
        _draw_text_fit(draw, _C1_MSL_NAME_X, y, name, _CFS_SKILL,
                       max_width=_C1_MSL_NAME_W, anchor="lm", min_size=_CFS_SKILL)
        # S=short range, L=medium range, E=long range, ES=damage
        _draw_text(draw, _C1_MSL_S_X,  y, ms.get('s_range', '–'), f_small, "mm")
        _draw_text(draw, _C1_MSL_L_X,  y, ms.get('m_range', '–'), f_small, "mm")
        _draw_text(draw, _C1_MSL_E_X,  y, ms.get('l_range', '–'), f_small, "mm")
        _draw_text(draw, _C1_MSL_ES_X, y, ms.get('damage',  '–'), f_small, "mm")

    # ── Armour table ──────────────────────────────────────────────────────────
    for i, name in enumerate(char.armour_items[:5]):
        ast = get_armour_stats(name)
        if not ast:
            continue
        y = _C1_ARM_START_Y + i * _C1_ARM_SPACING
        _draw_text_fit(draw, _C1_ARM_NAME_X, y, name, _CFS_SKILL,
                       max_width=_C1_ARM_NAME_W, anchor="lm", min_size=_CFS_SKILL)
        _draw_text_fit(draw, _C1_ARM_LOC_X - 28, y, ast.get('location','–'),
                       _CFS_SMALL, max_width=58, anchor="lm", min_size=_CFS_SMALL)
        _draw_text(draw, _C1_ARM_ENC_X, y, str(ast.get('enc','–')), f_small, "mm")

    # ── Armour Points (body diagram) ──────────────────────────────────────────
    def _sum_ap(loc: str) -> int:
        return sum(
            get_armour_stats(item)[loc]
            for item in char.armour_items
            if get_armour_stats(item) and loc in get_armour_stats(item)
        )
    for x, y, loc in [
        (_C1_AP_HEAD_X, _C1_AP_HEAD_Y, "head"),
        (_C1_AP_RARM_X, _C1_AP_RARM_Y, "arms"),
        (_C1_AP_LARM_X, _C1_AP_LARM_Y, "arms"),
        (_C1_AP_BODY_X, _C1_AP_BODY_Y, "body"),
        (_C1_AP_RLEG_X, _C1_AP_RLEG_Y, "legs"),
        (_C1_AP_LLEG_X, _C1_AP_LLEG_Y, "legs"),
    ]:
        total = _sum_ap(loc)
        if total:
            _draw_text(draw, x, y, str(total), f_small, "mm")

    # ── Skills (two columns) ──────────────────────────────────────────────────
    all_skills = char.skills[:_C1_SKILL_ROWS * 2]
    col1 = all_skills[:_C1_SKILL_ROWS]
    col2 = all_skills[_C1_SKILL_ROWS:]
    for i, skill in enumerate(col1):
        y = _C1_SKILL_START_Y + i * _C1_SKILL_SPACING
        _draw_text_fit(draw, _C1_SKILL_L_X, y, skill, _CFS_SKILL,
                       max_width=_C1_SKILL_L_W, anchor="lm", min_size=_CFS_SKILL)
    for i, skill in enumerate(col2):
        y = _C1_SKILL_START_Y + i * _C1_SKILL_SPACING
        _draw_text_fit(draw, _C1_SKILL_R_X, y, skill, _CFS_SKILL,
                       max_width=_C1_SKILL_R_W, anchor="lm", min_size=_CFS_SKILL)


def _fill_classic_page2(img: Image.Image, char: Character, pc_mode: bool) -> None:
    """Draw character data onto the classic backside template."""
    draw = ImageDraw.Draw(img)
    f_field = _get_font(_CFS_FIELD)
    f_stat  = _get_font(_CFS_STAT)
    f_skill = _get_font(_CFS_SKILL)
    f_small = _get_font(_CFS_SMALL)

    # ── Spells ────────────────────────────────────────────────────────────────
    for i, spell_name in enumerate(char.spells[:5]):
        y = _C2_SPELL_START_Y + i * _C2_SPELL_SPACING
        data = get_spell(spell_name) or {}
        _draw_text_fit(draw, _C2_SPELL_NAME_X, y, spell_name, _CFS_SKILL,
                       max_width=354, anchor="lm", min_size=_CFS_SKILL)
        if data:
            _draw_text(draw, _C2_SPELL_SL_X, y, data.get('sl', 0),  f_small, "mm")
            _draw_text(draw, _C2_SPELL_MP_X, y, data.get('mp', 0),  f_small, "mm")
            _draw_text(draw, _C2_SPELL_R_X,  y, data.get('r','–'),  f_small, "mm")
            _draw_text(draw, _C2_SPELL_D_X,  y, data.get('d','–'),  f_small, "mm")
            _draw_text_fit(draw, _C2_SPELL_ING_X, y, data.get('ingredients','–'),
                           _CFS_SMALL, max_width=255, anchor="lm", min_size=_CFS_SMALL)
            _draw_text_fit(draw, _C2_SPELL_EFF_X, y, data.get('effect','–'),
                           _CFS_SMALL, max_width=280, anchor="lm", min_size=_CFS_SMALL)

    # ── Right-column stat boxes ───────────────────────────────────────────────
    _draw_text(draw, _C2_FP_X,  _C2_FP_Y,  str(char.FP),  f_field, "mm")
    # Mag: only show when character actually has magic ability
    if char.Mag > 0:
        _draw_text(draw, _C2_MAG_X, _C2_MAG_Y, str(char.Mag), f_field, "mm")
    # Power Level: only draw for magic users
    pl = getattr(char, 'power_level', 0)
    if pl > 0:
        _draw_text(draw, _C2_PL_X, _C2_PL_Y, str(pl), f_field, "mm")
    # XP: blank for PC (filled during play); show 0 for NPC
    if not pc_mode:
        _draw_text(draw, _C2_XP_X, _C2_XP_Y, "0", f_field, "mm")

    # ── Equipment / Trappings ─────────────────────────────────────────────────
    all_items = list(char.trappings)
    for i, item in enumerate(all_items):
        y = _C2_TRAP_START_Y + i * _C2_TRAP_SPACING
        if y > _C2_TRAP_MAX_Y:
            break
        _draw_text_fit(draw, _C2_TRAP_NAME_X, y, item, _CFS_SKILL,
                       max_width=240, anchor="lm", min_size=_CFS_SKILL)

    # ── Movement rates ────────────────────────────────────────────────────────
    M  = char.M
    mv_rows = [
        # (yds/10secs,  yds/min,   mph,                    y)
        (M,     M *  6,          round(M *  6 * 60 / 1760, 1), _C2_MV_CAUT_Y),
        (M * 2, M * 12,          round(M * 12 * 60 / 1760, 1), _C2_MV_STD_Y),
        (M * 4, M * 24,          round(M * 24 * 60 / 1760, 1), _C2_MV_RUN_Y),
    ]
    for v10, vmin, vmph, y in mv_rows:
        _draw_text(draw, _C2_MV_10_X,  y, str(v10),  f_small, "mm")
        _draw_text(draw, _C2_MV_MIN_X, y, str(vmin), f_small, "mm")
        _draw_text(draw, _C2_MV_MPH_X, y, str(vmph), f_small, "mm")

    # ── Insanity Points ───────────────────────────────────────────────────────
    # Always show for NPC; PC leaves blank (filled during play)
    if not pc_mode:
        _draw_text(draw, _C2_IP_X, _C2_IP_Y, "0", f_field, "mm")

    # ── Languages ─────────────────────────────────────────────────────────────
    for i, lang in enumerate(char.languages[:9]):
        y = _C2_LANG_START_Y + i * _C2_LANG_SPACING
        _draw_text_fit(draw, _C2_LANG_X, y, lang, _CFS_SKILL,
                       max_width=440, anchor="lm", min_size=_CFS_SKILL)

    # ── Background fields (labels are pre-printed on the sheet) ───────────────
    if char.place_of_birth:
        _draw_text_fit(draw, _C2_BIRTH_X, _C2_BIRTH_Y, char.place_of_birth,
                       _CFS_FIELD, max_width=460, anchor="lm")
    if char.parents_occupation:
        _draw_text_fit(draw, _C2_PARENT_X, _C2_PARENT_Y, char.parents_occupation,
                       _CFS_FIELD, max_width=420, anchor="lm")
    if char.family_members:
        _draw_text_fit(draw, _C2_FAMILY_X, _C2_FAMILY_Y, char.family_members,
                       _CFS_FIELD, max_width=445, anchor="lm")

    # Extra space: star sign + narrative (wrapped, more lines)
    back_y = _C2_BACK_Y
    if char.star_sign:
        _draw_text_fit(draw, _C2_BACK_X, back_y,
                       f"Star sign: {char.star_sign}", _CFS_SMALL,
                       max_width=740, anchor="lm", min_size=_CFS_SMALL)
        back_y += 22   # one line height — keep tight so narrative gets room
    if char.background_narrative:
        _BACK_LINE_H = 18
        _BACK_FONT   = 15   # slightly smaller than _CFS_SMALL to fit more lines
        # Limit to background box boundary (dividing line before Social Level)
        avail_h = _C2_BACK_END_Y - back_y - 5
        dynamic_max = max(1, avail_h // _BACK_LINE_H)
        _draw_paragraph(draw, _C2_BACK_X, back_y,
                        char.background_narrative, _BACK_FONT,
                        max_width=740, line_height=_BACK_LINE_H, max_lines=dynamic_max,
                        shrink=False)

    # ── Social Level / Religion ───────────────────────────────────────────────
    if char.social_level:
        _draw_text_fit(draw, _C2_SOCIAL_X, _C2_SOCIAL_Y, char.social_level,
                       _CFS_FIELD, max_width=140, anchor="lm")
    if char.religion:
        _draw_text_fit(draw, _C2_RELIG_X, _C2_RELIG_Y, char.religion,
                       _CFS_FIELD, max_width=300, anchor="lm")

    # ── Wealth ────────────────────────────────────────────────────────────────
    # PC: leave blank if 0. NPC: always show value (even 0).
    # Show "GC: X", "SS: X", "BP: X" labels with values.
    if getattr(char, 'wealth_gc', 0) or not pc_mode:
        _draw_text_fit(draw, _C2_WGC_X, _C2_WGC_Y,
                       f"GC: {getattr(char,'wealth_gc',0)}", _CFS_SMALL,
                       max_width=160, anchor="lm")
    if getattr(char, 'wealth_ss', 0) or not pc_mode:
        _draw_text_fit(draw, _C2_WSS_X, _C2_WSS_Y,
                       f"SS: {getattr(char,'wealth_ss',0)}", _CFS_SMALL,
                       max_width=160, anchor="lm")
    if getattr(char, 'wealth_bp', 0) or not pc_mode:
        _draw_text_fit(draw, _C2_WBP_X, _C2_WBP_Y,
                       f"BP: {getattr(char,'wealth_bp',0)}", _CFS_SMALL,
                       max_width=160, anchor="lm")

    # ── Companions & Animals ─────────────────────────────────────────────────
    companions = getattr(char, "companions", [])
    for row_idx, comp in enumerate(companions[:3]):
        cy = _C2_COMP_ROW1_Y + row_idx * _C2_COMP_ROW_H
        _draw_text_fit(draw, _C2_COMP_NAME_X, cy, comp["name"],
                       _CFS_SMALL, max_width=_C2_COMP_NAME_MAX, anchor="mm")
        stats = comp.get("stats", {})
        for col_idx, stat in enumerate(_C2_COMP_STATS):
            val = stats.get(stat)
            if val is not None:
                cx = _C2_COMP_STAT_XS[col_idx]
                _draw_text(draw, cx, cy, val, _get_font(_CFS_SMALL - 2), "mm")


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def save_classic_spread(char: Character,
                        path: str = "character_sheet_classic.jpg",
                        pc_mode: bool = False) -> str:
    """
    Render both pages of the classic WFRP character sheet side by side.
    Returns the output path.
    """
    page1 = Image.open(_FRONT_TMPL).copy().convert("RGB")
    _fill_classic_page1(page1, char, pc_mode=pc_mode)

    page2 = Image.open(_BACK_TMPL).copy().convert("RGB")
    _fill_classic_page2(page2, char, pc_mode=pc_mode)

    W1, H1 = page1.size
    W2, H2 = page2.size
    H = max(H1, H2)
    spread = Image.new("RGB", (W1 + _PAGE_GAP + W2, H), (140, 140, 140))
    spread.paste(page1, (0, 0))
    spread.paste(page2, (W1 + _PAGE_GAP, 0))

    spread.save(path, "JPEG", quality=95)
    return path
