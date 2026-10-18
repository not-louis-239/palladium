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


from enum import StrEnum
from typing import Generator

import math
import pygame as pg

from palladium.core.utils import clamp
from palladium.generators.noise_port import snoise2


MAP_WIDTH = 180
MAP_HEIGHT = 90

_HALF_MAP_WIDTH = MAP_WIDTH // 2


class BiomeType(StrEnum):
    """Enum values must match lowercase display name"""

    # Height-restricted biomes
    VOLCANO = "volcano"
    FROZEN_PEAKS = "frozen peaks"
    ALPINE = "alpine"
    EXTREME_HILLS = "extreme hills"

    # Hot biomes
    PYRO = "pyro"
    LAVA = "lava"
    MAGMA = "magma"

    # Mid biomes
    SALT_FLATS = "salt flats"
    HOT_DESERT = "hot desert"
    DESERT = "desert"
    COLD_DESERT = "cold desert"
    ASPHALT = "asphalt"
    GEYSER = "geyser"
    HOT_SPRING = "hot spring"
    SAVANNA = "savanna"
    TROPICAL_RAINFOREST = "tropical rainforest"
    SWAMP = "swamp"
    PRAIRIE = "prairie"
    TROPICAL_GRASS = "tropical grass"
    FOREST = "forest"
    RAINFOREST = "rainforest"
    PINE_FOREST = "pine forest"
    BOREAL_FOREST = "boreal forest"
    TUNDRA = "tundra"
    FROZEN_PLAINS = "frozen plains"

    # Ocean biomes
    VOLCANIC_BEACH = "volcanic beach"
    SULPHUR_COAST = "sulphur coast"
    SULPHUR = "sulphur"
    TROPICAL_BEACH = "tropical beach"
    REEF = "reef"
    TROPICAL_OCEAN = "tropical ocean"
    BEACH = "beach"
    WARM_SEA = "warm sea"
    OCEAN = "ocean"
    STONY_SHORE = "stony shore"
    COLD_SEA = "cold sea"
    ABYSS = "abyss"
    SNOWY_BEACH = "snowy beach"
    FROZEN_COAST = "frozen coast"
    FROZEN_OCEAN = "frozen ocean"


BIOME_COLOURS = {
    BiomeType.VOLCANO: (128, 0, 0),
    BiomeType.FROZEN_PEAKS: (227, 220, 255),
    BiomeType.ALPINE: (167, 197, 209),
    BiomeType.EXTREME_HILLS: (149, 166, 158),
    BiomeType.PYRO: (255, 207, 76),
    BiomeType.LAVA: (255, 170, 23),
    BiomeType.MAGMA: (255, 105, 0),
    BiomeType.SALT_FLATS: (192, 192, 192),
    BiomeType.HOT_DESERT: (255, 210, 127),
    BiomeType.DESERT: (255, 234, 198),
    BiomeType.COLD_DESERT: (255, 250, 239),
    BiomeType.ASPHALT: (45, 45, 45),
    BiomeType.GEYSER: (255, 101, 166),
    BiomeType.HOT_SPRING: (0, 255, 172),
    BiomeType.SAVANNA: (198, 218, 117),
    BiomeType.TROPICAL_RAINFOREST: (0, 69, 0),
    BiomeType.SWAMP: (108, 129, 55),
    BiomeType.PRAIRIE: (255, 219, 73),
    BiomeType.TROPICAL_GRASS: (201, 189, 11),
    BiomeType.FOREST: (83, 220, 23),
    BiomeType.RAINFOREST: (0, 142, 0),
    BiomeType.PINE_FOREST: (88, 175, 141),
    BiomeType.BOREAL_FOREST: (156, 217, 192),
    BiomeType.TUNDRA: (207, 255, 255),
    BiomeType.FROZEN_PLAINS: (207, 200, 255),
    BiomeType.VOLCANIC_BEACH: (131, 91, 80),
    BiomeType.SULPHUR_COAST: (226, 255, 153),
    BiomeType.SULPHUR: (208, 255, 84),
    BiomeType.TROPICAL_BEACH: (255, 248, 157),
    BiomeType.REEF: (0, 255, 235),
    BiomeType.TROPICAL_OCEAN: (0, 116, 148),
    BiomeType.BEACH: (255, 250, 187),
    BiomeType.WARM_SEA: (0, 214, 255),
    BiomeType.OCEAN: (0, 76, 112),
    BiomeType.STONY_SHORE: (195, 195, 195),
    BiomeType.COLD_SEA: (0, 155, 255),
    BiomeType.ABYSS: (15, 0, 33),
    BiomeType.SNOWY_BEACH: (228, 221, 255),
    BiomeType.FROZEN_COAST: (123, 212, 255),
    BiomeType.FROZEN_OCEAN: (177, 230, 255),
}


