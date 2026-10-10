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
from palladium.core.constants import KELVIN_COLOURS, WN_W, WN_H
from palladium.gui.constants import BORDER_W, UI_MARGIN_M
from palladium.terrain.star_gen import StarProfile
from palladium.core.custom_types import Colour


# TODO: there are some other GUI functions in the other utils.py that should probably go here


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
