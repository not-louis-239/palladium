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

import pygame as pg
from pygame import Rect, Surface

from james import Element, Label
from james.helpers.custom_types import SupportsGetItemColour

from palladium.gui.constants import ICON_SIZE, UI_MARGIN_S
from palladium.core.custom_types import Colour
from palladium.core.asset_manager import Images


ARROW_SURFACE = pg.image.load(Images().proceed)


@lru_cache(maxsize=500)
def get_arrow_surface(size: int, colour: Colour, rotation: int) -> Surface:
    size_ratio = size / ARROW_SURFACE.get_width()
    tinted = pg.transform.scale_by(ARROW_SURFACE.copy(), size_ratio)

    colour_surface = pg.Surface(tinted.get_size(), pg.SRCALPHA)
    colour_surface.fill(colour)
    tinted.blit(colour_surface, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

    rotated = pg.transform.rotate(tinted, -rotation)
    return rotated


class DirectionIcon[K](Element[K]):
    def __init__(
            self, *, flex: float = 0, shrink: float = 0,
            interactive: bool = False, hover_tooltip: Label | None = None,
            size: int = ICON_SIZE, inset: int = UI_MARGIN_S, bearing: int = 0,
            k_bg: K | None = None, k_fg: K,
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, interactive=interactive, hover_tooltip=hover_tooltip)

        self.size = size
        self.inset = inset
        self.set_bearing(bearing)

        self.k_fg = k_fg
        self.k_bg = k_bg

    def set_bearing(self, degrees: int) -> None:
        """Set `self`'s bearing."""
        self.bearing = degrees % 360

    def contains_point(self, pos: tuple[int, int]) -> bool:
        radius = self.size / 2
        cx, cy = self.rect.center
        return (cx - pos[0]) ** 2 + (cy - pos[1]) ** 2 <= radius ** 2

    def preferred_size(self) -> tuple[int, int]:
        return self.size, self.size

    def layout(self, rect: Rect) -> None:
        self.assign_rect(rect)

    def draw_default(self, surface: Surface, theme: SupportsGetItemColour) -> None:
        radius = self.size / 2

        # Draw the background
        if self.k_bg is not None:
            pg.draw.circle(surface, theme[self.k_bg], self.rect.center, radius)

        # Draw the arrow
        # Subtract 90° to compensate for the fact that the proceed icon points right
        img_rotation = self.bearing - 90
        img_size = max(self.size - 2 * self.inset, 0)
        self.img = get_arrow_surface(img_size, theme[self.k_fg], img_rotation)

        surface.blit(self.img, self.img.get_rect(center=self.rect.center))
