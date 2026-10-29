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

import numpy as np
import pygame as pg
from james import GUI, CircleButton, Divider, HBox, Label, Panel, ScrollableDisplay, Spacer, VBox
from pygame import Event, Surface
from pygame.key import ScancodeWrapper

from palladium.core.constants import WN_W
from palladium.gui.constants import (
    DEFAULT_ATTRS_DARK_BG,
    ICON_SIZE,
    SCREEN_RECT,
    UI_MARGIN_L,
    UI_MARGIN_M,
    UI_MARGIN_S,
)
from palladium.generation.objects.field_types import FieldType
from palladium.gui.renderer import draw_elem
from palladium.gui.elements.histogram import HorizontalHistogram
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import CLEAR, ThemeKey
from palladium.gui.utils import get_seed_messages
from palladium.gui.histogram import generate_bins
from palladium.gui.view_colour_schemes import ViewMode, COLOUR_SCHEMES

if TYPE_CHECKING:
    from palladium.game.game import Game


NUM_HISTOGRAM_BINS = 50

class PlanetInfoState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.work_surface = pg.Surface(SCREEN_RECT.size, pg.SRCALPHA)

        self._setup_ui()

    def _setup_ui(self) -> None:
        info_vbox = VBox(
            Spacer(
                min_h=UI_MARGIN_L
            ),
            HBox(
                Spacer(),
                planet_name_label := Label(
                    text="",
                    font=self.fonts.ui,
                    k_fg=ThemeKey.FG_ELEMS,
                    inset=UI_MARGIN_M
                ),
                Spacer(),
            ),
            Divider(k_fg=ThemeKey.FG_ELEMS),
            Label(
                text="Altitude Distribution",
                font=self.fonts.text,
                k_fg=ThemeKey.FG_ELEMS,
            ),
            histogram_vbox := VBox(),
            gap=UI_MARGIN_S,
        )

        self.planet_name_label = planet_name_label
        self.histogram_vbox = histogram_vbox

        self.info_panel = Panel(
            info_scrollable := ScrollableDisplay(child=info_vbox, min_internal_w=WN_W - 2 * UI_MARGIN_M),
            horiz_padding=UI_MARGIN_M
        )

        self.info_scrollable = info_scrollable

        self.overlay_panel = Panel(
            VBox(
                HBox(
                    back_button := CircleButton(
                        r=ICON_SIZE // 2,
                        font=self.fonts.text,
                        img_path=self.images.back,
                        **DEFAULT_ATTRS_DARK_BG,
                    ),
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    Panel(
                        seed_hbox := HBox(
                            seed_label := Label(
                                text="",
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_ACCENT,
                                shrink=1.0,
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
                        ),
                        horiz_padding=UI_MARGIN_S,
                        k_bg=ThemeKey.BG_DARK,
                    ),
                    Spacer(),
                ),
                Spacer(),
            ),
            horiz_padding=UI_MARGIN_M,
            interactive=False
        )

        self.overlay_panel.layout(SCREEN_RECT)

        self.gui = GUI(self.info_panel, self.overlay_panel, renderer=draw_elem)

        self.seed_hbox = seed_hbox
        self.back_button = back_button
        self.seed_label = seed_label
        self.offset_label = offset_label
        self.seed_int_label = seed_int_label

    def _update_labels(self) -> None:
        assert self.game.star_system is not None

        planet = self.game.current_planet()
        assert planet.surface is not None
        height_surface = planet.surface.fields[FieldType.HEIGHT]
        flattened = height_surface.ravel()
        total_cells = len(flattened)

        # Generate data and convert to 0..1
        bins = generate_bins(flattened, num_bins=NUM_HISTOGRAM_BINS)
        data = {b: (value / total_cells) for b, value in bins.items()}

        # Labels
        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)

        # Histogram
        self.histogram_vbox.clear_children()
        self.histogram_vbox.add_child(
            HorizontalHistogram(
                data=data,  # type: ignore
                axis_label_font=self.fonts.tips,
                data_label_font=self.fonts.tiny,
                axis_title_font=self.fonts.text,
                k_fg_bin_axis=ThemeKey.FG_ELEMS,
                bin_axis_title="altitude (m)",
                k_fg_axis_value_labels=ThemeKey.FG_ELEMS,
                num_bin_axis_labels=21,
                k_fg_data_value_labels=ThemeKey.FG_ELEMS,
                k_fg_data_value_gridlines=ThemeKey.BG_ACTIVE,
                data_value_gridlines_interval=0.01,
                axis_formatter=lambda x: f"{x:,.0f}",
                data_formatter=lambda perc: f"{perc:.4%}" if perc < 0.001 else f"{perc:.3%}" if perc < 0.01 else f"{perc:.2%}",
                bar_colour_scheme=COLOUR_SCHEMES[ViewMode.ALTITUDE][0]
            )
        )

        # Layout
        self.info_panel.layout(SCREEN_RECT)
        self.overlay_panel.layout(SCREEN_RECT)

    def on_entered(self) -> None:
        # Refresh planet information
        planet = self.game.current_planet()
        self.planet_name_label.set_text(planet.name)

        # Update labels
        self._update_labels()

    def update(self, dt_s: float) -> None:
        self.gui.update(dt_s)

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        elem = self.gui.hit_test(pg.mouse.get_pos())

        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if elem is self.back_button:
                    self.game.enter_state(StateID.BROWSE_TERRAIN)

            if event.type == pg.MOUSEWHEEL and (
                elem is not None
                and self.info_scrollable in elem.parents
                or elem is self.info_scrollable
            ):
                self.info_scrollable.handle_scroll(event)

    def draw(self, screen: Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])

        self.work_surface.fill(CLEAR)
        draw_elem(self.work_surface, self.info_panel, self.game.current_theme())
        screen.blit(self.work_surface)

        self.work_surface.fill(CLEAR)
        draw_elem(self.work_surface, self.overlay_panel, self.game.current_theme())
        screen.blit(self.work_surface)
