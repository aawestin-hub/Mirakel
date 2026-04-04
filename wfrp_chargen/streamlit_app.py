"""
WFRP 1st Edition – Streamlit Character Generator
Run with:  streamlit run streamlit_app.py
"""

import io
import os
import sys
import tempfile
import traceback

import streamlit as st
from PIL import Image

# ── Make sure our local packages are importable ──────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from chargen.generator import generate_character
from data.names import random_name
from data.careers import CAREERS, CAREER_CLASS_TABLES

# Lazy import – may not be needed if we hit an error early
def _save_spread(char, path, pc_mode, template):
    from sheet_image import save_character_spread
    return save_character_spread(char, path, pc_mode=pc_mode, template=template)

# ── Careers organised by class (for the dropdown) ─────────────────────────────
_CAREER_CLASSES = ["Warrior", "Ranger", "Rogue", "Academic"]

def _careers_for_class(cls: str) -> list[str]:
    careers: set[str] = set()
    for race_list in CAREER_CLASS_TABLES.get(cls, {}).values():
        for _, _, name in race_list:
            careers.add(name)
    return sorted(careers)

def _advanced_careers() -> list[str]:
    basic = {
        name
        for race_tbl in CAREER_CLASS_TABLES.values()
        for r_list in race_tbl.values()
        for _, _, name in r_list
    }
    return sorted(name for name in CAREERS if name not in basic)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WFRP 1e Character Generator",
    page_icon="⚔️",
    layout="wide",
)

# ── CSS tweaks ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English&display=swap');
[data-testid="stMetricValue"] { font-size: 1.1rem; }
h1, h2, h3, .stTitle > *, [data-testid="stHeadingWithActionElements"] h1 {
    font-family: 'IM Fell English', Georgia, serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("⚔️ WFRP 1st Edition — Character Generator")
st.caption("Warhammer Fantasy Roleplay · 1st Edition · Automatically generates stats, skills, trappings, spells and background narrative")
st.divider()

# ── Sidebar — character options ───────────────────────────────────────────────
with st.sidebar:
    st.header("Character Options")

    char_type = st.radio("Character type", ["PC", "NPC"], horizontal=True,
                         help="PC: leaves advance scheme blank for player. NPC: auto-fills advances.")

    st.subheader("Sheet template")
    template_choice = st.radio(
        "Sheet style",
        ["Weskon's Fantasy Roleplay", "Classic Edited Sheet"],
        help="Weskon's sheet has more room for details. Classic is the original 1e layout.",
    )
    template_key = "weskon" if template_choice == "Weskon's Fantasy Roleplay" else "classic"

    st.subheader("Identity")

    race_options = ["Random", "Human", "Elf", "Dwarf", "Halfling"]
    race_choice  = st.selectbox("Race", race_options)

    gender_options = ["Random", "Male", "Female"]
    gender_choice  = st.selectbox("Gender", gender_options)

    name_input = st.text_input(
        "Name",
        placeholder="Leave blank for random",
        help="A race-appropriate name is generated if left blank.",
    )

    if char_type == "PC":
        st.subheader("Career")
        class_options = ["Random"] + _CAREER_CLASSES
        class_choice  = st.selectbox("Career class", class_options,
                                     help="Warrior / Ranger / Rogue / Academic — or Random.")

        if class_choice != "Random":
            career_options = ["Random"] + _careers_for_class(class_choice)
        else:
            career_options = ["Random"] + sorted(CAREERS.keys())
        career_choice = st.selectbox("Career", career_options)
    else:
        st.subheader("Career (NPC)")
        st.caption("NPCs have no prerequisites — any career is available.")
        npc_class_options = ["Random"] + _CAREER_CLASSES + ["Advanced careers"]
        class_choice = st.selectbox("Career class", npc_class_options)

        if class_choice == "Random":
            career_options = ["Random"] + sorted(CAREERS.keys())
        elif class_choice == "Advanced careers":
            career_options = ["Random"] + _advanced_careers()
        else:
            career_options = ["Random"] + _careers_for_class(class_choice)
        career_choice = st.selectbox("Career", career_options)

    st.divider()
    generate_btn = st.button("🎲 Generate character", type="primary", use_container_width=True)

# ── Generate ──────────────────────────────────────────────────────────────────
if generate_btn:
    import random as _rand

    with st.spinner("Rolling dice and filling the sheet…"):
        try:
            gen_log = []   # list of (label, value) strings for the generation log

            # Resolve race
            race_was_rolled = False
            if race_choice == "Random":
                roll = _rand.randint(1, 100)
                if roll <= 90:
                    race = "Human"
                elif roll <= 95:
                    race = "Elf"
                elif roll <= 98:
                    race = "Dwarf"
                else:
                    race = "Halfling"
                race_was_rolled = True
                gen_log.append(("Race roll", f"d100={roll} → **{race}**"))
            else:
                race = race_choice
                gen_log.append(("Race", race))

            # Resolve gender
            gender = None if gender_choice == "Random" else gender_choice
            gender_was_rolled = False

            # Resolve name
            if name_input.strip():
                name = name_input.strip()
                gen_log.append(("Name", name + " (custom)"))
            else:
                resolved_gender = gender or _rand.choice(["Male", "Female"])
                used_names = st.session_state.get("used_names", set())
                name = random_name(race, resolved_gender, exclude=used_names)
                if gender is None:
                    gender = resolved_gender
                    gender_was_rolled = True
                    gen_log.append(("Gender roll", f"→ **{gender}**"))
                gen_log.append(("Name", name + " (random)"))

            # Resolve career options
            career_class = None if class_choice in ("Random", "Advanced careers") else class_choice
            career_class_was_rolled = career_class is None
            career_name  = None if career_choice == "Random" else career_choice

            # Generate character
            char = generate_character(
                race_name=race,
                char_name=name,
                career_class=career_class,
                career_name=career_name,
                gender=gender,
                npc_mode=(char_type == "NPC"),
            )
            char.character_type = char_type
            char._gender_was_rolled     = gender_was_rolled
            char._race_was_rolled       = race_was_rolled
            char._class_was_rolled      = career_class_was_rolled
            char._career_was_rolled     = (career_choice == "Random")

            # Log career class and career
            if career_class_was_rolled:
                gen_log.append(("Career class roll", f"→ **{char.career_class}**"))
            else:
                gen_log.append(("Career class", char.career_class or career_class))
            if career_choice == "Random":
                gen_log.append(("Career roll", f"→ **{char.career}**"))
            else:
                gen_log.append(("Career", char.career))

            # Log key character facts
            gen_log.append(("Alignment", char.alignment or "—"))
            gen_log.append(("Star sign", getattr(char, "star_sign", "—") or "—"))
            gen_log.append(("Place of birth", getattr(char, "place_of_birth", "—") or "—"))
            gen_log.append(("Religion", getattr(char, "religion", "—") or "—"))
            starter = f"WS {char.WS}  BS {char.BS}  S {char.S}  T {char.T}  W {char.W}  I {char.I}  A {char.A}  Dex {char.Dex}  Ld {char.Ld}  Int {char.Int}  Cl {char.Cl}  WP {char.WP}  Fel {char.Fel}"
            gen_log.append(("Starter stats", starter))
            wealth_parts = []
            if getattr(char, "wealth_gc", 0): wealth_parts.append(f"{char.wealth_gc} GC")
            if getattr(char, "wealth_ss", 0): wealth_parts.append(f"{char.wealth_ss} SS")
            if getattr(char, "wealth_bp", 0): wealth_parts.append(f"{char.wealth_bp} BP")
            gen_log.append(("Starting wealth", ", ".join(wealth_parts) if wealth_parts else "none"))

            # Render to in-memory image
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                _save_spread(char, tmp_path, pc_mode=(char_type == "PC"), template=template_key)
                img = Image.open(tmp_path)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=95)
                buf.seek(0)
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

            # Store in session state
            st.session_state["last_char"]    = char
            st.session_state["last_img"]     = buf.getvalue()
            st.session_state["gen_error"]    = None
            st.session_state["gen_log"]      = gen_log
            # Track used names to avoid repeats within a session
            used = st.session_state.get("used_names", set())
            used.add(char.name)
            st.session_state["used_names"] = used

        except Exception as exc:
            st.session_state["gen_error"] = traceback.format_exc()
            st.error(f"⚠️ Error generating character: {exc}")

