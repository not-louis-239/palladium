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



# noise_port.py
# typed port of noise's functions because the `noise` library's type stubs
# kinda suck ngl

from noise import snoise2 as _snoise2


def snoise2(
        x: float, y: float, *, scale: float = 1.0,
        octaves: int = 1, persistence: float = 0.5,
        repeatx: int | None = None, repeaty: int | None = None,
        lacunarity: float = 2.0, base: int | None = None,
    ) -> float:
    """Return a float from -1 to 1 based on snoise2 function.
    This is a wrapper function around noise.snoise2 because
    it has no type stubs, which is a bit annoying."""

    if scale == 0:
        raise ValueError("Scale cannot be zero.")

    x *= scale
    y *= scale

    kwargs = {
        "octaves": octaves,
        "persistence": persistence,
        "lacunarity": lacunarity,
    }

    if repeatx is not None:
        kwargs["repeatx"] = repeatx
    if repeaty is not None:
        kwargs["repeaty"] = repeaty
    if base is not None:
        kwargs["base"] = base

    return _snoise2(x, y, **kwargs)
