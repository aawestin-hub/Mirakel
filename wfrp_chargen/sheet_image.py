"""
Fills character data onto the official WFRP 1st Edition character sheet image.

Uses Pillow to overlay text at calibrated field positions.
Image: sheet_page0.png  (2550 × 3300 px, rendered from PDF at 300 DPI)

Usage:
    from sheet_image import save_character_image
    save_character_image(char, "output.jpg")
"""

from PIL import Image, ImageDraw, ImageFont
import os

from chargen.character import Character
from data.weapons import get_hth_stats, get_missile_stats, get_armour_stats
from data.spells import get_spell

# ── Image & font setup ────────────────────────────────────────────────────────

_HERE  = os.path.dirname(os.path.abspath(__file__))
_SHEET  = os.path.join(_HERE, "templates", "sheet_page0.png")
_SHEET2 = os.path.join(_HERE, "templates", "sheet_page1.png")

def _get_font(size: int):
    # Prefer handwritten/print-style fonts; fall back to bold then regular
    candidates = [
        "C:/Windows/Fonts/segoeprb.ttf",   # Segoe Print Bold – clean handprint
        "C:/Windows/Fonts/segoescb.ttf",   # Segoe Script Bold – cursive
        "C:/Windows/Fonts/comicbd.ttf",    # Comic Sans Bold – thick, informal
        "C:/Windows/Fonts/LHANDW.TTF",     # Lucida Handwriting
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()

# Font sizes – calibrated for 2550 × 3300 px sheet
_FS_FIELD   = 42   # identity fields
_FS_STAT    = 40   # stat grid values
_FS_SKILL   = 34   # skill / weapon names
_FS_SMALL   = 32   # advance scheme / table values

_INK = (20, 20, 20)


def _draw_text(draw, x, y, text, font, anchor="mm", colour=_INK):
    draw.text((x, y), str(text), font=font, fill=colour, anchor=anchor)


def _text_width(draw, text: str, font) -> int:
    """Return pixel width of text with given font.
    Adds a small safety margin (+10px) since textlength can slightly
    underestimate actual rendered ink width for some fonts."""
    return int(draw.textlength(str(text), font=font)) + 10


def _draw_text_fit(draw, x, y, text: str, base_size: int, max_width: int,
                   anchor="lm", colour=_INK, min_size: int = 22):
    """Draw text, shrinking font size until it fits within max_width."""
    text = str(text)
    size = base_size
    while size >= min_size:
        font = _get_font(size)
        if _text_width(draw, text, font) <= max_width:
            draw.text((x, y), text, font=font, fill=colour, anchor=anchor)
            return
        size -= 2
    # Last resort: draw at min_size (may still overflow, but best effort)
    draw.text((x, y), text, font=_get_font(min_size), fill=colour, anchor=anchor)


def _best_split(draw, words: list, n: int, font, max_width: int) -> list[str] | None:
    """Split words into exactly n lines, each fitting max_width. Returns lines or None."""
    if n == 1:
        line = " ".join(words)
        return [line] if _text_width(draw, line, font) <= max_width else None
    # Try every split point; pick the one that balances line lengths
    best = None
    for i in range(1, len(words)):
        line1 = " ".join(words[:i])
        if _text_width(draw, line1, font) > max_width:
            break
        rest = _best_split(draw, words[i:], n - 1, font, max_width)
        if rest is not None:
            best = [line1] + rest
    return best


def _draw_text_wrap(draw, x, y, text: str, base_size: int, max_width: int,
                    line_height: int, anchor="lm", colour=_INK,
                    min_size: int = 18, max_lines: int = 3):
    """Draw text, wrapping to up to max_lines lines and shrinking font to fit."""
    text = str(text)
    for size in range(base_size, min_size - 1, -2):
        font = _get_font(size)
        for n in range(1, max_lines + 1):
            lines = _best_split(draw, text.split(), n, font, max_width)
            if lines is not None:
                total_h = (len(lines) - 1) * line_height
                start_y = y - total_h // 2
                for i, line in enumerate(lines):
                    draw.text((x, start_y + i * line_height),
                              line, font=font, fill=colour, anchor=anchor)
                return
    # Absolute last resort: draw at min_size, split evenly into max_lines
    font = _get_font(min_size)
    words = text.split()
    chunk = max(1, len(words) // max_lines)
    lines = [" ".join(words[i:i+chunk]) for i in range(0, len(words), chunk)]
    lines = lines[:max_lines]
    total_h = (len(lines) - 1) * line_height
    start_y = y - total_h // 2
    for i, line in enumerate(lines):
        draw.text((x, start_y + i * line_height),
                  line, font=font, fill=colour, anchor=anchor)


# Keep old name as alias for backwards compat
def _draw_text_wrap2(draw, x, y, text: str, base_size: int, max_width: int,
                     line_height: int, anchor="lm", colour=_INK, min_size: int = 20):
    _draw_text_wrap(draw, x, y, text, base_size, max_width, line_height,
                    anchor=anchor, colour=colour, min_size=min_size, max_lines=2)


# ── Coordinates (calibrated via calibrate_ui.py) ─────────────────────────────

# Row 1
_R1_Y       = 530
_NAME_X     = 355
_RACE_X     = 1042
_GENDER_X   = 1265
_CLASS_X    = 1507
_ALIGN_X    = 2017

# Description
_DESC_X     = 1512
_DESC_Y     = 702

# Row 2 – physical
_R2_Y       = 700
_AGE_X      = 350
_HEIGHT_X   = 580
_WEIGHT_X   = 807
_HAIR_X     = 1037
_EYES_X     = 1267

# Row 3 – career
_R3_Y       = 897
_CAREER_X   = 335
_PATH_X     = 837
_EXITS_X    = 1582

# Stat profile grid
_STAT_X = {
    "M":   722, "WS":  842, "BS":  962, "S":   1067,
    "T":   1192, "W":  1305, "I":  1417, "A":   1535,
    "Dex": 1650, "Ld": 1767, "Int": 1877, "Cl": 1995,
    "WP":  2105, "Fel": 2225,
}
_STARTER_Y  = 1097
_ADVANCE_Y  = 1215
_CURRENT_Y  = 1327

# Skills
_SKILL_LEFT_X      = 1247
_SKILL_RIGHT_X     = 1802
_SKILL_START_Y     = 1495
_SKILL_SPACING     = 52
_SKILL_MAX_PER_COL = 25   # rows available in each column before overflowing

# Hand-to-hand weapons table
_HTH_X        = 342
_HTH_START_Y  = 1495
_HTH_SPACING  = 60
_HTH_IMOD_X   = 807
_HTH_WS_X     = 920   # WS modifier column
_HTH_DMG_X    = 1020   # D column (was 922 = WS column)
_HTH_PARRY_X  = 1135

# Missile weapons table
_MIS_X        = 335
_MIS_START_Y  = 2042
_MIS_SPACING  = 55
_MIS_SR_X     = 702
_MIS_MR_X     = 817
_MIS_LR_X     = 912
_MIS_DMG_X    = 1020
_MIS_RLD_X    = 1130

# Armour table
_ARM_X        = 327
_ARM_START_Y  = 2572
_ARM_SPACING  = 53
_ARM_LOC_X    = 805
_ARM_ENC_X    = 1127

# Armour location boxes around avatar figure
_AV_HEAD_X     = 1312
_AV_HEAD_Y     = 2380
_AV_R_ARM_X    = 1245
_AV_R_ARM_Y    = 2610
_AV_L_ARM_X    = 1685
_AV_L_ARM_Y    = 2510
_AV_BODY_X     = 1690
_AV_BODY_Y     = 2727
_AV_R_LEG_X    = 1250
_AV_R_LEG_Y    = 2877
_AV_L_LEG_X    = 1685
_AV_L_LEG_Y    = 2940
_AV_SHIELD_X   = 1572
_AV_SHIELD_Y   = 2347

# ── Page 2 coordinates (relative to page-2 image origin) ──────────────────────

_P2_FP_X           = 2100
_P2_FP_Y           = 340
_P2_MAG_X          = 2082
_P2_MAG_Y          = 520
_P2_IP_X           = 1817
_P2_IP_Y           = 1445
_P2_XP_X           = 2010
_P2_XP_Y           = 870

_P2_TRAP_X         = 337
_P2_TRAP_START_Y   = 1080
_P2_TRAP_SPACING   = 57
_P2_TRAP_LOC_X     = 865
_P2_TRAP_ENC_X     = 972

_P2_WGC_X          = 332
_P2_WGC_Y          = 2400
_P2_WSS_X          = 335
_P2_WSS_Y          = 2455
_P2_WBP_X          = 337
_P2_WBP_Y          = 2507

_P2_MV_X           = 1357   # row-label anchor (also used as 10-SECS col)
_P2_MV_CAUT_Y      = 1082
_P2_MV_STD_Y       = 1175
_P2_MV_RUN_Y       = 1272
_P2_MV_10_X        = 1357   # "m/10 SEK" column
_P2_MV_MIN_X       = 1467   # "m/Min." column
_P2_MV_MPH_X       = 1560   # "km/t" column

_P2_LANG_X         = 1690
_P2_LANG_START_Y   = 1077
_P2_LANG_SPACING   = 58

_P2_BIRTH_X        = 1342
_P2_BIRTH_Y        = 1830
_P2_PARENT_X       = 1440
_P2_PARENT_Y       = 1880
_P2_FAMILY_X       = 1385
_P2_FAMILY_Y       = 1940
_P2_SOCIAL_X       = 1307
_P2_SOCIAL_Y       = 2202
_P2_RELIG_X        = 1720
_P2_RELIG_Y        = 2202

_PAGE_GAP = 20


# ── Page 2 spell section coordinates (calibrated from sheet_page1.png pixel scan) ──
# Column dividers found at x: 294, 713, 815, 921, 1023, 1130, 1519, 1946
_P2_SPELL_NAME_X    = 310    # Left anchor: spell name (inside left border x=294)
_P2_SPELL_SL_X      = 764    # SL column centre  (713–815)
_P2_SPELL_MP_X      = 868    # MP column centre  (815–921)
_P2_SPELL_R_X       = 972    # R (range) centre  (921–1023)
_P2_SPELL_D_X       = 1076   # D (duration) centre (1023–1130)
_P2_SPELL_ING_X     = 1145   # Ingredients left anchor (1130+15)
_P2_SPELL_EFF_X     = 1534   # Effect left anchor (1519+15)
_P2_SPELL_START_Y   = 342    # First spell row Y (header ends ~294, first row centre ~342)
_P2_SPELL_SPACING   = 97     # Pixels between rows (~7 rows fit in table)


def _fill_page1(char: Character, draw: ImageDraw.ImageDraw) -> None:
    """Draw all character data onto an already-opened page-1 ImageDraw context."""
    f_field = _get_font(_FS_FIELD)
    f_stat  = _get_font(_FS_STAT)
    f_skill = _get_font(_FS_SKILL)
    f_small = _get_font(_FS_SMALL)

    # ── Row 1: NAME / RACE / GENDER / CLASS / ALIGNMENT ─────────────────────
    # Cell widths: NAME 355-1042(687px), RACE 1042-1265(223px), GENDER 1265-1507(242px),
    # CLASS 1507-2017(510px), ALIGN 2017-2490(473px)
    _draw_text_fit(draw, _NAME_X,   _R1_Y, char.name or "(unnamed)", _FS_FIELD,
                   max_width=670, anchor="lm")
    _draw_text_fit(draw, _RACE_X,   _R1_Y, char.race,                _FS_FIELD,
                   max_width=210, anchor="lm")
    if char.gender:
        _draw_text_fit(draw, _GENDER_X, _R1_Y, char.gender,          _FS_FIELD,
                       max_width=225, anchor="lm")
    _draw_text_fit(draw, _CLASS_X,  _R1_Y, char.career_class,        _FS_FIELD,
                   max_width=490, anchor="lm")
    _draw_text_fit(draw, _ALIGN_X,  _R1_Y, char.alignment,           _FS_FIELD,
                   max_width=450, anchor="lm")

    # ── Description ──────────────────────────────────────────────────────────
    if char.description:
        _draw_text_fit(draw, _DESC_X, _DESC_Y, char.description, _FS_SMALL,
                       max_width=990, anchor="lm")

    # ── Row 2: AGE / HEIGHT / WEIGHT / HAIR / EYES ───────────────────────────
    # Cell widths: AGE 350-580(230px), HEIGHT 580-807(227px), WEIGHT 807-1037(230px),
    # HAIR 1037-1267(230px), EYES 1267-1507(240px)
    _draw_text_fit(draw, _AGE_X,    _R2_Y, char.age,         _FS_FIELD, max_width=210, anchor="lm")
    _draw_text_fit(draw, _HEIGHT_X, _R2_Y, char.height,      _FS_FIELD, max_width=210, anchor="lm")
    _draw_text_fit(draw, _WEIGHT_X, _R2_Y, char.weight,      _FS_FIELD, max_width=210, anchor="lm")
    _draw_text_fit(draw, _HAIR_X,   _R2_Y, char.hair_colour, _FS_FIELD, max_width=210, anchor="lm")
    _draw_text_fit(draw, _EYES_X,   _R2_Y, char.eye_colour,  _FS_FIELD, max_width=220, anchor="lm")

    # ── Row 3: CURRENT CAREER / CAREER PATH / CAREER EXITS ──────────────────
    # CAREER box: x=335, ends ~x=830 → width ~495px
    _draw_text_fit(draw, _CAREER_X, _R3_Y, char.career, _FS_FIELD, max_width=490, anchor="lm")
    # CAREER PATH box: x=837, ends ~x=1575 → width ~738px; use field-size font
    _draw_text_fit(draw, _PATH_X, _R3_Y, f"[{char.career}]", _FS_FIELD, max_width=730, anchor="lm")
    if char.career_exits:
        exits_text = ", ".join(char.career_exits)
        # EXITS box: x=1582, ends ~x=2510 → width ~928px; row height ~180px
        _draw_text_wrap(draw, _EXITS_X, _R3_Y, exits_text,
                        _FS_SMALL, max_width=880, line_height=55, anchor="lm",
                        max_lines=3)

    # ── STARTER PROFILE ───────────────────────────────────────────────────────
    for stat, x in _STAT_X.items():
        val = getattr(char, stat, None)
        if val is not None:
            _draw_text(draw, x, _STARTER_Y, val, f_stat, "mm")

    # ── ADVANCE SCHEME ────────────────────────────────────────────────────────
    for stat, x in _STAT_X.items():
        if stat in char.advance_scheme:
            raw = char.advance_scheme[stat]
            try:
                n = int(raw)
                label = f"+{n}" if n >= 0 else str(n)
            except (TypeError, ValueError):
                label = str(raw)
            _draw_text(draw, x, _ADVANCE_Y, label, f_small, "mm")

    # ── CURRENT PROFILE ───────────────────────────────────────────────────────
    for stat, x in _STAT_X.items():
        val = getattr(char, stat, None)
        if val is not None:
            _draw_text(draw, x, _CURRENT_Y, val, f_stat, "mm")

    # ── SKILLS ────────────────────────────────────────────────────────────────
    # Fill left column fully before starting right column
    left_skills  = char.skills[:_SKILL_MAX_PER_COL]
    right_skills = char.skills[_SKILL_MAX_PER_COL:]
    for i, skill in enumerate(left_skills):
        _draw_text_fit(draw, _SKILL_LEFT_X,
                       _SKILL_START_Y + i * _SKILL_SPACING,
                       skill, _FS_SKILL, max_width=460, anchor="lm")
    for i, skill in enumerate(right_skills[:_SKILL_MAX_PER_COL]):
        _draw_text_fit(draw, _SKILL_RIGHT_X,
                       _SKILL_START_Y + i * _SKILL_SPACING,
                       skill, _FS_SKILL, max_width=620, anchor="lm")

    # ── HAND TO HAND WEAPONS ──────────────────────────────────────────────────
    for i, weapon in enumerate(char.hth_weapons):
        y = _HTH_START_Y + i * _HTH_SPACING
        _draw_text_fit(draw, _HTH_X, y, weapon, _FS_SKILL, max_width=450, anchor="lm")
        stats = get_hth_stats(weapon)
        if stats:
            _draw_text(draw, _HTH_IMOD_X,  y, stats["i_mod"],  f_small, "mm")
            _draw_text(draw, _HTH_WS_X,    y, stats.get("ws_mod", "-"), f_small, "mm")
            _draw_text(draw, _HTH_DMG_X,   y, stats["damage"], f_small, "mm")
            _draw_text(draw, _HTH_PARRY_X, y, stats["parry"],  f_small, "mm")

    # ── MISSILE WEAPONS ───────────────────────────────────────────────────────
    for i, weapon in enumerate(char.missile_weapons):
        y = _MIS_START_Y + i * _MIS_SPACING
        _draw_text_wrap(draw, _MIS_X, y, weapon, _FS_SKILL,
                        max_width=350, line_height=28, anchor="lm", max_lines=2)
        stats = get_missile_stats(weapon)
        if stats:
            _draw_text(draw, _MIS_SR_X,  y, stats["s_range"], f_small, "mm")
            _draw_text(draw, _MIS_MR_X,  y, stats["m_range"], f_small, "mm")
            _draw_text(draw, _MIS_LR_X,  y, stats["l_range"], f_small, "mm")
            _draw_text(draw, _MIS_DMG_X, y, stats["damage"],  f_small, "mm")
            _draw_text(draw, _MIS_RLD_X, y, stats["reload"],  f_small, "mm")

    # ── ARMOUR ────────────────────────────────────────────────────────────────
    for i, item in enumerate(char.armour_items):
        y = _ARM_START_Y + i * _ARM_SPACING
        _draw_text_fit(draw, _ARM_X, y, item, _FS_SKILL, max_width=460, anchor="lm")
        stats = get_armour_stats(item)
        if stats:
            _draw_text(draw, _ARM_LOC_X, y, stats["location"], f_small, "lm")
            _draw_text(draw, _ARM_ENC_X, y, str(stats["enc"]), f_small, "mm")

    # ── ARMOUR AVATAR BOXES (total AP per location) ───────────────────────────
    def _sum_ap(loc: str) -> str:
        total = sum(
            get_armour_stats(item)[loc]
            for item in char.armour_items
            if get_armour_stats(item)
        )
        return str(total) if total else "-"

    _draw_text(draw, _AV_HEAD_X,  _AV_HEAD_Y,  _sum_ap("head"), f_stat, "mm")
    _draw_text(draw, _AV_BODY_X,  _AV_BODY_Y,  _sum_ap("body"), f_stat, "mm")
    _draw_text(draw, _AV_R_ARM_X, _AV_R_ARM_Y, _sum_ap("arms"), f_stat, "mm")
    _draw_text(draw, _AV_L_ARM_X, _AV_L_ARM_Y, _sum_ap("arms"), f_stat, "mm")
    _draw_text(draw, _AV_R_LEG_X, _AV_R_LEG_Y, _sum_ap("legs"), f_stat, "mm")
    _draw_text(draw, _AV_L_LEG_X, _AV_L_LEG_Y, _sum_ap("legs"), f_stat, "mm")
    _draw_text(draw, _AV_SHIELD_X, _AV_SHIELD_Y, "-",            f_stat, "mm")


def save_character_image(char: Character,
                          path: str = "character_sheet_filled.jpg") -> str:
    """Fill page 1 and save as JPEG. Returns output path."""
    img  = Image.open(_SHEET).copy()
    draw = ImageDraw.Draw(img)
    _fill_page1(char, draw)
    img.save(path, "JPEG", quality=95)
    return path


def _fill_page2(char: Character, draw: ImageDraw.ImageDraw) -> None:
    """Draw all character data onto page-2 ImageDraw context."""
    f_field = _get_font(_FS_FIELD)
    f_stat  = _get_font(_FS_STAT)
    f_skill = _get_font(_FS_SKILL)
    f_small = _get_font(_FS_SMALL)

    # ── Info boxes ────────────────────────────────────────────────────────────
    _draw_text(draw, _P2_FP_X,  _P2_FP_Y,  str(char.FP),  f_stat, "mm")
    _draw_text(draw, _P2_MAG_X, _P2_MAG_Y, str(char.Mag), f_stat, "mm")
    _draw_text(draw, _P2_IP_X,  _P2_IP_Y,  str(char.IP),  f_stat, "mm")
    _draw_text(draw, _P2_XP_X,  _P2_XP_Y,  str(char.experience), f_stat, "mm")

    # ── Spells ────────────────────────────────────────────────────────────────
    # Column boundaries (from pixel scan): NAME 294-713, SL 713-815, MP 815-921,
    # R 921-1023, D 1023-1130, ING 1130-1519, EFF 1519-1946
    for i, spell_name in enumerate(char.spells):
        y = _P2_SPELL_START_Y + i * _P2_SPELL_SPACING
        data = get_spell(spell_name)
        _draw_text_fit(draw, _P2_SPELL_NAME_X, y, spell_name,
                       _FS_SKILL, max_width=390, anchor="lm")
        if data:
            _draw_text_fit(draw, _P2_SPELL_SL_X,  y, str(data["sl"]),
                           26, max_width=90, anchor="mm")
            _draw_text_fit(draw, _P2_SPELL_MP_X,  y, str(data["mp"]),
                           26, max_width=90, anchor="mm")
            _draw_text_fit(draw, _P2_SPELL_R_X,   y, data["r"],
                           26, max_width=90, anchor="mm", min_size=14)
            _draw_text_fit(draw, _P2_SPELL_D_X,   y, data["d"],
                           26, max_width=90, anchor="mm", min_size=14)
            _draw_text_fit(draw, _P2_SPELL_ING_X, y, data["ingredients"],
                           26, max_width=360, anchor="lm")
            _draw_text_wrap(draw, _P2_SPELL_EFF_X, y, data["effect"],
                            26, max_width=400, line_height=_P2_SPELL_SPACING // 2,
                            anchor="lm", max_lines=2)

    # ── Trappings (items not already listed as weapons/armour) ────────────────
    weapon_set = set(char.hth_weapons) | set(char.missile_weapons)
    armour_set = set(char.armour_items)
    other_items = [t for t in char.trappings
                   if t not in weapon_set and t not in armour_set]
    # Append spells with a prefix so they appear in the equipment table
    spell_entries = []  # spells are now drawn in dedicated section above
    all_items = other_items + spell_entries
    for i, item in enumerate(all_items):
        y = _P2_TRAP_START_Y + i * _P2_TRAP_SPACING
        _draw_text_fit(draw, _P2_TRAP_X, y, item, _FS_SKILL, max_width=510, anchor="lm")

    # ── Wealth ────────────────────────────────────────────────────────────────
    _draw_text(draw, _P2_WGC_X, _P2_WGC_Y, f"{char.wealth_gc} GC", f_field, "lm")
    _draw_text(draw, _P2_WSS_X, _P2_WSS_Y, f"{char.wealth_ss} SS", f_field, "lm")
    _draw_text(draw, _P2_WBP_X, _P2_WBP_Y, f"{char.wealth_bp} BP", f_field, "lm")

    # ── Movement rates ────────────────────────────────────────────────────────
    M = char.M
    _Y = 0.9144   # yards -> metres
    _K = 1.60934  # mph -> km/t
    mv_rows = [
        (round(M     * _Y, 1), round(M *  6 * _Y, 1), round(M *  6 * 60 / 1760 * _K, 1), _P2_MV_CAUT_Y),
        (round(M * 2 * _Y, 1), round(M * 12 * _Y, 1), round(M * 12 * 60 / 1760 * _K, 1), _P2_MV_STD_Y),
        (round(M * 4 * _Y, 1), round(M * 24 * _Y, 1), round(M * 24 * 60 / 1760 * _K, 1), _P2_MV_RUN_Y),
    ]
    for v10, vmin, vkph, y in mv_rows:
        _draw_text(draw, _P2_MV_10_X,  y, str(v10),  f_small, "mm")
        _draw_text(draw, _P2_MV_MIN_X, y, str(vmin), f_small, "mm")
        _draw_text(draw, _P2_MV_MPH_X, y, str(vkph), f_small, "mm")

    # ── Languages ─────────────────────────────────────────────────────────────
    for i, lang in enumerate(char.languages):
        y = _P2_LANG_START_Y + i * _P2_LANG_SPACING
        _draw_text(draw, _P2_LANG_X, y, lang, f_skill, "lm")

    # ── Background ────────────────────────────────────────────────────────────
    if char.place_of_birth:
        _draw_text(draw, _P2_BIRTH_X,  _P2_BIRTH_Y,  char.place_of_birth,     f_field, "lm")
    if char.parents_occupation:
        _draw_text(draw, _P2_PARENT_X, _P2_PARENT_Y, char.parents_occupation, f_field, "lm")
    if char.family_members:
        _draw_text(draw, _P2_FAMILY_X, _P2_FAMILY_Y, char.family_members,     f_field, "lm")
    if char.social_level:
        _draw_text(draw, _P2_SOCIAL_X, _P2_SOCIAL_Y, char.social_level,       f_field, "lm")
    if char.religion:
        _draw_text(draw, _P2_RELIG_X,  _P2_RELIG_Y,  char.religion,           f_field, "lm")


def save_character_spread(char: Character,
                           path: str = "character_sheet_spread.jpg") -> str:
    """
    Render both pages of the character sheet side by side (landscape).
    Page 1 (filled) on the left, page 2 (filled) on the right.
    Returns the output path.
    """
    # Fill page 1
    page1 = Image.open(_SHEET).copy()
    draw1 = ImageDraw.Draw(page1)
    _fill_page1(char, draw1)

    # Fill page 2
    if os.path.exists(_SHEET2):
        page2 = Image.open(_SHEET2).copy()
    else:
        page2 = Image.new("RGB", page1.size, (255, 255, 255))
    draw2 = ImageDraw.Draw(page2)
    _fill_page2(char, draw2)

    # Combine side by side with a small gap
    W1, H1 = page1.size
    W2, H2 = page2.size
    H = max(H1, H2)
    spread = Image.new("RGB", (W1 + _PAGE_GAP + W2, H), (180, 180, 180))
    spread.paste(page1, (0, 0))
    spread.paste(page2, (W1 + _PAGE_GAP, 0))

    spread.save(path, "JPEG", quality=95)
    return path
