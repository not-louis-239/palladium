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


import math
import random
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass
class InterpolationAxis:
    i0: np.ndarray
    i1: np.ndarray
    i2: np.ndarray
    i3: np.ndarray

    w0: np.ndarray
    w1: np.ndarray
    w2: np.ndarray
    w3: np.ndarray


@dataclass
class SampleAxes:
     x_axis: InterpolationAxis
     y_axis: InterpolationAxis


def _prepare_axis(
        coordinates: np.ndarray,
        fidelity: int,
    ) -> InterpolationAxis:
        pos = coordinates * fidelity

        i1 = np.floor(pos).astype(np.intp)
        t = pos - i1

        i0 = (i1 - 1) % fidelity
        i1 = i1 % fidelity
        i2 = (i1 + 1) % fidelity
        i3 = (i1 + 2) % fidelity

        t2 = t * t
        t3 = t2 * t

        w0 = -0.5 * t + t2 - 0.5 * t3
        w1 = 1.0 - 2.5 * t2 + 1.5 * t3
        w2 = 0.5 * t + 2.0 * t2 - 1.5 * t3
        w3 = -0.5 * t2 + 0.5 * t3

        return InterpolationAxis(
            i0, i1, i2, i3,
            w0, w1, w2, w3,
        )


def prepare_axes(fidelity: int, xs: np.ndarray, ys: np.ndarray) -> SampleAxes:
     x_axis = _prepare_axis(coordinates=xs, fidelity=fidelity)
     y_axis = _prepare_axis(coordinates=ys, fidelity=fidelity)
     return SampleAxes(x_axis, y_axis)


def _noise_offset(seed_int: int) -> tuple[float, float, float]:
    rng = random.Random(seed_int)

    return (
        rng.uniform(-10_000, 10_000),
        rng.uniform(-10_000, 10_000),
        rng.uniform(-10_000, 10_000),
    )


_TWO_TIMES_PI = 2 * math.pi


def seeded_bicubic_snoise3_array(
        fidelity: int, axes: SampleAxes, seed_int: int,
        generator: Callable[[float, float, float], float],
    ) -> np.ndarray:

    # Generate offset from seed
    ox, oy, oz = _noise_offset(seed_int)

    # Get values first
    values: list[list[float]] = []
    for cell_y in range(fidelity + 1):
        row: list[float] = []
        for cell_x in range(fidelity + 1):
            # 0..1
            frac_x = cell_x / fidelity
            frac_y = cell_y / fidelity

            # Latitude and longitude in radians
            longitude = frac_x * _TWO_TIMES_PI
            latitude = math.pi * (0.5 - frac_y)

            # Convert to Cartesian coordinates -> unit sphere with range -1..1
            x = math.cos(latitude) * math.cos(longitude)
            z = math.cos(latitude) * math.sin(longitude)
            y = math.sin(latitude)

            row.append(generator(x + ox, y + oy, z + oz))
        values.append(row)

    # Convert to NumPy array
    values_arr = np.array(values, dtype=np.float32)

    # Sample using bicubic interpolation
    x_axis, y_axis = axes.x_axis, axes.y_axis

    horizontal = (
        values_arr[:, x_axis.i0] * x_axis.w0
        + values_arr[:, x_axis.i1] * x_axis.w1
        + values_arr[:, x_axis.i2] * x_axis.w2
        + values_arr[:, x_axis.i3] * x_axis.w3
    )

    result = (
        horizontal[y_axis.i0, :] * y_axis.w0[:, None]
        + horizontal[y_axis.i1, :] * y_axis.w1[:, None]
        + horizontal[y_axis.i2, :] * y_axis.w2[:, None]
        + horizontal[y_axis.i3, :] * y_axis.w3[:, None]
    )

    return result