class Cell:
    def __init__(
            self,
            height: float,  # m above sea level
            temperature: float,  # °C
            humidity: float  # % relative humidity
        ) -> None:
        self.height = height
        self.temp = temperature
        self.humidity = humidity
        self.biome = stats_to_biome(height, temperature, humidity, seed=0)


class TerrainSurface:
    def __init__(self, cells: list[list[Cell]]) -> None:
        self.cells = cells

    def __getitem__(self, pos: tuple[int, int]) -> Cell:
        return self.cells[pos[1]][pos[0]]

    def __iter__(self):
        for row in self.cells:
            yield row

    def get_neighbours(self, x: int, y: int) -> Generator[tuple[int, int], None, None]:
        left = ((x - 1) % MAP_WIDTH, y)
        right = ((x + 1) % MAP_WIDTH, y)

        if y == 0:  # top of map
            above = ((x + _HALF_MAP_WIDTH) % MAP_WIDTH, y)
            below = (x, 1)
        elif y == MAP_HEIGHT - 1:  # bottom of map
            above = (x, MAP_HEIGHT - 2)
            below = ((x + _HALF_MAP_WIDTH) % MAP_WIDTH, y)
        else:
            above = (x, y - 1)
            below = (x, y + 1)

        yield left
        yield right
        yield above
        yield below

    def get_normal_at(self, x: int, y: int) -> pg.Vector3:
        left, right, above, below = self.get_neighbours(x, y)

        h_left = self.cells[left[1]][left[0]].height
        h_right = self.cells[right[1]][right[0]].height
        h_above = self.cells[above[1]][above[0]].height
        h_below = self.cells[below[1]][below[0]].height

        dx = (h_right - h_left) / 2
        dy = (h_below - h_above) / 2

        return pg.Vector3(-dx, -dy, 1).normalize()

    def get_cell(self, x: int, y: int) -> Cell:
        return self.cells[y][x]