# Show error details if any
if st.session_state.get("gen_error"):
    with st.expander("🐛 Error details (click to expand)", expanded=False):
        st.code(st.session_state["gen_error"])

# ── Display result ────────────────────────────────────────────────────────────
if "last_char" in st.session_state and st.session_state.get("gen_error") is None:
    char      = st.session_state["last_char"]
    img_bytes = st.session_state["last_img"]

    # Character summary row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Name",   char.name  or "—")
    race_label = (char.race or "—") + (" 🎲" if getattr(char, "_race_was_rolled", False) else "")
    col2.metric("Race",   race_label)
    career_label = (char.career or "—") + (" 🎲" if getattr(char, "_career_was_rolled", False) else "")
    col3.metric("Career", career_label)
    gender_label = char.gender or "—"
    if getattr(char, "_gender_was_rolled", False):
        gender_label += " 🎲"
    col4.metric("Gender", gender_label)
    class_label = (getattr(char, "career_class", None) or "—") + (" 🎲" if getattr(char, "_class_was_rolled", False) else "")
    col5.metric("Class",  class_label)

    st.image(img_bytes, use_container_width=True)

    st.download_button(
        label="⬇️ Download sheet (JPG)",
        data=img_bytes,
        file_name=f"{(char.name or 'character').replace(' ', '_')}_sheet.jpg",
        mime="image/jpeg",
    )

    # Generation log
    gen_log = st.session_state.get("gen_log", [])
    if gen_log:
        with st.expander("🎲 Generation log — see what was rolled", expanded=False):
            for label, value in gen_log:
                st.markdown(f"**{label}:** {value}")

    # Expandable stat block
    with st.expander("📊 Stats & details", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Primary stats**")
            primary = ["WS", "BS", "S", "T", "I", "Dex", "Ld", "Int", "Cl", "WP", "Fel"]
            for stat in primary:
                val = getattr(char, stat, None)
                if val is not None:
                    st.text(f"  {stat:>4} : {val}")
        with c2:
            st.markdown("**Secondary stats**")
            secondary = ["A", "W", "SB", "TB", "M", "Mag", "IP", "FP"]
            for stat in secondary:
                val = getattr(char, stat, None)
                if val is not None:
                    st.text(f"  {stat:>4} : {val}")

        if char.skills:
            st.markdown("**Skills**")
            st.write(", ".join(char.skills))

        if char.trappings:
            st.markdown("**Trappings**")
            st.write(", ".join(char.trappings))

        if char.spells:
            st.markdown("**Spells**")
            st.write(", ".join(char.spells))

        bg = getattr(char, "background_narrative", None)
        if bg:
            st.markdown("**Background**")
            st.write(bg)

