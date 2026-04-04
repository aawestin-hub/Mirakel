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
_C1_HAIR_X,   _C1_HAIR_Y   = 485,  465
_C1_EYES_X,   _C1_EYES_Y   = 703,  465
_C1_DESC_X,   _C1_DESC_Y   = 883,  465

# Row 3: Current Career / Career Path / Career Exits
# Header band at y=473-560 (x=200 pixel scan); data cell y=560-653, center≈607
_C1_CAREER_X, _C1_CAREER_Y = 175,  563   # PC: lt anchor (top of cell, just below header)
_C1_CPATH_X,  _C1_CPATH_Y  = 373,  563
_C1_EXITS_X,  _C1_EXITS_Y  = 883,  563

# Stats grid  (14 columns; row-label col ends at x≈295)
_C1_STAT_COLS = {
    'M':   343, 'WS':  439, 'BS':  535, 'S':   631,
    'T':   727, 'W':   823, 'I':   919, 'A':  1015,
    'Dex':1111, 'Ld': 1207, 'Int':1303, 'Cl': 1399,
    'WP': 1495, 'Fel':1591,
}
_C1_STARTER_Y = 757
_C1_ADV_Y     = 812
_C1_CURR_Y    = 867

# Hand-to-hand weapons  (name col + I / WS / D / PY columns)
_C1_HTH_NAME_X  = 175
_C1_HTH_I_X     = 281
_C1_HTH_WS_X    = 339
_C1_HTH_D_X     = 397
_C1_HTH_PY_X    = 455
_C1_HTH_START_Y = 975   # header band y=851-971; content starts y=971
_C1_HTH_SPACING = 55

# Missile weapons  (S / L / E / ES / Load columns)
_C1_MSL_NAME_X  = 175
_C1_MSL_S_X     = 281
_C1_MSL_L_X     = 339
_C1_MSL_E_X     = 397
_C1_MSL_ES_X    = 455
_C1_MSL_LOAD_X  = 513
_C1_MSL_START_Y = 1227
_C1_MSL_SPACING = 53

# Armour table  (name / Loc / ENC columns)
_C1_ARM_NAME_X  = 175
_C1_ARM_LOC_X   = 350
_C1_ARM_ENC_X   = 415
_C1_ARM_START_Y = 1447
_C1_ARM_SPACING = 55

# Armour Points – body-location boxes around the figure diagram
_C1_AP_HEAD_X,  _C1_AP_HEAD_Y  = 565, 1600
_C1_AP_RARM_X,  _C1_AP_RARM_Y  = 510, 1720
_C1_AP_LARM_X,  _C1_AP_LARM_Y  = 1065, 1685
_C1_AP_BODY_X,  _C1_AP_BODY_Y  = 1100, 1790
_C1_AP_RLEG_X,  _C1_AP_RLEG_Y  = 565, 1910
_C1_AP_LLEG_X,  _C1_AP_LLEG_Y  = 1100, 1950

# Skills – two columns (right half of the weapon section)
_C1_SKILL_L_X     = 505
_C1_SKILL_R_X     = 800
_C1_SKILL_START_Y = 975  # same start as HTH weapons
_C1_SKILL_SPACING = 55
_C1_SKILL_ROWS    = 11   # rows per column  →  22 skills max


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2  (Backside)  –  1701×2200 coordinate grid
# ─────────────────────────────────────────────────────────────────────────────

# Spells table  (name / SL / MP / R / D / Ingredients / Effect)
_C2_SPELL_NAME_X  = 120
_C2_SPELL_SL_X    = 315   # mm center
_C2_SPELL_MP_X    = 355   # mm center
_C2_SPELL_R_X     = 375   # lm start
_C2_SPELL_D_X     = 420   # lm start
_C2_SPELL_ING_X   = 465   # lm start
_C2_SPELL_EFF_X   = 750   # lm start
_C2_SPELL_START_Y = 201
_C2_SPELL_SPACING = 67

