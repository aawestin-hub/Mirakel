"""
Fills character data onto the WFRP 1st Edition character sheet image.

Uses Pillow to overlay text at calibrated field positions.
Image: sheet_page0.png  (2250 × 3250 px, rendered from PDF at 300 DPI)

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

# Font sizes – calibrated for 2250 × 3250 px sheet
_FS_FIELD   = 37   # identity fields
_FS_STAT    = 35   # stat grid values
_FS_SKILL   = 30   # skill / weapon names
_FS_SMALL   = 28   # advance scheme / table values

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
    top_anchor = "t" in anchor  # "lt" → start at y; "lm" → centre block around y
    for size in range(base_size, min_size - 1, -2):
        font = _get_font(size)
        for n in range(1, max_lines + 1):
            lines = _best_split(draw, text.split(), n, font, max_width)
            if lines is not None:
                total_h = (len(lines) - 1) * line_height
                start_y = y if top_anchor else y - total_h // 2
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
    start_y = y if top_anchor else y - total_h // 2
    for i, line in enumerate(lines):
        draw.text((x, start_y + i * line_height),
                  line, font=font, fill=colour, anchor=anchor)


def _draw_exits(draw, x: int, y: int, items: list[str], base_size: int,
                max_width: int, line_height: int, anchor: str = "lm",
                min_size: int = 18, max_lines: int = 4) -> None:
    """
    Render a comma-separated list of exit names, keeping multi-word names
    (e.g. 'Outlaw Chief', 'Sapper (Dwarfs only)') on the same line.
    Shrinks font if the list doesn't fit at the given size.
    """
    top_anchor = "t" in anchor
    for size in range(base_size, min_size - 1, -2):
        font = _get_font(size)
        lines: list[str] = []
        current: list[str] = []
        for item in items:
            candidate = ", ".join(current + [item])
            if _text_width(draw, candidate, font) <= max_width:
                current.append(item)
            else:
                if current:
                    lines.append(", ".join(current))
                current = [item]
        if current:
            lines.append(", ".join(current))
        if len(lines) <= max_lines and all(
            _text_width(draw, ln, font) <= max_width for ln in lines
        ):
            total_h = (len(lines) - 1) * line_height
            start_y = y if top_anchor else y - total_h // 2
            for i, line in enumerate(lines):
                draw.text((x, start_y + i * line_height),
                          line, font=font, fill=_INK, anchor=anchor)
            return
    # Last resort at min_size
    font = _get_font(min_size)
    lines = [", ".join(items[:len(items) // 2]),
             ", ".join(items[len(items) // 2:])][:max_lines]
    total_h = (len(lines) - 1) * line_height
    start_y = y if top_anchor else y - total_h // 2
    for i, line in enumerate(lines):
        draw.text((x, start_y + i * line_height),
                  line, font=font, fill=_INK, anchor=anchor)


# ── Coordinates (calibrated via calibrate_ui.py) ─────────────────────────────

# Row 1
_R1_Y       = 522
_NAME_X     = 213
_RACE_X     = 895
_GENDER_X   = 1120
_CLASS_X    = 1345
_ALIGN_X    = 1845

# Description
_DESC_X     = 1340
_DESC_Y     = 668

# Row 2 – physical
_R2_Y       = 690
_AGE_X      = 206
_HEIGHT_X   = 434
_WEIGHT_X   = 659
_HAIR_X     = 884
_EYES_X     = 1115

# Row 3 – career
_R3_Y       = 900
_CAREER_X   = 200
_PATH_X     = 681
_EXITS_X    = 1422

# Stat profile grid
_STAT_X = {
    "M":   584, "WS":  697, "BS":  811, "S":   925,
    "T":  1031, "W":  1152, "I":  1263, "A":  1379,
    "Dex": 1493, "Ld": 1609, "Int": 1720, "Cl": 1834,
    "WP":  1940, "Fel": 2052,
}
_STARTER_Y  = 1086
_ADVANCE_Y  = 1197
_CURRENT_Y  = 1311

# Skills
_SKILL_LEFT_X      = 1638
_SKILL_START_Y     = 1470
_SKILL_SPACING     = 50
_SKILL_MAX_ROWS    = 30   # max skills that fit in a single column

# Hand-to-hand weapons table
_HTH_X        = 204
_HTH_START_Y  = 1477
_HTH_SPACING  = 50
_HTH_IMOD_X   = 663
_HTH_WS_X     = 769   # estimated proportionally (between imod and dmg)
_HTH_DMG_X    = 875
_HTH_PARRY_X  = 986

# Missile weapons table
_MIS_X        = 195
_MIS_START_Y  = 2006
_MIS_SPACING  = 48
_MIS_SR_X     = 556
_MIS_MR_X     = 665
_MIS_LR_X     = 763
_MIS_DMG_X    = 872
_MIS_RLD_X    = 979

# Armour table
_ARM_X        = 188
_ARM_START_Y  = 2538
_ARM_SPACING  = 50
_ARM_LOC_X    = 647
_ARM_ENC_X    = 972

# Armour location boxes around avatar figure
_AV_HEAD_X     = 1161
_AV_HEAD_Y     = 2347
_AV_R_ARM_X    = 1093
_AV_R_ARM_Y    = 2570
_AV_L_ARM_X    = 1525
_AV_L_ARM_Y    = 2475
_AV_BODY_X     = 1531
_AV_BODY_Y     = 2693
_AV_R_LEG_X    = 1097
_AV_R_LEG_Y    = 2838
_AV_L_LEG_X    = 1529
_AV_L_LEG_Y    = 2895
_AV_SHIELD_X   = 1420
_AV_SHIELD_Y   = 2322

# ── Page 2 coordinates (relative to page-2 image origin) ──────────────────────

_P2_FP_X           = 2040
_P2_FP_Y           = 340
_P2_MAG_X          = 2040
_P2_MAG_Y          = 520
_P2_PL_X           = 2040  # Power Level
_P2_PL_Y           = 686
_P2_IP_X           = 2040
_P2_IP_Y           = 1459
_P2_XP_X           = 2040
_P2_XP_Y           = 870

_P2_TRAP_X         = 191
_P2_TRAP_START_Y   = 1059
_P2_TRAP_SPACING   = 50
_P2_TRAP_LOC_X     = 716
_P2_TRAP_ENC_X     = 827

_P2_WGC_X          = 293
_P2_WGC_Y          = 2384
_P2_WSS_X          = 509
_P2_WSS_Y          = 2381
_P2_WBP_X          = 736
_P2_WBP_Y          = 2384

_P2_MV_X           = 1216
_P2_MV_CAUT_Y      = 1072
_P2_MV_STD_Y       = 1156
_P2_MV_RUN_Y       = 1247
_P2_MV_10_X        = 1214
_P2_MV_MIN_X       = 1314
_P2_MV_MPH_X       = 1416

_P2_LANG_X         = 1527
_P2_LANG_START_Y   = 1056
_P2_LANG_SPACING   = 48

_P2_SOCIAL_X       = 2040
_P2_SOCIAL_Y       = 1756
_P2_RELIG_X        = 2040
_P2_RELIG_Y        = 2000

# Background free-text area (birthplace / parents / family / star sign / mark merged here)
_P2_BACK_X         = 200
_P2_BACK_Y         = 2554
_P2_BACK_SPACING   = 48

_PAGE_GAP = 20


# ── Page 2 spell section coordinates ──────────────────────────────────────────
_P2_SPELL_NAME_X    = 20
_P2_SPELL_SL_X      = 727
_P2_SPELL_MP_X      = 820
_P2_SPELL_R_X       = 913
_P2_SPELL_D_X       = 1025   # shifted right to avoid left-edge clipping
_P2_SPELL_ING_X     = 1075
_P2_SPELL_EFF_X     = 1490
_P2_SPELL_START_Y   = 352   # first data row center (header ends y≈287)
_P2_SPELL_SPACING   = 130   # each row ~130px tall (660px / 5 rows)


def _fill_page1(char: Character, draw: ImageDraw.ImageDraw,
                pc_mode: bool = False) -> None:
    """Draw all character data onto an already-opened page-1 ImageDraw context."""
    f_field = _get_font(_FS_FIELD)
    f_stat  = _get_font(_FS_STAT)
    f_skill = _get_font(_FS_SKILL)
    f_small = _get_font(_FS_SMALL)

    # ── Row 1: NAME / RACE / GENDER / CLASS / ALIGNMENT ─────────────────────
    # Cell widths: NAME 355-1042(687px), RACE 1042-1265(223px), GENDER 1265-1507(242px),
    # CLASS 1330-1780(450px), ALIGN 1780-2200(420px)
    _draw_text_fit(draw, _NAME_X,   _R1_Y, char.name or "(unnamed)", _FS_FIELD,
                   max_width=591, anchor="lm")
    _draw_text_fit(draw, _RACE_X,   _R1_Y, char.race,                _FS_FIELD,
                   max_width=185, anchor="lm")
    if char.gender:
        _draw_text_fit(draw, _GENDER_X, _R1_Y, char.gender,          _FS_FIELD,
                       max_width=199, anchor="lm")
    _draw_text_fit(draw, _CLASS_X,  _R1_Y, char.career_class,        _FS_FIELD,
                   max_width=432, anchor="lm")
    _draw_text_fit(draw, _ALIGN_X,  _R1_Y, char.alignment,           _FS_FIELD,
                   max_width=397, anchor="lm")

    # ── Description ──────────────────────────────────────────────────────────
    if char.description:
        _draw_text_fit(draw, _DESC_X, _DESC_Y, char.description, _FS_SMALL,
                       max_width=873, anchor="lm")

    # ── Row 2: AGE / HEIGHT / WEIGHT / HAIR / EYES ───────────────────────────
    _draw_text_fit(draw, _AGE_X,    _R2_Y, char.age,         _FS_FIELD, max_width=185, anchor="lm")
    _draw_text_fit(draw, _HEIGHT_X, _R2_Y, char.height,      _FS_FIELD, max_width=185, anchor="lm")
    _draw_text_fit(draw, _WEIGHT_X, _R2_Y, char.weight,      _FS_FIELD, max_width=185, anchor="lm")
    _draw_text_fit(draw, _HAIR_X,   _R2_Y, char.hair_colour, _FS_FIELD, max_width=185, anchor="lm")
    _draw_text_fit(draw, _EYES_X,   _R2_Y, char.eye_colour,  _FS_FIELD, max_width=194, anchor="lm")

    # ── Row 3: CURRENT CAREER / CAREER PATH / CAREER EXITS ──────────────────
    career_y      = _R3_Y - 80 if pc_mode else _R3_Y
    career_anchor = "lt" if pc_mode else "lm"
    _draw_text_fit(draw, _CAREER_X, career_y, char.career, _FS_FIELD, max_width=432, anchor=career_anchor)
    # CAREER PATH box: blank for starting PC (history starts empty); NPC shows career
    if not pc_mode:
        _draw_text_fit(draw, _PATH_X, career_y, char.career, _FS_FIELD, max_width=644, anchor=career_anchor)
    if char.career_exits:
        exits_y = career_y
        _draw_exits(draw, _EXITS_X, exits_y, char.career_exits,
                    _FS_SMALL, max_width=750, line_height=40,
                    anchor=career_anchor, max_lines=4)

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
    if not pc_mode:
        adv = char.advance_scheme if getattr(char, "is_advanced_career", False) else {}
        for stat, x in _STAT_X.items():
            val = getattr(char, stat, None)
            if val is not None:
                if adv and stat in adv:
                    try:
                        val = val + int(adv[stat])
                    except (TypeError, ValueError):
                        pass
                _draw_text(draw, x, _CURRENT_Y, val, f_stat, "mm")

    # ── SKILLS ────────────────────────────────────────────────────────────────
    # ── SKILLS (single column, all skills) ───────────────────────────────────
    for i, skill in enumerate(char.skills[:_SKILL_MAX_ROWS]):
        _draw_text_fit(draw, _SKILL_LEFT_X,
                       _SKILL_START_Y + i * _SKILL_SPACING,
                       skill, _FS_SKILL, max_width=1050, anchor="lm")

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
    def _sum_ap(loc: str) -> int:
        return sum(
            get_armour_stats(item)[loc]
            for item in char.armour_items
            if get_armour_stats(item)
        )

    def _ap_label(loc: str) -> str | None:
        total = _sum_ap(loc)
        return str(total) if total else None  # blank when no armour, in both modes

    for x, y, loc in [
        (_AV_HEAD_X,  _AV_HEAD_Y,  "head"),
        (_AV_BODY_X,  _AV_BODY_Y,  "body"),
        (_AV_R_ARM_X, _AV_R_ARM_Y, "arms"),
        (_AV_L_ARM_X, _AV_L_ARM_Y, "arms"),
        (_AV_R_LEG_X, _AV_R_LEG_Y, "legs"),
        (_AV_L_LEG_X, _AV_L_LEG_Y, "legs"),
    ]:
        label = _ap_label(loc)
        if label is not None:
            _draw_text(draw, x, y, label, f_stat, "mm")
    # Shield box: always blank (player/GM fills in if relevant)


def save_character_image(char: Character,
                          path: str = "character_sheet_filled.jpg",
                          pc_mode: bool = False) -> str:
    """Fill page 1 and save as JPEG. Returns output path."""
    img  = Image.open(_SHEET).copy()
    draw = ImageDraw.Draw(img)
    _fill_page1(char, draw, pc_mode=pc_mode)
    img.save(path, "JPEG", quality=95)
    return path


def _draw_paragraph(draw, x: int, y: int, text: str, base_size: int,
                    max_width: int, line_height: int, max_lines: int = 15,
                    colour=_INK) -> None:
    """Word-wrap text into multiple lines, shrinking font to fit."""
    if not text:
        return
    words = text.split()
    for size in range(base_size, 20, -2):
        font = _get_font(size)
        lines, cur = [], []
        for word in words:
            test = " ".join(cur + [word])
            if _text_width(draw, test, font) <= max_width:
                cur.append(word)
            else:
                if cur:
                    lines.append(" ".join(cur))
                cur = [word]
        if cur:
            lines.append(" ".join(cur))
        if len(lines) <= max_lines:
            for i, line in enumerate(lines):
                draw.text((x, y + i * line_height), line,
                          font=font, fill=colour, anchor="lm")
            return
    # fallback at min size
    font = _get_font(22)
    lines, cur = [], []
    for word in words:
        test = " ".join(cur + [word])
        if _text_width(draw, test, font) <= max_width:
            cur.append(word)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [word]
    if cur:
        lines.append(" ".join(cur))
    for i, line in enumerate(lines[:max_lines]):
        draw.text((x, y + i * line_height), line, font=font, fill=colour, anchor="lm")


def _fill_page2(char: Character, draw: ImageDraw.ImageDraw,
                pc_mode: bool = False) -> None:
    """Draw all character data onto page-2 ImageDraw context."""
    f_field = _get_font(_FS_FIELD)
    f_stat  = _get_font(_FS_STAT)
    f_skill = _get_font(_FS_SKILL)
    f_small = _get_font(_FS_SMALL)

    # ── Info boxes ────────────────────────────────────────────────────────────
    # FP: always shown (meaningful starting value)
    _draw_text(draw, _P2_FP_X, _P2_FP_Y, str(char.FP), f_stat, "mm")
    # Mag: only show if character has magic (Mag > 0)
    if char.Mag:
        _draw_text(draw, _P2_MAG_X, _P2_MAG_Y, str(char.Mag), f_stat, "mm")
    # Power Level: show starting value of 0
    _draw_text(draw, _P2_PL_X, _P2_PL_Y, "0", f_stat, "mm")
    # IP and XP: always start at 0 — leave blank; player/GM fills in

    # ── Spells ────────────────────────────────────────────────────────────────
    # Column boundaries (from pixel scan): NAME 294-713, SL 713-815, MP 815-921,
    # R 921-1023, D 1023-1130, ING 1130-1519, EFF 1519-1946
    for i, spell_name in enumerate(char.spells):
        y = _P2_SPELL_START_Y + i * _P2_SPELL_SPACING
        data = get_spell(spell_name)
        _draw_text_fit(draw, _P2_SPELL_NAME_X, y, spell_name,
                       _FS_SKILL, max_width=640, anchor="lm")
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
                           26, max_width=330, anchor="lm")
            _draw_text_wrap(draw, _P2_SPELL_EFF_X, y, data["effect"],
                            26, max_width=260, line_height=_P2_SPELL_SPACING // 2,
                            anchor="lm", max_lines=2)

    # ── Trappings (items not already listed as weapons/armour) ────────────────
    weapon_set = set(char.hth_weapons) | set(char.missile_weapons)
    armour_set = set(char.armour_items)
    other_items = [t for t in char.trappings
                   if t not in weapon_set and t not in armour_set]
    spell_entries = []  # spells are now drawn in dedicated section above
    all_items = other_items + spell_entries

    _TRAP_MAX_W  = 450          # item text column width (px)
    _TRAP_ROW_H  = _P2_TRAP_SPACING
    _TRAP_WRAP_H = 25           # line-height when wrapping within a 2-row block
    _TRAP_MAX_Y  = _P2_WGC_Y - 70           # stop well before the WEALTH section
    trap_font    = _get_font(_FS_SKILL)

    y_top = _P2_TRAP_START_Y
    for item in all_items:
        if y_top >= _TRAP_MAX_Y:
            break
        if _text_width(draw, item, trap_font) <= _TRAP_MAX_W:
            # Fits on a single row — draw centred in the row
            draw.text((_P2_TRAP_X, y_top + _TRAP_ROW_H // 2), item,
                      font=trap_font, fill=_INK, anchor="lm")
            y_top += _TRAP_ROW_H
        elif y_top + _TRAP_ROW_H * 2 <= _TRAP_MAX_Y:
            # Wrap across two rows — centre block in the 2-row space
            _draw_text_wrap(draw, _P2_TRAP_X, y_top + _TRAP_ROW_H,
                            item, _FS_SKILL, max_width=_TRAP_MAX_W,
                            line_height=_TRAP_WRAP_H, anchor="lm", max_lines=2)
            y_top += _TRAP_ROW_H * 2
        else:
            # Only 1 row left — shrink to fit rather than overflow
            _draw_text_fit(draw, _P2_TRAP_X, y_top + _TRAP_ROW_H // 2,
                           item, _FS_SKILL, max_width=_TRAP_MAX_W, anchor="lm")
            y_top += _TRAP_ROW_H

    # ── Wealth ────────────────────────────────────────────────────────────────
    # Sheet has pre-printed labels; write only the number. Leave blank if 0.
    if char.wealth_gc:
        _draw_text(draw, _P2_WGC_X, _P2_WGC_Y, str(char.wealth_gc), f_field, "lm")
    if char.wealth_ss:
        _draw_text(draw, _P2_WSS_X, _P2_WSS_Y, str(char.wealth_ss), f_field, "lm")
    if char.wealth_bp:
        _draw_text(draw, _P2_WBP_X, _P2_WBP_Y, str(char.wealth_bp), f_field, "lm")

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
    if char.social_level:
        _draw_text(draw, _P2_SOCIAL_X, _P2_SOCIAL_Y, char.social_level, f_field, "mm")
    if char.religion:
        _draw_text_fit(draw, _P2_RELIG_X - 170, _P2_RELIG_Y, char.religion,
                       _FS_FIELD, max_width=340, anchor="lm")

    # ── Background free-text (birthplace / parents / family merged) ───────────
    # ── Background narrative ───────────────────────────────────────────────────
    if char.background_narrative:
        _draw_paragraph(draw, _P2_BACK_X, _P2_BACK_Y,
                        char.background_narrative,
                        _FS_SMALL, max_width=1900, line_height=48, max_lines=12)
    else:
        # Fallback: list key facts
        back_lines = []
        if char.place_of_birth:      back_lines.append(f"Birthplace: {char.place_of_birth}")
        if char.parents_occupation:  back_lines.append(f"Parents: {char.parents_occupation}")
        if char.family_members:      back_lines.append(f"Family: {char.family_members}")
        if char.star_sign:           back_lines.append(f"Star Sign: {char.star_sign}")
        if char.distinguishing_marks: back_lines.append(f"Mark: {char.distinguishing_marks}")
        for i, line in enumerate(back_lines):
            _draw_text_fit(draw, _P2_BACK_X, _P2_BACK_Y + i * _P2_BACK_SPACING,
                           line, _FS_SMALL, max_width=1900, anchor="lm")


def save_character_spread(char: Character,
                           path: str = "character_sheet_spread.jpg",
                           pc_mode: bool = False,
                           template: str = "weskon") -> str:
    """
    Render both pages of the character sheet side by side (landscape).
    Page 1 (filled) on the left, page 2 (filled) on the right.

    Args:
        template: "weskon"  – Weskon's Fantasy Roleplay sheet (default, 2250×3250)
                  "classic" – Classic Edited sheet (1700×2200)
    Returns the output path.
    """
    if template == "classic":
        from sheet_classic import save_classic_spread
        return save_classic_spread(char, path=path, pc_mode=pc_mode)

    # ── Weskon's sheet (default) ───────────────────────────────────────────────
    page1 = Image.open(_SHEET).copy()
    draw1 = ImageDraw.Draw(page1)
    _fill_page1(char, draw1, pc_mode=pc_mode)

    if os.path.exists(_SHEET2):
        page2 = Image.open(_SHEET2).copy()
    else:
        page2 = Image.new("RGB", page1.size, (255, 255, 255))
    draw2 = ImageDraw.Draw(page2)
    _fill_page2(char, draw2, pc_mode=pc_mode)

    W1, H1 = page1.size
    W2, H2 = page2.size
    H = max(H1, H2)
    spread = Image.new("RGB", (W1 + _PAGE_GAP + W2, H), (180, 180, 180))
    spread.paste(page1, (0, 0))
    spread.paste(page2, (W1 + _PAGE_GAP, 0))

    spread.save(path, "JPEG", quality=95)
    return path
