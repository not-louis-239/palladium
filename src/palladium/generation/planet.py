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

from palladium.core.constants import SOLAR_RADIUS_IN_AU, SECONDS_PER_YEAR
from palladium.generation.star_gen import StarProfile
from palladium.generation.terrain_gen import TerrainSurface, generate_terrain_surface

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


HABITABLE_INNER_FLUX_LIMIT = 1.10  # solar flux
HABITABLE_OUTER_FLUX_LIMIT = 0.35  # solar flux

def calculate_habitable_zone(luminosity: float) -> tuple[float, float]:
    """Calculates the (inner, outer) distance from the parent star, in astronomical units,
    between which a planet's stellar flux received is between
    `HABITABLE_INNER_FLUX_LIMIT` and `HABITABLE_OUTER_FLUX_LIMIT`."""

    inner_distance = (luminosity / HABITABLE_INNER_FLUX_LIMIT) ** 0.5
    outer_distance = (luminosity / HABITABLE_OUTER_FLUX_LIMIT) ** 0.5
    return inner_distance, outer_distance


def generate_planet(seed_int: int, star: StarProfile) -> Planet:
    inst = random.Random(seed_int)

    orbit_radius = star.radius * 10 ** inst.uniform(1, 6)  # solar radii
    orbit_au = orbit_radius * SOLAR_RADIUS_IN_AU

    base_temp = 287 * calculate_stellar_flux(star.luminosity, orbit_au) ** 0.25  # using Stefan-Boltzmann's Law
    day_length = 10 ** inst.uniform(3.255, 7.499)  # seconds, anywhere from ~30min to ~1yr
    greenhouse_modifier = 10 ** inst.uniform(-0.82, 0.82)  # from ~1/6.7 -> 6.7
    temp = greenhouse_modifier * base_temp

    # Clamp temperature to never exceed star temperature
    # At low values, this does basically nothing
    # At high values, it clamps the temperature aggressively
    temp = star.temp * math.tanh(temp / star.temp)  # °K

    radius = 10 ** inst.uniform(-2.4, -0.824)

    # Assume a density of Earth, so 2,700 kg/m^3
    # 1 M☉ = 1.989e+30 kg
    # 1 R☉ = approx. 6.957e+8
    # 1 kg/m^3 = 0.00016928997 M☉/R☉^3
    volume = 1.3333 * math.pi * radius ** 3  # solar radii cubed
    mass = 2_700 * KG_PER_M3_TO_MSUN_PER_RSUN3 * volume  # solar masses

    # Using Kepler's Law
    orbit_duration = math.sqrt(orbit_au ** 3 / (star.mass + mass)) * SECONDS_PER_YEAR

    p = Planet(
        name="",  # assign names in generation
        day_length=day_length,
        orbit_radius=orbit_radius,
        orbit_duration=orbit_duration,
        radius=radius,
        mass=mass,
        rotation_seed=seed_int,
        displayed_surface_temp=temp * _ESTIMATED_SURFACE_TEMP_RATIO,
        base_temp=temp,
        seed_int=seed_int
    )

    return p
