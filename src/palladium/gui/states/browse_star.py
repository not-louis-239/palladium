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

from james import Label, Spacer, CircleButton, HBox, VBox, Panel

from palladium.gui.utils import draw_star, draw_transparent_rect, draw_scale_bar, get_seed_messages
from palladium.core.constants import WN_W, WN_H
from palladium.gui.constants import UI_MARGIN_M, ICON_SIZE, SCREEN_RECT, UI_MARGIN_S
from palladium.gui.themes import TRANSLUCENT_BLACK
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import ThemeKey

if TYPE_CHECKING:
    from palladium.game.game import Game


def _format_qty(v: float) -> str:
    if v >= 1:
        return f"{v:,.2f}"
    if v >= 0.1:
        return f"{v:,.3f}"
    if v >= 0.01:
        return f"{v:,.4f}"
    if v >= 0.001:
        return f"{v:,.5f}"
    if v >= 0.0001:
        return f"{v:,.6f}"
    return f"{v:,.3g}"


class BrowseStarState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.zoom_level = 0.03

        self.back_button = CircleButton(
            r=ICON_SIZE // 4,
            img_path=self.images.back,
            font=self.fonts.heading,
            k_fg_colour=ThemeKey.FG,
            k_fg_hovered=ThemeKey.FG_HOVERED,
            k_fg_active=ThemeKey.FG_ACTIVE
        )

        self.seed_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_ACCENT,
        )

        self.offset_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_ACCENT2,
        )

        self.seed_int_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_SENTINEL,
        )

        self.temp_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.radius_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.mass_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.luminosity_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.header_hbox = HBox(
            self.back_button,
            Spacer(min_w=UI_MARGIN_S),
            self.seed_label,
            self.offset_label,
            self.seed_int_label,
            renderer=draw_elem,
            padding=UI_MARGIN_S
        )

        self.info_vbox = VBox(
            Label(
                text="surface temperature",
                font=self.fonts.text,
                k_fg=ThemeKey.FG
            ),
            self.temp_label,
            Spacer(flex=0.0, min_h=UI_MARGIN_S),
            Label(
                text="radius",
                font=self.fonts.text,
                k_fg=ThemeKey.FG
            ),
            self.radius_label,
            Spacer(flex=0.0, min_h=UI_MARGIN_S),
            Label(
                text="mass",
                font=self.fonts.text,
                k_fg=ThemeKey.FG
            ),
            self.mass_label,
            Spacer(flex=0.0, min_h=UI_MARGIN_S),
            Label(
                text="luminosity",
                font=self.fonts.text,
                k_fg=ThemeKey.FG
            ),
            self.luminosity_label,
            padding=UI_MARGIN_S,
            renderer=draw_elem
        )

        # TODO: fix text overflow in some places

        self.overlay_panel = Panel(
            child=HBox(
                VBox(
                    HBox(
                        self.header_hbox,
                        Spacer(),
                        renderer=draw_elem
                    ),
                    Spacer(),
                    renderer=draw_elem,
                ),
                Spacer(),
                VBox(
                    self.info_vbox,
                    Spacer(),
                    renderer=draw_elem
                ),
                gap=UI_MARGIN_M,
                renderer=draw_elem
            ),
            vert_padding=UI_MARGIN_M,
            horiz_padding=UI_MARGIN_M,
            renderer=draw_elem
        )

    def _refresh_labels(self) -> None:
        assert self.game.star_system is not None

        # Refresh seed labels
        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)

        # Star properties

        # Temperature
        self.temp_label.set_text(f"    {self.game.star_system.star.temp - 273.15:,.2f}°C")

        # Radius
        self.radius_label.set_text(f"    {_format_qty(self.game.star_system.star.radius)} × Sun")

        # Mass
        self.mass_label.set_text(f"    {_format_qty(self.game.star_system.star.mass)} × Sun")

        # Luminosity
        self.luminosity_label.set_text(f"    {_format_qty(self.game.star_system.star.luminosity)} × Sun")

        # Refresh UI

        # Layout components
        self.overlay_panel.layout(SCREEN_RECT)

    def on_entered(self) -> None:
        self._refresh_labels()

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.back_button.check_overlaps(event.pos):
                    self.game.enter_state(StateID.BROWSE_SYSTEM)

    def draw(self, screen: pg.Surface) -> None:
        assert self.game.star_system is not None

        screen.fill(self.game.current_theme()[ThemeKey.BG])

        # Draw star
        draw_star(screen, self.game.star_system.star, self.zoom_level, (WN_W // 2, WN_H // 2))

        # Scale bar
        width = int(1 / self.zoom_level)
        height = 8
        bar_x = UI_MARGIN_M + UI_MARGIN_S
        bar_y = WN_H - 80

        # TODO: scale bar auto-changes quantity depending on zoom level,
        # e.g. 0.1 -> 0.2 -> 0.5 -> 1 -> 2 -> 5 -> 10 -> 20 -> 50 -> 100 solar radii
        scale_font = self.fonts.text
        scale_text = "1 solar radius"
        draw_transparent_rect(
            screen, TRANSLUCENT_BLACK,
            pg.Rect(
                bar_x - UI_MARGIN_S, bar_y - scale_font.get_height() // 2 - UI_MARGIN_S,
                width + UI_MARGIN_M + 2 * UI_MARGIN_S + scale_font.size(scale_text)[0], scale_font.get_height() + 2 * UI_MARGIN_S
            )
        )

        draw_scale_bar(screen, self.game.current_theme()[ThemeKey.FG], bar_x, bar_y, width, height, scale_font, "1 solar radius")

        # Draw overlay panel
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.header_hbox.rect)
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.info_vbox.rect)
        draw_elem(screen, self.overlay_panel, self.game.current_theme())
