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

from palladium.terrain.noise_port import snoise2


MAP_WIDTH = 180
MAP_HEIGHT = 90


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


class Cell:
    def __init__(
            self,
            height: float,  # m above sea level
            temperature: float,  # °C
            humidity: float  # % relative humidity
        ) -> None:
        self.height = height
        self.temperature = temperature
        self.humidity = humidity
        self.biome = stats_to_biome(height, temperature, humidity, seed=0)


class TerrainSurface:
    def __init__(self, cells: list[list[Cell]]) -> None:
        self.cells = cells

    def get_cell(self, x: int, y: int) -> Cell:
        return self.cells[y][x]


def generate_terrain_surface(base_temp: float) -> TerrainSurface:
    grid: list[list[Cell]] = []

    # TODO: this is a stub, finish it later

    for x in range(MAP_WIDTH):
        row: list[Cell] = []
        for y in range(MAP_HEIGHT):
            # Assign heights - metres
            height = snoise2(x, y, scale=0.05, octaves=4, base=0)

            # Assign temperature - °K
            temp = 293.15 - 0.007 * height

            # Assign humidity - values from 0 to 1
            humidity = 0.8

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

    if humidity <= 0.54:
        if temp >= 30 or temp >= 25 and humidity >= 0.46:
            return BiomeType.TROPICAL_GRASS

    # Other biomes

    if temp >= 25 and humidity >= 0.68 or temp >= 20 and humidity >= 0.76:
        return BiomeType.RAINFOREST

    if humidity >= 0.76:
        if temp >= 20:
            return BiomeType.RAINFOREST
        elif temp >= 10:
            return BiomeType.PINE_FOREST

    if humidity >= 0.92:
        if temp >= 5:
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
