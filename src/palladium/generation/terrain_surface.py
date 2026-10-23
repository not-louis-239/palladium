from dataclasses import dataclass

from palladium.generation.biome_classifier import stats_to_biome_array
from palladium.generation.field_types import FieldType
from palladium.generation.biomes import BiomeID
from palladium.gui.constants import LIGHT_NORMAL

import numpy as np


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

        self.normals = self._calculate_normals()
        self.dot_products = self.normals @ np.asarray(LIGHT_NORMAL, dtype=np.float32)
        self.biomes = stats_to_biome_array(fields=fields)

    def info_at(self, x: int, y: int) -> CellWrapper:
        return CellWrapper(
            height=float(self.fields[FieldType.HEIGHT][y, x]),
            temp=float(self.fields[FieldType.TEMP][y, x]),
            humidity=float(self.fields[FieldType.HUMIDITY][y, x]),
            biome_id=BiomeID(self.biomes[y, x]),
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
