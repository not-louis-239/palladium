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

from james import Panel, VBox, HBox, Spacer, Label, RectButton
import pygame as pg

from palladium.gui.constants import UI_MARGIN_M, UI_MARGIN_S, BORDER_W, DEFAULT_ATTRS, SCREEN_RECT
from palladium.gui.themes import ThemeKey
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import StateID, State

if TYPE_CHECKING:
    from palladium.game.game import Game


class TitleState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.begin_button = RectButton(
            text="begin",
            font=self.game.assets.fonts.font_ui,
            **DEFAULT_ATTRS,
            border_w=BORDER_W
        )

        self.panel = Panel(
            renderer=draw_elem,
            vert_padding=UI_MARGIN_M,
            horiz_padding=UI_MARGIN_M,
            child=VBox(
                Spacer(flex=0.5),
                HBox(
                    Spacer(),
                    Label(
                        text="palladium",
                        font=self.game.assets.fonts.font_title,
                        k_fg=ThemeKey.FG,
                    ),
                    Spacer(),
                    renderer=draw_elem
                ),
                Spacer(),
                HBox(
                    Spacer(),
                    self.begin_button,
                    Spacer(),
                    renderer=draw_elem
                ),
                Spacer(),
                renderer=draw_elem
            ),
        )

        self.panel.layout(SCREEN_RECT)

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.begin_button.check_overlaps(event.pos):
                    self.game.state = StateID.ENTER_SEED

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG])
        draw_elem(screen, self.panel, self.game.current_theme())
