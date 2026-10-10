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
from enum import StrEnum

from palladium.core.utils import str_to_seed

SUN_TEMP = 5778.0  # °K


class StarType(StrEnum):
    SUPERGIANT = "supergiant"
    GIANT = "giant"
    MAIN_SEQ = "main_seq"
    WHITE_DWARF = "white_dwarf"
    RED_DWARF = "red_dwarf"
    BROWN_DWARF = "brown_dwarf"


# chance of each star to generate
STAR_WEIGHTS: dict[StarType, float] = {
    StarType.SUPERGIANT: 0.005,
    StarType.GIANT: 0.045,
    StarType.MAIN_SEQ: 0.28,
    StarType.RED_DWARF: 0.6,
    StarType.BROWN_DWARF: 0.06,
    StarType.WHITE_DWARF: 0.01,
}


@dataclass
class StarProfile:
    mass: float  # solar masses
    radius: float  # solar radii
    temp: float  # °K

    @property
    def luminosity(self) -> float:
        # crude approximation using Stefan-Boltzmann law
        return (self.radius ** 2) * ((self.temp / SUN_TEMP) ** 4)


def generate_star_profile(seed: int) -> StarProfile:
    inst = random.Random(seed)

    population = list(STAR_WEIGHTS.keys())
    weights = list(STAR_WEIGHTS.values())

    profile = inst.choices(population, weights=weights, k=1)[0]

    match profile:
        case StarType.SUPERGIANT:
            radius = 10 ** inst.uniform(1.5, 3)
            mass = (radius ** 0.5) * inst.uniform(1.5, 3)
            temp = 10 ** inst.uniform(3.5, 4.6)
        case StarType.GIANT:
            radius = 10 ** inst.uniform(1, 2.2)
            mass = radius * inst.uniform(0.08, 0.12)
            temp = 10 ** inst.uniform(3.4, 4)
        case StarType.MAIN_SEQ:
            radius = 10 ** inst.uniform(-1, 1.2)
            mass = (radius ** 1.25) * inst.uniform(0.8, 1.2)
            temp = SUN_TEMP * radius ** 0.5 * inst.uniform(0.75, 1.25)
        case StarType.RED_DWARF:
            radius = 10 ** inst.uniform(-1, -0.2)
            mass = (radius ** 1.25) * inst.uniform(0.8, 1.2)
            temp = 10 ** inst.uniform(3.3, 3.6)
        case StarType.BROWN_DWARF:
            radius = inst.uniform(0.08, 0.12)
            mass = inst.uniform(0.012, 0.075)
            temp = 10 ** inst.uniform(2.4, 3.3)
        case StarType.WHITE_DWARF:
            radius = 10 ** inst.uniform(-2.1, -1.7)
            mass = radius * inst.uniform(50, 75)
            temp = 10 ** inst.uniform(3.9, 4.3)

    return StarProfile(mass=mass, radius=radius, temp=temp)


def _test():
    # more crude approximations for testing, I'm not an astrophysicist
    # using 0 as a placeholder for mass since the Stefan-Boltzmann law doesn't actually seem
    # to care about it.
    test_cases = [
        StarProfile(0, 0.01, 40_000),  # white dwarf
        StarProfile(0, 0.5, 2_300),  # red dwarf
        StarProfile(0, 0.7, 3_900),  # yellow dwarf
        StarProfile(0, 1, 6000),  # sun
        StarProfile(0, 1.8, 10_000),  # giant
        StarProfile(0, 6.6, 33_000)  # supergiant
    ]

    column_widths = (10, 10, 10)
    print(f"{'Radius':{column_widths[0]}} | {'Temp':{column_widths[1]}} | {'Luminosity':{column_widths[2]}}")
    for test_case in test_cases:
        print(f"{f'{test_case.radius:.2f}':{column_widths[0]}} | {f'{test_case.temp:.2f}':{column_widths[1]}} | {f'{test_case.luminosity:,.3g}':{column_widths[2]}}")

    seed = str_to_seed(input("\nEnter a seed: "))
    print(f"Generated star profile: {generate_star_profile(seed)}")


if __name__ == "__main__":
    _test()
