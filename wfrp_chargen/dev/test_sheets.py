"""Quick test to generate sample sheets for visual inspection."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chargen.generator import generate_character
from sheet_classic import save_classic_spread

tests = [
    ('Human', 'Mercenary', False, 'output/test_merc_pc.jpg'),
    ('Human', 'Initiate', False, 'output/test_initiate_pc.jpg'),
    ('Human', 'Assassin', True, 'output/test_assassin_npc.jpg'),
    ('Human', 'Troll Slayer', False, 'output/test_troll_pc.jpg'),
    ('Dwarf', 'Troll Slayer', True, 'output/test_troll_npc_dwarf.jpg'),
    ('Elf', 'Scout', True, 'output/test_scout_npc_elf.jpg'),
]

for race, career, npc, path in tests:
    c = generate_character(race, career_name=career, npc_mode=npc)
    save_classic_spread(c, path, pc_mode=not npc)
    sp = getattr(c, 'spells', [])
    adv_ws = c.advance_scheme.get('WS', '?')
    print(f"{'[NPC]' if npc else '[PC] '} {race} {career}: WS={c.WS} adv_WS={adv_ws} spells={len(sp)}")

print("ALL DONE")
