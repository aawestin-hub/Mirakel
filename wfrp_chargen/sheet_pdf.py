"""
PDF character sheet renderer for WFRP 1st Edition.

Generates a PDF that faithfully mimics the layout of the original 1986
character sheet: bordered stat boxes, section headers in Courier bold,
and a clean monochrome look.

Usage:
    from sheet_pdf import save_character_pdf
    save_character_pdf(char, "my_character.pdf")
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas

from chargen.character import Character

# ── Layout constants (all in mm from bottom-left corner) ─────────────────────
PAGE_W, PAGE_H = A4          # 210 × 297 mm in points
MARGIN = 12 * mm
COL_W  = (PAGE_W - 2 * MARGIN) / 2   # two-column layout

# Font choices
FONT_TITLE  = "Courier-Bold"
FONT_HEADER = "Courier-Bold"
FONT_LABEL  = "Courier-Bold"
FONT_VALUE  = "Courier"
FONT_BODY   = "Courier"

# Colours
C_BLACK = colors.black
C_WHITE = colors.white
C_GREY  = colors.Color(0.85, 0.85, 0.85)   # light grey box fill


def _box(c: Canvas, x, y, w, h,
         fill=C_WHITE, stroke=C_BLACK, line_width=0.6):
    c.setLineWidth(line_width)
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    c.rect(x, y, w, h, fill=1, stroke=1)


def _text(c: Canvas, x, y, text, font=FONT_BODY, size=8, colour=C_BLACK):
    c.setFont(font, size)
    c.setFillColor(colour)
    c.drawString(x, y, str(text))


def _centred(c: Canvas, x, y, w, text, font=FONT_BODY, size=8, colour=C_BLACK):
    c.setFont(font, size)
    c.setFillColor(colour)
    c.drawCentredString(x + w / 2, y, str(text))


def _section_header(c: Canvas, x, y, w, title: str):
    """Draw a filled dark banner with white title text."""
    h = 5.5 * mm
    _box(c, x, y, w, h, fill=C_BLACK)
    c.setFont(FONT_HEADER, 7)
    c.setFillColor(C_WHITE)
    c.drawCentredString(x + w / 2, y + 1.6 * mm, title.upper())


def _stat_cell(c: Canvas, x, y, cell_w, cell_h, label: str, value):
    """Draw a labelled stat cell: label on top, value below."""
    _box(c, x, y, cell_w, cell_h, fill=C_WHITE)
    # label
    c.setFont(FONT_LABEL, 5.5)
    c.setFillColor(C_BLACK)
    c.drawCentredString(x + cell_w / 2, y + cell_h - 3.8 * mm, label)
    # divider
    c.setLineWidth(0.3)
    c.line(x, y + cell_h - 4.5 * mm, x + cell_w, y + cell_h - 4.5 * mm)
    # value
    c.setFont(FONT_VALUE, 10)
    c.drawCentredString(x + cell_w / 2, y + 1 * mm, str(value))


# ── Main renderer ─────────────────────────────────────────────────────────────

def save_character_pdf(char: Character, path: str = "character_sheet.pdf") -> str:
    """
    Render the character to a PDF and save it to *path*.
    Returns the path on success.
    """
    c = Canvas(path, pagesize=A4)
    _draw_sheet(c, char)
    c.save()
    return path


def _draw_sheet(c: Canvas, char: Character) -> None:
    W = PAGE_W
    H = PAGE_H

    # ── Title banner ──────────────────────────────────────────────────────────
    banner_h = 18 * mm
    banner_y = H - MARGIN - banner_h
    _box(c, MARGIN, banner_y, W - 2 * MARGIN, banner_h, fill=C_BLACK)
    c.setFont(FONT_TITLE, 14)
    c.setFillColor(C_WHITE)
    c.drawCentredString(W / 2, banner_y + 10 * mm,
                        "WARHAMMER FANTASY ROLEPLAY")
    c.setFont(FONT_TITLE, 9)
    c.drawCentredString(W / 2, banner_y + 4 * mm,
                        "CHARACTER SHEET  ·  1st Edition")

    cursor_y = banner_y - 4 * mm   # current top of the next element

    # ── Identity block ────────────────────────────────────────────────────────
    id_h = 22 * mm
    id_y = cursor_y - id_h
    _box(c, MARGIN, id_y, W - 2 * MARGIN, id_h)

    fields = [
        ("Name",         char.name or "(unnamed)"),
        ("Race",         char.race),
        ("Career Class", char.career_class),
        ("Career",       char.career),
    ]
    field_w = (W - 2 * MARGIN) / len(fields)
    for i, (label, value) in enumerate(fields):
        fx = MARGIN + i * field_w
        c.setFont(FONT_LABEL, 6)
        c.setFillColor(C_BLACK)
        c.drawString(fx + 2 * mm, id_y + id_h - 4.5 * mm, label.upper())
        c.setLineWidth(0.3)
        c.line(fx + 2 * mm, id_y + id_h - 5.5 * mm,
               fx + field_w - 2 * mm, id_y + id_h - 5.5 * mm)
        c.setFont(FONT_VALUE, 8)
        c.drawString(fx + 2 * mm, id_y + 3 * mm, value)
        if i > 0:
            c.setLineWidth(0.4)
            c.line(fx, id_y, fx, id_y + id_h)

    cursor_y = id_y - 3 * mm

    # ── Primary characteristics ───────────────────────────────────────────────
    _section_header(c, MARGIN, cursor_y - 5.5 * mm, W - 2 * MARGIN,
                    "Primary Characteristics")
    cursor_y -= 5.5 * mm + 2 * mm

    primary_stats = [
        ("WS",  char.WS),  ("BS",  char.BS),  ("S",   char.S),
        ("T",   char.T),   ("I",   char.I),   ("Dex", char.Dex),
        ("Ld",  char.Ld),  ("Int", char.Int), ("Cl",  char.Cl),
        ("WP",  char.WP),  ("Fel", char.Fel),
    ]
    n_cols = len(primary_stats)
    cell_w = (W - 2 * MARGIN) / n_cols
    cell_h = 13 * mm
    stat_y = cursor_y - cell_h
    for i, (label, value) in enumerate(primary_stats):
        _stat_cell(c, MARGIN + i * cell_w, stat_y, cell_w, cell_h, label, value)
    cursor_y = stat_y - 3 * mm

    # ── Secondary characteristics ─────────────────────────────────────────────
    _section_header(c, MARGIN, cursor_y - 5.5 * mm, W - 2 * MARGIN,
                    "Secondary Characteristics")
    cursor_y -= 5.5 * mm + 2 * mm

    secondary_stats = [
        ("A",   char.A),   ("W",   char.W),   ("SB",  char.SB),
        ("TB",  char.TB),  ("M",   char.M),   ("Mag", char.Mag),
        ("IP",  char.IP),  ("FP",  char.FP),
    ]
    n_sec = len(secondary_stats)
    sec_cell_w = (W - 2 * MARGIN) / n_sec
    sec_y = cursor_y - cell_h
    for i, (label, value) in enumerate(secondary_stats):
        _stat_cell(c, MARGIN + i * sec_cell_w, sec_y, sec_cell_w, cell_h,
                   label, value)
    cursor_y = sec_y - 3 * mm

    # ── Advance scheme ────────────────────────────────────────────────────────
    _section_header(c, MARGIN, cursor_y - 5.5 * mm, W - 2 * MARGIN,
                    "Advance Scheme  (max advances)")
    cursor_y -= 5.5 * mm + 2 * mm

    adv_order = ["WS","BS","S","T","I","Dex","Ld","Int","Cl","WP","Fel","A","W"]
    adv_stats = [(k, char.advance_scheme.get(k, "-")) for k in adv_order
                 if k in char.advance_scheme]
    n_adv = len(adv_stats)
    adv_cell_w = (W - 2 * MARGIN) / n_adv
    adv_h = 11 * mm
    adv_y = cursor_y - adv_h
    for i, (label, value) in enumerate(adv_stats):
        _stat_cell(c, MARGIN + i * adv_cell_w, adv_y, adv_cell_w, adv_h,
                   label, value)
    cursor_y = adv_y - 3 * mm

    # ── Skills & Trappings  (two columns) ────────────────────────────────────
    col_gap = 4 * mm
    col_w   = (W - 2 * MARGIN - col_gap) / 2
    bottom_y = MARGIN

    # LEFT: Skills
    skills_x = MARGIN
    _section_header(c, skills_x, cursor_y - 5.5 * mm, col_w, "Skills")
    skills_top = cursor_y - 5.5 * mm - 1 * mm
    skills_box_h = skills_top - bottom_y
    _box(c, skills_x, bottom_y, col_w, skills_box_h)
    sy = skills_top - 4 * mm
    for skill in char.skills:
        if sy < bottom_y + 3 * mm:
            break
        _text(c, skills_x + 2 * mm, sy, f"• {skill}", size=7)
        sy -= 4 * mm

    # RIGHT: Trappings
    trap_x = MARGIN + col_w + col_gap
    _section_header(c, trap_x, cursor_y - 5.5 * mm, col_w, "Trappings")
    trap_top = cursor_y - 5.5 * mm - 1 * mm
    trap_box_h = trap_top - bottom_y
    _box(c, trap_x, bottom_y, col_w, trap_box_h)
    ty = trap_top - 4 * mm
    for item in char.trappings:
        if ty < bottom_y + 3 * mm:
            break
        _text(c, trap_x + 2 * mm, ty, f"• {item}", size=7)
        ty -= 4 * mm

    # Optional career note at very bottom
    if char.career_note:
        c.setFont(FONT_BODY, 6)
        c.setFillColor(colors.Color(0.4, 0.4, 0.4))
        c.drawString(MARGIN, MARGIN / 2,
                     f"Note: {char.career_note}")
