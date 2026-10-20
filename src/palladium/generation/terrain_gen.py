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


import time
from collections.abc import Callable, Generator
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np

from palladium.generation.biomes import BiomeID, stats_to_biome_array
from palladium.generation.noise_port import snoise2
from palladium.gui.constants import LIGHT_NORMAL

MAP_WIDTH = 1280
MAP_HEIGHT = 720

_HALF_MAP_WIDTH = MAP_WIDTH // 2
_TERRAIN_SCALE_COEFF = 2.5
_NUM_OCTAVES = 4


class NoiseLayers(Enum):
    BASE = auto()
    MOUNTAINS = auto()
    DETAIL = auto()
    HUMIDITY = auto()
    DRYNESS = auto()


def _signed_pow4_array(x: np.ndarray) -> np.ndarray:
    return np.sign(x) * np.abs(x) ** 4
def _signed_sqrt_array(x: np.ndarray) -> np.ndarray:
    return np.sign(x) * np.sqrt(np.abs(x))
def _sigmoid_array(value: np.ndarray, strength: float) -> np.ndarray:
    return 1 / (1 + np.exp(-strength * value))


@dataclass
class CellWrapper:
    height: float
    temp: float
    humidity: float
    biome_id: BiomeID


class NoiseField:
    def __init__(
        self,
        fidelity: int,
        generator: Callable[[float, float], float],
    ):
        self.fidelity = fidelity
        self.values = np.array([[
            generator(x / fidelity, y / fidelity)
            for x in range(fidelity + 1)
        ] for y in range(fidelity + 1)], dtype=np.float32)

    def sample(self, x: float, y: float) -> float:
        pos_x = x * self.fidelity
        pos_y = y * self.fidelity

        x0 = int(pos_x)
        y0 = int(pos_y)

        tx = pos_x - x0
        ty = pos_y - y0

        x_indices = (
            (x0 - 1) % self.fidelity,
            x0 % self.fidelity,
            (x0 + 1) % self.fidelity,
            (x0 + 2) % self.fidelity,
        )

        y_indices = (
            (y0 - 1) % self.fidelity,
            y0 % self.fidelity,
            (y0 + 1) % self.fidelity,
            (y0 + 2) % self.fidelity,
        )

        def cubic(
            p0: float,
            p1: float,
            p2: float,
            p3: float,
            t: float,
        ) -> float:
            return 0.5 * (
                2 * p1
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t
            )

        rows = [
            cubic(
                self.values[y, x_indices[0]],
                self.values[y, x_indices[1]],
                self.values[y, x_indices[2]],
                self.values[y, x_indices[3]],
                tx,
            )
            for y in y_indices
        ]

        return float(
            cubic(
                rows[0],
                rows[1],
                rows[2],
                rows[3],
                ty,
            )
        )

    def sample_array(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Batch-bicubically interpolate at normalized coordinates
        [0..1] for an array of x's and y's."""

        pos_x = x * self.fidelity
        pos_y = y * self.fidelity

        x0 = np.floor(pos_x).astype(np.intp)
        y0 = np.floor(pos_y).astype(np.intp)

        tx = pos_x - x0
        ty = pos_y - y0

        xm1 = (x0 - 1) % self.fidelity
        xp0 = x0 % self.fidelity
        xp1 = (x0 + 1) % self.fidelity
        xp2 = (x0 + 2) % self.fidelity

        ym1 = (y0 - 1) % self.fidelity
        yp0 = y0 % self.fidelity
        yp1 = (y0 + 1) % self.fidelity
        yp2 = (y0 + 2) % self.fidelity

        def cubic(
            p0: np.ndarray,
            p1: np.ndarray,
            p2: np.ndarray,
            p3: np.ndarray,
            t: np.ndarray,
        ) -> np.ndarray:
            return 0.5 * (
                2 * p1
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t
            )

        row0 = cubic(
            self.values[ym1, xm1],
            self.values[ym1, xp0],
            self.values[ym1, xp1],
            self.values[ym1, xp2],
            tx,
        )

        row1 = cubic(
            self.values[yp0, xm1],
            self.values[yp0, xp0],
            self.values[yp0, xp1],
            self.values[yp0, xp2],
            tx,
        )

        row2 = cubic(
            self.values[yp1, xm1],
            self.values[yp1, xp0],
            self.values[yp1, xp1],
            self.values[yp1, xp2],
            tx,
        )

        row3 = cubic(
            self.values[yp2, xm1],
            self.values[yp2, xp0],
            self.values[yp2, xp1],
            self.values[yp2, xp2],
            tx,
        )

        return cubic(
            row0,
            row1,
            row2,
            row3,
            ty,
        )


class TerrainSurface:
    def __init__(self, heights: np.ndarray, temps: np.ndarray, humidities: np.ndarray) -> None:
        """Expects arrays containing `np.float32` values."""

        self.heights = heights
        self.temps = temps
        self.humidities = humidities

        self.normals = self._calculate_normals()
        self.dot_products = self.normals @ np.asarray(LIGHT_NORMAL, dtype=np.float32)
        self.biomes = stats_to_biome_array(heights=heights, temps=temps, humidities=humidities)

    def info_at(self, x: int, y: int) -> CellWrapper:
        return CellWrapper(
            height=float(self.heights[y, x]),
            temp=float(self.temps[y, x]),
            humidity=float(self.humidities[y, x]),
            biome_id=BiomeID(self.biomes[y, x]),
        )

    def _calculate_normals(self) -> np.ndarray:
        heights = self.heights

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


def generate_terrain_surface(seed_int: int, base_temp: float) -> TerrainSurface:
    """Expects base_temp in °K"""

    t_i = time.time()

    # Arrays of x and y where x, y in [0..1]
    x = np.arange(MAP_WIDTH, dtype=np.float32) / MAP_WIDTH
    y = np.arange(MAP_HEIGHT, dtype=np.float32) / MAP_HEIGHT
    x_grid, y_grid = np.meshgrid(x, y)

    # Noise fields
    fields = {
        NoiseLayers.BASE: NoiseField(
            fidelity=40,
            generator=lambda x, y: snoise2(
                x, y, octaves=_NUM_OCTAVES, scale=_TERRAIN_SCALE_COEFF, base=(seed_int) % 32_768
            )
        ),
        NoiseLayers.MOUNTAINS: NoiseField(
            fidelity=40,
            generator=lambda x, y: snoise2(
                x * 0.5, y * 0.5, octaves=_NUM_OCTAVES, scale=_TERRAIN_SCALE_COEFF, base=(seed_int + 1) % 32_768
            )
        ),
        NoiseLayers.DETAIL: NoiseField(
            fidelity=240,
            generator=lambda x, y: snoise2(
                x * 4, y * 4, octaves=_NUM_OCTAVES, scale=_TERRAIN_SCALE_COEFF, base=(seed_int + 2) % 32_768
            )
        ),
        NoiseLayers.HUMIDITY: NoiseField(
            fidelity=40,
            generator=lambda x, y: snoise2(
                x, y, scale=_TERRAIN_SCALE_COEFF * 3, octaves=_NUM_OCTAVES, base=(seed_int + 1) % 32_768
            )
        ),
        NoiseLayers.DRYNESS: NoiseField(
            fidelity=40,
            generator=lambda x, y: snoise2(
                x, y, scale=_TERRAIN_SCALE_COEFF * 3, octaves=_NUM_OCTAVES, base=(seed_int + 3) % 32_768
            )
        )
    }

    # Get noise fields
    base_noise = fields[NoiseLayers.BASE].sample_array(x_grid, y_grid)
    mount_noise = fields[NoiseLayers.MOUNTAINS].sample_array(x_grid, y_grid)
    detail_noise = fields[NoiseLayers.DETAIL].sample_array(x_grid, y_grid)
    humidity_noise = fields[NoiseLayers.HUMIDITY].sample_array(x_grid, y_grid)
    dryness_noise = fields[NoiseLayers.DRYNESS].sample_array(x_grid, y_grid)

    # Height layer
    base = _sigmoid_array(base_noise, 35) - 0.8
    mount = _signed_pow4_array(mount_noise)
    detail = _signed_sqrt_array(detail_noise)

    heights = (
        base * 4_000
        + mount * 40_000
        + detail * 1_000
    )

    # Latitude
    latitude_abs = np.abs(2 * (y_grid - 0.5))

    # Temp and humidity multipliers
    temp_latitude_multiplier = 1.05 * np.cos(y_grid - 0.5)
    humidity_latitude_multiplier = 1.15 * np.cos(y_grid - 0.5)

    # 2.1% drop per km in temperature
    altitude_penalty = 0.000021 * heights

    temps = (
        base_temp
        * temp_latitude_multiplier
        * np.maximum(0, 1 - altitude_penalty)
    )

    # Base humidity
    base_humidity = 0.65 + 0.15 * humidity_noise

    # Coast bonus
    coast_bonus = np.clip(0.025 - 0.00025 * heights, 0, 0.05)

    # Dry band humidity penalty
    strength = np.zeros_like(latitude_abs)
    dry_band = (
        (latitude_abs >= 0.1)
        & (latitude_abs <= 0.35)
    )
    strength[dry_band] = 1 - np.abs(latitude_abs[dry_band] - 0.225) / 0.125

    dry_band_factor = np.ones_like(latitude_abs)
    dry_band_factor[dry_band] = 1 - (dryness_noise[dry_band] + 1) * strength[dry_band] * 0.4

    # Humidity
    humidities = np.clip((base_humidity + coast_bonus) * humidity_latitude_multiplier * dry_band_factor, 0, 1)

    t_f = time.time()
    print(f"Generated terrain surface in {1000 * (t_f - t_i):.4f} ms")

    # Grid
    return TerrainSurface(
        heights=heights,
        temps=temps,
        humidities=humidities
    )
