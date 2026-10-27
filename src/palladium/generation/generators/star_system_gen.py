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


from palladium.core.utils import random_seed, str_to_seed
from palladium.generation.generators.star_gen import generate_star_profile
from palladium.generation.objects.generate_planet import generate_planet
from palladium.generation.objects.planet import Planet
from palladium.generation.objects.star_profile import StarProfile
from palladium.generation.objects.star_system import PLANET_COUNT_WEIGHTS, PLANET_SUFFIXES, SeedMetadata, StarSystem


import random


def _generate_planets(seed_int: int, star: StarProfile) -> list[Planet]:
    # Spawn planets - decide on a number of planets from a weighted distribution
    rng = random.Random(seed_int)
    num_planets = rng.choices(
        range(len(PLANET_COUNT_WEIGHTS)),
        weights=PLANET_COUNT_WEIGHTS
    )[0]

    planets: list[Planet] = []

    # planet seed generator - it generates seeds for planets, but is itself
    # determined by the master seed
    planet_seed_rng = random.Random(seed_int)

    for i in range(num_planets):
        planet_seed = random_seed(planet_seed_rng)
        planet = generate_planet(planet_seed, star)
        planet.name = star.name + PLANET_SUFFIXES[i]

        planets.append(planet)

        #planet.generate_surface()
        #mean_temp = np.mean(planet.surface.temps)
        #print(f"{mean_temp / planet.base_temp} mean temp : temp ratio for planet '{planet.name}'")

    return planets


def generate_star_system(seed: int | str, offset: int = 0) -> StarSystem:
    # Handling seed conversion and display
    # Merge seed and offset if seed is an integer
    seed_int, is_string = str_to_seed(str(seed))
    if not is_string:
        seed_int += offset
        offset = 0

    # Create the master seed for generation
    generation_seed = seed_int + offset

    # From here on out, use `generation_seed` for generation, and make each stage its own function
    star = generate_star_profile(generation_seed)
    planets = _generate_planets(generation_seed, star)

    # Return StarSystem with all its metadata
    return StarSystem(star, planets, seed_metadata=SeedMetadata(
        display_str=str(seed_int if not is_string else seed),
        offset=offset, is_string=is_string, integer_value=seed_int + offset
    ))