# Right-column stat boxes (FATE POINTS / MAGIC POINTS / POWER LEVEL / EXPERIENCE)
_C2_FP_X,  _C2_FP_Y  = 1520, 205
_C2_MAG_X, _C2_MAG_Y = 1520, 299
_C2_PL_X,  _C2_PL_Y  = 1520, 393
_C2_XP_X,  _C2_XP_Y  = 1520, 483

# Equipment / Trappings  (name / Loc / ENC)
_C2_TRAP_NAME_X  = 120
_C2_TRAP_LOC_X   = 330
_C2_TRAP_ENC_X   = 390
_C2_TRAP_START_Y = 487
_C2_TRAP_SPACING = 36
_C2_TRAP_MAX_Y   = 860   # stop before Movement section

# Movement rate (columns: 10 SECS / Min. / M.P.H.)
_C2_MV_10_X   = 527
_C2_MV_MIN_X  = 574
_C2_MV_MPH_X  = 614
_C2_MV_CAUT_Y = 512
_C2_MV_STD_Y  = 552
_C2_MV_RUN_Y  = 592

# Insanity Points  (box is below PSYCHOLOGY & HEALTH header, right side)
_C2_IP_X, _C2_IP_Y = 1175, 960

# Languages
_C2_LANG_X       = 1165
_C2_LANG_START_Y = 487
_C2_LANG_SPACING = 36

# Background fields  (labels "Place of Birth:" etc. are pre-printed in the BACKGROUND box)
# BACKGROUND header band: y=1140-1190.  Row centres confirmed by pixel scan.
_C2_BIRTH_X,  _C2_BIRTH_Y  = 940, 1212   # after "Place of Birth:" label (ends ~x=925)
_C2_PARENT_X, _C2_PARENT_Y = 950, 1255   # after "Parents Occupation:" label (ends ~x=933)
_C2_FAMILY_X, _C2_FAMILY_Y = 920, 1291   # after "Family Members:" label (ends ~x=901)

# Narrative / extra lines in the large open area below the three labelled rows
_C2_BACK_X, _C2_BACK_Y = 665, 1330

# Social Level  /  Religion  (row below the BACKGROUND box, y≈1463)
_C2_SOCIAL_X, _C2_SOCIAL_Y = 860, 1463
_C2_RELIG_X,  _C2_RELIG_Y  = 1120, 1463

