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

import numpy as np

from palladium.core.utils import clamp
from palladium.generation.biomes.biome_classifier import fields_to_biome_array
from palladium.generation.biomes.biomes import BiomeID
from palladium.generation.objects.field_types import FieldType
from palladium.gui.constants import LIGHT_NORMAL

MAP_WIDTH = 1280
MAP_HEIGHT = 720

_HALF_MAP_WIDTH = MAP_WIDTH // 2


@dataclass
class CellWrapper:
    height: float
    temp: float
    humidity: float
    biome_id: BiomeID


class TerrainSurface:
    def __init__(self, fields: dict[FieldType, np.ndarray]) -> None:
        """Expects arrays containing `np.float32` values."""

        self.fields = fields

        # Calculate terrain normals
        self.normals = self._calculate_normals()

        # Calculate dot products between terrain normals and light direction
        self.dot_products = self.normals @ np.asarray(LIGHT_NORMAL, dtype=np.float32)

        # Classify the terrain surface into biomes
        self.biomes = fields_to_biome_array(fields=fields)

    def info_at(self, x: int, y: int) -> CellWrapper:
        """Returns a CellWrapper containing the properties of the cell at (x, y)."""

        # Clamp to avoid IndexError from attempting to grab a cell that doesn't exist
        # or weird bugs caused by implicit wrapping from x<0 or y<0.
        clamped_x = clamp(x, 0, MAP_WIDTH - 1)
        clamped_y = clamp(y, 0, MAP_HEIGHT - 1)

        return CellWrapper(
            height=float(self.fields[FieldType.HEIGHT][clamped_y, clamped_x]),
            temp=float(self.fields[FieldType.TEMP][clamped_y, clamped_x]),
            humidity=float(self.fields[FieldType.HUMIDITY][clamped_y, clamped_x]),
            biome_id=BiomeID(self.biomes[clamped_y, clamped_x]),
        )

    def _calculate_normals(self) -> np.ndarray:
        heights = self.fields[FieldType.HEIGHT]

        left = np.roll(heights, 1, axis=1)
        right = np.roll(heights, -1, axis=1)

        above = np.empty_like(heights)
        below = np.empty_like(heights)

        # Normal rows
        above[1:-1] = heights[:-2]
        below[1:-1] = heights[2:]

        # North pole
        above[0] = np.roll(heights[0], _HALF_MAP_WIDTH)
        below[0] = heights[1]

        # South pole
        above[-1] = heights[-2]
        below[-1] = np.roll(heights[-1], _HALF_MAP_WIDTH)

        dx = (right - left) / 2
        dy = (below - above) / 2

        normals = np.stack(
            (dx, np.ones_like(dx), dy),
            axis=-1,
        )

        length = np.linalg.norm(normals, axis=-1, keepdims=True)

        return normals / length
