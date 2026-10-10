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

from james import Label, Spacer, CircleButton, HBox, SBox, VBox, Panel
from james.alignment_boxes import HAlign, VAlign

from palladium.gui.utils import draw_star, draw_scale_bar
from palladium.core.constants import WN_W, WN_H
from palladium.gui.constants import UI_MARGIN_M, ICON_SIZE, SCREEN_RECT, UI_MARGIN_S
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import ThemeKey

if TYPE_CHECKING:
    from palladium.game.game import Game


class BrowseStarState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.zoom_level = 0.03

        self.back_button = CircleButton(
            r=ICON_SIZE // 4,
            img_path=self.game.assets.images.back,
            font=self.game.assets.fonts.heading,
            k_fg_colour=ThemeKey.FG
        )

        self.seed_label = Label(
            text="",
            font=self.game.assets.fonts.text,
            k_fg=ThemeKey.FG_ACCENT,
        )

        self.mass_label = Label(
            text="",
            font=self.game.assets.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.radius_label = Label(
            text="",
            font=self.game.assets.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.temp_label = Label(
            text="",
            font=self.game.assets.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.luminosity_label = Label(
            text="",
            font=self.game.assets.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.overlay_panel = Panel(
            child=HBox(
                VBox(
                    SBox(
                        HBox(
                            self.back_button,
                            Spacer(),
                            Label(
                                text="star system ",
                                font=self.game.assets.fonts.text,
                                k_fg=ThemeKey.FG
                            ),
                            self.seed_label,
                            Spacer(),
                            renderer=draw_elem
                        ),
                        forced_width=WN_W // 2 - UI_MARGIN_M - UI_MARGIN_S // 2,
                        strict=True,
                        h_align=HAlign.CENTRE,
                        v_align=VAlign.TOP,
                        renderer=draw_elem
                    ),
                    Spacer(),
                    renderer=draw_elem,
                ),
                VBox(
                    Label(
                        text="surface temperature",
                        font=self.game.assets.fonts.text,
                        k_fg=ThemeKey.FG
                    ),
                    self.temp_label,
                    Label(
                        text="luminosity",
                        font=self.game.assets.fonts.text,
                        k_fg=ThemeKey.FG
                    ),
                    self.luminosity_label,
                    gap=UI_MARGIN_S,
                    renderer=draw_elem
                ),
                gap=UI_MARGIN_M,
                renderer=draw_elem
            ),
            vert_padding=UI_MARGIN_M,
            horiz_padding=UI_MARGIN_M,
            renderer=draw_elem
        )

    def on_entered(self) -> None:
        assert self.game.star_system is not None

        self.seed_label.set_text(self.game.star_system.seed_metadata.display_str)

        self.temp_label.set_text(f"    {self.game.star_system.star.temp - 273.15:,.2f}°C")

        lum = self.game.star_system.star.luminosity
        if lum >= 1:
            self.luminosity_label.set_text(f"    {lum:,.2f} × Sun")
        elif lum >= 0.1:
            self.luminosity_label.set_text(f"    {lum:,.3f} × Sun")
        elif lum >= 0.01:
            self.luminosity_label.set_text(f"    {lum:,.4f} × Sun")
        elif lum >= 0.001:
            self.luminosity_label.set_text(f"    {lum:,.5f} × Sun")
        elif lum >= 0.0001:
            self.luminosity_label.set_text(f"    {lum:,.6f} × Sun")
        else:
            self.luminosity_label.set_text(f"    {lum:,.3g} × Sun")

        self.overlay_panel.layout(SCREEN_RECT)

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button.check_overlaps(event.pos):
                    self.game.enter_state(StateID.BROWSE_SYSTEM)

    def draw(self, screen: pg.Surface) -> None:
        assert self.game.star_system is not None

        screen.fill(self.game.current_theme()[ThemeKey.BG])

        draw_star(screen, self.game.star_system.star, self.zoom_level, (WN_W // 4, WN_H // 2))

        width = int(1 / self.zoom_level)
        height = 8
        bar_x = UI_MARGIN_M
        bar_y = WN_H - 80
        draw_scale_bar(screen, self.game.current_theme()[ThemeKey.FG], bar_x, bar_y, width, height, self.game.assets.fonts.text, "1 solar radius")

        draw_elem(screen, self.overlay_panel, self.game.current_theme())
