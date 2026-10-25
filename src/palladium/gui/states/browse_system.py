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
from typing import TYPE_CHECKING

import pygame as pg
from james import CircleButton, HBox, Label, Panel, Spacer, VBox, GUI, Group

from palladium.core.constants import (
    SECONDS_PER_YEAR,
    SOLAR_RADIUS_IN_AU,
    SOLAR_RADIUS_IN_KM,
    WN_H,
    WN_W,
    ZOOM_RATE,
    Controls,
)
from palladium.core.utils import clamp
from palladium.generation.planet import calculate_habitable_zone
from palladium.generation.star_system import generate_star_system
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
from palladium.gui.renderer import draw_elem
from palladium.gui.states.base import State, StateID
from palladium.gui.themes import CLEAR, ThemeKey
from palladium.gui.utils import (
    get_seed_messages,
)

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
    10_000
]

# astronomical units per pixel
INNER_ZOOM_LIMIT = 0.00002
OUTER_ZOOM_LIMIT = 100

CENTRE_POS = (WN_W // 2, WN_H // 2)

SPEED_ADJUST_RATE = 10  # factor per second
MAX_SPEED = SECONDS_PER_YEAR * 1_000_000  # multiplier
MIN_SPEED = 1

DURATION_UNITS = (
    ("year", SECONDS_PER_YEAR),
    ("week", 7 * 24 * 60 * 60),
    ("day", 24 * 60 * 60),
    ("hour", 60 * 60),
    ("minute", 60),
    ("second", 1)
)

SCROLL_SENSITIVITY = 15
SCROLL_SPEED = 800  # pix/s
SCROLL_FRICTION = 0.9  # fraction of scroll velocity dissipated per second

DISTANCE_RINGS: list[float] = [0.001, 0.01, 0.1, 1, 10, 100, 1_000, 10_000]   # astronomical units
INNER_RING_DRAW_LIMIT = 10  # only draw a ring if its radius is more than this to avoid overcrowding


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


class BrowseSystemState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.work_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)

        # astronomical units
        self.scroll_disp = pg.Vector2(0, 0)
        self.scroll_vel = pg.Vector2(0, 0)

        self.zoom_level = 0.01  # astronomical units per pixel
        self.run_speed = 86_400  # multiplier
        self.paused = False

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
                        bar_width=round(1 / self.zoom_level),
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

                # TODO: add buttons: re-centre, 'click and drag' instruction

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
        self._adjust_zoom(self.zoom_level)
        self._adjust_speed(self.run_speed)

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
        orbit_radius_au = (orbit_radius * SOLAR_RADIUS_IN_AU)
        x = CENTRE_POS[0] + (-self.scroll_disp[0] - math.cos(orbit_angle_rads) * orbit_radius_au) / self.zoom_level
        y = CENTRE_POS[1] + (-self.scroll_disp[1] + math.sin(orbit_angle_rads) * orbit_radius_au) / self.zoom_level
        r = clamp(SOLAR_RADIUS_PIXELS * MAGNITUDE_PIXEL_DIFF ** math.log10(body_radius), MIN_SIZE, MAX_SIZE)

        return (x, y, r)

    def _adjust_zoom(self, new_zoom: float) -> None:
        """Adjust zoom and refresh labels"""

        # Clamp and set zoom
        new_zoom = clamp(new_zoom, INNER_ZOOM_LIMIT, OUTER_ZOOM_LIMIT)
        self.zoom_level = new_zoom

        # Set the scale bar to an appropriate level
        scale = SCALE_BAR_LEVELS[0]  # number of astronomical units represented by the scale bar
        for candidate_scale in SCALE_BAR_LEVELS:
            if candidate_scale / self.zoom_level > PER_PIXELS:
                scale = candidate_scale
                break

        bar_w = scale / self.zoom_level
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

    def _refresh_ui_for_new_system(self) -> None:
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

        self._refresh_ui_for_new_system()

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
        self.hover_label_radius.set_text(f"{radius * SOLAR_RADIUS_IN_KM:,.0f} km")

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

    def on_entered(self) -> None:
        # shouldn't be None if entered properly
        self._refresh_ui_for_new_system()

    def update(self, dt_s: float) -> None:
        assert self.game.star_system is not None

        self.gui.update(dt_s)
        self.scroll_disp += self.scroll_vel * dt_s
        self.scroll_vel *= (1 - SCROLL_FRICTION) ** dt_s
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
                for i, button in enumerate(self.planet_buttons):
                    if elem is button:
                        self.game.planet_idx = i
                        self.game.enter_state(StateID.BROWSE_TERRAIN)
                        return
                if elem is self.recentre_button:
                    self.scroll_disp.update(0, 0)

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
                self.scroll_vel.x += event.x * SCROLL_SENSITIVITY * self.zoom_level
                self.scroll_vel.y -= event.y * SCROLL_SENSITIVITY * self.zoom_level

        if pg.mouse.get_pressed()[0]:
            if elem is self.zoom_in_button:
                self._adjust_zoom(self.zoom_level / ZOOM_RATE ** dt_s)
            if elem is self.zoom_out_button:
                self._adjust_zoom(self.zoom_level * ZOOM_RATE ** dt_s)
            if elem is self.fast_button:
                self._adjust_speed(self.run_speed * SPEED_ADJUST_RATE ** dt_s)
            if elem is self.slow_button:
                self._adjust_speed(self.run_speed / SPEED_ADJUST_RATE ** dt_s)

        for button, value, bound in (
            (self.zoom_out_button, self.zoom_level, OUTER_ZOOM_LIMIT),
            (self.zoom_in_button, self.zoom_level, INNER_ZOOM_LIMIT),
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

        # Draw the habitable zone
        centre_x = CENTRE_POS[0] - self.scroll_disp.x / self.zoom_level
        centre_y = CENTRE_POS[1] - self.scroll_disp.y / self.zoom_level

        inner, outer = calculate_habitable_zone(self.game.star_system.star.luminosity)
        inner_r, outer_r = inner / self.zoom_level, outer / self.zoom_level

        if outer_r < CIRCLE_RADIUS_DRAW_LIMIT:
            self.hz_surface.fill(CLEAR)
            pg.draw.circle(self.hz_surface, self.game.current_theme()[ThemeKey.FG_HABITABLE_ZONE], (centre_x, centre_y), outer_r)
            pg.draw.circle(self.hz_surface, CLEAR, (centre_x, centre_y), inner_r)
            screen.blit(self.hz_surface)

        # TODO: add star background parallax effect

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
            radius = distance / self.zoom_level
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
        draw_elem(self.work_surface, self.overlay_panel, self.game.current_theme())
        screen.blit(self.work_surface)

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
