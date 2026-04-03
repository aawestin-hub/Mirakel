import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('_career_wiki_data.json', encoding='utf-8') as f:
    data = json.load(f)
for name in ["Wizard's Apprentice", "Initiate", "Mercenary", "Thief",
             "Bodyguard", "Scholar", "Hedge-Wizard's Apprentice"]:
    d = data.get(name, {})
    nz = {k: v for k, v in d.get('scheme', {}).items() if v}
    print(f"=== {name} ===")
    print("  scheme:", nz if nz else "(parse failed)")
    print("  skills:", d.get('skills', []))
    print()
