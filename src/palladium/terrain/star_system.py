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


from dataclasses import dataclass

from palladium.core.utils import str_to_seed
from palladium.terrain.planet import Planet
from palladium.terrain.star_gen import StarProfile, generate_star_profile


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


def generate_star_system(seed: int | str, offset: int = 0) -> StarSystem:
    seed_int, is_string = str_to_seed(str(seed))
    star = generate_star_profile(seed_int + offset)

    # TODO: add planet objects to star system generator

    return StarSystem(star, [], SeedMetadata(
        display_str=str(seed), offset=offset, is_string=is_string, integer_value=seed_int + offset
    ))
