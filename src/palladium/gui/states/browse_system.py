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
from dataclasses import dataclass, field
from functools import lru_cache

from typing import TYPE_CHECKING

import numpy as np
import pygame as pg
from james import GUI, CircleButton, Group, HBox, Label, Panel, Spacer, VBox

from palladium.core.units import SPEED_OF_LIGHT, SECOND, YEAR, R_SUN, KM, AU, METRE, LIGHT_YEAR, convert_units
from palladium.core.constants import (
    WN_H,
    WN_W,
    ZOOM_RATE,
    Controls,
)
from palladium.core.utils import clamp
from palladium.generation.generators.star_system_gen import generate_star_system
from palladium.generation.objects.generate_planet import calculate_habitable_zone
from palladium.gui.constants import (
    CIRCLE_RADIUS_DRAW_LIMIT,
    DEFAULT_ATTRS,
    DEFAULT_ATTRS_DARK_BG,
    ICON_SIZE,
    SCREEN_RECT,
    UI_MARGIN_M,
    UI_MARGIN_S,
    UI_MARGIN_XS,
)
from palladium.gui.elements.scale_bar import ScaleBar
from palladium.gui.elements.direction_icon import DirectionIcon
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import CLEAR, ThemeKey
from palladium.gui.utils import star_surface, generate_bg_star_positions, get_seed_messages
from palladium.debug.timer import log_segment

if TYPE_CHECKING:
    from palladium.game.game import Game


SOLAR_RADIUS_PIXELS = 5  # for rendering bodies, a body with 1 solar radius will have this radius in pixels
MAGNITUDE_PIXEL_DIFF = 2  # a 10x difference in size results in this much of a factor of difference
MIN_SIZE = 2  # stars and planets will never be smaller than this
MAX_SIZE = 7

PER_PIXELS = 50
SCALE_BAR_LEVELS: list[float] = [  # astronomical units per `PER_PIXELS` pixels
    0.001, 0.002, 0.005,
    0.01, 0.02, 0.05,
    0.1, 0.2, 0.5,
    1, 2, 5,
    10, 20, 50,
    100, 200, 500,
    1_000, 2_000, 5_000,
    10_000, 20_000
]

# astronomical units per pixel
INNER_ZOOM_LIMIT = 0.00002
OUTER_ZOOM_LIMIT = 80

