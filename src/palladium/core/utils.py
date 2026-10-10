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


import hashlib
import random
from typing import Callable, Any


def _str_to_terrain_seed(s: str) -> int:
    """Hashes a string to a 64-bit signed integer, wrapping to -2^63 to 2^63-1.
    Used to generate the master terrain seed for a given string."""
    h = int(hashlib.sha256(s.encode()).hexdigest(), 16)
    return (h % (2**64)) - 2**63


def random_seed() -> int:
    return random.randint(-2**63, 2**63 - 1)


def str_to_seed(s: str) -> tuple[int, bool]:
    """Normalises input by case and leading or trailing whitespace,
    then attempts to convert the input directly to an integer seed.
    If that fails, it hashes the string to an integer seed.
    Then returns (seed, was_modified)."""
    s = s.strip().lower()
    try:
        return int(s), False
    except ValueError:
        return _str_to_terrain_seed(s), True


def clamp(val: float, lower: float, upper: float) -> float:
    return max(min(val, upper), lower)


def safe_convert[T](val, typ: Callable[[Any], T]) -> T | None:
    try:
        return typ(val)
    except TypeError, ValueError:
        return None
