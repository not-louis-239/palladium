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


from palladium.core.utils import lerp_gradient
from palladium.gui.constants import KELVIN_COLOURS


SUN_TEMP = 5778.0  # °K

class StarProfile:
    def __init__(self, name: str, mass: float, radius: float, temp: float):
        """
        Expects:
            name: str
            mass: float (solar masses)
            radius: float (solar radii)
            temp: float (°K)
        """

        self.name = name
        self.mass = mass
        self.radius = radius
        self.temp = temp

        # Calculate light colour.
        self.light_colour = lerp_gradient(self.temp, KELVIN_COLOURS)

        # Crude approximation using Stefan-Boltzmann law.
        # Luminosity is expressed in terms of the Sun.
        self.luminosity = (self.radius ** 2) * ((self.temp / SUN_TEMP) ** 4)
