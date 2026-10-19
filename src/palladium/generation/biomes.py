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
from enum import IntEnum, auto

import numpy as np

from palladium.core.custom_types import Colour


class BiomeID(IntEnum):
    INVALID = 0

    # Height-restricted biomes
    VOLCANO = auto()
    FROZEN_PEAKS = auto()
    ALPINE = auto()
    EXTREME_HILLS = auto()

    # Super hot biomes
    PYRO = auto()
    LAVA = auto()
    MAGMA = auto()

    # Warm biomes
    SALT_FLATS = auto()
    HOT_DESERT = auto()
    DESERT = auto()
    COLD_DESERT = auto()
    ASPHALT = auto()
    GEYSER = auto()
    HOT_SPRING = auto()
    SAVANNA = auto()
    TROPICAL_RAINFOREST = auto()
    SWAMP = auto()
    PRAIRIE = auto()
    TROPICAL_GRASS = auto()
    FOREST = auto()
    RAINFOREST = auto()

    # Cold biomes
    PINE_FOREST = auto()
    BOREAL_FOREST = auto()
    TUNDRA = auto()
    FROZEN_PLAINS = auto()

    # Ocean biomes
    VOLCANIC_BEACH = auto()
    SULPHUR_COAST = auto()
    SULPHUR = auto()
    TROPICAL_BEACH = auto()
    REEF = auto()
    TROPICAL_OCEAN = auto()
    BEACH = auto()
    WARM_SEA = auto()
    OCEAN = auto()
    STONY_SHORE = auto()
    COLD_SEA = auto()
    ABYSS = auto()
    SNOWY_BEACH = auto()
    FROZEN_COAST = auto()
    FROZEN_OCEAN = auto()


@dataclass
class BiomeProfile:
    display_name: str
    colour: Colour


BIOME_PROFILES: dict[BiomeID, BiomeProfile] = {
    BiomeID.INVALID: BiomeProfile("Invalid", (255, 0, 0)),

    # Height-restricted biomes
    BiomeID.VOLCANO: BiomeProfile("Volcano", (128, 0, 0)),
    BiomeID.FROZEN_PEAKS: BiomeProfile("Frozen Peaks", (227, 220, 255)),
    BiomeID.ALPINE: BiomeProfile("Alpine", (167, 197, 209)),
    BiomeID.EXTREME_HILLS: BiomeProfile("Extreme Hills", (149, 166, 158)),

    # Super hot biomes
    BiomeID.PYRO: BiomeProfile("Pyro", (255, 207, 76)),
    BiomeID.LAVA: BiomeProfile("Lava", (255, 170, 23)),
    BiomeID.MAGMA: BiomeProfile("Magma", (255, 105, 0)),

    # Warm biomes
    BiomeID.SALT_FLATS: BiomeProfile("Salt Flats", (192, 192, 192)),
    BiomeID.HOT_DESERT: BiomeProfile("Hot Desert", (255, 210, 127)),
    BiomeID.DESERT: BiomeProfile("Desert", (255, 234, 198)),
    BiomeID.COLD_DESERT: BiomeProfile("Cold Desert", (255, 250, 239)),
    BiomeID.ASPHALT: BiomeProfile("Asphalt", (45, 45, 45)),
    BiomeID.GEYSER: BiomeProfile("Geyser", (255, 101, 166)),
    BiomeID.HOT_SPRING: BiomeProfile("Hot Spring", (0, 255, 172)),
    BiomeID.SAVANNA: BiomeProfile("Savanna", (198, 218, 117)),
    BiomeID.TROPICAL_RAINFOREST: BiomeProfile("Tropical Rainforest", (0, 69, 0)),
    BiomeID.SWAMP: BiomeProfile("Swamp", (108, 129, 55)),
    BiomeID.PRAIRIE: BiomeProfile("Prairie", (255, 219, 73)),
    BiomeID.TROPICAL_GRASS: BiomeProfile("Tropical Grass", (201, 189, 11)),
    BiomeID.FOREST: BiomeProfile("Forest", (83, 220, 23)),
    BiomeID.RAINFOREST: BiomeProfile("Rainforest", (0, 142, 0)),

    # Cold biomes
    BiomeID.PINE_FOREST: BiomeProfile("Pine Forest", (88, 175, 141)),
    BiomeID.BOREAL_FOREST: BiomeProfile("Boreal Forest", (156, 217, 192)),
    BiomeID.TUNDRA: BiomeProfile("Tundra", (207, 255, 255)),
    BiomeID.FROZEN_PLAINS: BiomeProfile("Frozen Plains", (207, 200, 255)),

    # Ocean biomes
    BiomeID.VOLCANIC_BEACH: BiomeProfile("Volcanic Beach", (131, 91, 80)),
    BiomeID.SULPHUR_COAST: BiomeProfile("Sulphur Coast", (226, 255, 153)),
    BiomeID.SULPHUR: BiomeProfile("Sulphur", (208, 255, 84)),
    BiomeID.TROPICAL_BEACH: BiomeProfile("Tropical Beach", (255, 248, 157)),
    BiomeID.REEF: BiomeProfile("Reef", (0, 255, 235)),
    BiomeID.TROPICAL_OCEAN: BiomeProfile("Tropical Ocean", (0, 116, 148)),
    BiomeID.BEACH: BiomeProfile("Beach", (255, 250, 187)),
    BiomeID.WARM_SEA: BiomeProfile("Warm Sea", (0, 214, 255)),
    BiomeID.OCEAN: BiomeProfile("Ocean", (0, 76, 112)),
    BiomeID.STONY_SHORE: BiomeProfile("Stony Shore", (195, 195, 195)),
    BiomeID.COLD_SEA: BiomeProfile("Cold Sea", (0, 155, 255)),
    BiomeID.ABYSS: BiomeProfile("Abyss", (15, 0, 33)),
    BiomeID.SNOWY_BEACH: BiomeProfile("Snowy Beach", (228, 221, 255)),
    BiomeID.FROZEN_COAST: BiomeProfile("Frozen Coast", (123, 212, 255)),
    BiomeID.FROZEN_OCEAN: BiomeProfile("Frozen Ocean", (177, 230, 255)),
}


