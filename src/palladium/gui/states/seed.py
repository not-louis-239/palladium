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

from james import Panel, HBox, VBox, SBox, InputBox, Spacer, Label, CircleButton, RectButton, Table

from palladium.gui.states.base import State, StateID
from palladium.gui.themes import ThemeKey
from palladium.gui.constants import DEFAULT_ATTRS, DEFAULT_INPUT_BOX_ATTRS, BORDER_W, ICON_SIZE, UI_MARGIN_M, UI_MARGIN_S, SCREEN_RECT
from palladium.gui.renderer import draw_elem

if TYPE_CHECKING:
    from palladium.game.game import Game


class SeedState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.back_button = CircleButton(
            **DEFAULT_ATTRS,
            r=ICON_SIZE // 2,
            font=game.assets.fonts.font_ui,
            img_path=game.assets.images.back
        )

        self.proceed_button = RectButton(
            **DEFAULT_ATTRS,
            font=self.game.assets.fonts.font_ui,
            text="proceed",
            border_w=BORDER_W
        )

        self.seed_input_box = InputBox(
            flex=1.0,
            font=self.game.assets.fonts.font_ui,
            k_sentinel=ThemeKey.FG_SENTINEL,
            border_w=BORDER_W,
            sentinel_text="type a string or leave blank for random",
            k_cursor=ThemeKey.CURSOR,
            **DEFAULT_INPUT_BOX_ATTRS,
        )

        self.panel = Panel(
            renderer=draw_elem,
            horiz_padding=UI_MARGIN_M,
            vert_padding=UI_MARGIN_M,
            child=VBox(
                HBox(
                    self.back_button,
                    Spacer(),
                    Label(
                        text="generation",
                        font=self.game.assets.fonts.font_heading,
                        k_fg=ThemeKey.FG
                    ),
                    Spacer(),
                    renderer=draw_elem
                ),
                Spacer(min_h=UI_MARGIN_S, flex=0.0),
                Table(
                    HBox(
                        SBox(
                            Label(
                                text="seed",
                                font=self.game.assets.fonts.font_ui,
                                k_fg=ThemeKey.FG
                            ),
                            renderer=draw_elem
                        ),
                        Spacer(flex=0.0, min_w=UI_MARGIN_M),
                        self.seed_input_box,
                        renderer=draw_elem
                    ),
                    column_flexes=[0, 0, 1],
                    cell_renderer=draw_elem,
                ),
                Spacer(),
                HBox(
                    Spacer(),
                    self.proceed_button,
                    Spacer(),
                    renderer=draw_elem
                ),
                gap=UI_MARGIN_S,
                renderer=draw_elem
            )
        )

        self.panel.layout(SCREEN_RECT)

    def on_entered(self) -> None:
        pass

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button.check_overlaps(event.pos):
                    self.game.state = StateID.TITLE
                if self.proceed_button.check_overlaps(event.pos):
                    self.game.state = StateID.BROWSE_SYSTEM

        self.seed_input_box.handle_input(keys, events, dt_s)

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG])
        draw_elem(screen, self.panel, self.game.current_theme())
