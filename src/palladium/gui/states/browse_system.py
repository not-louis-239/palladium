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


import pygame as pg

from james import HBox, Panel, Spacer, VBox

from palladium.game.game import Game
from palladium.gui.states.base import State
from palladium.gui.renderer import draw_elem


class BrowseSystemState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.overlay_panel = Panel(
            child=VBox(
                HBox(
                    renderer=draw_elem
                ),
                Spacer(),
                HBox(
                    renderer=draw_elem
                ),
                HBox(
                    renderer=draw_elem
                ),
                HBox(
                    renderer=draw_elem
                ),
                HBox(
                    renderer=draw_elem
                ),
                renderer=draw_elem
            ),
            renderer=draw_elem
        )

    def on_entered(self) -> None:
        pass

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        pass

    def draw(self, screen: pg.Surface) -> None:
        pass

        # TODO: add star background parallax effect
