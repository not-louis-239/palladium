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
from palladium.gui.constants import KELVIN_COLOURS, SCREEN_RECT, UI_MARGIN_M, UI_MARGIN_S, DEFAULT_ATTRS, ICON_SIZE
from palladium.gui.utils import lerp_gradient, get_seed_messages, draw_transparent_rect
from palladium.gui.renderer import draw_elem
from palladium.gui.themes import ThemeKey, TRANSLUCENT_BLACK
from palladium.gui.states.base import State
from palladium.terrain.star_system import generate_star_system

if TYPE_CHECKING:
    from palladium.game.game import Game


STAR_DISPLAY_RADIUS = 8
PLANET_DISPLAY_RADIUS = 2


class BrowseSystemState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.not_to_scale_label = Label(
            text="not to scale",
            font=self.fonts.text,
            inset=UI_MARGIN_S,
            k_fg=ThemeKey.FG
        )

        self.back_button = CircleButton(
            **DEFAULT_ATTRS,
            r=ICON_SIZE // 2,
            img_path=self.images.back,
            font=self.fonts.ui
        )

        self.seed_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_ACCENT
        )

        self.offset_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_ACCENT2
        )

        self.seed_int_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_SENTINEL
        )

        # Making the star button slightly bigger than the displayed star size itself for ease of use
        self.star_button = CircleButton(
            r=STAR_DISPLAY_RADIUS + UI_MARGIN_S, font=self.fonts.ui, k_fg_colour=ThemeKey.FG,
            k_bg_colour=ThemeKey.BG,
            k_bg_hovered=ThemeKey.BG_HOVERED,
            k_bg_active=ThemeKey.BG_ACTIVE
        )

        self.header_hbox = HBox(
            Label(
                text="star system ",
                font=self.fonts.text,
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
                    self.back_button,
                    Spacer(),
                    self.header_hbox,
                    Spacer(),
                    renderer=draw_elem
                ),
                Spacer(),
                HBox(
                    self.not_to_scale_label,
                    Spacer(),
                    renderer=draw_elem
                ),

                # TODO: add buttons: re-centre, 'click and drag' instruction

                renderer=draw_elem
            ),
            horiz_padding=UI_MARGIN_M,
            vert_padding=UI_MARGIN_M,
            renderer=draw_elem
        )

        self.overlay_panel.layout(SCREEN_RECT)

    def _refresh_ui(self) -> None:
        assert self.game.star_system is not None

        # Refresh seed labels
        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)

        # Refresh interactive invisible star button
        radius = self.star_button.r
        self.star_button.rect.update(WN_W // 2 - radius, WN_H // 2 - radius, 2 * radius, 2 * radius)

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
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.back_button.check_overlaps(event.pos):
                    self.game.enter_state(StateID.ENTER_SEED)
                    return
                if self.star_button.check_overlaps(event.pos):
                    self.game.enter_state(StateID.BROWSE_STAR)
                    return

            if event.type == pg.KEYDOWN and event.key == Controls.SEED_MINUS_ONE:
                self._refresh_with_seed_offset(self.game.star_system.seed_metadata.offset - 1)
            if event.type == pg.KEYDOWN and event.key == Controls.SEED_PLUS_ONE:
                self._refresh_with_seed_offset(self.game.star_system.seed_metadata.offset + 1)

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG])

        # TODO: add star background parallax effect

        # self.game.star_system should not be None if this state was entered properly
        assert self.game.star_system is not None

        # Drawing the star at a constant size so that the system remains visible
        star_pos = (WN_W // 2, WN_H // 2)
        draw_elem(screen, self.star_button, self.game.current_theme())
        temp_colour = lerp_gradient(self.game.star_system.star.temp, KELVIN_COLOURS)
        pg.draw.circle(screen, temp_colour, star_pos, STAR_DISPLAY_RADIUS)

        # Draw UI
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.header_hbox.rect)
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.not_to_scale_label.rect)
        draw_elem(screen, self.overlay_panel, self.game.current_theme())
