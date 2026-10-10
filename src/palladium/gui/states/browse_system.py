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

import pygame as pg
from james import HBox, Panel, Spacer, VBox, Label

from palladium.core.constants import KELVIN_COLOURS, WN_H, WN_W
from palladium.core.utils import lerp_gradient
from palladium.gui.constants import SCREEN_RECT, UI_MARGIN_M, UI_MARGIN_S
from palladium.gui.renderer import draw_elem
from palladium.gui.themes import ThemeKey
from palladium.gui.states.base import State

if TYPE_CHECKING:
    from palladium.game.game import Game


class BrowseSystemState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.seed_label = Label(
            text="",
            font=self.game.assets.fonts.font_ui,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.overlay_panel = Panel(
            child=VBox(
                HBox(
                    Spacer(),
                    HBox(
                        Label(
                            text="star system ",
                            font=self.game.assets.fonts.font_ui,
                            k_fg=ThemeKey.FG
                        ),
                        self.seed_label,
                        renderer=draw_elem
                    ),
                    Spacer(),
                    renderer=draw_elem
                ),
                Spacer(),
                HBox(
                    renderer=draw_elem
                ),
                HBox(
                    renderer=draw_elem
                ),
                HBox(
                    renderer=draw_elem
                ),
                HBox(
                    renderer=draw_elem
                ),
                renderer=draw_elem
            ),
            vert_padding=UI_MARGIN_M,
            renderer=draw_elem
        )

        self.overlay_panel.layout(SCREEN_RECT)

    def on_entered(self) -> None:
        # shouldn't be None if entered properly
        assert self.game.star_system is not None

        self.seed_label.set_text(self.game.star_system.seed_str)
        self.overlay_panel.layout(SCREEN_RECT)

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        pass

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG])

        # TODO: add star background parallax effect

        # self.game.star_system should not be None if this state was entered properly
        assert self.game.star_system is not None

        temp_colour = lerp_gradient(self.game.star_system.star.temp, KELVIN_COLOURS)
        pg.draw.circle(screen, temp_colour, (WN_W // 2, WN_H // 2), 100)

        # Draw UI
        draw_elem(screen, self.overlay_panel, self.game.current_theme())
