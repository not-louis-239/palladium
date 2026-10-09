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
from dataclasses import dataclass


type Colour = tuple[int, int, int]


class ThemeKey(StrEnum):
    BG = "BG"
    BG_HOVERED = "BG_HOVERED"
    BG_CLICKED = "BG_CLICKED"
    FG = "FG"
    FG_HOVERED = "FG_HOVERED"
    FG_CLICKED = "FG_CLICKED"
    BORDER = "BORDER"
    BORDER_HOVERED = "BORDER_HOVERED"
    BORDER_CLICKED = "BORDER_CLICKED"


@dataclass
class Theme:
    display_name: str
    _mapping: dict[ThemeKey, Colour]

    def __getitem__(self, key: ThemeKey) -> Colour:
        return self._mapping[key]


THEMES = [
    Theme("Dark", {
        ThemeKey.BG: (12, 12, 24),
        ThemeKey.BG_HOVERED: (15, 15, 29),
        ThemeKey.BG_CLICKED: (19, 19, 34),
        ThemeKey.FG: (210, 210, 255),
        ThemeKey.FG_HOVERED: (235, 235, 255),
        ThemeKey.FG_CLICKED: (255, 255, 255),
        ThemeKey.BORDER: (170, 170, 220),
        ThemeKey.BORDER_HOVERED: (205, 205, 240),
        ThemeKey.BORDER_CLICKED: (240, 240, 255)
    })
]


# Runtime check that all `Theme`s are complete
bad: list[tuple[Theme, list[ThemeKey]]] = []  # (theme, missing_keys)

for theme in THEMES:
    missing_keys = [key for key in ThemeKey if key not in theme._mapping]
    if missing_keys:
        bad.append((theme, missing_keys))

if bad:
    err_msg = "The following themes are missing required keys:"

    for theme, missing in bad:
        err_msg += f"\n  - {theme.display_name}:"
        err_msg += "".join(f"\n      - {key}" for key in missing)

    raise RuntimeError(err_msg)
