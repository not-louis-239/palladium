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


from enum import StrEnum
from functools import total_ordering


class Dims(StrEnum):
    LENGTH = "LENGTH"
    MASS = "MASS"
    TIME = "TIME"


@total_ordering
class Quantity:
    def __init__(self, scalar: float, dimensions: dict[str, int]) -> None:
        self.scalar = scalar
        self.dimensions = dimensions

    def __add__(self, other: Quantity) -> Quantity:
        if self.dimensions != other.dimensions:
            raise ValueError(f"Cannot add quantities with different dimensions: {self.dimensions} != {other.dimensions}")

        return Quantity(self.scalar + other.scalar, self.dimensions)

    def __sub__(self, other: Quantity) -> Quantity:
        if self.dimensions != other.dimensions:
            raise ValueError(f"Cannot subtract quantities with different dimensions: {self.dimensions} != {other.dimensions}")

        return Quantity(self.scalar - other.scalar, self.dimensions)

    def __rmul__(self, other: float) -> Quantity:
        return Quantity(self.scalar * other, self.dimensions)

    def __mul__(self, other: Quantity | float):
        if isinstance(other, (int, float)):
            return Quantity(self.scalar * other, self.dimensions)

        scalar = self.scalar * other.scalar
        dimensions = self.dimensions.copy()

        for dim in other.dimensions:
            if dim in dimensions:
                dimensions[dim] += other.dimensions[dim]
            else:
                dimensions[dim] = other.dimensions[dim]

        return Quantity(scalar, {d: v for d, v in dimensions.items() if v != 0})

    def __rtruediv__(self, other: float) -> Quantity:
        return Quantity(other / self.scalar, {d: -v for d, v in self.dimensions.items() if v != 0})

    def __truediv__(self, other: Quantity | float):
        if isinstance(other, (int, float)):
            return Quantity(self.scalar / other, self.dimensions)

        scalar = self.scalar / other.scalar
        dimensions = self.dimensions.copy()

        for dim in other.dimensions:
            if dim in dimensions:
                dimensions[dim] -= other.dimensions[dim]
            else:
                dimensions[dim] = -other.dimensions[dim]

        return Quantity(scalar, {d: v for d, v in dimensions.items() if v != 0})

    def __pow__(self, power: int) -> Quantity:
        scalar = self.scalar ** power
        dimensions = self.dimensions.copy()

        for dim in dimensions:
            dimensions[dim] *= power

        return Quantity(scalar, dimensions)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Quantity):
            return False
        return self.scalar == value.scalar and self.dimensions == value.dimensions

    def __lt__(self, other: Quantity):
        if other.dimensions != self.dimensions:
            raise ValueError(f"Cannot compare units with different dimensions: {self.dimensions} != {other.dimensions}.")
        return self.scalar < other.scalar

    def __repr__(self) -> str:
        return f"Unit({self.scalar} * {self.dimensions})"


def convert_units(quantity_in: Quantity, unit_out: Quantity) -> float:
    """Convert a value from one unit to another."""
    if quantity_in.dimensions != unit_out.dimensions:
        raise ValueError("Cannot convert units with different dimensions.")
    return quantity_in.scalar / unit_out.scalar


METRE = Quantity(1, {Dims.LENGTH: 1})
KG = Quantity(1, {Dims.MASS: 1})
SECOND = Quantity(1, {Dims.TIME: 1})

NEWTON = KG * METRE / SECOND ** 2
JOULE = NEWTON * METRE
WATT = JOULE / SECOND
SOLAR_FLUX = 1_361.0 * WATT / METRE ** 2

KM = METRE * 1000
R_SUN = 695_700 * KM
M_SUN = 1.98847e30 * KG
AU = 149_597_870_719 * METRE
SPEED_OF_LIGHT = 299_792_458 * METRE / SECOND
YEAR = 365.242 * 24 * 60 * 60 * SECOND
LIGHT_YEAR = SPEED_OF_LIGHT * YEAR