BIOME_COLOURS = np.array([
    BIOME_PROFILES[biome].colour
    for biome in BiomeID
], dtype=np.uint8)


def stats_to_biome_array(heights: np.ndarray, temps: np.ndarray, humidities: np.ndarray) -> np.ndarray:
    """Accepts three `np.ndarray`s and creates an `np.ndarray` of biome IDs."""

    def assign(mask: np.ndarray, biome: BiomeID) -> None:
        mask &= remaining
        biomes[mask] = biome
        remaining[mask] = False

    # convert °K -> °C
    temps_c = temps - 273.15

    biomes = np.full(heights.shape, -1, dtype=np.int8)

    remaining = np.ones(
        heights.shape,
        dtype=bool,
    )

    # Superheated biomes
    assign(temps_c >= 2_500, BiomeID.PYRO)
    assign(temps_c >= 800, BiomeID.LAVA)
    assign(temps_c >= 250, BiomeID.MAGMA)

    # Hot land biomes
    assign((temps_c >= 95) & (heights >= 2_000), BiomeID.VOLCANO)

    # Second magma block
    assign((temps_c >= 100) & (humidities <= 0.38), BiomeID.MAGMA)

    # Water biomes
    shore = (heights > -50) & (heights < 0)
    shallow = (heights > -500) & (heights <= -50)
    deep_water = heights <= -500

    assign(
        deep_water
        & (temps_c <= -5),
        BiomeID.FROZEN_OCEAN
    )

    assign(
        deep_water
        & (
            ((temps_c <= 5) & (heights <= -1_000))
            | ((temps_c <= 25) & (heights <= -3_000))
        ),
        BiomeID.ABYSS,
    )

    assign(
        deep_water
        & (
            (temps_c <= 35)
            | ((temps_c <= 40) & (heights <= -1_000))
            | ((temps_c <= 45) & (heights <= -3_000))
        ),
        BiomeID.OCEAN,
    )

    assign(
        deep_water
        & (
            (temps_c <= 50)
            | ((temps_c <= 55) & (heights <= -1_000))
        ),
        BiomeID.TROPICAL_OCEAN,
    )

    assign(
        deep_water,
        BiomeID.SULPHUR,
    )

    assign(
        shallow
        & (
            (temps_c <= -5)
            | ((temps_c <= 0) & (heights >= -100))
        ),
        BiomeID.FROZEN_COAST,
    )

    assign(
        shallow & (temps_c <= 15),
        BiomeID.COLD_SEA,
    )

    assign(
        shallow & (temps_c <= 35),
        BiomeID.WARM_SEA,
    )

    assign(
        shallow & (temps_c <= 50),
        BiomeID.REEF,
    )

    assign(
        shallow,
        BiomeID.SULPHUR_COAST,
    )

    assign(
        shore & (temps_c <= 0),
        BiomeID.SNOWY_BEACH,
    )

    assign(
        shore & (temps_c <= 15),
        BiomeID.STONY_SHORE,
    )

    assign(
        shore & (temps_c <= 35),
        BiomeID.BEACH,
    )

    assign(
        shore & (temps_c <= 50),
        BiomeID.TROPICAL_BEACH,
    )

    assign(
        shore,
        BiomeID.VOLCANIC_BEACH,
    )

    # Frozen plains
    frozen = (
        (temps_c <= -20)
        | ((temps_c <= -15) & (humidities >= 0.25))
        | ((temps_c <= -10) & (humidities >= 0.68))
    )

    assign(
        frozen & (heights >= 4_000),
        BiomeID.FROZEN_PEAKS,
    )

    assign(
        frozen,
        BiomeID.FROZEN_PLAINS,
    )

    # Salt flats
    assign(
        (humidities <= 0.08)
        | ((humidities <= 0.15) & (temps_c >= 70)),
        BiomeID.SALT_FLATS,
    )

    # Geyser
    assign(
        (
            ((temps_c >= 100) & (humidities >= 0.75))
            | ((temps_c >= 95) & (humidities >= 0.82))
        ),
        BiomeID.GEYSER,
    )

    # Asphalt
    assign(
        (
            ((temps_c >= 90)
             & (humidities >= 0.55)
             & (humidities <= 0.75))
            |
            ((temps_c >= 85)
             & (humidities >= 0.55)
             & (humidities <= 0.68))
        ),
        BiomeID.ASPHALT,
    )

    # Hot desert / hot spring
    hot = temps_c >= 50

    assign(
        hot & (humidities >= 0.68),
        BiomeID.HOT_SPRING,
    )

    assign(
        hot,
        BiomeID.HOT_DESERT,
    )

    assign(
        (
            ((temps_c >= 45) & (humidities <= 0.48))
            | ((temps_c >= 40) & (humidities <= 0.24))
            | ((temps_c >= 30) & (humidities <= 0.16))
        ),
        BiomeID.HOT_DESERT,
    )

    # Desert / cold desert
    dry = humidities <= 0.32

    assign(
        dry & (heights >= 3_000) & (temps_c <= 20),
        BiomeID.ALPINE,
    )

    assign(
        dry & (temps_c >= 10),
        BiomeID.DESERT,
    )

    assign(dry, BiomeID.COLD_DESERT)

    # Swamp
    assign(
        ((temps_c >= 45) & (humidities >= 0.88))
        | ((temps_c >= 30) & (humidities >= 0.94)),
        BiomeID.SWAMP,
    )

    # Warm biomes
    warm = temps_c >= 35

    assign(
        warm & (humidities >= 0.68),
        BiomeID.TROPICAL_RAINFOREST,
    )

    assign(
        warm,
        BiomeID.SAVANNA,
    )

    assign(
        (humidities <= 0.4) & (temps_c >= 30),
        BiomeID.SAVANNA,
    )

    assign(
        ((temps_c >= 30) & (humidities <= 0.54))
        | ((temps_c >= 25) & (humidities >= 0.46)),
        BiomeID.TROPICAL_GRASS,
    )

    # Rainforest
    assign(
        ((temps_c >= 25) & (humidities >= 0.68))
        | ((temps_c >= 20) & (humidities >= 0.76)),
        BiomeID.RAINFOREST,
    )

    # Pine forest
    assign(
        (humidities >= 0.76) & (temps_c >= 20),
        BiomeID.RAINFOREST,
    )

    assign(
        (humidities >= 0.76) & (temps_c >= 10),
        BiomeID.PINE_FOREST,
    )

    assign(
        (humidities >= 0.92) & (temps_c >= 5),
        BiomeID.PINE_FOREST,
    )

    # Tundra
    assign(
        (
            ((temps_c <= -5) & (humidities <= 0.92))
            | ((temps_c <= 0) & (humidities <= 0.85))
            | ((temps_c <= 5) & (humidities <= 0.69))
        ),
        BiomeID.TUNDRA,
    )

    # Boreal forest / extreme hills
    boreal = (
        ((temps_c <= 10) & (humidities >= 0.46))
        | ((temps_c <= 15) & (humidities >= 0.62))
    )

    assign(
        boreal & (heights >= 4_000),
        BiomeID.EXTREME_HILLS,
    )

    assign(
        boreal,
        BiomeID.BOREAL_FOREST,
    )

    # Forest
    assign(
        (((temps_c <= 15) & (humidities >= 0.46))
        | (humidities >= 0.54)),
        BiomeID.FOREST,
    )

    # Anything remaining becomes a prairie
    assign(
        remaining,
        BiomeID.PRAIRIE,
    )

    return biomes
