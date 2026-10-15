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
from james import CircleButton, HBox, Label, Panel, Spacer, VBox

from palladium.core.constants import SOLAR_RADIUS_IN_KM, WN_H, WN_W
from palladium.core.utils import clamp
from palladium.gui.constants import ICON_SIZE, SCREEN_RECT, UI_MARGIN_M, UI_MARGIN_S
from palladium.gui.elements.scale_bar import ScaleBar
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import TRANSLUCENT_BLACK, ThemeKey
from palladium.gui.utils import draw_star, draw_transparent_rect, get_seed_messages

if TYPE_CHECKING:
    from palladium.game.game import Game


ZOOM_RATE = 5 # multiply/divide by this per second

PER_PIXELS = 50 # minimum scale bar size
SCALE_BAR_LEVELS: list[float] = [  # solar radii per `PER_PIXELS` pixels
    0.001, 0.002, 0.005,
    0.01, 0.02, 0.05,
    0.1, 0.2, 0.5,
    1, 2, 5,
    10, 20, 50,
    100, 200, 500,
    1000
]

INNER_ZOOM_LIMIT = 0.0001
OUTER_ZOOM_LIMIT = 10


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


def _disable(button: CircleButton):
    button.k_fg_colour = ThemeKey.FG_SENTINEL
    button.k_fg_hovered = ThemeKey.FG_SENTINEL
    button.k_fg_active = ThemeKey.FG_SENTINEL
    button.disabled = True

def _enable(button: CircleButton):
    button.k_fg_colour = ThemeKey.FG
    button.k_fg_hovered = ThemeKey.FG_HOVERED
    button.k_fg_active = ThemeKey.FG_ACTIVE
    button.disabled = False