def generate_terrain_surface(seed_int: int, base_temp: float) -> TerrainSurface:
    """Expects base_temp in °K"""

    grid: list[list[Cell]] = []

    # TODO: this is a stub, finish it later

    for y in range(MAP_HEIGHT):
        row: list[Cell] = []

        for x in range(MAP_WIDTH):
            # Assign heights - metres
            # seed_int needs to be a small enough seed that `snoise2` doesn't break
            height = -1000 + 4000 * snoise2(x, y, scale=0.015, octaves=4, base=seed_int % 32_768)

            # Assign temperature - °K
            altitude_penalty = 0.000021 * height  # temperature drops by 0.0021% per metre
            latitude_multiplier = 1.2 * math.cos((y - MAP_HEIGHT // 2) / MAP_HEIGHT)
            temp = base_temp * latitude_multiplier * max(0, (1 - altitude_penalty))

            # Assign humidity - values from 0 to 1
            base_humidity = 0.65 + 0.15 * snoise2(x, y, scale=0.05, octaves=4, base=(seed_int + 1) % 32_768)

            # Coasts and oceans have higher humidity
            if height < 100:
                gap = 100 - height
                coast_bonus = min(0.05, 0.00025 * gap)
            else:
                coast_bonus = 0

            # Humidity decreases with latitude - first slowly, then rapid dropoff
            latitude_multiplier = 1.15 * math.cos((y - MAP_HEIGHT // 2) / MAP_HEIGHT)

            # Dry bands around ±30°
            latitude_abs = abs((y - MAP_HEIGHT // 2) / (MAP_HEIGHT // 2))
            if 0.1 <= latitude_abs <= 0.35:
                strength = 1 - abs(latitude_abs - 0.225) / 0.125
                dry_band_factor = 1 - snoise2(x, y, scale=0.05, octaves=4, base=(seed_int + 2) % 32_768) * strength * 2
            else:
                dry_band_factor = 1

            humidity = clamp((base_humidity + coast_bonus) * latitude_multiplier * dry_band_factor, 0, 1)

            # Cell assigns itself a biome on creation
            cell = Cell(height, temp, humidity)
            row.append(cell)

        grid.append(row)

    return TerrainSurface(grid)


def stats_to_biome(height: float, temp: float, humidity: float, seed: int) -> BiomeType:
    # Note: use `>=` and `<=`, not `>` or `<` for most comparisons, to prevent hard-to-detect seams

    # Convert temperature from °K -> °C to make it easier to work with
    temp -= 273.15

    # Superheated biomes
    if temp >= 2_500:
        return BiomeType.PYRO
    if temp >= 800:
        return BiomeType.LAVA
    if temp >= 250:
        return BiomeType.MAGMA

    # Hot land biomes turn to volcano at 2,000m+
    if temp >= 95 and height >= 2_000:
        return BiomeType.VOLCANO

    # Second magma block
    if temp >= 100 and humidity <= 0.38:
        return BiomeType.MAGMA

    # Water biomes
    if height < 0:
        if height <= -500:
            if temp <= -5:
                return BiomeType.FROZEN_OCEAN

            if (
                temp <= 5 and height <= -1_000
                or temp <= 25 and height <= -3_000
            ):
                return BiomeType.ABYSS

            if (
                temp <= 35
                or temp <= 40 and height <= -1_000
                or temp <= 45 and height <= -3_000
            ):
                return BiomeType.OCEAN

            if (
                temp <= 50
                or temp <= 55 and height <= -1_000
            ):
                return BiomeType.TROPICAL_OCEAN

            return BiomeType.SULPHUR
        elif height <= -50:
            if (
                temp <= -5
                or temp <= 0 and height >= -100
            ):
                return BiomeType.FROZEN_COAST

            if temp <= 15:
                return BiomeType.COLD_SEA
            if temp <= 35:
                return BiomeType.WARM_SEA
            if temp <= 50:
                return BiomeType.REEF
            return BiomeType.SULPHUR_COAST

        if temp <= 0:
            return BiomeType.SNOWY_BEACH
        if temp <= 15:
            return BiomeType.STONY_SHORE
        if temp <= 35:
            return BiomeType.BEACH
        if temp <= 50:
            return BiomeType.TROPICAL_BEACH
        return BiomeType.VOLCANIC_BEACH

    # ## Land biomes

    # Frozen plains - turns to frozen peaks at 4,000m+
    if (
        temp <= -20
        or temp <= -15 and humidity >= 0.25
        or temp <= -10 and humidity >= 0.68
    ):

        if height >= 4_000:
            return BiomeType.FROZEN_PEAKS
        return BiomeType.FROZEN_PLAINS

    # Salt flats
    if humidity <= 0.08 or humidity <= 0.15 and temp >= 70:
        return BiomeType.SALT_FLATS

    # Geyser
    if (
        temp >= 100 and humidity >= 0.75
        or temp >= 95 and humidity >= 0.82
    ):
        return BiomeType.GEYSER

    # Asphalt
    if (
        temp >= 90 and 0.55 <= humidity <= 0.75
        or temp >= 85 and 0.55 <= humidity <= 0.68
    ):
        return BiomeType.ASPHALT

    # Hot desert - turns to hot spring at 0.75 humidity or higher
    if temp >= 50:
        if humidity >= 0.68:
            return BiomeType.HOT_SPRING
        return BiomeType.HOT_DESERT

    if (
        temp >= 45 and humidity <= 0.48
        or temp >= 40 and humidity <= 0.24
        or temp >= 30 and humidity <= 0.16
    ):
        return BiomeType.HOT_DESERT

    # Desert and cold deserts
    if humidity <= 0.32:
        # Desert turns to alpine at 3,000m+ if <20°C
        if height >= 3_000 and temp <= 20:
            return BiomeType.ALPINE

        if temp >= 10:
            return BiomeType.DESERT
        return BiomeType.COLD_DESERT

    if temp >= 45 and humidity >= 0.88 or temp >= 30 and humidity >= 0.94:
        return BiomeType.SWAMP

    # Warm biomes
    if temp >= 35:
        if humidity >= 0.68:
            return BiomeType.TROPICAL_RAINFOREST
        return BiomeType.SAVANNA

    if humidity <= 0.4 and temp >= 30:
        return BiomeType.SAVANNA

    if temp >= 30 and humidity <= 0.54 or temp >= 25 and humidity >= 0.46:
        return BiomeType.TROPICAL_GRASS

    # Other biomes

    if temp >= 25 and humidity >= 0.68 or temp >= 20 and humidity >= 0.76:
        return BiomeType.RAINFOREST

    if humidity >= 0.76:
        if temp >= 20:
            return BiomeType.RAINFOREST
        elif temp >= 10:
            return BiomeType.PINE_FOREST

    if humidity >= 0.92 and temp >= 5:
        return BiomeType.PINE_FOREST

    if (
        temp <= -5 and humidity <= 0.92
        or temp <= 0 and humidity <= 0.85
        or temp <= 5 and humidity <= 0.69
    ):
        return BiomeType.TUNDRA

    if (
        temp <= 10 and humidity >= 0.46
        or temp <= 15 and humidity >= 0.62
    ):
        # Boreal forest turns to extreme hills at 4,000m+
        if height >= 4_000:
            return BiomeType.EXTREME_HILLS
        return BiomeType.BOREAL_FOREST

    if (
        temp <= 15 and humidity >= 0.46
        or humidity >= 0.54
    ):
        return BiomeType.FOREST

    return BiomeType.PRAIRIE
