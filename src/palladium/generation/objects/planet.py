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


import math
import random

from palladium.generation.generators.terrain_gen import generate_terrain_surface
from palladium.generation.objects.terrain_surface import TerrainSurface

_ESTIMATED_SURFACE_TEMP_RATIO = 1.0316
KG_PER_M3_TO_MSUN_PER_RSUN3 = 0.0016928997


class Planet:
    def __init__(
            self, name: str, day_length: float, mass: float,
            orbit_radius: float, orbit_duration: float, radius: float, rotation_seed: int,
            displayed_surface_temp: float, base_temp: float, seed_int: int
        ) -> None:
        self.name = name
        self.day_length = day_length  # seconds
        self.orbit_duration = orbit_duration  # seconds
        self.orbit_radius = orbit_radius  # solar radii
        self.radius = radius  # solar radii
        self.mass = mass  # solar masses
        self.displayed_surface_temp = displayed_surface_temp  # Kelvin
        self.base_temp = base_temp  # Kelvin
        self.seed_int = seed_int  # used for terrain gen

        # Rotation seed sets initial rotation phase and direction
        rng = random.Random(rotation_seed)
        self.orbit_phase = rng.uniform(0, 2 * math.pi)
        self.orbit_direction = rng.choice([-1, 1])

        self.surface: TerrainSurface | None = None

    def generate_surface(self) -> None:
        self.surface = generate_terrain_surface(self.seed_int, self.base_temp)


def calculate_stellar_flux(luminosity: float, distance_au: float) -> float:
    """Calculate the stellar flux of a planet given its luminosity and distance from the star,
    relative to the flux received by Earth from the Sun."""
    return luminosity / distance_au ** 2