class BrowseStarState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.zoom_level = 0.015  # solar radii per pixel
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.scale_bar = ScaleBar(
            k_fg=ThemeKey.FG,
            bar_width=round(1 / self.zoom_level),
            text="",
            font=self.fonts.text,
            inset=UI_MARGIN_S,
            gap=UI_MARGIN_S
        )

        self.back_button = CircleButton(
            r=ICON_SIZE // 4,
            img_path=self.images.back,
            font=self.fonts.heading,
            k_fg_colour=ThemeKey.FG,
            k_fg_hovered=ThemeKey.FG_HOVERED,
            k_fg_active=ThemeKey.FG_ACTIVE
        )

        self.zoom_in_button = CircleButton(
            r=ICON_SIZE // 4,
            img_path=self.images.zoom_in,
            font=self.fonts.heading,
            k_fg_colour=ThemeKey.FG,
            k_fg_hovered=ThemeKey.FG_HOVERED,
            k_fg_active=ThemeKey.FG_ACTIVE
        )

        self.zoom_out_button = CircleButton(
            r=ICON_SIZE // 4,
            img_path=self.images.zoom_out,
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

        self.radius_km_label = Label(
            text="",
            font=self.fonts.text,
            k_fg=ThemeKey.FG_SENTINEL
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
            HBox(
                Spacer(flex=0.0, min_w=UI_MARGIN_M),
                self.temp_label,
                renderer=draw_elem
            ),
            Spacer(flex=0.0, min_h=UI_MARGIN_S),
            Label(
                text="radius",
                font=self.fonts.text,
                k_fg=ThemeKey.FG
            ),
            HBox(
                Spacer(flex=0.0, min_w=UI_MARGIN_M),
                self.radius_label,
                renderer=draw_elem
            ),
            HBox(
                Spacer(flex=0.0, min_w=UI_MARGIN_M),
                self.radius_km_label,
                renderer=draw_elem
            ),
            Spacer(flex=0.0, min_h=UI_MARGIN_S),
            Label(
                text="mass",
                font=self.fonts.text,
                k_fg=ThemeKey.FG
            ),
            HBox(
                Spacer(flex=0.0, min_w=UI_MARGIN_M),
                self.mass_label,
                renderer=draw_elem
            ),
            Spacer(flex=0.0, min_h=UI_MARGIN_S),
            Label(
                text="luminosity",
                font=self.fonts.text,
                k_fg=ThemeKey.FG
            ),
            HBox(
                Spacer(flex=0.0, min_w=UI_MARGIN_M),
                self.luminosity_label,
                renderer=draw_elem
            ),
            padding=UI_MARGIN_S,
            renderer=draw_elem
        )

        self.zoom_hbox = HBox(
            self.zoom_in_button,
            self.zoom_out_button,
            padding=UI_MARGIN_S,
            gap=UI_MARGIN_S,
            renderer=draw_elem
        )

        # TODO: fix potential text overflow in some places

        self.overlay_panel = Panel(
            child=HBox(
                VBox(
                    HBox(
                        self.header_hbox,
                        Spacer(),
                        renderer=draw_elem
                    ),
                    Spacer(),
                    HBox(
                        self.zoom_hbox,
                        Spacer(),
                        renderer=draw_elem
                    ),
                    HBox(
                        self.scale_bar,
                        Spacer(),
                        renderer=draw_elem
                    ),
                    gap=UI_MARGIN_S,
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

        # Initialise the scale bar
        self._adjust_zoom(self.zoom_level)

    def _adjust_zoom(self, new_zoom: float) -> None:
        """Adjust zoom and refresh labels"""

        # Clamp and set zoom
        new_zoom = clamp(new_zoom, INNER_ZOOM_LIMIT, OUTER_ZOOM_LIMIT)
        self.zoom_level = new_zoom

        # Set the scale bar to an appropriate level
        scale = SCALE_BAR_LEVELS[0]  # number of solar radii represented by the scale bar
        for candidate_scale in SCALE_BAR_LEVELS:
            if candidate_scale / self.zoom_level > PER_PIXELS:
                scale = candidate_scale
                break

        bar_w = scale / self.zoom_level
        bar_zoom_str = f"{round(scale):,.0f}" if scale > 1 else str(scale)
        self.scale_bar.text = f"{bar_zoom_str} solar radi{'us' if scale == 1 else 'i'}"
        self.scale_bar.bar_width = int(bar_w)

        self.overlay_panel.layout(SCREEN_RECT)

    def _refresh_labels(self) -> None:
        assert self.game.star_system is not None

        # Refresh seed labels
        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)

        # Star properties

        # Temperature
        self.temp_label.set_text(f"{self.game.star_system.star.temp - 273.15:,.2f}°C")

        # Radius
        self.radius_label.set_text(f"{_format_qty(self.game.star_system.star.radius)} × Sun")
        self.radius_km_label.set_text(f" ({self.game.star_system.star.radius * SOLAR_RADIUS_IN_KM:,.0f} km)")

        # Mass
        self.mass_label.set_text(f"{_format_qty(self.game.star_system.star.mass)} × Sun")

        # Luminosity
        self.luminosity_label.set_text(f"{_format_qty(self.game.star_system.star.luminosity)} × Sun")

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

        if self.zoom_in_button.check_held():
            self._adjust_zoom(self.zoom_level / ZOOM_RATE ** dt_s)
        if self.zoom_out_button.check_held():
            self._adjust_zoom(self.zoom_level * ZOOM_RATE ** dt_s)

        # Grey out zoom buttons when zoom is at max or min
        if self.zoom_level >= OUTER_ZOOM_LIMIT:
            _disable(self.zoom_out_button)
        else:
            _enable(self.zoom_out_button)

        if self.zoom_level <= INNER_ZOOM_LIMIT:
            _disable(self.zoom_in_button)
        else:
            _enable(self.zoom_in_button)

    def draw(self, screen: pg.Surface) -> None:
        assert self.game.star_system is not None

        screen.fill(self.game.current_theme()[ThemeKey.BG])

        # Draw star
        draw_star(screen, self.game.star_system.star, self.zoom_level, (WN_W // 2, WN_H // 2))

        # Draw overlay panel and transparent rects for improved contrast
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.zoom_hbox.rect)
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.header_hbox.rect)
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.info_vbox.rect)
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.scale_bar.rect)
        draw_elem(screen, self.overlay_panel, self.game.current_theme())
