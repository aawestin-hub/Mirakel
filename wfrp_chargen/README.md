# WFRP 1st Edition – Character Generator

A terminal-based character generator for **Warhammer Fantasy Roleplay (1st Edition, 1986)**, written in Python 3.10+.

## Requirements

- Python 3.10 or newer (no third-party packages needed)

## Running

```bash
cd wfrp_chargen
python main.py
```

The generator will ask you to choose a race (or press Enter to roll randomly), optionally name the character, then print a full character sheet.

## Project Structure

```
wfrp_chargen/
├── main.py              # Entry point – interactive CLI
├── display.py           # Character sheet formatting
├── data/
│   ├── races.py         # Race stat bases, secondary stats, wounds & fate formulas
│   ├── careers.py       # d100 career tables per race + full career definitions
│   └── skills.py        # Skill reference dictionary
└── chargen/
    ├── character.py     # Character dataclass
    ├── roller.py        # Dice-rolling utilities (pure functions)
    └── generator.py     # Generation logic: rolls stats, career, wounds, fate points
```

## Races

| Race      | Key traits                                    | M | Fate dice |
|-----------|-----------------------------------------------|---|-----------|
| Human     | Balanced, all stats +20 base                 | 4 | 1d3       |
| Dwarf     | Tough & dexterous, low Fellowship/Initiative  | 3 | 1d3−1     |
| Elf       | Lightning-fast Initiative, fragile            | 5 | 1d3       |
| Halfling  | Agile, lucky, and very strong-willed          | 4 | 1d3+1     |

## Starting Wounds formula

> **W = SB + TB + bonus roll**

| Race     | Bonus roll |
|----------|------------|
| Human    | 1d6        |
| Dwarf    | 1d8        |
| Elf      | 1d4        |
| Halfling | 1d4        |

## Careers

Each race has 10 starting careers on a d100 table.  
Human careers include: Agitator, Bawd, Bodyguard, Boatman, Charlatan, Entertainer, Estalian Diestro, Footpad, Herbalist, Hunter, Initiate, Labourer, Marine, Militiaman, Minstrel, Peasant, Pedlar, Pit Fighter, Soldier, Thief.

> **Note:** The Estalian Diestro requires Initiative ≥ 30 and will be re-rolled automatically if the character does not qualify.

## Extending

- Add or correct careers in `data/careers.py`
- Adjust racial stat bases in `data/races.py`
- Add new races by following the same dict structure in both files
