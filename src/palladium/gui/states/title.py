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


from __future__ import annotations

from typing import TYPE_CHECKING

from james import Panel, VBox, Spacer, Label, RectButton
from pygame import Event, Surface, Rect
from pygame.key import ScancodeWrapper

from palladium.core.constants import WN_W, WN_H
from palladium.gui.constants import UI_PADDING
from palladium.gui.themes import ThemeKey
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State

if TYPE_CHECKING:
    from palladium.game.game import Game


class TitleState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.panel = Panel(
            vert_padding=UI_PADDING,
            horiz_padding=UI_PADDING,
            child=VBox(
                Label(
                    text="palladium",
                    font=self.game.assets.fonts.font_title
                )
            )
        )

        self.panel.layout(Rect(0, 0, WN_W, WN_H))

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        pass

    def draw(self, screen: Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG])
        draw_elem(screen, self.panel)
