#!/usr/bin/env python3

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


import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import james
import pygame as pg
from rich.traceback import install
from OpenGL import GL

from palladium.gui.renderer import draw_elem

james.input_box.InputBox.CURSOR_FLASH_INTERVAL = 1.0
james.set_default_renderer(draw_elem)
install(show_locals=True)

from palladium.core.opengl import init_opengl, set_opengl_tex_params, clear_gl_colour_buffer, draw_fullscreen_opengl_quad
from palladium.core.constants import WN_H, WN_W
from palladium.game.game import Game


def main():
    pg.init()
    pg.key.set_repeat(500, 30)

    # The `flags` tell Pygame what kind of window we want.
    # We want a double-buffered, OpenGL window.
    # `pg.OPENGL` - We need an OpenGL window so that we can use `gl.gl*` functions.
    # `pg.DOUBLEBUF` - The window uses two buffers: a front buffer and a back buffer.
    # We draw to the back buffer, then `pg.display.flip()` swaps them so that
    # users don't see half-drawn frames.
    # These are flags, so we use Python's bitwise OR (`|`) to combine them.
    flags = pg.DOUBLEBUF | pg.OPENGL
    screen = pg.display.set_mode((WN_W, WN_H), flags)
    # screen = pg.Window("palladium", size=(WN_W, WN_H), allow_high_dpi=True, opengl=True)
    # window = pg.Window(
    #     "Palladium",
    #     size=(WN_W, WN_H),
    #     resizable=True,
    #     allow_high_dpi=True,
    # )

    # screen = window.get_surface()

    # Initialise our OpenGL context with width `WN_W` and height `WN_H`.
    init_opengl(WN_W, WN_H)

    # Generate an OpenGL texture slot for our screen texture.
    # The `1` tells OpenGL how many texture slots we want, in this case, just one.
    # Bind it to the Python variable `texture` so we can then work with it later.
    texture = GL.glGenTextures(1)

    # Select the texture we want to work with.
    # In this case, the texture slot we just generated using `glGenTextures(1)`.
    # We need to select the texture so that future calls know what texture to use.
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)

    set_opengl_tex_params()

    # Create the image storage for this texture.
    # `glTexImage2D` = create some storage for the image, while
    # `glTexSubImage2D` = put some pixel data into said storage.

    GL.glTexImage2D(
        GL.GL_TEXTURE_2D,  # target (uses the previously bound texture)
        0,  # mipmap level, i.e. the front, which is 0
        GL.GL_RGBA,  # internal format
        WN_W,  # width
        WN_H,  # height
        0,  # this is `border`, an outdated paramter, so we just set it to 0
        GL.GL_RGBA,  # input format the image is willing to accept
        GL.GL_UNSIGNED_BYTE,  # type of data in each channel, i.e. 8-bit unsigned integers
        None,  # any initial data, in this case no frame has been drawn, so it's None
    )

    pg.display.set_caption("Palladium")
    clock = pg.time.Clock()
    game = Game()

    running = True

    try:
        while running:
            dt_s = clock.tick(60) / 1_000.0
            keys = pg.key.get_pressed()
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    running = False

            t_i = time.time()
            game.update(dt_s)
            t_update = time.time()
            game.take_input(keys=keys, events=events, dt_s=dt_s)
            t_input = time.time()
            game.draw(screen)

            # Start moving the pg.Surface data down into OpenGL
            # The full pipeline: James -> Palladium -> pg.Surface -> bytes -> texture -> quads -> window

            # Convert the Pygame surface to bytes so that OpenGL can use it.
            pixels = pg.image.tobytes(screen, "RGBA", True)

            # Set the texture that we want OpenGL to use, i.e. `texture`, which is the framebuffer.
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture)

            # Copy the block of pixel data into the texture.
            GL.glTexSubImage2D(
                GL.GL_TEXTURE_2D,  # We are uploading to a 2D texture.
                0,  # Mipmap level. We want the top-level and we're not using mipmap, so 0 is OK.
                0,  # X-offset at which the replacement data begins (screen space).
                0,  # Y-offset at which the replacement data begins (screen space).
                WN_W,  # Width of the image being uploaded (screen space).
                WN_H,  # Height of the image being uploaded (screen space).
                GL.GL_RGBA,  # The format of the image data, i.e. RGBA (Red, Green, Blue, Alpha).
                GL.GL_UNSIGNED_BYTE,  # The type of data contained in each channel, i.e. unsigned 8-bit int.
                pixels,  # The actual byte array that we want to upload.
            )

            # Clear the previous frame from the OpenGL colour buffer.
            clear_gl_colour_buffer()
            # Draw our fullscreen quad.
            draw_fullscreen_opengl_quad()

            pg.display.flip()
            t_draw = time.time()

            game.profiler.record_snapshot(t_i=t_i, t_update=t_update, t_input=t_input, t_draw=t_draw)

    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting now.")

    game.quit()
    pg.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
