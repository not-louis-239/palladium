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
import numpy as np
from dataclasses import dataclass

from typing import Callable


@dataclass
class FixedArrays:
    x0: np.ndarray
    y0: np.ndarray

    x_weights: tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]

    y_weights: tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]

    xm1: np.ndarray
    xp0: np.ndarray
    xp1: np.ndarray
    xp2: np.ndarray

    ym1: np.ndarray
    yp0: np.ndarray
    yp1: np.ndarray
    yp2: np.ndarray


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


def cubic_weights(
        t: np.ndarray,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:
        t2 = t * t
        t3 = t2 * t

        return (
            -0.5 * t + t2 - 0.5 * t3,
            1.0 - 2.5 * t2 + 1.5 * t3,
            0.5 * t + 2.0 * t2 - 1.5 * t3,
            -0.5 * t2 + 0.5 * t3,
        )


def prepare_axis(
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


def prepare_fixed_arrays(
        fidelity: int,
        xs: np.ndarray,
        ys: np.ndarray,
    ) -> FixedArrays:
        pos_x = xs * fidelity
        pos_y = ys * fidelity

        x0 = np.floor(pos_x).astype(np.intp)
        y0 = np.floor(pos_y).astype(np.intp)

        tx = pos_x - x0
        ty = pos_y - y0

        return FixedArrays(
            x0=x0,
            y0=y0,

            x_weights=cubic_weights(tx),
            y_weights=cubic_weights(ty),

            xm1=(x0 - 1) % fidelity,
            xp0=x0 % fidelity,
            xp1=(x0 + 1) % fidelity,
            xp2=(x0 + 2) % fidelity,

            ym1=(y0 - 1) % fidelity,
            yp0=y0 % fidelity,
            yp1=(y0 + 1) % fidelity,
            yp2=(y0 + 2) % fidelity,
        )


class NoiseField:
    def __init__(
        self,
        fidelity: int,
        generator: Callable[[float, float], float],
        fixed_arrays: FixedArrays
    ):
        self.fidelity = fidelity
        self.values = np.array([[
            generator(x / fidelity, y / fidelity)
            for x in range(fidelity + 1)
        ] for y in range(fidelity + 1)], dtype=np.float32)
        self.fixed_arrays = fixed_arrays

    def sample_array(self, x_axis: InterpolationAxis, y_axis: InterpolationAxis) -> np.ndarray:
        fixed = self.fixed_arrays

        x0, x1, x2, x3 = fixed.x_weights
        y0, y1, y2, y3 = fixed.y_weights

        t_i = time.time()
        horizontal = (
            self.values[:, x_axis.i0] * x_axis.w0
            + self.values[:, x_axis.i1] * x_axis.w1
            + self.values[:, x_axis.i2] * x_axis.w2
            + self.values[:, x_axis.i3] * x_axis.w3
        )

        result = (
            horizontal[y_axis.i0, :] * y_axis.w0[:, None]
            + horizontal[y_axis.i1, :] * y_axis.w1[:, None]
            + horizontal[y_axis.i2, :] * y_axis.w2[:, None]
            + horizontal[y_axis.i3, :] * y_axis.w3[:, None]
        )

        t_f = time.time()
        print(f"Interpolation completed in {1000 * (t_f - t_i)} ms")

        return result
