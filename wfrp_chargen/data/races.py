"""
Race definitions for WFRP 1st Edition.

Each race entry contains:
  stat_bases  – base value added to each 2d10 characteristic roll
                (WS, BS, I, Dex, Ld, Int, Cl, WP, Fel)
  s_mod       – modifier added to the D3 roll for Strength  (S = D3 + s_mod)
  t_mod       – modifier added to the D3 roll for Toughness (T = D3 + t_mod)
  w_mod       – modifier added to the D3 roll for Wounds    (W = D3 + w_mod)
  m_die       – die size for Movement roll (2 or 3)
  m_mod       – modifier added to the Movement die          (M = 1dX + m_mod)
  fate_die    – die size for Fate Points roll
  fate_mod    – modifier added to the Fate Points roll (min result 1)

Sources: wfrp1e.fandom.com character creation table (via web.archive.org).
"""

RACES: dict[str, dict] = {
    "Human": {
        # Percentile stat bases (rolled as 2d10 + base)
        "stat_bases": {
            "WS": 20, "BS": 20, "I": 20,
            "Dex": 20, "Ld": 20, "Int": 20, "Cl": 20, "WP": 20, "Fel": 20,
        },
        # S = D3+1  →  range 2–4 ;  T = D3+1  →  range 2–4
        "s_mod": 1,
        "t_mod": 1,
        # W = D3+4  →  range 5–7
        "w_mod": 4,
        # M = D3+2  →  range 3–5
        "m_die": 3,
        "m_mod": 2,
        # FP = D3+1  →  range 2–4
        "fate_die": 3,
        "fate_mod": 1,
    },

    "Elf": {
        "stat_bases": {
            "WS": 30, "BS": 20, "I": 50,
            "Dex": 30, "Ld": 30, "Int": 40, "Cl": 40, "WP": 30, "Fel": 30,
        },
        # S = D3+1  →  2–4 ;  T = D3+1  →  2–4
        "s_mod": 1,
        "t_mod": 1,
        # W = D3+3  →  range 4–6
        "w_mod": 3,
        # M = D3+2  →  range 3–5
        "m_die": 3,
        "m_mod": 2,
        # FP = D3–1  (min 1)  →  range 1–2
        "fate_die": 3,
        "fate_mod": -1,
    },

    "Dwarf": {
        "stat_bases": {
            "WS": 30, "BS": 10, "I": 10,
            "Dex": 10, "Ld": 40, "Int": 20, "Cl": 40, "WP": 40, "Fel": 10,
        },
        # S = D3+1  →  2–4 ;  T = D3+2  →  3–5
        "s_mod": 1,
        "t_mod": 2,
        # W = D3+5  →  range 6–8
        "w_mod": 5,
        # M = D2+2  →  range 3–4
        "m_die": 2,
        "m_mod": 2,
        # FP = D3  →  range 1–3
        "fate_die": 3,
        "fate_mod": 0,
    },

    "Halfling": {
        "stat_bases": {
            "WS": 10, "BS": 20, "I": 40,
            "Dex": 30, "Ld": 10, "Int": 20, "Cl": 10, "WP": 30, "Fel": 30,
        },
        # S = D3  →  1–3 ;  T = D3  →  1–3
        "s_mod": 0,
        "t_mod": 0,
        # W = D3+3  →  range 4–6
        "w_mod": 3,
        # M = D2+2  →  range 3–4
        "m_die": 2,
        "m_mod": 2,
        # FP = D4  →  range 1–4
        "fate_die": 4,
        "fate_mod": 0,
    },
}
