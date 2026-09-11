# repo at: https://github.com/not-louis-239/palladium
# Palladium - Pygame terrain generator, for fun
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


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pygame as pg

from palladium.core.constants import WN_W, WN_H
from palladium.game.game import Game


def main():
    pg.init()

    game = Game()
    screen = pg.display.set_mode((WN_W, WN_H))
    clock = pg.time.Clock()

    while True:
        dt_s = clock.tick(60) / 1_000.0
        keys = pg.key.get_pressed()
        events = pg.event.get()

        game.update(dt_s)
        game.take_input(keys=keys, events=events, dt_s=dt_s)
        game.draw(screen)
        pg.display.flip()

if __name__ == "__main__":
    main()