# Wealth  (rows below the WEALTH header band at y=1520-1575)
_C2_WGC_X, _C2_WGC_Y = 220, 1600
_C2_WSS_X, _C2_WSS_Y = 220, 1635
_C2_WBP_X, _C2_WBP_Y = 220, 1670


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
    _draw_text_fit(draw, _C1_DESC_X, _C1_DESC_Y, char.distinguishing_marks,
                   _CFS_FIELD, max_width=730, anchor="lm")

    # ── Career ────────────────────────────────────────────────────────────────
    # Career cell spans y≈563-653, center≈607
    _career_center_y = _C1_CAREER_Y + 44   # center of cell for lm anchor
    if pc_mode:
        # Place at top of cell so player can strike out & write new career
        _draw_text_fit(draw, _C1_CAREER_X, _C1_CAREER_Y, char.career,
                       _CFS_FIELD, max_width=270, anchor="lt")
        # Career path: also at top so player can track career progression
        if hasattr(char, 'career_path') and char.career_path:
            _draw_text_fit(draw, _C1_CPATH_X, _C1_CPATH_Y, char.career_path,
                           _CFS_SMALL, max_width=480, anchor="lt")
    else:
        _draw_text_fit(draw, _C1_CAREER_X, _career_center_y, char.career,
                       _CFS_FIELD, max_width=270, anchor="lm")
        if char.career_exits:
            exits = ", ".join(char.career_exits[:3])
            _draw_text_fit(draw, _C1_EXITS_X, _career_center_y, exits,
                           _CFS_SMALL, max_width=720, anchor="lm")

    # ── Stats ─────────────────────────────────────────────────────────────────
    STAT_ORDER = ['M','WS','BS','S','T','W','I','A','Dex','Ld','Int','Cl','WP','Fel']
    for stat in STAT_ORDER:
        x = _C1_STAT_COLS[stat]
        val = getattr(char, stat, None)
        if val is not None:
            _draw_text(draw, x, _C1_STARTER_Y, val, f_stat, "mm")
            if not pc_mode:
                _draw_text(draw, x, _C1_CURR_Y, val, f_stat, "mm")
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
                       max_width=165, anchor="lm")
        _draw_text(draw, _C1_HTH_I_X,  y, ws.get('I', '–'),  f_small, "mm")
        _draw_text(draw, _C1_HTH_WS_X, y, ws.get('WS','–'), f_small, "mm")
        _draw_text(draw, _C1_HTH_D_X,  y, ws.get('D', '–'),  f_small, "mm")
        _draw_text(draw, _C1_HTH_PY_X, y, ws.get('PY','–'), f_small, "mm")

    # ── Missile Weapons ───────────────────────────────────────────────────────
    for i, name in enumerate(char.missile_weapons[:4]):
        ms = get_missile_stats(name)
        if not ms:
            continue
        y = _C1_MSL_START_Y + i * _C1_MSL_SPACING
        _draw_text_fit(draw, _C1_MSL_NAME_X, y, name, _CFS_SKILL,
                       max_width=165, anchor="lm")
        _draw_text(draw, _C1_MSL_S_X,    y, ms.get('S',   '–'), f_small, "mm")
        _draw_text(draw, _C1_MSL_L_X,    y, ms.get('L',   '–'), f_small, "mm")
        _draw_text(draw, _C1_MSL_E_X,    y, ms.get('E',   '–'), f_small, "mm")
        _draw_text(draw, _C1_MSL_ES_X,   y, ms.get('ES',  '–'), f_small, "mm")
        _draw_text(draw, _C1_MSL_LOAD_X, y, ms.get('Load','–'), f_small, "mm")

    # ── Armour table ──────────────────────────────────────────────────────────
    for i, name in enumerate(char.armour_items[:5]):
        ast = get_armour_stats(name)
        if not ast:
            continue
        y = _C1_ARM_START_Y + i * _C1_ARM_SPACING
        _draw_text_fit(draw, _C1_ARM_NAME_X, y, name, _CFS_SKILL,
                       max_width=215, anchor="lm")
        _draw_text(draw, _C1_ARM_LOC_X, y, ast.get('location','–'), f_small, "lm")
        _draw_text(draw, _C1_ARM_ENC_X, y, ast.get('enc','–'),      f_small, "mm")

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
                       max_width=270, anchor="lm")
    for i, skill in enumerate(col2):
        y = _C1_SKILL_START_Y + i * _C1_SKILL_SPACING
        _draw_text_fit(draw, _C1_SKILL_R_X, y, skill, _CFS_SKILL,
                       max_width=270, anchor="lm")


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
                       max_width=230, anchor="lm")
        if data:
            _draw_text(draw, _C2_SPELL_SL_X, y, data.get('sl', 0),  f_small, "mm")
            _draw_text(draw, _C2_SPELL_MP_X, y, data.get('mp', 0),  f_small, "mm")
            _draw_text_fit(draw, _C2_SPELL_R_X, y, data.get('r','–'),
                           _CFS_SMALL, max_width=45,  anchor="lm")
            _draw_text_fit(draw, _C2_SPELL_D_X, y, data.get('d','–'),
                           _CFS_SMALL, max_width=45,  anchor="lm")
            _draw_text_fit(draw, _C2_SPELL_ING_X, y, data.get('ingredients','–'),
                           _CFS_SMALL, max_width=285, anchor="lm")
            _draw_text_fit(draw, _C2_SPELL_EFF_X, y, data.get('effect','–'),
                           _CFS_SMALL, max_width=890, anchor="lm")

    # ── Right-column stat boxes ───────────────────────────────────────────────
    _draw_text(draw, _C2_FP_X,  _C2_FP_Y,  str(char.FP),  f_field, "mm")
    # Mag: always show for NPC; PC shows only if > 0
    if char.Mag or not pc_mode:
        _draw_text(draw, _C2_MAG_X, _C2_MAG_Y, str(char.Mag), f_field, "mm")
    _draw_text(draw, _C2_PL_X,  _C2_PL_Y,  str(getattr(char, 'power_level', 0)), f_field, "mm")
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
                       max_width=240, anchor="lm")

    # ── Movement rates ────────────────────────────────────────────────────────
    M  = char.M
    _Y = 0.9144   # yards → metres
    _K = 1.60934  # mph → km/h
    mv_rows = [
        (round(M     * _Y, 1), round(M *  6 * _Y, 1),
         round(M *  6 * 60 / 1760 * _K, 1), _C2_MV_CAUT_Y),
        (round(M * 2 * _Y, 1), round(M * 12 * _Y, 1),
         round(M * 12 * 60 / 1760 * _K, 1), _C2_MV_STD_Y),
        (round(M * 4 * _Y, 1), round(M * 24 * _Y, 1),
         round(M * 24 * 60 / 1760 * _K, 1), _C2_MV_RUN_Y),
    ]
    for v10, vmin, vkph, y in mv_rows:
        _draw_text(draw, _C2_MV_10_X,  y, str(v10),  f_small, "mm")
        _draw_text(draw, _C2_MV_MIN_X, y, str(vmin), f_small, "mm")
        _draw_text(draw, _C2_MV_MPH_X, y, str(vkph), f_small, "mm")

    # ── Insanity Points ───────────────────────────────────────────────────────
    # Always show for NPC; PC leaves blank (filled during play)
    if not pc_mode:
        _draw_text(draw, _C2_IP_X, _C2_IP_Y, "0", f_field, "mm")

    # ── Languages ─────────────────────────────────────────────────────────────
    for i, lang in enumerate(char.languages[:9]):
        y = _C2_LANG_START_Y + i * _C2_LANG_SPACING
        _draw_text_fit(draw, _C2_LANG_X, y, lang, _CFS_SKILL,
                       max_width=440, anchor="lm")

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

    # Extra space: star sign + narrative snippet (wrapped)
    if char.star_sign:
        _draw_text_fit(draw, _C2_BACK_X, _C2_BACK_Y,
                       f"Star sign: {char.star_sign}", _CFS_SMALL,
                       max_width=740, anchor="lm")
    if char.background_narrative:
        first_sent = char.background_narrative.split('.')[0] + '.'
        _draw_paragraph(draw, _C2_BACK_X, _C2_BACK_Y + 36,
                        first_sent, _CFS_SMALL,
                        max_width=740, line_height=28, max_lines=2)

    # ── Social Level / Religion ───────────────────────────────────────────────
    if char.social_level:
        _draw_text_fit(draw, _C2_SOCIAL_X, _C2_SOCIAL_Y, char.social_level,
                       _CFS_FIELD, max_width=140, anchor="lm")
    if char.religion:
        _draw_text_fit(draw, _C2_RELIG_X, _C2_RELIG_Y, char.religion,
                       _CFS_FIELD, max_width=300, anchor="lm")

    # ── Wealth ────────────────────────────────────────────────────────────────
    # ── Wealth ────────────────────────────────────────────────────────────────
    # PC: leave blank if 0. NPC: always show value (even 0).
    if getattr(char, 'wealth_gc', 0) or not pc_mode:
        _draw_text(draw, _C2_WGC_X, _C2_WGC_Y, str(getattr(char,'wealth_gc',0)), f_small, "lm")
    if getattr(char, 'wealth_ss', 0) or not pc_mode:
        _draw_text(draw, _C2_WSS_X, _C2_WSS_Y, str(getattr(char,'wealth_ss',0)), f_small, "lm")
    if getattr(char, 'wealth_bp', 0) or not pc_mode:
        _draw_text(draw, _C2_WBP_X, _C2_WBP_Y, str(getattr(char,'wealth_bp',0)), f_small, "lm")


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
