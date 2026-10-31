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

import random
from typing import TYPE_CHECKING

import pygame as pg
from james import GUI, Label, Panel, RectButton, SBox, Spacer, VBox

from palladium.core.constants import WN_H, WN_W
from palladium.gui.constants import BORDER_W, DEFAULT_ATTRS, SCREEN_RECT, UI_MARGIN_M
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import CLEAR, ThemeKey
from palladium.gui.utils import draw_bg_star, generate_bg_star_positions

if TYPE_CHECKING:
    from palladium.game.game import Game


STAR_BG_SEED = 102


class TitleState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.work_surface = pg.Surface(SCREEN_RECT.size, pg.SRCALPHA)

        # Draw background star overlay
        self.star_overlay_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)
        star_positions = generate_bg_star_positions(
            seed=STAR_BG_SEED, 
            wrap_bounds=(WN_W, WN_H), 
            star_density_per_pix2=0.0001
        )

        for star_pos in star_positions:
            draw_bg_star(self.star_overlay_surface, (int(star_pos[0]), int(star_pos[1])))

        self.panel = Panel(
            horiz_padding=UI_MARGIN_M,
            child=VBox(
                Spacer(flex=0.5),
                SBox(
                    Label(
                        text="palladium",
                        font=self.fonts.title,
                        k_fg=ThemeKey.FG_ELEMS,
                    ),
                ),
                Spacer(),
                SBox(
                    begin_button := RectButton(
                        text="begin",
                        font=self.fonts.ui,
                        **DEFAULT_ATTRS,
                        border_w=BORDER_W
                    ),
                ),
                Spacer(),
            ),
        )

        self.begin_button = begin_button

        self.panel.layout(SCREEN_RECT)
        self.gui = GUI(self.panel, renderer=draw_elem)

    def on_entered(self) -> None:
        pass

    def update(self, dt_s: float) -> None:
        self.gui.update(dt_s)

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        elem = self.gui.hit_test(pg.mouse.get_pos())

        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if elem is self.begin_button:
                    self.game.enter_state(StateID.ENTER_SEED)

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])
        screen.blit(self.star_overlay_surface)

        self.work_surface.fill(CLEAR)
        draw_elem(self.work_surface, self.panel, self.game.current_theme())
        screen.blit(self.work_surface)
