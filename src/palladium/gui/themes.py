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
from enum import StrEnum

from palladium.core.custom_types import AColour

type Colour = tuple[int, int, int] | tuple[int, int, int, int]


CLEAR: AColour = (0, 0, 0, 0)
TRANSLUCENT_BLACK: AColour = (0, 0, 0, 170)


class ThemeKey(StrEnum):
    BG_SCREEN = "BG_SCREEN"  # this is screen background

    BG_ELEMS = "BG"
    BG_HOVERED = "BG_HOVERED"
    BG_ACTIVE = "BG_ACTIVE"

    BG_DARK = "BG_DARK"
    BG_DARK_HOVERED = "BG_DARK_HOVERED"
    BG_DARK_PRESSED = "BG_DARK_PRESSED"

    FG_ELEMS = "FG"
    FG_HOVERED = "FG_HOVERED"
    FG_PRESSED = "FG_PRESSED"

    FG_INPUT_TEXT = "FG_INPUT_TEXT"
    FG_INPUT_TEXT_HOVERED = "FG_INPUT_TEXT_HOVERED"
    FG_INPUT_TEXT_PRESSED = "FG_INPUT_TEXT_PRESSED"

    FG_ACCENT = "FG_ACCENT"
    FG_ACCENT2 = "FG_ACCENT2"
    FG_SENTINEL = "FG_SENTINEL"

    FG_ERROR = "FG_ERROR"
    FG_ERROR_HOVERED = "FG_ERROR_HOVERED"
    FG_ERROR_PRESSED = "FG_ERROR_PRESSED"

    BORDER = "BORDER"
    BORDER_HOVERED = "BORDER_HOVERED"
    BORDER_PRESSED = "BORDER_PRESSED"

    CURSOR = "CURSOR"
    FG_SELECTION = "FG_SELECTION"
    FG_HABITABLE_ZONE = "FG_HABITABLE_ZONE"

    FG_PROFILER_UPDATE = "FG_PROFILER_UPDATE"
    FG_PROFILER_INPUT = "FG_PROFILER_INPUT"
    FG_PROFILER_DRAW = "FG_PROFILER_DRAW"


@dataclass
class Theme:
    display_name: str
    _mapping: dict[ThemeKey, Colour]

    def __getitem__(self, key: ThemeKey) -> Colour:
        return self._mapping[key]


THEMES = [
    Theme("Dark", {
        ThemeKey.BG_SCREEN: (12, 12, 24),

        ThemeKey.BG_ELEMS: (0, 0, 0, 0),
        ThemeKey.BG_HOVERED: (210, 210, 255, 20),
        ThemeKey.BG_ACTIVE: (210, 210, 255, 30),

        ThemeKey.BG_DARK: TRANSLUCENT_BLACK,
        ThemeKey.BG_DARK_HOVERED: (30, 30, 38, 170),
        ThemeKey.BG_DARK_PRESSED: (45, 45, 58, 170),

        ThemeKey.FG_ELEMS: (210, 210, 255),
        ThemeKey.FG_HOVERED: (235, 235, 255),
        ThemeKey.FG_PRESSED: (255, 255, 255),

        ThemeKey.FG_INPUT_TEXT: (247, 220, 178),
        ThemeKey.FG_INPUT_TEXT_HOVERED: (255, 233, 199),
        ThemeKey.FG_INPUT_TEXT_PRESSED: (255, 245, 227),

        ThemeKey.FG_ACCENT: (90, 255, 255),
        ThemeKey.FG_ACCENT2: (230, 90, 255),
        ThemeKey.FG_SENTINEL: (128, 128, 145),

        ThemeKey.FG_ERROR: (255, 0, 76),
        ThemeKey.FG_ERROR_HOVERED: (255, 20, 90),
        ThemeKey.FG_ERROR_PRESSED: (255, 38, 117),

        ThemeKey.BORDER: (170, 170, 220),
        ThemeKey.BORDER_HOVERED: (205, 205, 240),
        ThemeKey.BORDER_PRESSED: (240, 240, 255),

        ThemeKey.CURSOR: (255, 255, 255),
        ThemeKey.FG_SELECTION: (75, 126, 166),
        ThemeKey.FG_HABITABLE_ZONE: (0, 50, 0),

        ThemeKey.FG_PROFILER_UPDATE: (100, 255, 255),
        ThemeKey.FG_PROFILER_INPUT: (100, 100, 255),
        ThemeKey.FG_PROFILER_DRAW: (100, 255, 100)
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
