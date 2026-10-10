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



from palladium.gui.utils import draw_star
from palladium.core.constants import WN_W, WN_H
from palladium.gui.states.base import State
from palladium.gui.themes import ThemeKey

if TYPE_CHECKING:
    from palladium.game.game import Game


class BrowseStarState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.zoom_level = 0.03

    def on_entered(self) -> None:
        pass

    def update(self, dt_s: float) -> None:
        pass

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        pass

    def draw(self, screen: pg.Surface) -> None:
        assert self.game.star_system is not None

        screen.fill(self.game.current_theme()[ThemeKey.BG])

        draw_star(screen, self.game.star_system.star, self.zoom_level, (WN_W // 4, WN_H // 2))
