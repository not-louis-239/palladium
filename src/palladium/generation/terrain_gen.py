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


from functools import lru_cache

import numpy as np
from noise import snoise3

from palladium.generation.field_types import FieldType
from palladium.generation.noise_field import prepare_axes, seeded_bicubic_snoise3_array
from palladium.generation.terrain_surface import MAP_HEIGHT, MAP_WIDTH, TerrainSurface

_TERRAIN_SCALE_COEFF = 0.75
_NUM_OCTAVES = 4


def _signed_pow4_array(x: np.ndarray) -> np.ndarray:
    return np.sign(x) * np.abs(x) ** 4

def _signed_sqrt_array(x: np.ndarray) -> np.ndarray:
    return np.sign(x) * np.sqrt(np.abs(x))

def _sigmoid_array(value: np.ndarray, strength: float) -> np.ndarray:
    return 1 / (1 + np.exp(-strength * value))


_FIDELITY_LOW = 40
_FIDELITY_HIGH = 160


@lru_cache(maxsize=16)
def generate_terrain_surface(seed_int: int, base_temp: float) -> TerrainSurface:
    """Expects base_temp in °K"""

    # Arrays of x and y where x, y in [0..1]
    xs = np.arange(MAP_WIDTH, dtype=np.float32) / MAP_WIDTH
    ys = np.arange(MAP_HEIGHT, dtype=np.float32) / MAP_HEIGHT

    y_grid = np.broadcast_to(
        ys[:, None],
        (MAP_HEIGHT, MAP_WIDTH),
    )

    axes_f_low = prepare_axes(fidelity=_FIDELITY_LOW, xs=xs, ys=ys)
    axes_f_high = prepare_axes(fidelity=_FIDELITY_HIGH, xs=xs, ys=ys)

    # Get noise fields - fidelity of axes must match fidelity of fields
    base_noise = seeded_bicubic_snoise3_array(
        fidelity=_FIDELITY_LOW, axes=axes_f_low, seed_int=seed_int,
        generator=lambda x, y, z: snoise3(
            x * _TERRAIN_SCALE_COEFF,
            y * _TERRAIN_SCALE_COEFF,
            z * _TERRAIN_SCALE_COEFF,
            octaves=_NUM_OCTAVES,
        )
    )

    mount_noise = seeded_bicubic_snoise3_array(
        fidelity=_FIDELITY_LOW, axes=axes_f_low, seed_int=seed_int + 1,
        generator=lambda x, y, z: snoise3(
            x * 0.5 * _TERRAIN_SCALE_COEFF,
            y * 0.5 * _TERRAIN_SCALE_COEFF,
            z * 0.5 * _TERRAIN_SCALE_COEFF,
            octaves=_NUM_OCTAVES,
        )
    )
    detail_noise = seeded_bicubic_snoise3_array(
        fidelity=_FIDELITY_HIGH, axes=axes_f_high, seed_int=seed_int + 2,
        generator=lambda x, y, z: snoise3(
            x * 4 * _TERRAIN_SCALE_COEFF,
            y * 4 * _TERRAIN_SCALE_COEFF,
            z * 4 * _TERRAIN_SCALE_COEFF,
            octaves=_NUM_OCTAVES,
        )
    )

    humidity_noise = seeded_bicubic_snoise3_array(
        fidelity=_FIDELITY_LOW, axes=axes_f_low, seed_int=seed_int + 3,
        generator=lambda x, y, z: snoise3(
            x * 3 * _TERRAIN_SCALE_COEFF,
            y * 3 * _TERRAIN_SCALE_COEFF,
            z * 3 * _TERRAIN_SCALE_COEFF,
            octaves=_NUM_OCTAVES,
        )
    )

    dryness_noise = seeded_bicubic_snoise3_array(
        fidelity=_FIDELITY_LOW, axes=axes_f_low, seed_int=seed_int + 4,
        generator=lambda x, y, z: snoise3(
            x * 3 * _TERRAIN_SCALE_COEFF,
            y * 3 * _TERRAIN_SCALE_COEFF,
            z * 3 * _TERRAIN_SCALE_COEFF,
            octaves=_NUM_OCTAVES,
        )
    )

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
    DRY_BAND_CENTRE = 0.225
    DRY_BAND_HALF_W = 0.16
    DRY_BAND_STRENGTH_COEFF = 0.6

    strength = np.zeros_like(latitude_abs)
    dry_band = (
        (latitude_abs >= (DRY_BAND_CENTRE - DRY_BAND_HALF_W))
        & (latitude_abs <= (DRY_BAND_CENTRE + DRY_BAND_HALF_W))
    )
    strength[dry_band] = 1 - np.abs(latitude_abs[dry_band] - DRY_BAND_CENTRE) / DRY_BAND_HALF_W

    dry_band_factor = np.ones_like(latitude_abs)
    dry_band_factor[dry_band] = 1 - (dryness_noise[dry_band] + 1) * strength[dry_band] * DRY_BAND_STRENGTH_COEFF

    # Humidity
    humidities = np.clip((base_humidity + coast_bonus) * humidity_latitude_multiplier * dry_band_factor, 0, 1)

    # Special fields
    special_fields: list[np.ndarray] = [
        seeded_bicubic_snoise3_array(
            fidelity=_FIDELITY_LOW, axes=axes_f_low, seed_int=seed_int + 5,
            generator=lambda x, y, z: snoise3(
                x * _TERRAIN_SCALE_COEFF,
                y * _TERRAIN_SCALE_COEFF,
                z * _TERRAIN_SCALE_COEFF,
                octaves=_NUM_OCTAVES,
            ),
        ),
        seeded_bicubic_snoise3_array(
            fidelity=_FIDELITY_LOW, axes=axes_f_low, seed_int=seed_int + 6,
            generator=lambda x, y, z: snoise3(
                x * _TERRAIN_SCALE_COEFF,
                y * _TERRAIN_SCALE_COEFF,
                z * _TERRAIN_SCALE_COEFF,
                octaves=_NUM_OCTAVES,
            ),
        ),
        seeded_bicubic_snoise3_array(
            fidelity=_FIDELITY_LOW, axes=axes_f_low, seed_int=seed_int + 7,
            generator=lambda x, y, z: snoise3(
                x * 6 * _TERRAIN_SCALE_COEFF,
                y * 6 * _TERRAIN_SCALE_COEFF,
                z * 6 * _TERRAIN_SCALE_COEFF,
                octaves=_NUM_OCTAVES,
            ),
        ),
    ]

    for noise in special_fields:
        # map [-1..1] to [0..1]
        noise += 1
        noise /= 2

    # Grid
    return TerrainSurface({
        FieldType.HEIGHT: heights,
        FieldType.TEMP: temps,
        FieldType.HUMIDITY: humidities,
        FieldType.SPECIAL_0: special_fields[0],
        FieldType.SPECIAL_1: special_fields[1],
        FieldType.SPECIAL_2: special_fields[2],
    })
