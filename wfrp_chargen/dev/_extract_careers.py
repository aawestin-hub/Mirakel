"""
Fetch and parse all WFRP 1e starting career data from the wayback archive.
Run from wfrp_chargen directory.
"""
import urllib.request
import re
import json
import time

BASE = "https://web.archive.org/web/20250123094744/https://wfrp1e.fandom.com/wiki/"

STAT_KEYS = ["M","WS","BS","S","T","W","I","A","Dex","Ld","Int","Cl","WP","Fel"]

CAREERS = [
    "Bodyguard","Labourer","Marine","Mercenary","Militiaman","Noble","Outlaw",
    "Pit_Fighter","Protagonist","Seaman","Servant","Soldier","Squire",
    "Troll_Slayer","Tunnel_Fighter","Watchman",
    "Boatman","Bounty_Hunter","Coachman","Farmer","Fisherman","Gamekeeper",
    "Herdsman","Hunter","Miner","Muleskinner","Outrider","Pilot","Prospector",
    "Rat_Catcher","Roadwarden","Runner","Toll-Keeper","Trapper","Woodsman",
    "Agitator","Bawd","Beggar","Entertainer","Footpad","Gambler",
    "Grave_Robber","Jailer","Minstrel","Pedlar","Raconteur","Rustler",
    "Smuggler","Thief","Tomb_Robber",
    "Alchemist%27s_Apprentice","Artisan%27s_Apprentice","Druid","Engineer",
    "Exciseman","Herbalist","Hedge-Wizard%27s_Apprentice","Hypnotist",
    "Initiate","Pharmacist","Physician%27s_Student","Runescribe",
    "Runesmith%27s_Apprentice","Scholar","Scribe","Seer","Student","Trader",
    "Wizard%27s_Apprentice","Wood_Elf_Mage%27s_Apprentice",
]

def parse_career(html: str, name: str) -> dict:
    # --- Advance scheme ---
    scheme = {k: 0 for k in STAT_KEYS}
    tbl_m = re.search(r'<tbody>(.*?)</tbody>', html, re.DOTALL)
    if tbl_m:
        cells = re.findall(r'<td[^>]*>\s*<p[^>]*><span[^>]*>(.*?)</span></p>', tbl_m.group(1), re.DOTALL)
        # normalise nbsp
        cells = [c.replace('\u00a0','').strip() for c in cells]
        # first 14 cells are the data row (after 14 header cells)
        data_cells = cells[:14] if len(cells) >= 14 else cells
        for i, val in enumerate(data_cells):
            if i < len(STAT_KEYS):
                val = val.strip()
                if val.startswith('+'):
                    try:
                        scheme[STAT_KEYS[i]] = int(val[1:])
                    except ValueError:
                        pass

    # --- Skills ---
    skills = []
    # find the Skills section
    skills_m = re.search(r'<b>Skills</b>.*?<ul>(.*?)</ul>', html, re.DOTALL)
    if not skills_m:
        skills_m = re.search(r'Skills.*?<ul>(.*?)</ul>', html, re.DOTALL)
    if skills_m:
        items = re.findall(r'<li>(.*?)</li>', skills_m.group(1), re.DOTALL)
        for item in items:
            # Strip HTML tags
            text = re.sub(r'<[^>]+>', '', item).strip()
            text = text.replace('\u00a0', ' ').strip()
            if text:
                skills.append(text)

    # --- Trappings ---
    trappings = []
    trap_m = re.search(r'<b>Trappings</b>.*?<ul>(.*?)</ul>', html, re.DOTALL)
    if not trap_m:
        trap_m = re.search(r'Trappings.*?<ul>(.*?)</ul>', html, re.DOTALL)
    if trap_m:
        items = re.findall(r'<li>(.*?)</li>', trap_m.group(1), re.DOTALL)
        for item in items:
            text = re.sub(r'<[^>]+>', '', item).strip().replace('\u00a0',' ').strip()
            if text:
                trappings.append(text)

    # --- Career exits ---
    exits = []
    exits_m = re.search(r'Career Exits.*?<ul>(.*?)</ul>', html, re.DOTALL)
    if exits_m:
        items = re.findall(r'<li>(.*?)</li>', exits_m.group(1), re.DOTALL)
        for item in items:
            text = re.sub(r'<[^>]+>', '', item).strip().replace('\u00a0',' ').strip()
            if text:
                exits.append(text)

    return {"scheme": scheme, "skills": skills, "trappings": trappings, "exits": exits}


results = {}
headers = {"User-Agent": "Mozilla/5.0 (compatible; career-extractor/1.0)"}

for career_slug in CAREERS:
    url = BASE + career_slug
    display = career_slug.replace('%27', "'").replace('_', ' ')
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        data = parse_career(html, display)
        results[display] = data
        non_zero = {k: v for k, v in data['scheme'].items() if v != 0}
        print(f"OK  {display}: scheme={non_zero}, skills={len(data['skills'])}, trappings={len(data['trappings'])}")
    except Exception as e:
        print(f"ERR {display}: {e}")
    time.sleep(0.5)  # be nice to archive.org

# Save results
with open("_career_wiki_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(results)} careers to _career_wiki_data.json")