CENTRE_POS = (WN_W // 2, WN_H // 2)

SPEED_ADJUST_RATE = 10  # factor per second
MAX_SPEED = convert_units(YEAR, SECOND) * 1_000_000  # multiplier
MIN_SPEED = 1

DURATION_UNITS = (
    ("year", convert_units(YEAR, SECOND)),
    ("week", 7 * 24 * 60 * 60),
    ("day", 24 * 60 * 60),
    ("hour", 60 * 60),
    ("minute", 60),
    ("second", 1)
)

SCROLL_SENSITIVITY = 15
SCROLL_SPEED = 800  # pix/s
SCROLL_FRICTION = 0.9  # fraction of scroll velocity dissipated per second

DISTANCE_RINGS: list[float] = [0.001, 0.01, 0.1, 1, 10, 100, 1_000, 10_000, 100_000]   # astronomical units
INNER_RING_DRAW_LIMIT = 10  # only draw a ring if its radius is more than this to avoid overcrowding


STAR_BG_WRAP_BOUNDS_AU = np.array([25_000, 25_000], dtype=np.float32)
STAR_DENSITY = 0.00002  # per au^2 per layer
STAR_BG_WRAP_BOUNDS_AU_ARR = np.asarray(
    STAR_BG_WRAP_BOUNDS_AU,
    dtype=np.float32,
)

HALF_WN_SIZE_ARR = np.array([WN_W / 2, WN_H / 2], dtype=np.float32)

PARALLAX_FACTORS = (
    0.02,
    0.05,
    0.10,
    0.18,
)

STAR_SURFACES = [
    pg.transform.smoothscale_by(star_surface, x / max(PARALLAX_FACTORS))
    for x in PARALLAX_FACTORS
]

EPS = 1e-6


def _format_zoom_value(val: float) -> str:
    return f"{round(val):,.0f}" if val > 1 else str(val)


_SUFFIXES: list[tuple[str, int]] = [
    ("Dc", 1_000_000_000_000_000_000_000_000_000_000_000),
    ("No", 1_000_000_000_000_000_000_000_000_000_000),
    ("Oc", 1_000_000_000_000_000_000_000_000_000),
    ("Sp", 1_000_000_000_000_000_000_000_000),
    ("Sx", 1_000_000_000_000_000_000_000),
    ("Qi", 1_000_000_000_000_000_000),
    ("Qa", 1_000_000_000_000_000),
    ("T", 1_000_000_000_000),
    ("B", 1_000_000_000),
    ("M", 1_000_000),
    ("k", 1_000),
]


def _format_speed_value(val: float) -> str:
    for suffix, min_val in _SUFFIXES:
        if val >= min_val:
            return f"{val / min_val:.2f}{suffix}"
    return f"{val:.2f}"


def _get_bearing_degrees(v: pg.Vector2) -> float:
    """Assuming a bearing of 000°T = upwards."""
    return math.degrees(math.atan2(v.y, v.x))


@lru_cache(maxsize=16)
def _get_star_layers(seed: int) -> list[_StarLayer]:
    """Returns a list of star layers, each containing a set of star positions and parallax values."""
    star_positions = [
        _StarLayer(
            positions := generate_bg_star_positions(
                seed=(seed + i) % 2**63,
                wrap_bounds=(int(STAR_BG_WRAP_BOUNDS_AU[0]), int(STAR_BG_WRAP_BOUNDS_AU[1])),
                star_density_per_pix2=STAR_DENSITY
            ),
            parallax,
            STAR_SURFACES[i],
            indices=np.arange(len(positions), dtype=np.uint32)
        )
        for i, parallax in enumerate(PARALLAX_FACTORS)
    ]

    return star_positions


@lru_cache(maxsize=1024)
def get_num_tiles(zoom_level: float) -> tuple[int, int]:
    """Returns the tile sizes for a given zoom level."""
    tile_size_pix = (STAR_BG_WRAP_BOUNDS_AU_ARR / zoom_level)
    tiles_x = int(np.ceil(WN_W / tile_size_pix[0] / 2)) + 1
    tiles_y = int(np.ceil(WN_H / tile_size_pix[1] / 2)) + 1
    return tiles_x, tiles_y


def _hash_stars(
        layer: _StarLayer,
        tile_x: int,
        tile_y: int,
    ) -> np.ndarray:
    tile_x_hash = np.uint32(tile_x % 2**32)
    tile_y_hash = np.uint32(tile_y % 2**32)

    values = (
        layer.indices
        + tile_x_hash * np.uint32(73856093)
        + tile_y_hash * np.uint32(19349663)
    )

    values ^= values >> np.uint32(13)
    values *= np.uint32(1274126177)
    values ^= values >> np.uint32(16)

    return values


def _get_star_hashes(
    layer: _StarLayer,
    tile_x: int,
    tile_y: int,
) -> np.ndarray:
    key = (tile_x, tile_y)

    if key not in layer.hash_cache:
        layer.hash_cache[key] = _hash_stars(
            layer,
            tile_x,
            tile_y,
        )

    return layer.hash_cache[key]


@dataclass
class _StarLayer:
    positions: np.ndarray
    parallax_value: float
    star_img: pg.Surface
    indices: np.ndarray
    hash_cache: dict[tuple[int, int], np.ndarray] = field(default_factory=dict)  # {(tile_x, tile_y): star_hashes}
    tile_cache: dict[tuple[int, int], np.ndarray] = field(default_factory=dict)  # {(tile_x, tile_y): star_positions}
    cache_zoom: int | None = None


class BrowseSystemState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.work_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)

        self.scroll_disp: pg.Vector2 = pg.Vector2(0, 0)  # astronomical units
        self.scroll_vel: pg.Vector2 = pg.Vector2(0, 0)  # astronomical units per second

        self.zoom_level_au_per_pixel = 0.01  # astronomical units per pixel
        self.run_speed = 86_400  # multiplier
        self.paused = False
        self.light_lock = False  # limit speed to a maximum of 1.00c

        # Making the star button slightly bigger than the displayed star size itself for ease of use
        self.star_button = CircleButton(
            r=0 + UI_MARGIN_S, font=self.fonts.ui,
            **DEFAULT_ATTRS,
        )

        self.overlay_panel = Panel(
            VBox(
                HBox(
                    back_button := CircleButton(
                        **DEFAULT_ATTRS_DARK_BG,
                        r=ICON_SIZE // 2,
                        img_path=self.images.back,
                        font=self.fonts.ui
                    ),
                    Spacer(),
                    Panel(
                        HBox(
                            Label(
                                text="star system ",
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_ELEMS
                            ),
                            seed_label := Label(
                                text="",
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_ACCENT,
                                shrink=1.0,
                            ),
                            offset_label := Label(
                                text="",
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_ACCENT2
                            ),
                            seed_int_label := Label(
                                text="",
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_SENTINEL
                            ),
                        ),
                        k_bg=ThemeKey.BG_DARK,
                        horiz_padding=UI_MARGIN_S,
                        ),
                    Spacer(),
                ),
                Spacer(),
                HBox(
                    light_lock_button := CircleButton(
                        r=ICON_SIZE // 2,
                        img_path=self.images.sun,
                        font=self.fonts.heading,
                        **DEFAULT_ATTRS_DARK_BG,
                        hover_tooltip=Label(
                            text=f"Limit scroll speed to the speed of light",
                            k_bg=ThemeKey.BG_DARK,
                            k_fg=ThemeKey.FG_ELEMS,
                            inset=UI_MARGIN_S,
                            font=self.fonts.text,
                        )
                    ),
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    scroll_hbox := Panel(
                        HBox(
                            scroll_direction_icon := DirectionIcon(
                                k_fg=ThemeKey.FG_ACCENT
                            ),
                            scroll_speed_label := Label(
                                k_fg=ThemeKey.FG_ACCENT,
                                font=self.fonts.text,
                                inset=UI_MARGIN_S
                            )
                        ),
                        k_bg=ThemeKey.BG_DARK
                    ),
                ),
                HBox(
                    coords_label := Label(
                        font=self.fonts.text,
                        k_fg=ThemeKey.FG_ELEMS,
                        inset=UI_MARGIN_S,
                        k_bg=ThemeKey.BG_DARK
                    ),
                ),
                HBox(
                    buttons_hbox := HBox(
                        zoom_in_button := CircleButton(
                            r=ICON_SIZE // 2,
                            img_path=self.images.zoom_in,
                            font=self.fonts.heading,
                            **DEFAULT_ATTRS_DARK_BG,
                        ),
                        zoom_out_button := CircleButton(
                            r=ICON_SIZE // 2,
                            img_path=self.images.zoom_out,
                            font=self.fonts.heading,
                            **DEFAULT_ATTRS_DARK_BG,
                        ),
                        slow_button := CircleButton(
                            r=ICON_SIZE // 2,
                            img_path=self.images.backward,
                            font=self.fonts.heading,
                            **DEFAULT_ATTRS_DARK_BG,
                        ),
                        fast_button := CircleButton(
                            r=ICON_SIZE // 2,
                            img_path=self.images.forward,
                            font=self.fonts.heading,
                            **DEFAULT_ATTRS_DARK_BG,
                        ),
                        recentre_button := CircleButton(
                            r=ICON_SIZE // 2,
                            img_path=self.images.recentre,
                            font=self.fonts.heading,
                            **DEFAULT_ATTRS_DARK_BG,
                        ),
                        gap=UI_MARGIN_S,
                    ),
                    Spacer(),
                ),
                HBox(
                    Panel(
                        HBox(
                            speed_text_label := Label(
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_ELEMS,
                            ),
                            speed_mult_label := Label(
                                font=self.fonts.text,
                                k_fg=ThemeKey.FG_SENTINEL,
                            ),
                        ),
                        horiz_padding=UI_MARGIN_S,
                        k_bg=ThemeKey.BG_DARK,
                    ),
                    Spacer(),
                ),
                HBox(
                    scale_bar := ScaleBar(
                        k_bg=ThemeKey.BG_DARK,
                        k_fg=ThemeKey.FG_ELEMS,
                        bar_width=round(1 / self.zoom_level_au_per_pixel),
                        text="",
                        font=self.fonts.text,
                        inset=UI_MARGIN_S,
                        gap=UI_MARGIN_S
                    ),
                    Spacer(),
                    Label(
                        text="star and planet sizes not to scale",
                        font=self.fonts.text,
                        inset=UI_MARGIN_S,
                        k_bg=ThemeKey.BG_DARK,
                        k_fg=ThemeKey.FG_ELEMS
                    ),
                ),

                gap=UI_MARGIN_S,
            ),
            horiz_padding=UI_MARGIN_M,
            )

        # Bind UI components from the main panel to `self`
        self.back_button = back_button
        self.scale_bar = scale_bar
        self.buttons_hbox = buttons_hbox

        self.zoom_in_button = zoom_in_button
        self.zoom_out_button = zoom_out_button
        self.slow_button = slow_button
        self.fast_button = fast_button
        self.recentre_button = recentre_button

        self.speed_text_label = speed_text_label
        self.speed_mult_label = speed_mult_label

        self.seed_label = seed_label
        self.offset_label = offset_label
        self.seed_int_label = seed_int_label

        self.coords_label = coords_label

        self.scroll_subpanel = scroll_hbox
        self.scroll_direction_icon = scroll_direction_icon
        self.scroll_speed_label = scroll_speed_label
        self.light_lock_button = light_lock_button

        # planet buttons
        self.planet_buttons: Group = Group()
        self.planet_buttons.layout(SCREEN_RECT)

        self.gui = GUI(
            self.overlay_panel,
            self.star_button,
            self.planet_buttons,
            renderer=draw_elem
        )

        # Star/planet hover boxes
        self.hover_box = Panel(
            VBox(
                hover_name := Label(
                    font=self.fonts.ui,
                    k_fg=ThemeKey.FG_ELEMS
                ),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(font=self.fonts.text, k_fg=ThemeKey.FG_ELEMS, text="surface temperature:"),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_label_temp := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                ),
                Spacer(flex=0, min_h=UI_MARGIN_XS),
                Label(font=self.fonts.text, k_fg=ThemeKey.FG_ELEMS, text="radius:"),
                HBox(
                    Spacer(flex=0, min_w=UI_MARGIN_S),
                    hover_label_radius := Label(font=self.fonts.text, k_fg=ThemeKey.FG_ACCENT),
                ),
            ),
            horiz_padding=UI_MARGIN_S,
        )

        self.hover_name = hover_name
        self.hover_label_radius = hover_label_radius
        self.hover_label_temp = hover_label_temp

        # Habitable zone setup
        self.hz_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)

        # refresh labels
        self._adjust_zoom(self.zoom_level_au_per_pixel)
        self._adjust_speed(self.run_speed)
        self._update_scroll_subpanel()
        self._update_light_lock_button_appearance()

    def _update_light_lock_button_appearance(self) -> None:
        if self.light_lock:
            self.light_lock_button.k_fg_colour = ThemeKey.FG_ACCENT
            self.light_lock_button.k_fg_hovered = ThemeKey.FG_ACCENT_HOVERED
            self.light_lock_button.k_fg_pressed = ThemeKey.FG_ACCENT_PRESSED
        else:
            self.light_lock_button.k_fg_colour = ThemeKey.FG_SENTINEL
            self.light_lock_button.k_fg_hovered = ThemeKey.FG_SENTINEL_HOVERED
            self.light_lock_button.k_fg_pressed = ThemeKey.FG_SENTINEL_PRESSED

    def _update_scroll_subpanel(self) -> None:
        if self.scroll_vel.length() < EPS:
            self.scroll_subpanel.hide()
            return

        speed_au_per_s = self.scroll_vel.length() / self.run_speed

        if speed_au_per_s > convert_units(SPEED_OF_LIGHT, AU / SECOND) * 0.01:
            # Show readout in multiples of the speed of light.
            speed_c = speed_au_per_s / convert_units(SPEED_OF_LIGHT, AU / SECOND)
            text = f"{_format_speed_value(speed_c)} c"
        else:
            # Show readout in metres per second
            speed_m_per_s = speed_au_per_s * convert_units(AU, METRE)
            if speed_m_per_s > 1_000.0:
                text = f"{speed_m_per_s / 1_000.0:,.2f} km/s"
            else:
                text = f"{speed_m_per_s:,.2f} m/s"

        self.scroll_subpanel.show()
        self.scroll_speed_label.set_text(text)

        # Quantise to int to avoid generating a ton of images for super similar angles.
        # This is also why the internal cache inside the module containing
        # `DirectionIcon` does not accept `float`s for rotation.
        self.scroll_direction_icon.set_bearing(int(_get_bearing_degrees(self.scroll_vel)) + 90)

    def _refresh_star_positions(self) -> None:
        if self.game.star_system is None:
            # Just initialise some dummy values
            self.star_positions = None
            return

        star_seed = self.game.star_system.seed_metadata.integer_value
        self.star_positions = _get_star_layers(star_seed)

    def _scaled_body_pos(self, orbit_angle_rads: float, orbit_radius: float, body_radius: float):
        """
        Expects:

        orbit_angle_rads: angle of the planet along its orbit in radians
        orbit_radius: radius of the planet's orbit in solar radii
        body_radius: radius of the planet in solar radii

        Returns (x, y, r) where:

        x is the x-position, in pixels, in screen space
        y is the y-position, in pixels, in screen space
        r is the radius, in pixels, in screen space

        Accounts for logarithmic scaling of bodies
        """
        orbit_radius_au = (orbit_radius * convert_units(R_SUN, AU))
        x = CENTRE_POS[0] + (-self.scroll_disp[0] - math.cos(orbit_angle_rads) * orbit_radius_au) / self.zoom_level_au_per_pixel
        y = CENTRE_POS[1] + (-self.scroll_disp[1] + math.sin(orbit_angle_rads) * orbit_radius_au) / self.zoom_level_au_per_pixel
        r = clamp(SOLAR_RADIUS_PIXELS * MAGNITUDE_PIXEL_DIFF ** math.log10(body_radius), MIN_SIZE, MAX_SIZE)

        return (x, y, r)

    def _adjust_zoom(self, new_zoom: float) -> None:
        """Adjust zoom and refresh labels"""

        # Clamp and set zoom
        new_zoom = clamp(new_zoom, INNER_ZOOM_LIMIT, OUTER_ZOOM_LIMIT)
        self.zoom_level_au_per_pixel = new_zoom

        # Set the scale bar to an appropriate level
        scale = SCALE_BAR_LEVELS[0]  # number of astronomical units represented by the scale bar
        for candidate_scale in SCALE_BAR_LEVELS:
            if candidate_scale / self.zoom_level_au_per_pixel > PER_PIXELS:
                scale = candidate_scale
                break

        bar_w = scale / self.zoom_level_au_per_pixel
        bar_zoom_str = _format_zoom_value(scale)
        self.scale_bar.text = f"{bar_zoom_str} astronomical unit{'' if scale == 1 else 's'}"
        self.scale_bar.bar_width = int(bar_w)

        self.overlay_panel.layout(SCREEN_RECT)

        if self.game.star_system is not None:
            self._refresh_body_buttons()

    def _adjust_speed(self, new_speed: float) -> None:
        self.run_speed = clamp(new_speed, MIN_SPEED, MAX_SPEED)

        if self.run_speed == 1:
            self.speed_text_label.set_text("real time speed")
            self.speed_mult_label.set_text("")
        else:
            for unit in DURATION_UNITS:
                name, num_seconds = unit
                if (num_units := self.run_speed / num_seconds) >= 1:

                    text = f"{num_units:,.2f} {name}{'' if 1 <= num_units < 1.005 else 's'}"
                    speed_text = f"1 second = {text}"
                    break
            else:
                speed_text = f"1 second = {self.run_speed} seconds"

            self.speed_text_label.set_text(speed_text)
            self.speed_mult_label.set_text(f" (×{_format_speed_value(self.run_speed)})")

        self.overlay_panel.layout(SCREEN_RECT)

    def _refresh_for_new_system(self) -> None:
        """Refresh UI when regenerating star system or scrolling through offsets"""

        assert self.game.star_system is not None

        # Refresh seed labels
        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)

        # Refresh planet stats
        self.planet_buttons.clear_children()
        for i in range(len(self.game.star_system.planets)):
            self.planet_buttons.add_child(CircleButton(
                r=0, font=self.fonts.text, **DEFAULT_ATTRS,
            ))

        self._refresh_body_buttons()
        self._refresh_star_positions()

        # Refresh overlay panel layout
        self.overlay_panel.layout(SCREEN_RECT)

        # Cancel scroll displacement and velocity
        self.scroll_disp.update(0, 0)
        self.scroll_vel.update(0, 0)

    def _refresh_with_seed_offset(self, offset: int) -> None:
        assert self.game.star_system is not None

        seed_string = self.game.star_system.seed_metadata.display_str

        if self.game.star_system.seed_metadata.is_string:
            star_system = generate_star_system(seed_string, offset)
        else:
            star_system = generate_star_system(int(seed_string) + offset, 0)
        self.game.star_system = star_system

        self._refresh_for_new_system()

    def _refresh_body_buttons(self) -> None:
        assert self.game.star_system is not None

        x, y, star_r = self._scaled_body_pos(0, 0, self.game.star_system.star.radius)
        self.star_button.r = int(star_r) + UI_MARGIN_S
        self.star_button.layout(pg.Rect(x - star_r, y - star_r, 2 * star_r, 2 * star_r))

        for i, planet in enumerate(self.game.star_system.planets):
            x, y, r = self._scaled_body_pos(planet.orbit_phase, planet.orbit_radius, planet.radius)
            r = int(r + UI_MARGIN_S)

            button = self.planet_buttons[i]
            assert isinstance(button, CircleButton)
            button.r = r
            button.layout(pg.Rect(x - r, y - r, 2 * r, 2 * r))

    def _refresh_hover_labels(self, name: str, temp: float, radius: float) -> None:
        """
        Expects:

        name
        temp in °K
        radius in solar radii
        """

        self.hover_name.set_text(name)
        self.hover_label_temp.set_text(f"{temp - 273.15:,.2f}°C")
        self.hover_label_radius.set_text(f"{radius * convert_units(R_SUN, KM):,.0f} km")

        hover_w, hover_h = self.hover_box.preferred_size()

        # Evaluate whether the hover panel needs to be left or right of, and above or below the cursor
        # Prefer bottom and right, unless there isn't enough space
        mx, my = pg.mouse.get_pos()
        right_space, bottom_space = WN_W - mx, WN_H - my

        if right_space >= hover_w + UI_MARGIN_XS:
            left = mx + UI_MARGIN_XS
        else:
            left = mx - hover_w - UI_MARGIN_XS

        if bottom_space >= hover_h + UI_MARGIN_XS:
            top = my + UI_MARGIN_XS
        else:
            top = my - hover_h - UI_MARGIN_XS

        self.hover_box.layout(pg.Rect(left, top, hover_w, hover_h))

    def _calculate_tile_stars(
            self,
            layer: _StarLayer,
            zoom: float,
            tile_x: int,
            tile_y: int,
        ) -> np.ndarray:
            """Return the indices of stars appearing in a world tile."""

            tile_size = STAR_BG_WRAP_BOUNDS_AU_ARR

            # World-space bounds of this tile.
            min_x = tile_x * tile_size[0]
            max_x = (tile_x + 1) * tile_size[0]

            min_y = tile_y * tile_size[1]
            max_y = (tile_y + 1) * tile_size[1]

            positions = layer.positions

            candidate = (
                (positions[:, 0] >= min_x)
                & (positions[:, 0] < max_x)
                & (positions[:, 1] >= min_y)
                & (positions[:, 1] < max_y)
            )

            candidate_indices = np.flatnonzero(candidate)

            if not candidate_indices.size:
                return candidate_indices

            # Density culling.
            density_factor = 1 / zoom**2

            if density_factor < 1.0:
                density_threshold = np.uint32(
                    density_factor * (2**32 - 1)
                )

                values = (
                    layer.indices[candidate_indices]
                    + np.uint32(tile_x % 2**32) * np.uint32(73856093)
                    + np.uint32(tile_y % 2**32) * np.uint32(19349663)
                )

                values ^= values >> np.uint32(13)
                values *= np.uint32(1274126177)
                values ^= values >> np.uint32(16)

                candidate_indices = candidate_indices[
                    values < density_threshold
                ]

            return candidate_indices

    def _draw_stars(self, screen: pg.Surface, layer: _StarLayer) -> None:
        # Density factor needs to be quadratic as zooming out by a factor of N
        # shows N^2 more stars, so this compensates.

        log_segment()

        # Camera / density factor
        zoom = self.zoom_level_au_per_pixel
        density_factor = 1 / zoom ** 2
        density_threshold = np.uint32(min(1, density_factor) * (2**32 - 1))
        tiles_x, tiles_y = get_num_tiles(zoom_level=self.zoom_level_au_per_pixel)
        tile_size_pix = (STAR_BG_WRAP_BOUNDS_AU_ARR / self.zoom_level_au_per_pixel)  # size of 1 star tile in pixels

        # Scroll offset in tiles
        bg_scroll_offset = self.scroll_disp * layer.parallax_value
        scroll_offset_tiles_x: int = math.floor(bg_scroll_offset.x / STAR_BG_WRAP_BOUNDS_AU_ARR[0])
        scroll_offset_tiles_y: int = math.floor(bg_scroll_offset.y / STAR_BG_WRAP_BOUNDS_AU_ARR[1])

        # Positioning - convert to screen space while we're at it
        screen_positions = (
            (layer.positions - (np.asarray(bg_scroll_offset) % STAR_BG_WRAP_BOUNDS_AU))
            / self.zoom_level_au_per_pixel
        )

        min_bound = -star_surface.get_width()

        log_segment("pre-loop")

        for dx in range(-tiles_x, tiles_x + 1):
            log_segment("calculating x values")

            # Calculate X-offsets and values
            offset_x = dx * tile_size_pix[0]

            x_positions = screen_positions[:, 0] + offset_x
            x_candidate = (
                (x_positions >= min_bound - HALF_WN_SIZE_ARR[0])
                & (x_positions <= WN_W - HALF_WN_SIZE_ARR[0])
            )

            if not x_candidate.size:
                continue

            tile_x = dx + scroll_offset_tiles_x
            x_indices = np.flatnonzero(x_candidate)
            y = screen_positions[x_indices, 1]

            for dy in range(-tiles_y, tiles_y + 1):
                log_segment("beginning inner loop")

                # Calculate Y-offsets and values
                offset_y = dy * tile_size_pix[1]

                # Cull by screen bounds
                candidate_indices = x_indices[
                    (y >= min_bound - offset_y - HALF_WN_SIZE_ARR[1])
                    & (y <= WN_H - offset_y - HALF_WN_SIZE_ARR[1])
                ]

                if not candidate_indices.size:
                    continue

                log_segment("candidate filtering")

                # Pseudo-random hashing and density culling
                if density_factor < 1.0:
                    tile_y = dy + scroll_offset_tiles_y
                    hashes = _get_star_hashes(layer, tile_x, tile_y)
                    keep = hashes[candidate_indices] < density_threshold
                    candidate_indices = candidate_indices[keep]

                log_segment("hashing")

                if not (tile_blits := screen_positions[candidate_indices]).size:
                    # No blits, so don't bother calculating offset.
                    continue

                # Account for tile offset
                tile_blits = tile_blits.copy()
                tile_blits[:, 0] += offset_x
                tile_blits[:, 1] += offset_y
                log_segment("accounting for offset")

                print(f"Tile blits shape: {tile_blits.shape}")
                print(f"Tile blits size: {tile_blits.size}")

                # Blit the star images
                # Compensate for the width of the star surface
                # and make sure that the positions converge at the centre
                screen.fblits([
                    (layer.star_img, b)
                    for b in (tile_blits + HALF_WN_SIZE_ARR - star_surface.get_width() / 2)
                ])

                log_segment("blitting")


    def on_entered(self) -> None:
        # shouldn't be None if entered properly
        self._refresh_for_new_system()

    def update(self, dt_s: float) -> None:
        assert self.game.star_system is not None

        # Flip the y-coordinate in the display so that +y = upwards.
        s_x, s_y = self.scroll_disp.x, -self.scroll_disp.y

        if abs(s_x) > convert_units(LIGHT_YEAR, AU):
            x_text = f"{s_x / convert_units(LIGHT_YEAR, AU):,.2f} ly"
        else:
            x_text = f"{s_x:,.2f} au"

        if abs(s_y) > convert_units(LIGHT_YEAR, AU):
            y_text = f"{s_y / convert_units(LIGHT_YEAR, AU):,.2f} ly"
        else:
            y_text = f"{s_y:,.2f} au"

        self.coords_label.set_text(f"({x_text}, {y_text})")
        self._update_scroll_subpanel()

        if self.overlay_panel.layout_dirty:
            self.overlay_panel.layout(SCREEN_RECT)

        self.gui.update(dt_s)
        self.scroll_disp += self.scroll_vel * dt_s
        self.scroll_vel *= (1 - SCROLL_FRICTION) ** dt_s

        if self.scroll_vel.length() < EPS:
            self.scroll_vel.update(0, 0)

        if self.light_lock:
            c_au = convert_units(SPEED_OF_LIGHT, AU / SECOND) * self.run_speed
            if self.scroll_vel.length() > c_au:
                self.scroll_vel = self.scroll_vel.clamp_magnitude(c_au)

        self._refresh_body_buttons()

        if self.paused:
            return

        for planet in self.game.star_system.planets:
            # TODO: how to make motion blur to avoid planets clipping or reversing their orbits visually?
            # hold up, I have an idea
            # draw copies at a fixed distance behind it
            # but the faster it is, the lower the alpha falloff
            # past a certain point, just draw a ring of motion blur
            planet.orbit_phase += self.run_speed * planet.orbit_direction * (2 * math.pi) * dt_s / planet.orbit_duration
            planet.orbit_phase %= (2 * math.pi)

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        assert self.game.star_system is not None

        elem = self.gui.hit_test(pg.mouse.get_pos())

        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if elem is self.back_button:
                    self.game.enter_state(StateID.ENTER_SEED)
                    return
                if elem is self.star_button:
                    self.game.enter_state(StateID.BROWSE_STAR)
                    return
                if elem is self.recentre_button:
                    self.scroll_disp.update(0, 0)
                    self.scroll_vel.update(0, 0)
                if elem is self.light_lock_button:
                    self.light_lock = not self.light_lock
                    self._update_light_lock_button_appearance()
                for i, button in enumerate(self.planet_buttons):
                    if elem is button:
                        self.game.planet_idx = i
                        self.game.enter_state(StateID.BROWSE_TERRAIN)
                        return

            if event.type == pg.KEYDOWN and event.key == Controls.SEED_MINUS_ONE:
                self._refresh_with_seed_offset(self.game.star_system.seed_metadata.offset - 1)
            if event.type == pg.KEYDOWN and event.key == Controls.SEED_PLUS_ONE:
                self._refresh_with_seed_offset(self.game.star_system.seed_metadata.offset + 1)

            if event.type == pg.KEYDOWN and event.key == Controls.PAUSE_SIMULATION:
                self.paused = not self.paused
                if self.paused:
                    self.speed_text_label.text = ""
                    self.speed_mult_label.text = "simulation paused"
                    self.overlay_panel.layout(SCREEN_RECT)
                else:
                    self._adjust_speed(self.run_speed)
            if event.type == pg.MOUSEWHEEL:
                self.scroll_vel.x += event.x * SCROLL_SENSITIVITY * self.zoom_level_au_per_pixel
                self.scroll_vel.y -= event.y * SCROLL_SENSITIVITY * self.zoom_level_au_per_pixel

                if self.light_lock:
                    c_au = convert_units(SPEED_OF_LIGHT, AU / SECOND) * self.run_speed
                    if self.scroll_vel.length() > c_au:
                        self.scroll_vel = self.scroll_vel.clamp_magnitude(c_au)

        if pg.mouse.get_pressed()[0]:
            if elem is self.zoom_in_button:
                self._adjust_zoom(self.zoom_level_au_per_pixel / ZOOM_RATE ** dt_s)
            if elem is self.zoom_out_button:
                self._adjust_zoom(self.zoom_level_au_per_pixel * ZOOM_RATE ** dt_s)
            if elem is self.fast_button:
                self._adjust_speed(self.run_speed * SPEED_ADJUST_RATE ** dt_s)
            if elem is self.slow_button:
                self._adjust_speed(self.run_speed / SPEED_ADJUST_RATE ** dt_s)

        for button, value, bound in (
            (self.zoom_out_button, self.zoom_level_au_per_pixel, OUTER_ZOOM_LIMIT),
            (self.zoom_in_button, self.zoom_level_au_per_pixel, INNER_ZOOM_LIMIT),
            (self.fast_button, self.run_speed, MAX_SPEED),
            (self.slow_button, self.run_speed, MIN_SPEED),
        ):
            button.disabled = value == bound

            if button.disabled:
                button.k_fg_colour = ThemeKey.FG_SENTINEL
                button.k_fg_hovered = ThemeKey.FG_SENTINEL
                button.k_fg_pressed = ThemeKey.FG_SENTINEL
            else:
                button.k_fg_colour = ThemeKey.FG_ELEMS
                button.k_fg_hovered = ThemeKey.FG_HOVERED
                button.k_fg_pressed = ThemeKey.FG_PRESSED

    def draw(self, screen: pg.Surface) -> None:
        assert self.game.star_system is not None

        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])

        # Draw the stars
        if self.star_positions is not None:
            for layer in self.star_positions:
                self._draw_stars(screen, layer)

        # Draw the habitable zone
        centre_x = CENTRE_POS[0] - self.scroll_disp.x / self.zoom_level_au_per_pixel
        centre_y = CENTRE_POS[1] - self.scroll_disp.y / self.zoom_level_au_per_pixel

        inner, outer = calculate_habitable_zone(self.game.star_system.star.luminosity)
        inner_r, outer_r = inner / self.zoom_level_au_per_pixel, outer / self.zoom_level_au_per_pixel

        if outer_r < CIRCLE_RADIUS_DRAW_LIMIT:
            self.hz_surface.fill(CLEAR)
            pg.draw.circle(self.hz_surface, self.game.current_theme()[ThemeKey.FG_HABITABLE_ZONE], (centre_x, centre_y), outer_r)
            pg.draw.circle(self.hz_surface, CLEAR, (centre_x, centre_y), inner_r)
            screen.blit(self.hz_surface)

        # Draw the star system

        # self.game.star_system should not be None if this state was entered properly
        assert self.game.star_system is not None

        # Draw star and planet buttons
        self.work_surface.fill(CLEAR)
        draw_elem(self.work_surface, self.star_button, self.game.current_theme())
        for button in self.planet_buttons:
            draw_elem(self.work_surface, button, self.game.current_theme())

        screen.blit(self.work_surface)

        # Draw distance rings
        for distance in DISTANCE_RINGS:
            radius = distance / self.zoom_level_au_per_pixel
            if INNER_RING_DRAW_LIMIT < radius < CIRCLE_RADIUS_DRAW_LIMIT:
                # TODO: eventually use pg.draw.arc hopefully so that I can draw the rings at any distance
                # without compromising performance
                # or just blit a portion of a larger circle
                pg.draw.circle(screen, self.game.current_theme()[ThemeKey.FG_SENTINEL], (centre_x, centre_y), radius, 1)

                text_bottom = centre_y - radius - UI_MARGIN_XS
                text_surf = self.fonts.tips.render(
                    f"{_format_zoom_value(distance)} au",
                    True, self.game.current_theme()[ThemeKey.FG_SENTINEL]
                )

                screen.blit(text_surf, text_surf.get_rect(centerx=centre_x, bottom=text_bottom))

        # Draw planets
        for planet in self.game.star_system.planets:
            x, y, r = self._scaled_body_pos(planet.orbit_phase, planet.orbit_radius, planet.radius)
            # TODO: colour planets according to composition and properties
            # could use preset sprites for this, but for now we'll make it a constant colour
            pg.draw.circle(screen, (0, 255, 130), (x, y), r)

        # Drawing the star at a logarithmic scale so that the system remains visible
        # but it shouldn't go below a minimum size
        x, y, r = self._scaled_body_pos(0, 0, self.game.star_system.star.radius)
        temp_colour = self.game.star_system.star.light_colour
        pg.draw.circle(screen, temp_colour, (x, y), r)

        # Draw UI
        self.work_surface.fill(CLEAR)
        self.gui.draw(self.work_surface, self.game.current_theme())
        screen.blit(self.work_surface, (0, 0))

        elem = self.gui.hit_test(pg.mouse.get_pos())

        # Draw hover boxes over planets or stars
        if elem is self.star_button:
            self._refresh_hover_labels(
                name=self.game.star_system.star.name,
                temp=self.game.star_system.star.temp,
                radius=self.game.star_system.star.radius
            )
            draw_elem(screen, self.hover_box, self.game.current_theme())
        else:
            for planet, button in zip(self.game.star_system.planets, self.planet_buttons):
                if elem is button:
                    self._refresh_hover_labels(
                        name=planet.name,
                        temp=planet.displayed_surface_temp,
                        radius=planet.radius
                    )
                    draw_elem(screen, self.hover_box, self.game.current_theme())
                    break
