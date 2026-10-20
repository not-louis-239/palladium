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


from dataclasses import dataclass
from typing import Callable

from palladium.generation.biomes import BiomeID

import numpy as np


type BiomeCondition = Callable[
    # height, temperature, humidity, geology
    [np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    # truth mask
    np.ndarray,
]


# The universal condition
all_remaining: BiomeCondition = lambda h, t, hum, g: np.ones(h.shape, dtype=bool)


## Descriptors


# Height
H_MOUNTAINS = 4_000
H_HIGHLANDS = 2_500
H_ELEVATED = 1_000
H_LAND = 50
H_COASTAL = 0
H_SHALLOW = -1_200
H_DEEP = -3_200


# Temperature (°C)
T_NITROGEN_MELTING_PT = -210
T_METHANE_MELTING_PT = -182
T_C02_MELTING_PT = -80
T_CRYO = -100
T_PERMAFROST = -50
T_POLAR = -20
T_ARCTIC = -13
T_SUBARCTIC = -7
T_FREEZING = 0
T_VERY_COLD = 5
T_COLD = 10
T_COOL = 15
T_ROOM = 20
T_LUKEWARM = 25
T_WARM = 30
T_VERY_WARM = 35
T_HOT = 40
T_VERY_HOT = 50
T_SCORCHING = 75
T_VOLCANIC = 100
T_SUPERHEATED = 250


# Humidity
HUM_EXTREMELY_HUMID = 0.92
HUM_VERY_HUMID = 0.85
HUM_HUMID = 0.76
HUM_SLIGHTLY_HUMID = 0.68
HUM_SLIGHTLY_DRY = 0.55
HUM_DRY = 0.46
HUM_VERY_DRY = 0.3
HUM_EXTREMELY_DRY = 0.15


# Geology
G_ALTERNATE = 0.5
G_RARE = 0.75
G_SUPER_RARE = 0.92

def alternate(g: np.ndarray) -> np.ndarray:
    return g >= G_ALTERNATE

def rare(g: np.ndarray) -> np.ndarray:
    return g >= G_RARE

def super_rare(g: np.ndarray) -> np.ndarray:
    return g >= G_SUPER_RARE

# Composite descriptors
def boreal(t: np.ndarray, hum: np.ndarray) -> np.ndarray:
    return (
        ((t <= 10) & (hum >= 0.46))
        | ((t <= 15) & (hum >= 0.62))
    )

def frozen(t: np.ndarray, hum: np.ndarray) -> np.ndarray:
    return (
        (t <= -20)
        | ((t <= -15) & (hum >= 0.25))
        | ((t <= -10) & (hum >= 0.68))
    )
