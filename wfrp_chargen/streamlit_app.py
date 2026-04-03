"""
WFRP 1st Edition – Streamlit Character Generator
Run with:  streamlit run streamlit_app.py
"""

import io
import os
import sys
import tempfile

import streamlit as st
from PIL import Image

# ── Make sure our local packages are importable ──────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from chargen.generator import generate_character
from data.names import random_name
from data.careers import CAREERS
from sheet_image import save_character_spread

# ── Careers organised by class (for the dropdown) ─────────────────────────────
_CAREER_CLASSES = ["Warrior", "Ranger", "Rogue", "Academic"]

def _careers_for_class(cls: str) -> list[str]:
    return sorted(
        name
        for name, data in CAREERS.items()
        if data.get("career_class") == cls
    )

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WFRP 1e Character Generator",
    page_icon="⚔️",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("⚔️ WFRP 1st Edition — Character Generator")
st.caption("Warhammer Fantasy Roleplay · 1st Edition")
st.divider()

# ── Sidebar — character options ───────────────────────────────────────────────
with st.sidebar:
    st.header("Character Options")

    char_type = st.radio("Character type", ["PC", "NPC"], horizontal=True)

    st.subheader("Identity")

    race_options = ["Random", "Human", "Elf", "Dwarf", "Halfling"]
    race_choice  = st.selectbox("Race", race_options)

    gender_options = ["Random", "Male", "Female"]
    gender_choice  = st.selectbox("Gender", gender_options)

    name_input = st.text_input(
        "Name",
        placeholder="Leave blank for random",
        help="A race-appropriate name is suggested if left blank.",
    )

    if char_type == "PC":
        st.subheader("Career")
        class_options = ["Random"] + _CAREER_CLASSES
        class_choice  = st.selectbox("Career class", class_options)

        if class_choice != "Random":
            career_options = ["Random"] + _careers_for_class(class_choice)
        else:
            career_options = ["Random"] + sorted(CAREERS.keys())
        career_choice = st.selectbox("Career", career_options)
    else:
        class_choice  = "Random"
        career_choice = "Random"

    st.divider()
    generate_btn = st.button("🎲 Generate character", type="primary", use_container_width=True)

# ── Generate ──────────────────────────────────────────────────────────────────
if generate_btn:
    with st.spinner("Rolling dice…"):
        import random as _rand

        # Resolve race
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
        else:
            race = race_choice

        # Resolve gender
        gender = None if gender_choice == "Random" else gender_choice

        # Resolve name
        if name_input.strip():
            name = name_input.strip()
        else:
            resolved_gender = gender or _rand.choice(["Male", "Female"])
            name = random_name(race, resolved_gender)
            if gender is None:
                gender = resolved_gender

        # Resolve career options
        career_class  = None if class_choice  == "Random" else class_choice
        career_name   = None if career_choice == "Random" else career_choice

        # Generate character
        char = generate_character(
            race_name=race,
            char_name=name,
            career_class=career_class,
            career_name=career_name,
            gender=gender,
        )
        char.character_type = char_type

        # Render to in-memory image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            save_character_spread(char, tmp_path, pc_mode=(char_type == "PC"))
            img = Image.open(tmp_path)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            buf.seek(0)
        finally:
            os.unlink(tmp_path)

    # Store result in session state so it persists across reruns
    st.session_state["last_char"] = char
    st.session_state["last_img"]  = buf.getvalue()

# ── Display result ────────────────────────────────────────────────────────────
if "last_char" in st.session_state:
    char      = st.session_state["last_char"]
    img_bytes = st.session_state["last_img"]

    # Character summary row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Name",   char.name  or "—")
    col2.metric("Race",   char.race  or "—")
    col3.metric("Career", char.career or "—")
    col4.metric("Type",   char.character_type or "—")

    st.image(img_bytes, use_container_width=True)

    st.download_button(
        label="⬇️ Download sheet (JPG)",
        data=img_bytes,
        file_name=f"{(char.name or 'character').replace(' ', '_')}_sheet.jpg",
        mime="image/jpeg",
    )

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
