# Copyright 2026 Louis Masarei-Boulton

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from itertools import pairwise

import pygame as pg

from palladium.core.utils import clamp
from palladium.core.constants import KELVIN_COLOURS
from palladium.gui.constants import BORDER_W, UI_MARGIN_M
from palladium.terrain.star_gen import StarProfile
from palladium.terrain.star_system import SeedMetadata
from palladium.core.custom_types import Colour, AColour


def draw_transparent_rect(surface: pg.Surface, colour: AColour, rect: pg.Rect) -> None:
    """Draws a transparent rectangle. This function is dedicated
    to this purpose because `pg.draw.rect` doesn't work well: it overwrites
    alpha values on the destination surface instead of layering colours
    depending on opacity."""
    rect_surface = pg.Surface(rect.size, pg.SRCALPHA)
    rect_surface.fill(colour)
    surface.blit(rect_surface, rect)


def draw_scale_bar(screen: pg.Surface, colour: Colour, left: float, top: float, width: float, height: float, font: pg.font.Font, text: str):
    pg.draw.line(screen, colour, (left, top), (left, top + height), width=BORDER_W)
    pg.draw.line(screen, colour, (left + width, top), (left + width, top + height), width=BORDER_W)
    pg.draw.line(screen, colour, (left, top + height), (left + width, top + height), width=BORDER_W)
    screen.blit(
        font.render(text, True,
        colour),
        dest=(left + width + UI_MARGIN_M, top - font.get_height() // 2)
    )


def lerp_gradient(val: float, grad: dict[float, Colour]) -> Colour:
    """Returns a Colour determined by the anchor points in `grad`.
    If val < grad[0], returns the first anchor.
    If val > grad[-1], returns the last colour."""

    if not grad:
        raise ValueError("grad requires at least one value-colour pair")

    keys = sorted(grad)
    if val <= keys[0]:
        return grad[keys[0]]
    if val >= keys[-1]:
        return grad[keys[-1]]

    for k1, k2 in pairwise(keys):
        if k1 <= val <= k2:
            t = (val - k1) / (k2 - k1)
            c1, c2 = grad[k1], grad[k2]
            return lerp_colours(c1, c2, t)

    return grad[keys[-1]]


def draw_star(screen: pg.Surface, star: StarProfile, zoom_level: float, pos: tuple[int, int]) -> None:
    temp_colour = lerp_gradient(star.temp, KELVIN_COLOURS)
    pg.draw.circle(screen, temp_colour, pos, star.radius * 2 / zoom_level)


def get_seed_messages(seed_metadata: SeedMetadata) -> tuple[str, str, str]:
    """Returns: seed text, offset, internal integer value
    in the form of strings designed to be joined together visually."""

    # Seed text
    seed_str = seed_metadata.display_str

    # Offset text
    offset = seed_metadata.offset
    if not offset:
        offset_text = ""
    elif offset > 0:
        offset_text = f" + {offset}"
    else:
        offset_text = f" - {-offset}"

    # Internal integer
    if seed_metadata.is_string:
        seed_int_label = f" ({seed_metadata.integer_value})"
    else:
        seed_int_label = ""

    return (seed_str, offset_text, seed_int_label)


def lerp_colours(c1: Colour, c2: Colour, t: float) -> Colour:
    t = clamp(t, 0, 1)
    return tuple(
        int(c1[x] + t * (c2[x] - c1[x])) for x in range(len(c1))  # type: ignore
    )
