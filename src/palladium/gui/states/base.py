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
from abc import ABC, abstractmethod
from enum import StrEnum

import pygame as pg

if TYPE_CHECKING:
    from palladium.game.game import Game


class StateID(StrEnum):
    TITLE = "title"
    ENTER_SEED = "enter_seed"
    BROWSE_SYSTEM = "browse_system"
    BROWSE_TERRAIN = "browse_terrain"
    SAVED_SEEDS = "saved_seeds"
    PREFS = "prefs"

class State(ABC):
    def __init__(self, game: Game) -> None:
        self.game = game

    @abstractmethod
    def update(self, dt_s: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw(self, screen: pg.Surface) -> None:
        raise NotImplementedError
