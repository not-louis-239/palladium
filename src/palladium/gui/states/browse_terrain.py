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


from typing import TYPE_CHECKING

import pygame as pg

from james import Panel, HBox, VBox, CircleButton, Label, Spacer

from palladium.generators.planet import Planet
from palladium.generators.terrain_gen import MAP_HEIGHT, MAP_WIDTH, BIOME_COLOURS
from palladium.core.utils import clamp
from palladium.gui.states.base import State, StateID
from palladium.gui.utils import get_seed_messages, draw_transparent_rect
from palladium.gui.themes import ThemeKey, TRANSLUCENT_BLACK
from palladium.gui.renderer import draw_elem
from palladium.gui.constants import ICON_SIZE, SCREEN_RECT, UI_MARGIN_M, UI_MARGIN_S, WN_W, WN_H

if TYPE_CHECKING:
    from palladium.game.game import Game


LIGHT_NORMAL = pg.Vector3(1, -1, 1).normalize()  # 45° downwards in a south-easterly direction
BRIGHTNESS_FACTOR = 30  # how much tilt affects terrain brightness


class BrowseTerrainState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

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
                        renderer=draw_elem,
                        padding=UI_MARGIN_S,
                    ),
                    Spacer(),
                    renderer=draw_elem
                ),
                renderer=draw_elem
            ),
            horiz_padding=UI_MARGIN_M,
            vert_padding=UI_MARGIN_M,
            renderer=draw_elem
        )

        self.seed_hbox = seed_hbox
        self.back_button = back_button
        self.seed_label = seed_label
        self.offset_label = offset_label
        self.seed_int_label = seed_int_label

        self.planet_surface = pg.Surface((WN_W, WN_H))
        self.panel.layout(SCREEN_RECT)

    def _refresh_planet_surface(self) -> None:
        cell_w, cell_h = WN_W / MAP_WIDTH, WN_H / MAP_HEIGHT

        for y, row in enumerate(self.current_planet().surface):
            for x, cell in enumerate(row):
                colour = BIOME_COLOURS[cell.biome]

                # Draw colours based on the dot product between the gradient and the light's normal
                # Get the normal by getting the gradient between the cell and its neighbours
                normal = self.current_planet().surface.get_normal_at(x, y)
                brightness = normal.dot(LIGHT_NORMAL)

                colour = (
                    int(clamp(colour[0] + brightness * BRIGHTNESS_FACTOR, 0, 255)),
                    int(clamp(colour[1] + brightness * BRIGHTNESS_FACTOR, 0, 255)),
                    int(clamp(colour[2] + brightness * BRIGHTNESS_FACTOR, 0, 255))
                )

                pg.draw.rect(self.planet_surface, colour, pg.Rect(x * cell_w, y * cell_h, cell_w + 1, cell_h + 1))

    def _refresh_for_new_planet(self) -> None:
        assert self.game.star_system is not None

        seed_str, offset_text, seed_int_str = get_seed_messages(self.game.star_system.seed_metadata)
        self.seed_label.set_text(seed_str)
        self.seed_int_label.set_text(seed_int_str)
        self.offset_label.set_text(offset_text)
        self.panel.layout(SCREEN_RECT)

        self._refresh_planet_surface()

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

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])

        # Draw terrain
        screen.blit(self.planet_surface)

        # Draw overlay panel
        draw_transparent_rect(screen, TRANSLUCENT_BLACK, self.seed_hbox.rect)
        draw_elem(screen, self.panel, self.game.current_theme())
