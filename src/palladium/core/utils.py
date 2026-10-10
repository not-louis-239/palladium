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
from itertools import pairwise

from palladium.core.custom_types import Colour


def _str_to_terrain_seed(s: str) -> int:
    """Hashes a string to a 64-bit signed integer, wrapping to -2^63 to 2^63-1.
    Used to generate the master terrain seed for a given string."""
    h = int(hashlib.sha256(s.encode()).hexdigest(), 16)
    return (h % (2**64)) - 2**63


def random_seed() -> int:
    return random.randint(-2**63, 2**63 - 1)


def str_to_seed(s: str) -> int:
    """Normalises input by case and leading or trailing whitespace,
    then attempts to convert the input directly to an integer seed.
    If that fails, it hashes the string to an integer seed.
    Then returns the seed."""
    s = s.strip().lower()
    try:
        return int(s)
    except ValueError:
        return _str_to_terrain_seed(s)


def clamp(val: float, lower: float, upper: float) -> float:
    return max(min(val, upper), lower)


def lerp_colours(c1: Colour, c2: Colour, t: float) -> Colour:
    t = clamp(t, 0, 1)
    return tuple(
        int(c1[x] + t * (c2[x] - c1[x])) for x in range(len(c1))  # type: ignore
    )


def lerp_gradient(val: float, grad: dict[float, Colour]) -> Colour:
    """Returns a Colour determined by the anchor points in `grad`.
    If val < grad[0], returns the first anchor.
    If val > grad[-1], returns the last colour."""

    if not grad:
        raise ValueError("grad requires at least one value-colour pair")

    keys = sorted(grad)
    if val <= keys[0]:
        return grad[keys[0]]
    if val >= keys[-1]:
        return grad[keys[-1]]

    for k1, k2 in pairwise(keys):
        if k1 <= val <= k2:
            t = (val - k1) / (k2 - k1)
            c1, c2 = grad[k1], grad[k2]
            return lerp_colours(c1, c2, t)

    return grad[keys[-1]]
