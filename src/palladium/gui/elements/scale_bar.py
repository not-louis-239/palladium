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


from typing import Any

import pygame as pg
from pygame import Rect

import james
from james.utils import get_text_surf
from james import Colour, SupportsGetItemColour

from palladium.gui.constants import BORDER_W


class ScaleBar(james.Element):
    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            k_fg: str, bar_width: int,
            text: str, font: pg.font.Font,
            inset: int = 0, gap: int = 0,
            bar_height: int = 4
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.k_fg = k_fg
        self.bar_width = bar_width
        self.bar_height = bar_height
        self.text = text
        self.font = font
        self.inset = inset
        self.gap = gap

    def preferred_size(self) -> tuple[int, int]:
        text_w, _ = self.font.size(self.text)
        # Using self.font.get_height for a consistent element height
        return (2 * self.inset + self.bar_width + self.gap + text_w, 2 * self.inset + self.font.get_height())

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        bar_left, bar_top = self.rect.left + self.inset, self.rect.centery - self.bar_height // 2

        p1 = (bar_left, bar_top)
        p2 = (bar_left, bar_top + self.bar_height)
        p3 = (bar_left + self.bar_width, bar_top + self.bar_height)
        p4 = (bar_left + self.bar_width, bar_top)

        pg.draw.line(surface, theme[self.k_fg], p1, p2, width=BORDER_W)
        pg.draw.line(surface, theme[self.k_fg], p2, p3, width=BORDER_W)
        pg.draw.line(surface, theme[self.k_fg], p3, p4, width=BORDER_W)
        surface.blit(
            get_text_surf(self.font, self.text, theme[self.k_fg]),
            dest=(bar_left + self.bar_width + self.gap, self.rect.centery - self.font.get_height() // 2)
        )
