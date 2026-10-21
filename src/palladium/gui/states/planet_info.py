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
from pygame import Event, Surface
from pygame.key import ScancodeWrapper

from james import Panel, ScrollableDisplay, CircleButton, Spacer, VBox, HBox, Label

from palladium.gui.states.base import State, StateID
from palladium.gui.themes import ThemeKey, CLEAR
from palladium.gui.utils import get_seed_messages
from palladium.gui.renderer import draw_elem
from palladium.gui.constants import SCREEN_RECT, UI_MARGIN_M, UI_MARGIN_S, ICON_SIZE, DEFAULT_ATTRS_DARK_BG

if TYPE_CHECKING:
    from palladium.game.game import Game


class PlanetInfoState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.work_surface = pg.Surface(SCREEN_RECT.size, pg.SRCALPHA)

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.info_panel = Panel(
            child=ScrollableDisplay(
                child=VBox()
            ),
            vert_padding=UI_MARGIN_M,
            horiz_padding=UI_MARGIN_M
        )

        self.overlay_panel = Panel(
            child=VBox(
                HBox(
                    back_button := CircleButton(
                        r=ICON_SIZE // 2,
                        font=self.fonts.text,
                        img_path=self.images.back,
                        **DEFAULT_ATTRS_DARK_BG,
                    ),
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    seed_hbox := HBox(
                        seed_label := Label(
                            text="",
                            font=self.fonts.text,
                            k_fg=ThemeKey.FG_ACCENT,
                        ),
                        offset_label := Label(
                            text="",
                            font=self.fonts.text,
                            k_fg=ThemeKey.FG_ACCENT2,
                        ),
                        seed_int_label := Label(
                            text="",
                            font=self.fonts.text,
                            k_fg=ThemeKey.FG_SENTINEL,
                        ),
                        padding=UI_MARGIN_S,
                        k_bg_colour=ThemeKey.BG_DARK,
                    ),
                    Spacer(),
                ),
                Spacer(),
            ),
            vert_padding=UI_MARGIN_M,
            horiz_padding=UI_MARGIN_M
        )

        self.overlay_panel.layout(SCREEN_RECT)

        self.seed_hbox = seed_hbox
        self.back_button = back_button
        self.seed_label = seed_label
        self.offset_label = offset_label
        self.seed_int_label = seed_int_label

    def _update_labels(self) -> None:
        assert self.game.star_system is not None

        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)

        self.info_panel.layout(SCREEN_RECT)
        self.overlay_panel.layout(SCREEN_RECT)

    def on_entered(self) -> None:
        planet = self.game.current_planet()

        # TODO: refresh planet information

        # Update labels
        self._update_labels()

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.back_button.check_overlaps(event.pos):
                    self.game.enter_state(StateID.BROWSE_TERRAIN)

    def draw(self, screen: Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])

        self.work_surface.fill(CLEAR)
        draw_elem(self.work_surface, self.info_panel, self.game.current_theme())
        screen.blit(self.work_surface)

        self.work_surface.fill(CLEAR)
        draw_elem(self.work_surface, self.overlay_panel, self.game.current_theme())
        screen.blit(self.work_surface)
