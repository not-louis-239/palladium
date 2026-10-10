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
from james import HBox, Panel, Spacer, VBox, Label, CircleButton

from palladium.gui.states.base import StateID
from palladium.core.constants import WN_H, WN_W, Controls
from palladium.gui.constants import SCREEN_RECT, UI_MARGIN_M, UI_MARGIN_S
from palladium.gui.utils import draw_scale_bar, draw_star, get_seed_messages, draw_transparent_rect
from palladium.gui.renderer import draw_elem
from palladium.gui.themes import ThemeKey, TRANSLUCENT_BLACK
from palladium.gui.states.base import State
from palladium.terrain.star_system import generate_star_system

if TYPE_CHECKING:
    from palladium.game.game import Game


class BrowseSystemState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.zoom_level = 0.03  # solar radii per pixel

        self.seed_label = Label(
            text="",
            font=self.game.assets.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.offset_label = Label(
            text="",
            font=self.game.assets.fonts.text,
            k_fg=ThemeKey.FG_ACCENT2
        )

        self.seed_int_label = Label(
            text="",
            font=self.game.assets.fonts.text,
            k_fg=ThemeKey.FG_SENTINEL
        )

        self.star_button = CircleButton(
            r=0, font=self.game.assets.fonts.ui, k_fg_colour=ThemeKey.FG
        )

        self.header_hbox = HBox(
            Label(
                text="star system ",
                font=self.game.assets.fonts.text,
                k_fg=ThemeKey.FG
            ),
            self.seed_label,
            self.offset_label,
            self.seed_int_label,
            renderer=draw_elem,
            padding=UI_MARGIN_S
        )

        self.overlay_panel = Panel(
            child=VBox(
                HBox(
                    Spacer(),
                    self.header_hbox,
                    Spacer(),
                    renderer=draw_elem
                ),
                Spacer(),

                # TODO: add buttons: re-centre, zoom in, zoom out, 'click and drag' instruction

                # HBox(
                #     renderer=draw_elem
                # ),
                # HBox(
                #     renderer=draw_elem
                # ),
                # HBox(
                #     renderer=draw_elem
                # ),
                # HBox(
                #     renderer=draw_elem
                # ),

                renderer=draw_elem
            ),
            vert_padding=UI_MARGIN_M,
            renderer=draw_elem
        )

        self.overlay_panel.layout(SCREEN_RECT)

    def _adjust_zoom(self) -> None:
        ...  # TODO: finish this function, this should also account for adjusting some other things

    def _refresh_ui(self) -> None:
        assert self.game.star_system is not None

        # Refresh seed labels
        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)

        # Refresh interactive invisible star button
        visual_radius = int(self.game.star_system.star.radius * 2 / self.zoom_level)
        self.star_button.r = visual_radius
        self.star_button.rect.update(WN_W // 2 - visual_radius, WN_H // 2 - visual_radius, 2 * visual_radius, 2 * visual_radius)

        # Refresh overlay panel layout
        self.overlay_panel.layout(SCREEN_RECT)

    def _refresh_with_seed_offset(self, offset: int) -> None:
        assert self.game.star_system is not None

        seed_string = self.game.star_system.seed_metadata.display_str

        if self.game.star_system.seed_metadata.is_string:
            star_system = generate_star_system(seed_string, offset)
        else:
            star_system = generate_star_system(int(seed_string) + offset, 0)
        self.game.star_system = star_system

        self._refresh_ui()

    def on_entered(self) -> None:
        # shouldn't be None if entered properly
        self._refresh_ui()

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        assert self.game.star_system is not None

        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.star_button.check_overlaps(event.pos):
                    self.game.enter_state(StateID.BROWSE_STAR)

            if event.type == pg.KEYDOWN and event.key == Controls.SEED_MINUS_ONE:
                self._refresh_with_seed_offset(self.game.star_system.seed_metadata.offset - 1)
            if event.type == pg.KEYDOWN and event.key == Controls.SEED_PLUS_ONE:
                self._refresh_with_seed_offset(self.game.star_system.seed_metadata.offset + 1)

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG])

        # TODO: add star background parallax effect

        # self.game.star_system should not be None if this state was entered properly
        assert self.game.star_system is not None

        # Drawing the star may cause problems if the star is very big (hundreds of solar radii) at close zoom levels
        draw_star(screen, self.game.star_system.star, self.zoom_level, (WN_W // 2, WN_H // 2))

        # Draw scale bar
        # TODO: this should (probably) eventually be an inherited class from james.Element

        width = int(1 / self.zoom_level)
        height = 8
        bar_x = UI_MARGIN_M + UI_MARGIN_S
        bar_y = WN_H - 80

        # TODO: scale bar auto-changes quantity depending on zoom level,
        # e.g. 0.1 -> 0.2 -> 0.5 -> 1 -> 2 -> 5 -> 10 -> 20 -> 50 -> 100 solar radii
        scale_font = self.game.assets.fonts.text
        scale_text = "1 solar radius"
        draw_transparent_rect(
            screen, TRANSLUCENT_BLACK,
            pg.Rect(
                bar_x - UI_MARGIN_S, bar_y - scale_font.get_height() // 2 - UI_MARGIN_S,
                width + UI_MARGIN_M + 2 * UI_MARGIN_S + scale_font.size(scale_text)[0], scale_font.get_height() + 2 * UI_MARGIN_S
            )
        )

        draw_scale_bar(screen, self.game.current_theme()[ThemeKey.FG], bar_x, bar_y, width, height, scale_font, "1 solar radius")

        # Draw UI
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.header_hbox.rect)
        draw_elem(screen, self.overlay_panel, self.game.current_theme())
