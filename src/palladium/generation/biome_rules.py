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


@dataclass
class BiomeRule:
    biome_id: BiomeID
    condition: Callable[
        # height, temperature, humidity
        [np.ndarray, np.ndarray, np.ndarray],
        # truth mask
        np.ndarray,
    ]


BIOME_RULES: list[BiomeRule] = [
    # Superheated biomes
    BiomeRule(
        BiomeID.PYRO,
        lambda h, t, hum: t >= 2_500,
    ),
    BiomeRule(
        BiomeID.LAVA,
        lambda h, t, hum: t >= 800,
    ),
    BiomeRule(
        BiomeID.MAGMA,
        lambda h, t, hum: t >= 250,
    ),

    # Hot land biomes
    BiomeRule(
        BiomeID.VOLCANO,
        lambda h, t, hum:
            (t >= 95) & (h >= 2_000),
    ),

    # Water biomes
    BiomeRule(
        BiomeID.FROZEN_OCEAN,
        lambda h, t, hum:
            (h <= -500) & (t <= -5),
    ),
    BiomeRule(
        BiomeID.ABYSS,
        lambda h, t, hum:
            (h <= -500)
            & (
                ((t <= 5) & (h <= -1_000))
                | ((t <= 25) & (h <= -3_000))
            ),
    ),
    BiomeRule(
        BiomeID.OCEAN,
        lambda h, t, hum:
            (h <= -500)
            & (
                (t <= 35)
                | ((t <= 40) & (h <= -1_000))
                | ((t <= 45) & (h <= -3_000))
            ),
    ),
    BiomeRule(
        BiomeID.TROPICAL_OCEAN,
        lambda h, t, hum:
            (h <= -500)
            & (
                (t <= 50)
                | ((t <= 55) & (h <= -1_000))
            ),
    ),
    BiomeRule(
        BiomeID.SULPHUR,
        lambda h, t, hum: h <= -500,
    ),

    # Shallow water
    BiomeRule(
        BiomeID.FROZEN_COAST,
        lambda h, t, hum:
            (h > -500) & (h <= -50)
            & (
                (t <= -5)
                | ((t <= 0) & (h >= -100))
            ),
    ),
    BiomeRule(
        BiomeID.COLD_SEA,
        lambda h, t, hum:
            (h > -500) & (h <= -50) & (t <= 15),
    ),
    BiomeRule(
        BiomeID.WARM_SEA,
        lambda h, t, hum:
            (h > -500) & (h <= -50) & (t <= 35),
    ),
    BiomeRule(
        BiomeID.REEF,
        lambda h, t, hum:
            (h > -500) & (h <= -50) & (t <= 50),
    ),
    BiomeRule(
        BiomeID.SULPHUR_COAST,
        lambda h, t, hum:
            (h > -500) & (h <= -50),
    ),

    # Shore
    BiomeRule(
        BiomeID.SNOWY_BEACH,
        lambda h, t, hum:
            (h > -50) & (h < 0) & (t <= 0),
    ),
    BiomeRule(
        BiomeID.STONY_SHORE,
        lambda h, t, hum:
            (h > -50) & (h < 0) & (t <= 15),
    ),
    BiomeRule(
        BiomeID.BEACH,
        lambda h, t, hum:
            (h > -50) & (h < 0) & (t <= 35),
    ),
    BiomeRule(
        BiomeID.TROPICAL_BEACH,
        lambda h, t, hum:
            (h > -50) & (h < 0) & (t <= 50),
    ),
    BiomeRule(
        BiomeID.VOLCANIC_BEACH,
        lambda h, t, hum:
            (h > -50) & (h < 0),
    ),

    # Super cold biomes
    BiomeRule(
        BiomeID.FROZEN_PEAKS,
        lambda h, t, hum:
            (
                (t <= -20)
                | ((t <= -15) & (hum >= 0.25))
                | ((t <= -10) & (hum >= 0.68))
            )
            & (h >= 4_000),
    ),
    BiomeRule(
        BiomeID.FROZEN_PLAINS,
        lambda h, t, hum:
            (
                (t <= -20)
                | ((t <= -15) & (hum >= 0.25))
                | ((t <= -10) & (hum >= 0.68))
            ),
    ),

    # Salt flats
    BiomeRule(
        BiomeID.SALT_FLATS,
        lambda h, t, hum:
            (hum <= 0.08)
            | ((hum <= 0.15) & (t >= 70)),
    ),

    # Geyser
    BiomeRule(
        BiomeID.GEYSER,
        lambda h, t, hum:
            ((t >= 100) & (hum >= 0.75))
            | ((t >= 95) & (hum >= 0.82)),
    ),

    # Asphalt
    BiomeRule(
        BiomeID.ASPHALT,
        lambda h, t, hum:
            (
                (t >= 90)
                & (hum >= 0.55)
                & (hum <= 0.75)
            )
            |
            (
                (t >= 85)
                & (hum >= 0.55)
                & (hum <= 0.68)
            ),
    ),

    # Hot desert / hot spring
    BiomeRule(
        BiomeID.HOT_SPRING,
        lambda h, t, hum:
            (t >= 50) & (hum >= 0.68),
    ),
    BiomeRule(
        BiomeID.HOT_DESERT,
        lambda h, t, hum:
            t >= 50
            | ((t >= 45) & (hum <= 0.48))
            | ((t >= 40) & (hum <= 0.24))
            | ((t >= 30) & (hum <= 0.16))
    ),

    # Desert / cold desert
    BiomeRule(
        BiomeID.ALPINE,
        lambda h, t, hum:
            (hum <= 0.32)
            & (h >= 3_000)
            & (t <= 20),
    ),
    BiomeRule(
        BiomeID.DESERT,
        lambda h, t, hum:
            (hum <= 0.32) & (t >= 10),
    ),
    BiomeRule(
        BiomeID.COLD_DESERT,
        lambda h, t, hum:
            hum <= 0.32,
    ),

    # Swamp
    BiomeRule(
        BiomeID.SWAMP,
        lambda h, t, hum:
            ((t >= 45) & (hum >= 0.88))
            | ((t >= 30) & (hum >= 0.94)),
    ),

    # Warm biomes
    BiomeRule(
        BiomeID.TROPICAL_RAINFOREST,
        lambda h, t, hum:
            (t >= 35) & (hum >= 0.68),
    ),
    BiomeRule(
        BiomeID.SAVANNA,
        lambda h, t, hum:
            t >= 35
            | (hum <= 0.4) & (t >= 30)
    ),
    BiomeRule(
        BiomeID.TROPICAL_GRASS,
        lambda h, t, hum:
            ((t >= 30) & (hum <= 0.54))
            | ((t >= 25) & (hum >= 0.46)),
    ),

    # Rainforest
    BiomeRule(
        BiomeID.RAINFOREST,
        lambda h, t, hum:
            ((t >= 25) & (hum >= 0.68))
            | ((t >= 20) & (hum >= 0.76))
            | (t >= 20) & (hum >= 0.76)
    ),

    # Pine forest
    BiomeRule(
        BiomeID.PINE_FOREST,
        lambda h, t, hum:
            (hum >= 0.76) & (t >= 10)
            | (hum >= 0.92) & (t >= 5)
    ),

    # Tundra
    BiomeRule(
        BiomeID.TUNDRA,
        lambda h, t, hum:
            ((t <= -5) & (hum <= 0.92))
            | ((t <= 0) & (hum <= 0.85))
            | ((t <= 5) & (hum <= 0.69)),
    ),

    # Boreal forest / extreme hills
    BiomeRule(
        BiomeID.EXTREME_HILLS,
        lambda h, t, hum:
            (
                ((t <= 10) & (hum >= 0.46))
                | ((t <= 15) & (hum >= 0.62))
            )
            & (h >= 4_000),
    ),
    BiomeRule(
        BiomeID.BOREAL_FOREST,
        lambda h, t, hum:
            ((t <= 10) & (hum >= 0.46))
            | ((t <= 15) & (hum >= 0.62)),
    ),

    # Forest
    BiomeRule(
        BiomeID.FOREST,
        lambda h, t, hum:
            ((t <= 15) & (hum >= 0.46))
            | (hum >= 0.54),
    ),

    # Fallback
    BiomeRule(
        BiomeID.PRAIRIE,
        lambda h, t, hum: np.ones(h.shape, dtype=bool),
    ),
]


def stats_to_biome_array(
        heights: np.ndarray,
        temps: np.ndarray,
        humidities: np.ndarray,
    ) -> np.ndarray:
        """Accepts three `np.ndarray` inputs and creates an `np.ndarray` of `BiomeID`s."""

        temps_c = temps - 273.15

        biomes = np.empty(heights.shape, dtype=np.int8)
        remaining = np.ones(heights.shape, dtype=bool)

        for rule in BIOME_RULES:
            mask = rule.condition(heights, temps_c, humidities)
            mask &= remaining

            biomes[mask] = rule.biome_id
            remaining[mask] = False

        return biomes
