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


class Cell:
    def __init__(
            self,
            height: float,  # m above sea level
            temperature: float,  # °C
            humidity: float  # % relative humidity
        ) -> None:
        self.height = height
        self.temperature = temperature
        self.humidity = humidity


class TerrainSurface:
    def __init__(self, cells: list[list[Cell]]) -> None:
        self.cells = cells

    def get_cell(self, x: int, y: int) -> Cell:
        return self.cells[y][x]


def generate_terrain_surface() -> TerrainSurface:
    ...
