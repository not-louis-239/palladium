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


import random
from dataclasses import dataclass

from palladium.core.utils import str_to_seed
from palladium.terrain.planet import Planet, generate_planet
from palladium.terrain.star_gen import StarProfile, generate_star_profile


PLANET_COUNT_WEIGHTS: list[int] = [1, 5, 10, 25, 30, 20, 10, 3, 1, 1]


@dataclass(frozen=True, kw_only=True)
class SeedMetadata:
    display_str: str
    offset: int  # offset from the seed of `display_str`
    is_string: bool  # True if the `display_str` is not a pure integer
    integer_value: int  # internal integer value of the seed, including `offset`


class StarSystem:
    def __init__(self, star: StarProfile, planets: list[Planet], seed_metadata: SeedMetadata) -> None:
        self.star = star
        self.planets = planets
        self.seed_metadata = seed_metadata


def _generate_planets(seed_int: int, star_profile: StarProfile) -> list[Planet]:
    # Spawn planets - decide on a number of planets from a weighted distribution
    rng = random.Random(seed_int)
    num_planets = rng.choices(
        range(len(PLANET_COUNT_WEIGHTS)),
        weights=PLANET_COUNT_WEIGHTS
    )[0]

    planets: list[Planet] = []

    for _ in range(num_planets):
        # TODO: Generate planets
        planets.append(generate_planet(seed_int, star_profile))

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
