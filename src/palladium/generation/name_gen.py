# repo at: https://github.com/not-louis-239/palladium
# Palladium - Pygame terrain and star system generator
# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import random

NAME_PATTERNS = [
    ("prefix", "suffix"),
    ("prefix", "middle", "suffix"),
    ("prefix", "prefix", "suffix"),
]


STAR_PREFIXES = [
    "Al", "Bel", "Cor", "Del", "Eri", "Fal",
    "Gal", "Iri", "Kal", "Lor", "Mar", "Nor",
    "Or", "Vel", "Zar"
]

STAR_MIDDLES = [
    "a", "e", "i", "o", "u",
    "ae", "ia", "eo", "ara", "eri",
    "ora", "una", "yra"
]

STAR_SUFFIXES = [
    "n", "r", "s", "th", "m", "x",
    "on", "is", "ar", "us", "a"
]


def generate_star_name(seed_int: int) -> str:
    inst = random.Random(seed_int)

    pattern = inst.choice(NAME_PATTERNS)

    parts = []

    for part in pattern:
        match part:
            case "prefix":
                parts.append(inst.choice(STAR_PREFIXES))
            case "middle":
                parts.append(inst.choice(STAR_MIDDLES))
            case "suffix":
                parts.append(inst.choice(STAR_SUFFIXES))

    parts.append(f"-{random.randint(100000, 999999)}")

    return "".join(parts).title()
