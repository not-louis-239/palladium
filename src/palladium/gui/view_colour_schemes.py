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


from enum import IntEnum

from palladium.core.custom_types import Colour

import numpy as np


class ViewMode(IntEnum):
    FANCY = 0
    WHITE = 1
    ALTITUDE = 2
    TEMPERATURE = 3
    HUMIDITY = 4
    SHADING = 5


def _prepare_gradient(gradient: dict[float, Colour]) -> tuple[np.ndarray, np.ndarray]:
    """Compile a gradient of `float`s and `Colour`s into two `np.ndarray`s,
    one for the stops and one for the colours. """

    sorted_stops = sorted(gradient)

    stops = np.array(
        sorted_stops,
        dtype=np.float32,
    )

    colours = np.array(
        [gradient[stop] for stop in sorted_stops],
        dtype=np.float32,
    )

    return stops, colours


COLOUR_SCHEMES: dict[ViewMode, tuple[dict[float, Colour], tuple[np.ndarray, np.ndarray]]] = {
    ViewMode.ALTITUDE: (
        d := {  # m -> colour
            -20_000: (0, 0, 0),        # abyssal black
            -10_000: (5, 10, 45),      # very dark blue
            -5_000:  (10, 35, 120),    # deep blue
            -1_000:  (40, 150, 210),   # medium azure
            -1:      (170, 225, 235),  # pale cyan coast
            0:       (225, 195, 125),  # beach sand
            500:     (125, 180, 90),   # light green
            1_000:   (35, 105, 45),    # dark green
            2_000:   (75, 55, 35),     # dark brown
            4_000:   (165, 120, 75),   # light brown
            5_000:   (70, 80, 85),     # dark slate gray
            7_000:   (145, 155, 160),  # light slate gray
            10_000:  (205, 220, 220),  # pale cyan-grey snow
            20_000:  (255, 255, 255),  # white
        },
        _prepare_gradient(d)
    ),
    ViewMode.HUMIDITY: (
        d := {  # % -> colour
            0.0:  (150, 150, 145),  # salt flat grey
            0.15: (215, 195, 145),  # desert beige
            0.3:  (225, 220, 145),  # pale prairie yellow
            0.5:  (100, 190, 90),   # spring green
            0.8:  (135, 215, 225),  # light cyan-blue
            1.0:  (20, 75, 190),    # deep ocean blue
        },
        _prepare_gradient(d)
    ),
    ViewMode.TEMPERATURE: (
        d := {  # °C -> colour
            -273.15: (255, 255, 255),  # absolute zero, white
            -250:    (253, 145, 255),  # pale magenta-pink
            -210:    (150, 39, 219),  # pale purple
            -150:     (49, 30, 105),    # dark purple
            -90:     (34, 73, 189),    # dark blue
            -20:     (145, 205, 240),  # pale blue
            0:       (220, 250, 250),  # pale cyan-white
            10:      (100, 210, 175),  # green-cyan
            20:      (100, 210, 80),   # spring green
            30:      (245, 225, 45),   # yellow
            40:      (245, 125, 30),   # orange
            50:      (245, 25, 30),    # bright red
            100:     (145, 10, 20),    # deep scarlet
            500:     (232, 46, 46),  # bright scarlet
            2_000:   (255, 151, 107),  # very pale red-orange
            10_000:  (255, 240, 235),  # very slightly red off-white
        },
        _prepare_gradient(d)
    ),
    ViewMode.SHADING: (
        d := {  # dot_product(light, normal) -> colour
            -1.0: (10, 15, 55),      # midnight blue
            -0.5: (65, 25, 90),      # dark purple
            0.0: (165, 75, 125),    # muted magenta
            0.5: (219, 157, 112),    # orange
            1.0: (255, 240, 165),   # pale sunlight yellow
        },
        _prepare_gradient(d)
    )
}