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


from typing import TypedDict
from palladium.gui.themes import ThemeKey


UI_PADDING = 15


# ugh, pyright, you complained so I added this. happy now?
class UIKwargs(TypedDict, total=False):
    k_bg_colour: ThemeKey
    k_bg_hovered: ThemeKey
    k_bg_clicked: ThemeKey
    k_fg_colour: ThemeKey
    k_fg_hovered: ThemeKey
    k_fg_clicked: ThemeKey
    k_border_colour: ThemeKey
    k_border_hovered: ThemeKey
    k_border_clicked: ThemeKey

DEFAULT_ATTRS: UIKwargs = {
    "k_bg_colour": ThemeKey.BG,
    "k_bg_hovered": ThemeKey.BG_HOVERED,
    "k_bg_clicked": ThemeKey.BG_CLICKED,
    "k_fg_colour": ThemeKey.FG,
    "k_fg_hovered": ThemeKey.FG_HOVERED,
    "k_fg_clicked": ThemeKey.FG_CLICKED,
    "k_border_colour": ThemeKey.BORDER,
    "k_border_hovered": ThemeKey.BORDER_HOVERED,
    "k_border_clicked": ThemeKey.BORDER_CLICKED,
}
