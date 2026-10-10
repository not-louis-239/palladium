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
from james import HBox, Label, Panel, RectButton, Spacer, VBox

from palladium.core.constants import WN_H, WN_W
from palladium.gui.constants import BORDER_W, DEFAULT_ATTRS, SCREEN_RECT, UI_MARGIN_M
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import ThemeKey

if TYPE_CHECKING:
    from palladium.game.game import Game


STAR_BG_SEED = 102

LAYER_FIDELITY = 25
RADIUS = 100
LAYERS = [(
    int(255 * ((0.8 * i) / LAYER_FIDELITY) ** 12),
    int(RADIUS * (1 - i / LAYER_FIDELITY))
) for i in range(LAYER_FIDELITY)]


class TitleState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        star_rng = random.Random(STAR_BG_SEED)
        star_positions = [
            (star_rng.random() * WN_W, star_rng.random() * WN_H)
            for _ in range(100)
        ]

        self.star_overlay_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)
        for star in star_positions:
            for brightness, radius in LAYERS:
                surface = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
                pg.draw.circle(surface, (255, 255, 255, brightness), (radius, radius), radius)
                self.star_overlay_surface.blit(surface, (star[0] - radius, star[1] - radius))
            pg.draw.circle(self.star_overlay_surface, (255, 255, 255, 255), star, 2)

        self.begin_button = RectButton(
            text="begin",
            font=self.game.assets.fonts.ui,
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
                        font=self.game.assets.fonts.title,
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

    def on_entered(self) -> None:
        pass

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.begin_button.check_overlaps(event.pos):
                    self.game.enter_state(StateID.ENTER_SEED)

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG])
        screen.blit(self.star_overlay_surface)
        draw_elem(screen, self.panel, self.game.current_theme())
