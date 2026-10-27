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

import math
from enum import IntEnum
from typing import TYPE_CHECKING

import numpy as np
import pygame as pg
from james import CircleButton, HBox, Label, Panel, Spacer, VBox, GUI, Collapsible, ScrollableDisplay

from palladium.core.custom_types import Colour
from palladium.core.utils import lerp_gradient_array, map_range, clamp
from palladium.generation.biomes import BIOME_COLOURS, BIOME_PROFILES
from palladium.generation.field_types import FieldType
from palladium.generation.terrain_surface import MAP_HEIGHT, MAP_WIDTH
from palladium.gui.constants import (
    DEFAULT_ATTRS_DARK_BG,
    HOVER_LABEL_ATTRS,
    ICON_SIZE,
    SCREEN_RECT,
    UI_MARGIN_M,
    UI_MARGIN_S,
    UI_MARGIN_XS,
    WN_H,
    WN_W,
)
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.elements.gradient_scale import GradientScale
from palladium.gui.themes import ThemeKey
from palladium.gui.utils import (
    get_seed_messages,
)

if TYPE_CHECKING:
    from palladium.game.game import Game


class _ViewMode(IntEnum):
    FANCY = 0
    WHITE = 1
    ALTITUDE = 2
    TEMPERATURE = 3
    HUMIDITY = 4
    SHADING = 5


def _prepare_gradient(gradient: dict[float, Colour]) -> tuple[np.ndarray, np.ndarray]:
    """Compile a gradient of `float`s and `Colour`s into two `np.ndarray`s,
    one for the stops and one for the colours. """

    sorted_stops = sorted(gradient)

    stops = np.array(
        sorted_stops,
        dtype=np.float32,
    )

    colours = np.array(
        [gradient[stop] for stop in sorted_stops],
        dtype=np.float32,
    )

    return stops, colours


_WHITE_LIGHT = (30, 30, 30)
_STARLIGHT_STRENGTH_COEFF = 50

_COLOUR_SCHEMES: dict[_ViewMode, tuple[dict[float, Colour], tuple[np.ndarray, np.ndarray]]] = {
    _ViewMode.ALTITUDE: (
        d := {  # m -> colour
            -20_000: (0, 0, 0),        # abyssal black
            -10_000: (5, 10, 45),      # very dark blue
            -5_000:  (10, 35, 120),    # deep blue
            -1_000:  (40, 150, 210),   # medium azure
            -1:      (170, 225, 235),  # pale cyan coast
            0:       (225, 195, 125),  # beach sand
            500:     (125, 180, 90),   # light green
            1_000:   (35, 105, 45),    # dark green
            2_000:   (75, 55, 35),     # dark brown
            4_000:   (165, 120, 75),   # light brown
            5_000:   (70, 80, 85),     # dark slate gray
            7_000:   (145, 155, 160),  # light slate gray
            10_000:  (205, 220, 220),  # pale cyan-grey snow
            20_000:  (255, 255, 255),  # white
        },
        _prepare_gradient(d)
    ),
    _ViewMode.HUMIDITY: (
        d := {  # % -> colour
            0.0:  (150, 150, 145),  # salt flat grey
            0.15: (215, 195, 145),  # desert beige
            0.3:  (225, 220, 145),  # pale prairie yellow
            0.5:  (100, 190, 90),   # spring green
            0.8:  (135, 215, 225),  # light cyan-blue
            1.0:  (20, 75, 190),    # deep ocean blue
        },
        _prepare_gradient(d)
    ),
    _ViewMode.TEMPERATURE: (
        d := {  # °C -> colour
            -273.15: (255, 255, 255),  # absolute zero, white
            -250:    (253, 145, 255),  # pale magenta-pink
            -210:    (150, 39, 219),  # pale purple
            -150:     (49, 30, 105),    # dark purple
            -90:     (34, 73, 189),    # dark blue
            -20:     (145, 205, 240),  # pale blue
            0:       (220, 250, 250),  # pale cyan-white
            10:      (100, 210, 175),  # green-cyan
            20:      (100, 210, 80),   # spring green
            30:      (245, 225, 45),   # yellow
            40:      (245, 125, 30),   # orange
            50:      (245, 25, 30),    # bright red
            100:     (145, 10, 20),    # deep scarlet
            500:     (232, 46, 46),  # bright scarlet
            2_000:   (255, 151, 107),  # very pale red-orange
            10_000:  (255, 240, 235),  # very slightly red off-white
        },
        _prepare_gradient(d)
    ),
    _ViewMode.SHADING: (
        d := {  # dot_product(light, normal) -> colour
            -1.0: (10, 15, 55),      # midnight blue
            -0.5: (65, 25, 90),      # dark purple
            0.0: (165, 75, 125),    # muted magenta
            0.5: (219, 157, 112),    # orange
            1.0: (255, 240, 165),   # pale sunlight yellow
        },
        _prepare_gradient(d)
    )
}


