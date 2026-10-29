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
from james import (
    GUI,
    CircleButton,
    Collapsible,
    HBox,
    Label,
    Panel,
    ScrollableDisplay,
    Spacer,
    VBox,
)

from palladium.core.utils import clamp, lerp_gradient_array, map_range
from palladium.generation.biomes.biomes import BIOME_COLOURS, BIOME_PROFILES
from palladium.generation.objects.field_types import FieldType
from palladium.generation.objects.terrain_surface import MAP_HEIGHT, MAP_WIDTH
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
from palladium.gui.elements.gradient_scale import GradientScale
from palladium.gui.renderer import draw_elem
from palladium.gui.view_colour_schemes import COLOUR_SCHEMES, ViewMode
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import ThemeKey
from palladium.gui.utils import (
    get_seed_messages,
)

if TYPE_CHECKING:
    from palladium.game.game import Game


_WHITE_LIGHT = (30, 30, 30)
_STARLIGHT_STRENGTH_COEFF = 50

class BrowseTerrainState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.view_mode = ViewMode.FANCY
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
            ViewMode.FANCY: None,
            ViewMode.WHITE: None,
            ViewMode.ALTITUDE: GradientScale(
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
                gradient_anchors=COLOUR_SCHEMES[ViewMode.ALTITUDE][0],
                k_bg=ThemeKey.BG_DARK,
                k_fg=ThemeKey.FG_ELEMS,
                value_transform="equidistant"
            ),
            ViewMode.TEMPERATURE: GradientScale(
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
                gradient_anchors=COLOUR_SCHEMES[ViewMode.TEMPERATURE][0],
                k_bg=ThemeKey.BG_DARK,
                k_fg=ThemeKey.FG_ELEMS,
                value_transform="equidistant",
            ),
            ViewMode.HUMIDITY: GradientScale(
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
                gradient_anchors=COLOUR_SCHEMES[ViewMode.HUMIDITY][0],
                k_bg=ThemeKey.BG_DARK,
                k_fg=ThemeKey.FG_ELEMS,
            ),
            ViewMode.SHADING: GradientScale(
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
                gradient_anchors=COLOUR_SCHEMES[ViewMode.SHADING][0],
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

        if self.view_mode == ViewMode.FANCY:
            r, g, b = self.game.star_system.star.light_colour
            light_colour = np.array((r, g, b), dtype=np.float32,)
            length = np.linalg.norm(light_colour)
            if length != 0:
                light_colour = light_colour / length * _STARLIGHT_STRENGTH_COEFF

            biome_colours = BIOME_COLOURS[terrain.biomes]
            brightness = terrain.dot_products[..., np.newaxis]
            pixels = (biome_colours + brightness * light_colour)
            pixels = np.clip(pixels, 0, 255).astype(np.uint8)

        elif self.view_mode == ViewMode.WHITE:
            biome_colours = BIOME_COLOURS[terrain.biomes]
            brightness = terrain.dot_products[..., np.newaxis]
            pixels = (biome_colours + brightness * _WHITE_LIGHT)
            pixels = np.clip(pixels, 0, 255).astype(np.uint8)

        elif self.view_mode == ViewMode.ALTITUDE:
            pixels = lerp_gradient_array(
                terrain.fields[FieldType.HEIGHT],
                COLOUR_SCHEMES[ViewMode.ALTITUDE][1],
            )

        elif self.view_mode == ViewMode.TEMPERATURE:
            pixels = lerp_gradient_array(
                terrain.fields[FieldType.TEMP] - 273.15,
                COLOUR_SCHEMES[ViewMode.TEMPERATURE][1],
            )

        elif self.view_mode == ViewMode.HUMIDITY:
            pixels = lerp_gradient_array(
                terrain.fields[FieldType.HUMIDITY],
                COLOUR_SCHEMES[ViewMode.HUMIDITY][1],
            )

        elif self.view_mode == ViewMode.SHADING:
            pixels = lerp_gradient_array(
                terrain.dot_products,
                COLOUR_SCHEMES[ViewMode.SHADING][1],
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
                if elem is not None and (
                    self.view_modes_scrollable in elem.parents
                    or elem is self.view_modes_scrollable
                ):
                    self.view_modes_scrollable.handle_scroll(event)

        if self.panel.layout_dirty:
            self.panel.layout(SCREEN_RECT)

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])

        # Draw terrain
        screen.blit(self.scaled_planet_surface)

        # Draw overlay panel
        self.gui.draw(screen, self.game.current_theme())
