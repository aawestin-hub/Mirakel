"""
Interactive calibration tool for WFRP character sheet field positions.

Drag the coloured markers to the correct positions on the sheet.
Press S to save coordinates to calibration_result.py.
Press Q to quit.

Scale: the sheet is displayed at 40% size for screen fit,
but all saved coordinates are in full 2550×3300 pixel space.
Page 2 markers are stored relative to the top-left of page 2.
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os, json

_HERE    = os.path.dirname(os.path.abspath(__file__))
_SHEET   = os.path.join(_HERE, "sheet_page0.png")
_SHEET2  = os.path.join(_HERE, "sheet_page1.png")
_OUT     = os.path.join(_HERE, "calibration_result.py")

DISPLAY_SCALE = 0.40   # show at 40% of full size
_PAGE_GAP     = 20     # pixels between pages (full-res)

# ── Initial marker definitions ──────────────────────────────────────────────
# Each entry: (id, label, x, y, colour, anchor_hint)
# Page 2 markers use x > 2550 (offset by P1_W + _PAGE_GAP); saved coords are relative to p2 origin.
MARKERS = [
    # Row 1
    ("name",    "NAME",    355,  530, "#e00", "lm"),
    ("race",    "RACE",   1042,  530, "#e00", "mm"),
    ("gender",  "GENDER", 1265,  530, "#e00", "mm"),
    ("cls",     "CLASS",  1507,  530, "#e00", "lm"),
    ("align",   "ALIGN",  2017,  530, "#e00", "lm"),
    # Description (row 1, after alignment, or separate row)
    ("desc",    "DESC",    355,  615, "#800", "lm"),
    # Row 2
    ("age",     "AGE",     350,  700, "#c00", "lm"),
    ("height",  "HEIGHT",  580,  700, "#c00", "lm"),
    ("weight",  "WEIGHT",  807,  700, "#c00", "lm"),
    ("hair",    "HAIR",   1037,  700, "#c00", "lm"),
    ("eyes",    "EYES",   1267,  700, "#c00", "lm"),
    # Row 3
    ("career",  "CAREER",  335,  897, "#080", "lm"),
    ("path",    "PATH",    837,  897, "#080", "lm"),
    ("exits",   "EXITS",  1582,  897, "#080", "lm"),
    # Stat rows
    ("M_s",     "M",       722, 1097, "#00c", "mm"),
    ("WS_s",    "WS",      842, 1097, "#00c", "mm"),
    ("BS_s",    "BS",      962, 1097, "#00c", "mm"),
    ("S_s",     "S",      1067, 1097, "#00c", "mm"),
    ("T_s",     "T",      1192, 1097, "#00c", "mm"),
    ("W_s",     "W",      1305, 1097, "#00c", "mm"),
    ("I_s",     "I",      1417, 1097, "#00c", "mm"),
    ("A_s",     "A",      1535, 1097, "#00c", "mm"),
    ("Dex_s",   "Dex",    1650, 1097, "#00c", "mm"),
    ("Ld_s",    "Ld",     1767, 1097, "#00c", "mm"),
    ("Int_s",   "Int",    1877, 1097, "#00c", "mm"),
    ("Cl_s",    "Cl",     1995, 1097, "#00c", "mm"),
    ("WP_s",    "WP",     2105, 1097, "#00c", "mm"),
    ("Fel_s",   "Fel",    2225, 1097, "#00c", "mm"),
    # Advance / Current rows
    ("adv_y",   "ADV-Y",   722, 1215, "#a0a", "mm"),
    ("cur_y",   "CUR-Y",   722, 1327, "#a0a", "mm"),
    # Skills
    ("skl_l",   "SKL-L",  1247, 1495, "#c60", "lm"),
    ("skl_r",   "SKL-R",  1820, 1495, "#c60", "lm"),
    ("skl_l2",  "SKL-L2", 1247, 1547, "#fa0", "lm"),
    # Hand-to-hand weapons (first two rows to get Y + spacing)
    ("hth1",       "HTH-1",    100, 1900, "#0aa", "lm"),
    ("hth2",       "HTH-2",    100, 1960, "#0aa", "lm"),
    # HTH column X positions (name col already = hth1.x)
    ("hth_imod",   "HTH-IMOD", 700, 1900, "#0aa", "mm"),
    ("hth_dmg",    "HTH-DMG",  900, 1900, "#0aa", "mm"),
    ("hth_parry",  "HTH-PRRY",1100, 1900, "#0aa", "mm"),
    # Missile weapons (first two rows)
    ("mis1",       "MIS-1",    100, 2200, "#09a", "lm"),
    ("mis2",       "MIS-2",    100, 2260, "#09a", "lm"),
    # Missile column X positions
    ("mis_sr",     "MIS-SR",   700, 2200, "#09a", "mm"),
    ("mis_mr",     "MIS-MR",   850, 2200, "#09a", "mm"),
    ("mis_lr",     "MIS-LR",  1000, 2200, "#09a", "mm"),
    ("mis_dmg",    "MIS-DMG", 1150, 2200, "#09a", "mm"),
    ("mis_rld",    "MIS-RLD", 1350, 2200, "#09a", "mm"),
    # Armour (first two rows)
    ("arm1",       "ARM-1",    100, 2500, "#0c8", "lm"),
    ("arm2",       "ARM-2",    100, 2560, "#0c8", "lm"),
    # Armour column X positions: Location and Encumbrance
    ("arm_loc",    "ARM-LOC",  900, 2500, "#0c8", "lm"),
    ("arm_enc",    "ARM-ENC", 1350, 2500, "#0c8", "mm"),
    # Armour location boxes around the avatar figure (7 locations)
    ("av_head",    "AV-HEAD",  1600, 1570, "#f80", "mm"),
    ("av_r_arm",   "AV-RARM",  1450, 1720, "#f80", "mm"),
    ("av_l_arm",   "AV-LARM",  1750, 1720, "#f80", "mm"),
    ("av_body",    "AV-BODY",  1600, 1800, "#f80", "mm"),
    ("av_r_leg",   "AV-RLEG",  1480, 1980, "#f80", "mm"),
    ("av_l_leg",   "AV-LLEG",  1720, 1980, "#f80", "mm"),
    ("av_shield",  "AV-SHLD",  1900, 1800, "#f80", "mm"),
    # ── Page 2 markers (x = 2550 + 20 + relative_x on page 2) ─────────────
    # Right column boxes
    ("p2_fp",      "P2-FP",    2570+2090, 160,  "#55f", "mm"),
    ("p2_mag",     "P2-MAG",   2570+2090, 310,  "#55f", "mm"),
    ("p2_ip",      "P2-IP",    2570+1740, 1450, "#55f", "mm"),
    ("p2_xp",      "P2-XP",    2570+2090, 585,  "#55f", "mm"),
    # Equipment/Trappings table
    ("p2_trap1",   "P2-TR1",   2570+100,  530,  "#0bb", "lm"),
    ("p2_trap2",   "P2-TR2",   2570+100,  605,  "#0bb", "lm"),
    ("p2_traploc", "P2-TRLOC", 2570+820,  530,  "#0bb", "lm"),
    ("p2_trapenc", "P2-TRENC", 2570+1000, 530,  "#0bb", "mm"),
    # Wealth rows (GC / SS / BP)
    ("p2_wgc",     "P2-GC",    2570+100,  1320, "#b80", "lm"),
    ("p2_wss",     "P2-SS",    2570+100,  1375, "#b80", "lm"),
    ("p2_wbp",     "P2-BP",    2570+100,  1430, "#b80", "lm"),
    # Movement rate columns (use p2_mv_y_* for row Y, p2_mv_10/min/mph for col X)
    ("p2_mv_caut", "P2-CAUT",  2570+1060, 1250, "#080", "lm"),
    ("p2_mv_std",  "P2-STD",   2570+1060, 1310, "#080", "lm"),
    ("p2_mv_run",  "P2-RUN",   2570+1060, 1375, "#080", "lm"),
    ("p2_mv_10",   "P2-MV10",  2570+1260, 1250, "#080", "mm"),
    ("p2_mv_min",  "P2-MVMIN", 2570+1440, 1250, "#080", "mm"),
    ("p2_mv_mph",  "P2-MVMPH", 2570+1580, 1250, "#080", "mm"),
    # Languages
    ("p2_lang1",   "P2-LNG1",  2570+1680, 530,  "#a0a", "lm"),
    ("p2_lang2",   "P2-LNG2",  2570+1680, 595,  "#a0a", "lm"),
    # Background fields
    ("p2_birth",   "P2-BRTH",  2570+480,  1660, "#c44", "lm"),
    ("p2_parent",  "P2-PRNT",  2570+530,  1720, "#c44", "lm"),
    ("p2_family",  "P2-FAM",   2570+510,  1785, "#c44", "lm"),
    ("p2_social",  "P2-SOC",   2570+380,  1870, "#c44", "lm"),
    ("p2_relig",   "P2-REL",   2570+1200, 1870, "#c44", "lm"),
]

R = 10   # marker circle radius (display pixels)


def _load_saved() -> dict:
    """Read calibration_result.py and return {marker_id: (x, y)}."""
    if not os.path.exists(_OUT):
        return {}
    ns = {}
    try:
        with open(_OUT, encoding="utf-8") as f:
            exec(f.read(), ns)
    except Exception:
        return {}

    stat_keys = ["M", "WS", "BS", "S", "T", "W", "I", "A",
                 "Dex", "Ld", "Int", "Cl", "WP", "Fel"]
    sx  = ns.get("_STAT_X", {})
    c   = {}

    def _get(xvar, yvar=None, yfixed=None):
        x = ns.get(xvar)
        y = ns.get(yvar) if yvar else yfixed
        return (x, y) if (x is not None and y is not None) else None

    r1y = ns.get("_R1_Y")
    for mid, var in [("name","_NAME_X"), ("race","_RACE_X"), ("gender","_GENDER_X"),
                     ("cls","_CLASS_X"), ("align","_ALIGN_X")]:
        if var in ns and r1y:
            c[mid] = (ns[var], r1y)

    if "_DESC_X" in ns and "_DESC_Y" in ns:
        c["desc"] = (ns["_DESC_X"], ns["_DESC_Y"])

    r2y = ns.get("_R2_Y")
    for mid, var in [("age","_AGE_X"), ("height","_HEIGHT_X"), ("weight","_WEIGHT_X"),
                     ("hair","_HAIR_X"), ("eyes","_EYES_X")]:
        if var in ns and r2y:
            c[mid] = (ns[var], r2y)

    r3y = ns.get("_R3_Y")
    for mid, var in [("career","_CAREER_X"), ("path","_PATH_X"), ("exits","_EXITS_X")]:
        if var in ns and r3y:
            c[mid] = (ns[var], r3y)

    sy_s = ns.get("_STARTER_Y")
    sy_a = ns.get("_ADVANCE_Y")
    sy_c = ns.get("_CURRENT_Y")
    for k in stat_keys:
        x = sx.get(k)
        if x and sy_s:
            c[f"{k}_s"] = (x, sy_s)
    if sx.get("M") and sy_a:
        c["adv_y"] = (sx["M"], sy_a)
    if sx.get("M") and sy_c:
        c["cur_y"] = (sx["M"], sy_c)

    slx = ns.get("_SKILL_LEFT_X");  srx = ns.get("_SKILL_RIGHT_X")
    sly = ns.get("_SKILL_START_Y"); ssp = ns.get("_SKILL_SPACING", 52)
    if slx and sly:
        c["skl_l"]  = (slx, sly)
        c["skl_l2"] = (slx, sly + ssp)
    if srx and sly:
        c["skl_r"]  = (srx, sly)

    hx = ns.get("_HTH_X"); hy = ns.get("_HTH_START_Y"); hsp = ns.get("_HTH_SPACING", 53)
    if hx and hy:
        c["hth1"] = (hx, hy);  c["hth2"] = (hx, hy + hsp)
    for mid, var in [("hth_imod","_HTH_IMOD_X"), ("hth_dmg","_HTH_DMG_X"),
                     ("hth_parry","_HTH_PARRY_X")]:
        if var in ns and hy:
            c[mid] = (ns[var], hy)

    mx = ns.get("_MIS_X"); my = ns.get("_MIS_START_Y"); msp = ns.get("_MIS_SPACING", 55)
    if mx and my:
        c["mis1"] = (mx, my);  c["mis2"] = (mx, my + msp)
    for mid, var in [("mis_sr","_MIS_SR_X"), ("mis_mr","_MIS_MR_X"), ("mis_lr","_MIS_LR_X"),
                     ("mis_dmg","_MIS_DMG_X"), ("mis_rld","_MIS_RLD_X")]:
        if var in ns and my:
            c[mid] = (ns[var], my)

    ax = ns.get("_ARM_X"); ay = ns.get("_ARM_START_Y"); asp = ns.get("_ARM_SPACING", 53)
    if ax and ay:
        c["arm1"] = (ax, ay);  c["arm2"] = (ax, ay + asp)
    for mid, var in [("arm_loc","_ARM_LOC_X"), ("arm_enc","_ARM_ENC_X")]:
        if var in ns and ay:
            c[mid] = (ns[var], ay)

    for mid, xv, yv in [
        ("av_head",   "_AV_HEAD_X",   "_AV_HEAD_Y"),
        ("av_r_arm",  "_AV_R_ARM_X",  "_AV_R_ARM_Y"),
        ("av_l_arm",  "_AV_L_ARM_X",  "_AV_L_ARM_Y"),
        ("av_body",   "_AV_BODY_X",   "_AV_BODY_Y"),
        ("av_r_leg",  "_AV_R_LEG_X",  "_AV_R_LEG_Y"),
        ("av_l_leg",  "_AV_L_LEG_X",  "_AV_L_LEG_Y"),
        ("av_shield", "_AV_SHIELD_X", "_AV_SHIELD_Y"),
    ]:
        if xv in ns and yv in ns:
            c[mid] = (ns[xv], ns[yv])

    # Page 2 markers: load with offset so display is in spread coords
    _P2_SIMPLE = [
        ("p2_fp",      "_P2_FP_X",      "_P2_FP_Y"),
        ("p2_mag",     "_P2_MAG_X",     "_P2_MAG_Y"),
        ("p2_ip",      "_P2_IP_X",      "_P2_IP_Y"),
        ("p2_xp",      "_P2_XP_X",      "_P2_XP_Y"),
        ("p2_trap1",   "_P2_TRAP_X",    "_P2_TRAP_START_Y"),
        ("p2_traploc", "_P2_TRAP_LOC_X","_P2_TRAP_START_Y"),
        ("p2_trapenc", "_P2_TRAP_ENC_X","_P2_TRAP_START_Y"),
        ("p2_wgc",     "_P2_WGC_X",     "_P2_WGC_Y"),
        ("p2_wss",     "_P2_WSS_X",     "_P2_WSS_Y"),
        ("p2_wbp",     "_P2_WBP_X",     "_P2_WBP_Y"),
        ("p2_mv_caut", "_P2_MV_X",      "_P2_MV_CAUT_Y"),
        ("p2_mv_std",  "_P2_MV_X",      "_P2_MV_STD_Y"),
        ("p2_mv_run",  "_P2_MV_X",      "_P2_MV_RUN_Y"),
        ("p2_mv_10",   "_P2_MV_10_X",   "_P2_MV_CAUT_Y"),
        ("p2_mv_min",  "_P2_MV_MIN_X",  "_P2_MV_CAUT_Y"),
        ("p2_mv_mph",  "_P2_MV_MPH_X",  "_P2_MV_CAUT_Y"),
        ("p2_lang1",   "_P2_LANG_X",    "_P2_LANG_START_Y"),
        ("p2_birth",   "_P2_BIRTH_X",   "_P2_BIRTH_Y"),
        ("p2_parent",  "_P2_PARENT_X",  "_P2_PARENT_Y"),
        ("p2_family",  "_P2_FAMILY_X",  "_P2_FAMILY_Y"),
        ("p2_social",  "_P2_SOCIAL_X",  "_P2_SOCIAL_Y"),
        ("p2_relig",   "_P2_RELIG_X",   "_P2_RELIG_Y"),
    ]
    p2_off = ns.get("_P2_OFFSET", 2570)
    for mid, xv, yv in _P2_SIMPLE:
        xv_val = ns.get(xv)
        yv_val = ns.get(yv)
        if xv_val is not None and yv_val is not None:
            c[mid] = (xv_val + p2_off, yv_val)
    # p2_trap2 (row 2 of trappings)
    trap_sp = ns.get("_P2_TRAP_SPACING", 70)
    trap_y  = ns.get("_P2_TRAP_START_Y")
    trap_x  = ns.get("_P2_TRAP_X")
    if trap_x is not None and trap_y is not None:
        c["p2_trap2"] = (trap_x + p2_off, trap_y + trap_sp)
    # lang2
    lang_sp = ns.get("_P2_LANG_SPACING", 65)
    lang_y  = ns.get("_P2_LANG_START_Y")
    lang_x  = ns.get("_P2_LANG_X")
    if lang_x is not None and lang_y is not None:
        c["p2_lang2"] = (lang_x + p2_off, lang_y + lang_sp)

    return c


class CalibApp:
    def __init__(self, root):
        self.root = root
        root.title("WFRP Sheet Calibrator  —  Drag markers | S=Save | Q=Quit")

        # Load both pages and combine with gap
        p1 = Image.open(_SHEET)
        p2 = Image.open(_SHEET2) if os.path.exists(_SHEET2) else Image.new("RGB", p1.size, (255, 255, 255))
        self.p1_width = p1.size[0]
        W = p1.size[0] + _PAGE_GAP + p2.size[0]
        H = max(p1.size[1], p2.size[1])
        spread = Image.new("RGB", (W, H), (180, 180, 180))  # gray gap
        spread.paste(p1, (0, 0))
        spread.paste(p2, (p1.size[0] + _PAGE_GAP, 0))

        dW = int(W * DISPLAY_SCALE)
        dH = int(H * DISPLAY_SCALE)
        self.scale = DISPLAY_SCALE
        self.tk_img = ImageTk.PhotoImage(spread.resize((dW, dH), Image.LANCZOS))

        # Scrollable canvas
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(frame, width=min(dW, 1400), height=min(dH, 900),
                                scrollregion=(0, 0, dW, dH), bg="gray30")
        sb_v = tk.Scrollbar(frame, orient=tk.VERTICAL,   command=self.canvas.yview)
        sb_h = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        sb_v.pack(side=tk.RIGHT,  fill=tk.Y)
        sb_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Draw background
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        # Status bar
        self.status = tk.StringVar(value="Drag markers to correct positions. S=Save  Q=Quit")
        tk.Label(root, textvariable=self.status, anchor="w", bg="#222", fg="#eee",
                 font=("Consolas", 10)).pack(fill=tk.X)

        # Build markers (use saved coords if available, else defaults)
        self.markers = {}    # id -> {oval, text, x(full), y(full)}
        self._drag  = None   # currently dragged marker id
        saved = _load_saved()
        for mid, label, fx, fy, colour, anchor in MARKERS:
            sx, sy = saved.get(mid, (fx, fy))
            self._create_marker(mid, label, sx, sy, colour)

        # Bindings
        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        root.bind("<s>", lambda e: self._save())
        root.bind("<S>", lambda e: self._save())
        root.bind("<q>", lambda e: root.destroy())
        root.bind("<Q>", lambda e: root.destroy())

        # Mouse-wheel scroll
        self.canvas.bind("<MouseWheel>",        self._scroll_y)
        self.canvas.bind("<Shift-MouseWheel>",  self._scroll_x)

    # ── Marker creation ──────────────────────────────────────────────────────

    def _create_marker(self, mid, label, fx, fy, colour):
        s = self.scale
        dx, dy = fx * s, fy * s
        oval = self.canvas.create_oval(
            dx - R, dy - R, dx + R, dy + R,
            fill=colour, outline="white", width=2, tags=("marker", mid))
        text = self.canvas.create_text(
            dx + R + 3, dy, anchor="w", text=label,
            fill=colour, font=("Arial", 9, "bold"), tags=("marker", mid))
        self.markers[mid] = {"oval": oval, "text": text, "fx": fx, "fy": fy,
                             "colour": colour, "label": label}

    # ── Drag logic ───────────────────────────────────────────────────────────

    def _canvas_coords(self, event):
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

    def _on_press(self, event):
        cx, cy = self._canvas_coords(event)
        best_id, best_d = None, R * 3
        for mid, m in self.markers.items():
            dx = cx - m["fx"] * self.scale
            dy = cy - m["fy"] * self.scale
            d = (dx*dx + dy*dy) ** 0.5
            if d < best_d:
                best_d, best_id = d, mid
        self._drag = best_id

    def _on_drag(self, event):
        if not self._drag:
            return
        cx, cy = self._canvas_coords(event)
        mid = self._drag
        m   = self.markers[mid]
        s   = self.scale
        # Update display position
        self.canvas.coords(m["oval"], cx-R, cy-R, cx+R, cy+R)
        self.canvas.coords(m["text"], cx+R+3, cy)
        # Store full-res coords
        m["fx"] = int(cx / s)
        m["fy"] = int(cy / s)
        self.status.set(
            f"[{mid}]  x={m['fx']}  y={m['fy']}  "
            f"(display {int(cx)},{int(cy)})  —  S=Save  Q=Quit")

    def _on_release(self, event):
        self._drag = None

    # ── Scroll ───────────────────────────────────────────────────────────────

    def _scroll_y(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_x(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Save ─────────────────────────────────────────────────────────────────

    def _save(self):
        m = self.markers
        s = self.scale

        # Collect stat X centres from _s markers
        stat_keys = ["M","WS","BS","S","T","W","I","A","Dex","Ld","Int","Cl","WP","Fel"]
        stat_x = {k: m[f"{k}_s"]["fx"] for k in stat_keys}
        stat_y_starter  = m["M_s"]["fy"]
        stat_y_advance  = m["adv_y"]["fy"]
        stat_y_current  = m["cur_y"]["fy"]

        skill_spacing = m["skl_l2"]["fy"] - m["skl_l"]["fy"]

        lines = [
            "# Auto-generated by calibrate_ui.py",
            "# Copy these values into sheet_image.py",
            "",
            f"_R1_Y       = {m['name']['fy']}",
            f"_NAME_X     = {m['name']['fx']}",
            f"_RACE_X     = {m['race']['fx']}",
            f"_GENDER_X   = {m['gender']['fx']}",
            f"_CLASS_X    = {m['cls']['fx']}",
            f"_ALIGN_X    = {m['align']['fx']}",
            "",
            f"_DESC_X     = {m['desc']['fx']}",
            f"_DESC_Y     = {m['desc']['fy']}",
            "",
            f"_R2_Y       = {m['age']['fy']}",
            f"_AGE_X      = {m['age']['fx']}",
            f"_HEIGHT_X   = {m['height']['fx']}",
            f"_WEIGHT_X   = {m['weight']['fx']}",
            f"_HAIR_X     = {m['hair']['fx']}",
            f"_EYES_X     = {m['eyes']['fx']}",
            "",
            f"_R3_Y       = {m['career']['fy']}",
            f"_CAREER_X   = {m['career']['fx']}",
            f"_PATH_X     = {m['path']['fx']}",
            f"_EXITS_X    = {m['exits']['fx']}",
            "",
            f"_STARTER_Y  = {stat_y_starter}",
            f"_ADVANCE_Y  = {stat_y_advance}",
            f"_CURRENT_Y  = {stat_y_current}",
            "",
            "_STAT_X = {",
        ]
        for k in stat_keys:
            lines.append(f'    "{k}": {stat_x[k]},')
        lines += [
            "}",
            "",
            f"_SKILL_LEFT_X  = {m['skl_l']['fx']}",
            f"_SKILL_RIGHT_X = {m['skl_r']['fx']}",
            f"_SKILL_START_Y = {m['skl_l']['fy']}",
            f"_SKILL_SPACING = {skill_spacing}",
            "",
            f"_HTH_START_Y   = {m['hth1']['fy']}",
            f"_HTH_X         = {m['hth1']['fx']}",
            f"_HTH_SPACING   = {m['hth2']['fy'] - m['hth1']['fy']}",
            f"_HTH_IMOD_X    = {m['hth_imod']['fx']}",
            f"_HTH_DMG_X     = {m['hth_dmg']['fx']}",
            f"_HTH_PARRY_X   = {m['hth_parry']['fx']}",
            "",
            f"_MIS_START_Y   = {m['mis1']['fy']}",
            f"_MIS_X         = {m['mis1']['fx']}",
            f"_MIS_SPACING   = {m['mis2']['fy'] - m['mis1']['fy']}",
            f"_MIS_SR_X      = {m['mis_sr']['fx']}",
            f"_MIS_MR_X      = {m['mis_mr']['fx']}",
            f"_MIS_LR_X      = {m['mis_lr']['fx']}",
            f"_MIS_DMG_X     = {m['mis_dmg']['fx']}",
            f"_MIS_RLD_X     = {m['mis_rld']['fx']}",
            "",
            f"_ARM_START_Y   = {m['arm1']['fy']}",
            f"_ARM_X         = {m['arm1']['fx']}",
            f"_ARM_SPACING   = {m['arm2']['fy'] - m['arm1']['fy']}",
            f"_ARM_LOC_X     = {m['arm_loc']['fx']}",
            f"_ARM_ENC_X     = {m['arm_enc']['fx']}",
            "",
            "# Armour location boxes around avatar figure",
            f"_AV_HEAD_X     = {m['av_head']['fx']}",
            f"_AV_HEAD_Y     = {m['av_head']['fy']}",
            f"_AV_R_ARM_X    = {m['av_r_arm']['fx']}",
            f"_AV_R_ARM_Y    = {m['av_r_arm']['fy']}",
            f"_AV_L_ARM_X    = {m['av_l_arm']['fx']}",
            f"_AV_L_ARM_Y    = {m['av_l_arm']['fy']}",
            f"_AV_BODY_X     = {m['av_body']['fx']}",
            f"_AV_BODY_Y     = {m['av_body']['fy']}",
            f"_AV_R_LEG_X    = {m['av_r_leg']['fx']}",
            f"_AV_R_LEG_Y    = {m['av_r_leg']['fy']}",
            f"_AV_L_LEG_X    = {m['av_l_leg']['fx']}",
            f"_AV_L_LEG_Y    = {m['av_l_leg']['fy']}",
            f"_AV_SHIELD_X   = {m['av_shield']['fx']}",
            f"_AV_SHIELD_Y   = {m['av_shield']['fy']}",
        ]

        # ── Page 2 fields (coords saved relative to page 2 origin) ──────────
        p2_off = self.p1_width + _PAGE_GAP

        def p2x(mid): return m[mid]["fx"] - p2_off
        def p2y(mid): return m[mid]["fy"]

        lines += [
            "",
            "# ── Page 2 ──────────────────────────────────────────────────────",
            f"_P2_OFFSET         = {p2_off}",
            "",
            "# Info boxes (top right)",
            f"_P2_FP_X           = {p2x('p2_fp')}",
            f"_P2_FP_Y           = {p2y('p2_fp')}",
            f"_P2_MAG_X          = {p2x('p2_mag')}",
            f"_P2_MAG_Y          = {p2y('p2_mag')}",
            f"_P2_IP_X           = {p2x('p2_ip')}",
            f"_P2_IP_Y           = {p2y('p2_ip')}",
            f"_P2_XP_X           = {p2x('p2_xp')}",
            f"_P2_XP_Y           = {p2y('p2_xp')}",
            "",
            "# Equipment/Trappings table",
            f"_P2_TRAP_X         = {p2x('p2_trap1')}",
            f"_P2_TRAP_START_Y   = {p2y('p2_trap1')}",
            f"_P2_TRAP_SPACING   = {m['p2_trap2']['fy'] - m['p2_trap1']['fy']}",
            f"_P2_TRAP_LOC_X     = {p2x('p2_traploc')}",
            f"_P2_TRAP_ENC_X     = {p2x('p2_trapenc')}",
            "",
            "# Wealth",
            f"_P2_WGC_X          = {p2x('p2_wgc')}",
            f"_P2_WGC_Y          = {p2y('p2_wgc')}",
            f"_P2_WSS_X          = {p2x('p2_wss')}",
            f"_P2_WSS_Y          = {p2y('p2_wss')}",
            f"_P2_WBP_X          = {p2x('p2_wbp')}",
            f"_P2_WBP_Y          = {p2y('p2_wbp')}",
            "",
            "# Movement rate",
            f"_P2_MV_X           = {p2x('p2_mv_caut')}",
            f"_P2_MV_CAUT_Y      = {p2y('p2_mv_caut')}",
            f"_P2_MV_STD_Y       = {p2y('p2_mv_std')}",
            f"_P2_MV_RUN_Y       = {p2y('p2_mv_run')}",
            f"_P2_MV_10_X        = {p2x('p2_mv_10')}",
            f"_P2_MV_MIN_X       = {p2x('p2_mv_min')}",
            f"_P2_MV_MPH_X       = {p2x('p2_mv_mph')}",
            "",
            "# Languages",
            f"_P2_LANG_X         = {p2x('p2_lang1')}",
            f"_P2_LANG_START_Y   = {p2y('p2_lang1')}",
            f"_P2_LANG_SPACING   = {m['p2_lang2']['fy'] - m['p2_lang1']['fy']}",
            "",
            "# Background",
            f"_P2_BIRTH_X        = {p2x('p2_birth')}",
            f"_P2_BIRTH_Y        = {p2y('p2_birth')}",
            f"_P2_PARENT_X       = {p2x('p2_parent')}",
            f"_P2_PARENT_Y       = {p2y('p2_parent')}",
            f"_P2_FAMILY_X       = {p2x('p2_family')}",
            f"_P2_FAMILY_Y       = {p2y('p2_family')}",
            f"_P2_SOCIAL_X       = {p2x('p2_social')}",
            f"_P2_SOCIAL_Y       = {p2y('p2_social')}",
            f"_P2_RELIG_X        = {p2x('p2_relig')}",
            f"_P2_RELIG_Y        = {p2y('p2_relig')}",
        ]

        with open(_OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        self.status.set(f"✓ Saved to {_OUT}")
        messagebox.showinfo("Lagret", f"Koordinater lagret til:\n{_OUT}")


def main():
    root = tk.Tk()
    app = CalibApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
