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


from typing import TypedDict

import pygame as pg

from palladium.core.constants import WN_H, WN_W
from palladium.core.custom_types import Colour
from palladium.gui.themes import ThemeKey

BORDER_W = 2

UI_MARGIN_XS = 7
UI_MARGIN_S = 15
UI_MARGIN_M = 32

ICON_SIZE = 64

SCREEN_RECT = pg.Rect(0, 0, WN_W, WN_H)


# ugh, pyright, you complained so I added this. happy now?
class UIKwargs(TypedDict, total=False):
    k_bg_colour: ThemeKey
    k_bg_hovered: ThemeKey
    k_bg_active: ThemeKey
    k_fg_colour: ThemeKey
    k_fg_hovered: ThemeKey
    k_fg_active: ThemeKey
    k_border_colour: ThemeKey
    k_border_hovered: ThemeKey
    k_border_active: ThemeKey
    inset: int

DEFAULT_ATTRS: UIKwargs = {
    "k_bg_colour": ThemeKey.BG,
    "k_bg_hovered": ThemeKey.BG_HOVERED,
    "k_bg_active": ThemeKey.BG_ACTIVE,
    "k_fg_colour": ThemeKey.FG,
    "k_fg_hovered": ThemeKey.FG_HOVERED,
    "k_fg_active": ThemeKey.FG_ACTIVE,
    "k_border_colour": ThemeKey.BORDER,
    "k_border_hovered": ThemeKey.BORDER_HOVERED,
    "k_border_active": ThemeKey.BORDER_ACTIVE,
    "inset": UI_MARGIN_S
}

DEFAULT_INPUT_BOX_ATTRS: UIKwargs = {
    "k_bg_colour": ThemeKey.BG,
    "k_bg_hovered": ThemeKey.BG_HOVERED,
    "k_bg_active": ThemeKey.BG_ACTIVE,
    "k_fg_colour": ThemeKey.FG_INPUT_TEXT,
    "k_fg_hovered": ThemeKey.FG_INPUT_TEXT_HOVERED,
    "k_fg_active": ThemeKey.FG_INPUT_TEXT_ACTIVE,
    "k_border_colour": ThemeKey.BORDER,
    "k_border_hovered": ThemeKey.BORDER_HOVERED,
    "k_border_active": ThemeKey.BORDER_ACTIVE,
    "inset": UI_MARGIN_S
}
# blackbody colours in terms of {°K: tuple[int, int, int]}
KELVIN_COLOURS: dict[float, Colour] = {
    400.0: (0, 0, 0),
    800.0: (70, 0, 0),
    1000.0: (255, 56, 0),
    2000.0: (255, 137, 18),
    4000.0: (255, 209, 163),
    6000.0: (255, 255, 255),
    10000.0: (201, 226, 255),
    20000.0: (162, 198, 255),
    40000.0: (143, 184, 255),
}
