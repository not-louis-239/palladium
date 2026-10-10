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


from enum import IntEnum

import pygame as pg

from palladium.core.custom_types import Colour


class Controls(IntEnum):
    SEED_MINUS_ONE = pg.K_j
    SEED_PLUS_ONE = pg.K_l


WN_W, WN_H = 1280, 720


# blackbody colours in terms of {°K: tuple[int, int, int]}
KELVIN_COLOURS: dict[float, Colour] = {
    400.0: (0, 0, 0),
    800.0: (70, 0, 0),
    1000.0: (255, 56, 0),
    2000.0: (255, 137, 18),
    4000.0: (255, 209, 163),
    6000.0: (255, 255, 255),
    10000.0: (201, 226, 255),
    20000.0: (162, 198, 255),
    40000.0: (143, 184, 255),
}
