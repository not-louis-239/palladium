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

import time
from enum import IntEnum
from typing import TYPE_CHECKING

import numpy as np
import pygame as pg
from james import CircleButton, HBox, Label, Panel, Spacer, VBox

from palladium.core.constants import Controls
from palladium.core.custom_types import Colour
from palladium.core.utils import lerp_gradient_array, map_range
from palladium.generation.biomes import BIOME_COLOURS, BIOME_PROFILES
from palladium.generation.planet import Planet
from palladium.generation.terrain_gen import MAP_HEIGHT, MAP_WIDTH
from palladium.gui.constants import (
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
from palladium.gui.themes import TRANSLUCENT_BLACK, ThemeKey
from palladium.gui.utils import (
    draw_transparent_rect,
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
    NORMALS = 5

_NUM_VIEW_MODES = len(_ViewMode)


def _prepare_gradient(gradient: dict[float, Colour]) -> tuple[np.ndarray, np.ndarray]:
    """Turns a gradient of `float`s and `Colour`s into two `np.ndarrays`,
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

_COLOUR_SCHEME_ALTITUDE = _prepare_gradient({  # m -> colour
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
})

_COLOUR_SCHEME_HUMIDITY = _prepare_gradient({  # % -> colour
    0.0:  (150, 150, 145),  # salt flat grey
    0.15: (215, 195, 145),  # desert beige
    0.3:  (225, 220, 145),  # pale prairie yellow
    0.5:  (100, 190, 90),   # spring green
    0.8:  (135, 215, 225),  # light cyan-blue
    1.0:  (20, 75, 190),    # deep ocean blue
})

_COLOUR_SCHEME_TEMPERATURE = _prepare_gradient({  # °C -> colour
    -273.15: (255, 255, 255),  # absolute zero, white
    -150:    (245, 185, 225),  # pale magenta-pink
    -100:    (195, 165, 220),  # pale purple
    -50:     (75, 30, 105),    # dark purple
    -35:     (25, 55, 145),    # dark blue
    -20:     (145, 205, 240),  # pale blue
    0:       (220, 250, 250),  # pale cyan-white
    10:      (100, 210, 175),  # green-cyan
    20:      (100, 210, 80),   # spring green
    30:      (245, 225, 45),   # yellow
    40:      (245, 125, 30),   # orange
    50:      (245, 25, 30),    # bright red
    100:     (145, 10, 20),    # deep scarlet
    500:     (235, 115, 105),  # pale scarlet red
    2_000:   (250, 200, 195),  # very pale red
    10_000:  (255, 240, 235),  # very slightly red off-white
})

_COLOUR_SCHEME_NORMALS = _prepare_gradient({  # dot_product(light, normal) -> colour
    -1.0: (10, 15, 55),      # midnight blue
    -0.5: (65, 25, 90),      # dark purple
     0.0: (165, 75, 125),    # muted magenta
     0.5: (235, 125, 45),    # orange
     1.0: (255, 240, 165),   # pale sunlight yellow
})


class BrowseTerrainState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.view_mode = _ViewMode.FANCY

        self.panel = Panel(
            child=VBox(
                HBox(
                    seed_hbox := HBox(
                        back_button := CircleButton(
                            r=ICON_SIZE // 4,
                            font=self.fonts.text,
                            img_path=self.images.back,
                            k_fg_colour=ThemeKey.FG,
                            k_fg_hovered=ThemeKey.FG_HOVERED,
                            k_fg_active=ThemeKey.FG_ACTIVE
                        ),
                        Spacer(flex=0, min_w=UI_MARGIN_S),
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
                    ),
                    Spacer(),
                ),
            ),
            horiz_padding=UI_MARGIN_M,
            vert_padding=UI_MARGIN_M,
        )

        self.hover_panel = Panel(
            child=VBox(
                hover_location := Label(font=self.fonts.text, k_fg=ThemeKey.FG),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(text="surface temperature:", font=self.fonts.text, k_fg=ThemeKey.FG),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_surface_temp := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                ),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(text="altitude:", font=self.fonts.text, k_fg=ThemeKey.FG),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_altitude := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                ),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(text="humidity:", font=self.fonts.text, k_fg=ThemeKey.FG),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_humidity := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                ),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(text="biome:", font=self.fonts.text, k_fg=ThemeKey.FG),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_biome := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                )
            ),
            vert_padding=UI_MARGIN_S,
            horiz_padding=UI_MARGIN_S,
        )

        self.seed_hbox = seed_hbox
        self.back_button = back_button
        self.seed_label = seed_label
        self.offset_label = offset_label
        self.seed_int_label = seed_int_label

        self.hover_location = hover_location
        self.hover_surface_temp = hover_surface_temp
        self.hover_altitude = hover_altitude
        self.hover_humidity = hover_humidity
        self.hover_altitude = hover_altitude
        self.hover_biome = hover_biome

        self.scaled_planet_surface = pg.Surface((WN_W, WN_H))
        self.panel.layout(SCREEN_RECT)

    def _refresh_planet_surface(self) -> None:
        t_i = time.time()

        planet = self.current_planet()
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
                terrain.heights,
                _COLOUR_SCHEME_ALTITUDE,
            )

        elif self.view_mode == _ViewMode.TEMPERATURE:
            pixels = lerp_gradient_array(
                terrain.temps - 273.15,
                _COLOUR_SCHEME_TEMPERATURE,
            )

        elif self.view_mode == _ViewMode.HUMIDITY:
            pixels = lerp_gradient_array(
                terrain.humidities,
                _COLOUR_SCHEME_HUMIDITY,
            )

        elif self.view_mode == _ViewMode.NORMALS:
            pixels = lerp_gradient_array(
                terrain.dot_products,
                _COLOUR_SCHEME_NORMALS,
            )

        else:
            raise RuntimeError(f"Unknown view mode: {self.view_mode}")

        surface = pg.surfarray.make_surface(pixels.swapaxes(0, 1))

        self.scaled_planet_surface = pg.transform.smoothscale(
            surface,
            (WN_W, WN_H),
        )

        t_f = time.time()
        print(f"Refreshed planet surface in {1000 * (t_f - t_i):.4f} ms")

    def _refresh_for_new_planet(self) -> None:
        assert self.game.star_system is not None

        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)
        self.panel.layout(SCREEN_RECT)

        if self.current_planet().surface is None:
            self.current_planet().generate_surface()

        self._refresh_planet_surface()

    def _refresh_hover_panel(self) -> None:
        planet = self.current_planet()
        assert planet.surface is not None

        # Get the cell
        mx, my = pg.mouse.get_pos()
        cell_x, cell_y = int(MAP_WIDTH * (mx / WN_W)), int(MAP_HEIGHT * (my / WN_H))
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

    def current_planet(self) -> Planet:
        assert self.game.star_system is not None
        assert self.game.planet_idx is not None
        return self.game.star_system.planets[self.game.planet_idx]

    def on_entered(self) -> None:
        self._refresh_for_new_planet()

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.back_button.check_overlaps(event.pos):
                    self.game.enter_state(StateID.BROWSE_SYSTEM)

            if event.type == pg.KEYDOWN and event.key == Controls.CHANGE_VIEW_MODE:
                self.view_mode = (self.view_mode + 1) % _NUM_VIEW_MODES
                self._refresh_planet_surface()

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])

        # Draw terrain
        screen.blit(self.scaled_planet_surface)

        # Draw overlay panel
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.seed_hbox.rect)
        draw_elem(screen, self.panel, self.game.current_theme())

        if pg.mouse.get_pressed()[0]:
            self._refresh_hover_panel()
            draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.hover_panel.rect)
            draw_elem(screen, self.hover_panel, self.game.current_theme())
