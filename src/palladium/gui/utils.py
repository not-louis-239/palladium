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


import pygame as pg

from palladium.core.utils import lerp_gradient
from palladium.core.constants import KELVIN_COLOURS
from palladium.gui.constants import BORDER_W, UI_MARGIN_M
from palladium.terrain.star_gen import StarProfile
from palladium.terrain.star_system import SeedMetadata
from palladium.core.custom_types import Colour, AColour


# TODO: there are some other GUI functions in the other utils.py that should probably go here


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
