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
from james import (
    CircleButton,
    HBox,
    InputBox,
    Label,
    Panel,
    RectButton,
    SBox,
    Spacer,
    Table,
    VBox,
    GUI,
)

from palladium.core.constants import WN_H, WN_W
from palladium.core.utils import random_seed, safe_convert
from palladium.generation.star_system import generate_star_system
from palladium.gui.constants import (
    BORDER_W,
    DEFAULT_ATTRS,
    DEFAULT_INPUT_BOX_ATTRS,
    ICON_SIZE,
    SCREEN_RECT,
    UI_MARGIN_M,
    UI_MARGIN_S,
    UI_MARGIN_XS,
)
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import CLEAR, ThemeKey

if TYPE_CHECKING:
    from palladium.game.game import Game


class SeedState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.is_valid = True
        self.work_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)

        self.panel = Panel(
            horiz_padding=UI_MARGIN_M,
            child=VBox(
                HBox(
                    back_button := CircleButton(
                        **DEFAULT_ATTRS,
                        r=ICON_SIZE // 2,
                        font=game.assets.fonts.ui,
                        img_path=game.assets.images.back
                    ),
                    Spacer(),
                    Label(
                        text="generation",
                        font=self.fonts.heading,
                        k_fg=ThemeKey.FG_ELEMS
                    ),
                    Spacer(),
                ),
                Spacer(min_h=UI_MARGIN_S, flex=0.0),
                Table(
                    HBox(
                        SBox(
                            Label(
                                text="seed",
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_ELEMS
                            ),
                        ),
                        Spacer(flex=0.0, min_w=UI_MARGIN_S),
                        seed_input_box := InputBox(
                            flex=1.0,
                            font=self.fonts.text,
                            k_bg_selection=ThemeKey.FG_SELECTION,
                            k_sentinel=ThemeKey.FG_SENTINEL,
                            border_w=BORDER_W,
                            sentinel_text="enter text or leave blank for random",
                            k_cursor=ThemeKey.CURSOR,
                            **DEFAULT_INPUT_BOX_ATTRS,
                        ),
                    ),
                    HBox(
                        SBox(
                            Label(
                                text="offset",
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_ELEMS
                            ),
                        ),
                        Spacer(flex=0.0, min_w=UI_MARGIN_S),
                        offset_input_box := InputBox(
                            flex=1.0,
                            font=self.fonts.text,
                            k_bg_selection=ThemeKey.FG_SELECTION,
                            k_sentinel=ThemeKey.FG_SENTINEL,
                            border_w=BORDER_W,
                            sentinel_text="0",
                            tooltip_font=self.fonts.tips,
                            k_cursor=ThemeKey.CURSOR,
                            k_tooltip=ThemeKey.FG_ERROR,
                            tooltip_inset=UI_MARGIN_XS,
                            **DEFAULT_INPUT_BOX_ATTRS,
                        ),
                    ),
                    column_flexes=[0, 0, 1],
                    cell_renderer=draw_elem,
                    cell_inset=UI_MARGIN_S // 2,
                ),
                Spacer(),
                SBox(
                    proceed_button := RectButton(
                        **DEFAULT_ATTRS,
                        font=self.fonts.ui,
                        text="proceed",
                        border_w=BORDER_W
                    ),
                ),
                gap=UI_MARGIN_S,
            )
        )

        self.back_button = back_button
        self.proceed_button = proceed_button
        self.seed_input_box = seed_input_box
        self.offset_input_box = offset_input_box

        self.panel.layout(SCREEN_RECT)
        self.gui = GUI(self.panel, renderer=draw_elem)

    def _validate(self) -> None:
        if self.offset_input_box.text and safe_convert(self.offset_input_box.text, int) is None:
            self.offset_input_box.k_border_colour = ThemeKey.FG_ERROR
            self.offset_input_box.k_border_hovered = ThemeKey.FG_ERROR_HOVERED
            self.offset_input_box.k_border_active = ThemeKey.FG_ERROR_PRESSED
            self.offset_input_box.set_tooltip("Invalid integer value.")
            self.is_valid = False
        else:
            self.offset_input_box.k_border_colour = ThemeKey.BORDER
            self.offset_input_box.k_border_hovered = ThemeKey.BORDER_HOVERED
            self.offset_input_box.k_border_active = ThemeKey.BORDER_PRESSED
            self.offset_input_box.clear_tooltip()
            self.is_valid = True

        # Grey out the proceed button if not all fields are valid
        if not self.is_valid:
            self.proceed_button.disabled = True
            self.proceed_button.k_fg_colour = ThemeKey.FG_SENTINEL
            self.proceed_button.k_fg_hovered = ThemeKey.FG_SENTINEL
            self.proceed_button.k_fg_pressed = ThemeKey.FG_SENTINEL
        else:
            self.proceed_button.disabled = False
            self.proceed_button.k_fg_colour = ThemeKey.FG_ELEMS
            self.proceed_button.k_fg_hovered = ThemeKey.FG_HOVERED
            self.proceed_button.k_fg_pressed = ThemeKey.FG_PRESSED

    def _proceed(self) -> None:
        # MUST create star system before entering system browser
        seed = self.seed_input_box.text or random_seed()

        try:
            offset = int(self.offset_input_box.text)
        except ValueError:
            offset = 0

        self.game.star_system = generate_star_system(seed, offset)
        self.game.enter_state(StateID.BROWSE_SYSTEM)

    def on_entered(self) -> None:
        pass

    def update(self, dt_s: float) -> None:
        self.gui.update(dt_s)

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        elem = self.gui.hit_test(pg.mouse.get_pos())

        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if elem is self.back_button:
                    self.game.enter_state(StateID.TITLE)
                if elem is self.proceed_button and self.is_valid:
                    self._proceed()

        self.seed_input_box.handle_input(keys, events, dt_s)
        if self.offset_input_box.handle_input(keys, events, dt_s):
            self._validate()

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])

        self.work_surface.fill(CLEAR)
        draw_elem(self.work_surface, self.panel, self.game.current_theme())
        screen.blit(self.work_surface)