class BrowseTerrainState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.view_mode = _ViewMode.FANCY
        self.work_surface = pg.Surface(SCREEN_RECT.size, pg.SRCALPHA)

        self._setup_ui()
        self._setup_gradients()

    def _setup_ui(self) -> None:
        self.panel = Panel(
            HBox(
                content_vbox := VBox(
                    HBox(
                        back_button := CircleButton(
                            r=ICON_SIZE // 2,
                            font=self.fonts.text,
                            img_path=self.images.back,
                            **DEFAULT_ATTRS_DARK_BG,
                        ),
                        Spacer(flex=0.0, min_w=UI_MARGIN_S),
                        Panel(
                            HBox(
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
                        # allow that Label to shrink inside the HBox,
                        # but don't allow this HBox itself to shrink
                        shrink=0.0,
                    ),
                    gradient_hbox := HBox(
                        Spacer(),
                        flex=1,
                    ),
                    HBox(
                        HBox(
                            info_button := CircleButton(
                                r=ICON_SIZE // 2,
                                font=self.fonts.ui,
                                **DEFAULT_ATTRS_DARK_BG,
                                img_path=self.images.info
                            ),
                            planet_name_label := Label(
                                k_bg=ThemeKey.BG_DARK,
                                k_fg=ThemeKey.FG_ELEMS,
                                font=self.fonts.text,
                                inset=UI_MARGIN_S
                            ),
                            gap=UI_MARGIN_S,
                        ),
                        Spacer(),
                    ),
                    gap=UI_MARGIN_S
                ),
                Spacer(),
                VBox(
                    hide_gui_button := CircleButton(
                        r=ICON_SIZE // 2,
                        font=self.fonts.text,
                        **DEFAULT_ATTRS_DARK_BG,
                        img_path=self.images.eye_crossed_out,
                    ),
                    view_mode_collapsible := Collapsible(
                        trigger=(view_modes_button := CircleButton(
                            r=ICON_SIZE // 2,
                            font=self.fonts.ui,
                            **DEFAULT_ATTRS_DARK_BG,
                            img_path=self.images.view_modes,
                        )),
                        content=(view_modes_scrollable := ScrollableDisplay(
                            child=(view_modes_vbox := VBox(
                                CircleButton(
                                    r=ICON_SIZE // 2,
                                    font=self.fonts.ui,
                                    **DEFAULT_ATTRS_DARK_BG,
                                    img_path=self.images.trees,
                                    hover_tooltip=Label(
                                        text="Natural Light",
                                        font=self.fonts.text,
                                        **HOVER_LABEL_ATTRS
                                    )
                                ),
                                CircleButton(
                                    r=ICON_SIZE // 2,
                                    font=self.fonts.ui,
                                    **DEFAULT_ATTRS_DARK_BG,
                                    img_path=self.images.sun,
                                    hover_tooltip=Label(
                                        text="White Light",
                                        font=self.fonts.text,
                                        **HOVER_LABEL_ATTRS
                                    )
                                ),
                                CircleButton(
                                    r=ICON_SIZE // 2,
                                    font=self.fonts.ui,
                                    **DEFAULT_ATTRS_DARK_BG,
                                    img_path=self.images.height,
                                    hover_tooltip=Label(
                                        text="Altitude",
                                        font=self.fonts.text,
                                        **HOVER_LABEL_ATTRS
                                    )
                                ),
                                CircleButton(
                                    r=ICON_SIZE // 2,
                                    font=self.fonts.ui,
                                    **DEFAULT_ATTRS_DARK_BG,
                                    img_path=self.images.flame,
                                    hover_tooltip=Label(
                                        text="Temperature",
                                        font=self.fonts.text,
                                        **HOVER_LABEL_ATTRS
                                    )
                                ),
                                CircleButton(
                                    r=ICON_SIZE // 2,
                                    font=self.fonts.ui,
                                    **DEFAULT_ATTRS_DARK_BG,
                                    img_path=self.images.water,
                                    hover_tooltip=Label(
                                        text="Humidity",
                                        font=self.fonts.text,
                                        **HOVER_LABEL_ATTRS
                                    )
                                ),
                                CircleButton(
                                    r=ICON_SIZE // 2,
                                    font=self.fonts.ui,
                                    **DEFAULT_ATTRS_DARK_BG,
                                    img_path=self.images.shading,
                                    hover_tooltip=Label(
                                        text="Shading",
                                        font=self.fonts.text,
                                        **HOVER_LABEL_ATTRS
                                    )
                                ),
                                gap=UI_MARGIN_S,
                            )),
                        )),
                        gap=UI_MARGIN_S,
                        shrink=1.0,
                    ),
                    Spacer(),
                    gap=UI_MARGIN_S
                ),
            ),
            horiz_padding=UI_MARGIN_M,
            interactive=False
        )

        self.hover_panel = Panel(
            k_bg=ThemeKey.BG_DARK,
            child=VBox(
                hover_location := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ELEMS),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(text="surface temperature:", font=self.fonts.text, k_fg=ThemeKey.FG_ELEMS),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_surface_temp := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                ),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(text="altitude:", font=self.fonts.text, k_fg=ThemeKey.FG_ELEMS),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_altitude := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                ),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(text="humidity:", font=self.fonts.text, k_fg=ThemeKey.FG_ELEMS),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_humidity := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                ),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(text="biome:", font=self.fonts.text, k_fg=ThemeKey.FG_ELEMS),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_biome := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                )
            ),
            horiz_padding=UI_MARGIN_S,
            interactive=False,
        )

        self.gui = GUI(
            self.panel,
            self.hover_panel,
            renderer=draw_elem
        )

        self.back_button = back_button
        self.hide_gui_button = hide_gui_button
        self.seed_label = seed_label
        self.offset_label = offset_label
        self.seed_int_label = seed_int_label

        self.hover_location = hover_location
        self.hover_surface_temp = hover_surface_temp
        self.hover_altitude = hover_altitude
        self.hover_humidity = hover_humidity
        self.hover_altitude = hover_altitude
        self.hover_biome = hover_biome

        self.info_button = info_button
        self.content_vbox = content_vbox
        self.view_modes_button = view_modes_button
        self.view_mode_collapsible = view_mode_collapsible
        self.view_modes_scrollable = view_modes_scrollable
        self.view_modes_vbox = view_modes_vbox
        self.planet_name_label = planet_name_label
        self.gradient_hbox = gradient_hbox

        self.scaled_planet_surface = pg.Surface((WN_W, WN_H))
        self.panel.layout(SCREEN_RECT)

    def _setup_gradients(self) -> None:
        self.gradient_elems = {
            _ViewMode.FANCY: None,
            _ViewMode.WHITE: None,
            _ViewMode.ALTITUDE: GradientScale(
                inset=UI_MARGIN_S,
                gradient_w=UI_MARGIN_S,
                gap=UI_MARGIN_XS,
                max_val=15_000,
                min_val=-15_000,
                labels={
                    val: f"{val:,.0f}"
                    for val in [
                        -15_000, -10_000, -6_000, -3_000, -1_000, -500, -100,
                        0, 100, 500, 1_000, 2_000, 4_000, 6_000, 10_000, 15_000
                    ]
                },
                label_font=self.fonts.tips,
                title_font=self.fonts.text,
                title_text="altitude (m)",
                gradient_anchors=_COLOUR_SCHEMES[_ViewMode.ALTITUDE][0],
                k_bg=ThemeKey.BG_DARK,
                k_fg=ThemeKey.FG_ELEMS,
                value_transform="equidistant"
            ),
            _ViewMode.TEMPERATURE: GradientScale(
                inset=UI_MARGIN_S,
                gradient_w=UI_MARGIN_S,
                gap=UI_MARGIN_XS,
                max_val=10_000,
                min_val=-273.15,
                labels={
                    val: f"{val:,}"
                    for val in [-273.15, -200, -100, -20, 0, 20, 50, 100, 1_000, 10_000]
                },
                label_font=self.fonts.tips,
                title_font=self.fonts.text,
                title_text="temperature (°C)",
                gradient_anchors=_COLOUR_SCHEMES[_ViewMode.TEMPERATURE][0],
                k_bg=ThemeKey.BG_DARK,
                k_fg=ThemeKey.FG_ELEMS,
                value_transform="equidistant",
            ),
            _ViewMode.HUMIDITY: GradientScale(
                inset=UI_MARGIN_S,
                gradient_w=UI_MARGIN_S,
                gap=UI_MARGIN_XS,
                max_val=1,
                min_val=0,
                labels={
                    val: f"{val:.0%}"
                    for val in  [0, 0.2, 0.4, 0.6, 0.8, 1]
                },
                label_font=self.fonts.tips,
                title_font=self.fonts.text,
                title_text="humidity (%)",
                gradient_anchors=_COLOUR_SCHEMES[_ViewMode.HUMIDITY][0],
                k_bg=ThemeKey.BG_DARK,
                k_fg=ThemeKey.FG_ELEMS,
            ),
            _ViewMode.SHADING: GradientScale(
                inset=UI_MARGIN_S,
                gradient_w=UI_MARGIN_S,
                gap=UI_MARGIN_XS,
                max_val=1,
                min_val=-1,
                labels={
                    1: "Towards",
                    0.5: "Mostly Towards",
                    0: "Neutral",
                    -0.5: "Mostly Away",
                    -1: "Away",
                },
                label_font=self.fonts.tips,
                title_font=self.fonts.text,
                title_text="lighting",
                gradient_anchors=_COLOUR_SCHEMES[_ViewMode.SHADING][0],
                k_bg=ThemeKey.BG_DARK,
                k_fg=ThemeKey.FG_ELEMS,
            ),
        }

    def _toggle_gui_visibility(self) -> None:
        currently_visible = self.content_vbox.visible
        self.content_vbox.toggle_visibility()
        self.view_mode_collapsible.toggle_visibility()

        if currently_visible:
            self.hide_gui_button.img_path = self.images.eye
        else:
            self.hide_gui_button.img_path = self.images.eye_crossed_out

    def _refresh_planet_surface(self) -> None:
        planet = self.game.current_planet()
        assert planet.surface is not None
        assert self.game.star_system is not None

        terrain = planet.surface

        if self.view_mode == _ViewMode.FANCY:
            r, g, b = self.game.star_system.star.light_colour
            light_colour = np.array((r, g, b), dtype=np.float32,)
            length = np.linalg.norm(light_colour)
            if length != 0:
                light_colour = light_colour / length * _STARLIGHT_STRENGTH_COEFF

            biome_colours = BIOME_COLOURS[terrain.biomes]
            brightness = terrain.dot_products[..., np.newaxis]
            pixels = (biome_colours + brightness * light_colour)
            pixels = np.clip(pixels, 0, 255).astype(np.uint8)

        elif self.view_mode == _ViewMode.WHITE:
            biome_colours = BIOME_COLOURS[terrain.biomes]
            brightness = terrain.dot_products[..., np.newaxis]
            pixels = (biome_colours + brightness * _WHITE_LIGHT)
            pixels = np.clip(pixels, 0, 255).astype(np.uint8)

        elif self.view_mode == _ViewMode.ALTITUDE:
            pixels = lerp_gradient_array(
                terrain.fields[FieldType.HEIGHT],
                _COLOUR_SCHEMES[_ViewMode.ALTITUDE][1],
            )

        elif self.view_mode == _ViewMode.TEMPERATURE:
            pixels = lerp_gradient_array(
                terrain.fields[FieldType.TEMP] - 273.15,
                _COLOUR_SCHEMES[_ViewMode.TEMPERATURE][1],
            )

        elif self.view_mode == _ViewMode.HUMIDITY:
            pixels = lerp_gradient_array(
                terrain.fields[FieldType.HUMIDITY],
                _COLOUR_SCHEMES[_ViewMode.HUMIDITY][1],
            )

        elif self.view_mode == _ViewMode.SHADING:
            pixels = lerp_gradient_array(
                terrain.dot_products,
                _COLOUR_SCHEMES[_ViewMode.SHADING][1],
            )

        else:
            raise RuntimeError(f"Unknown view mode: {self.view_mode}")

        surface = pg.surfarray.make_surface(pixels.swapaxes(0, 1))

        self.scaled_planet_surface = pg.transform.smoothscale(
            surface,
            (WN_W, WN_H),
        )

    def _refresh_for_new_planet(self) -> None:
        assert self.game.star_system is not None

        # Update labels
        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)

        self.planet_name_label.set_text(self.game.current_planet().name)

        # Layout
        self.panel.layout(SCREEN_RECT)

        # Generate planet surface if not present
        if self.game.current_planet().surface is None:
            self.game.current_planet().generate_surface()

        # Refresh planet surface view
        self._refresh_planet_surface()

    def _refresh_hover_panel(self) -> None:
        planet = self.game.current_planet()
        assert planet.surface is not None

        # Get the cell
        mx, my = pg.mouse.get_pos()
        mx = clamp(mx, 0, WN_W)
        my = clamp(my, 0, WN_H)
        cell_x = int(map_range(mx, 0, WN_W, 0, MAP_WIDTH - 1))
        cell_y = int(map_range(my, 0, WN_H, 0, MAP_HEIGHT - 1))
        cell = planet.surface.info_at(cell_x, cell_y)

        # Refresh panel information
        latitude_degs = map_range(my, 0, WN_H, 90, -90)
        longitude_degs = map_range(mx, 0, WN_W, -180, 180)

        if latitude_degs >= 0:
            latitude_text = f"{latitude_degs:.2f}°N"
        else:
            latitude_text = f"{-latitude_degs:.2f}°S"

        if longitude_degs >= 0:
            longitude_text = f"{longitude_degs:.2f}°E"
        else:
            longitude_text = f"{-longitude_degs:.2f}°W"

        self.hover_location.set_text(f"{latitude_text}, {longitude_text}")
        self.hover_surface_temp.set_text(f"{cell.temp - 273.15:,.2f}°C")
        self.hover_altitude.set_text(f"{cell.height:+,.2f} m")
        self.hover_humidity.set_text(f"{cell.humidity:.2%}")
        self.hover_biome.set_text(f"{BIOME_PROFILES[cell.biome_id].display_name}")

        # Figure out if the panel should be left or right of, and above or below the mouse
        hover_w, hover_h = self.hover_panel.preferred_size()
        right_space, bottom_space = WN_W - mx, WN_H - my

        if right_space >= hover_w + UI_MARGIN_XS:
            left = mx + UI_MARGIN_XS
        else:
            left = mx - hover_w - UI_MARGIN_XS

        if bottom_space >= hover_h + UI_MARGIN_XS:
            top = my + UI_MARGIN_XS
        else:
            top = my - hover_h - UI_MARGIN_XS

        self.hover_panel.layout(pg.Rect(left, top, hover_w, hover_h))

    def on_entered(self) -> None:
        self._refresh_for_new_planet()

    def update(self, dt_s: float) -> None:
        self.gui.update(dt_s)

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        elem = self.gui.hit_test(pg.mouse.get_pos())

        if pg.mouse.get_pressed()[0] and elem is None:
            self._refresh_hover_panel()
            self.hover_panel.visible = True
        else:
            self.hover_panel.visible = False

        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if elem is self.back_button:
                    self.game.enter_state(StateID.BROWSE_SYSTEM)
                elif elem is self.info_button:
                    self.game.enter_state(StateID.PLANET_INFO)
                elif elem is self.hide_gui_button:
                    self._toggle_gui_visibility()
                elif elem is self.view_modes_button:
                    self.view_mode_collapsible.toggle()

                for i, button in enumerate(self.view_modes_vbox.children):
                    if elem is button:
                        old_view_mode = self.view_mode
                        self.view_mode = i
                        if self.view_mode != old_view_mode:
                            if isinstance(self.gradient_hbox.children[0], GradientScale):
                                self.gradient_hbox.rm_child(0)
                            new_scale = self.gradient_elems.get(self.view_mode)  # type: ignore
                            if new_scale is not None:
                                self.gradient_hbox.add_child(new_scale, 0)
                            self._refresh_planet_surface()

            if event.type == pg.MOUSEWHEEL:
                if elem is self.view_modes_scrollable:
                    self.view_modes_scrollable.handle_scroll(event)

            if event.type == pg.MOUSEWHEEL:
                if elem is not None and self.view_modes_scrollable in elem.parents:
                    self.view_modes_scrollable.handle_scroll(event)

        if self.panel.layout_dirty:
            self.panel.layout(SCREEN_RECT)

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])

        # Draw terrain
        screen.blit(self.scaled_planet_surface)

        # Draw overlay panel
        self.gui.draw(screen, self.game.current_theme())
