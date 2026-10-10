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


import pygame as pg

from palladium.core.paths import FONTS_DIR, IMAGES_DIR


class Images:
    def __init__(self) -> None:
        self.back = IMAGES_DIR / "back.png"
        self.proceed = IMAGES_DIR / "proceed.png"
        self.recentre = IMAGES_DIR / "recentre.png"
        self.zoom_in = IMAGES_DIR / "zoom_in.png"
        self.zoom_out = IMAGES_DIR / "zoom_out.png"


class Fonts:
    def __init__(self) -> None:
        self.font_path = FONTS_DIR / "lato/Lato-Regular.ttf"
        self.font_title = pg.font.Font(self.font_path, 64)
        self.font_heading = pg.font.Font(self.font_path, 54)
        self.font_ui = pg.font.Font(self.font_path, 45)


class Assets:
    def __init__(self) -> None:
        self.images = Images()
        self.fonts = Fonts()
