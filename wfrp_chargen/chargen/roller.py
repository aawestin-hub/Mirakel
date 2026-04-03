"""
Dice-rolling utilities for WFRP 1st Edition.
All functions are pure (no side effects) and return integers.
"""

import random


def roll_dice(num: int, sides: int) -> int:
    """Roll num dice each with the given number of sides and return the sum."""
    return sum(random.randint(1, sides) for _ in range(num))


def roll_d3() -> int:
    """Roll a D3 (1–3). Used for S, T, W, and M in 1st Edition."""
    return random.randint(1, 3)


def roll_d100() -> int:
    """Roll percentile dice (1–100)."""
    return random.randint(1, 100)


def roll_stat(base: int) -> int:
    """Roll a percentile characteristic: 2d10 + base value."""
    return roll_dice(2, 10) + base


def roll_small_stat(mod: int) -> int:
    """
    Roll a small-scale characteristic (Strength or Toughness).
    1st Edition formula: D3 + racial modifier, minimum 1.
    The result IS the Strength/Toughness Bonus directly (no division).
    """
    return max(1, roll_d3() + mod)


def roll_direct(die_sides: int, mod: int, min_val: int = 1) -> int:
    """
    Roll 1dX + modifier with a floor.
    Used for Wounds (D3+mod), Movement (D2 or D3 + mod), and Fate Points.
    """
    return max(min_val, random.randint(1, die_sides) + mod)
