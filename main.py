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
from OpenGL import GL

from palladium.gui.renderer import draw_elem

james.input_box.InputBox.CURSOR_FLASH_INTERVAL = 1.0
james.set_default_renderer(draw_elem)

from palladium.core.constants import WN_H, WN_W
from palladium.game.game import Game


def init_opengl(width: int, height: int):
    # Set the viewport inside which we want OpenGL to draw stuff.
    # In this case, the full screen with top-left situated at (0, 0),
    # width `width` and height `height`.
    GL.glViewport(0, 0, width, height)

    # Set up the projection matrix.
    GL.glMatrixMode(GL.GL_PROJECTION)  # Set the matrix to modify
    GL.glLoadIdentity()  # Select the identity matrix

    # Set the projection matrix to orthographic projection.
    GL.glOrtho(
        0, width,  # left -> right = 0 -> width
        height, 0,  # bottom -> top = height -> 0
        -1, 1  # near -> far = -1->1
    )

    # Set up the modelview matrix.
    GL.glMatrixMode(GL.GL_MODELVIEW)  # Set the matrix to modify
    GL.glLoadIdentity()  # Select the identity matrix

    # Disable depth testing and enable 2D textures.
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_TEXTURE_2D)

    # Critical: don't interpolate our pixels.
    # This means "for the current 2d texture, if it needs to be drawn smaller than
    # its native size, use NN interpolation, not bilinear interpolation."
    GL.glTexParameteri(
        GL.GL_TEXTURE_2D,
        GL.GL_TEXTURE_MIN_FILTER,
        GL.GL_NEAREST,
    )
    GL.glTexParameteri(
        GL.GL_TEXTURE_2D,
        GL.GL_TEXTURE_MAG_FILTER,
        GL.GL_NEAREST,
    )


def clear_gl_colour_buffer():
    """Clear the OpenGL colour buffer bit."""
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # Clear the colour buffer bit


def draw_fullscreen_opengl_quad():
    """Draw the Pygame framebuffer texture across the entire OpenGL window."""

    # Tell OpenGL that we want to define a quad.
    # We need four vertices to make up one quadrilateral.
    GL.glBegin(GL.GL_QUADS)

    # glTexCoord2f tells OpenGL what part of the texture
    # to use for that vertex. Texture coordinates
    # are in the form of (u, v) instead of (x, y), where 0 <= u,v <= 1.

    # glVertex2f tells OpenGL where to put the vertex
    # with respect to the screen.

    # Top-left vertex
    GL.glTexCoord2f(0, 1)  # prepare to sample (0, 1) in texture coords, which is the top-left
    GL.glVertex2f(0, 0)  # draw this vertex at (0, 0) in screen coordinates, which is the top-left

    # Top-right vertex
    GL.glTexCoord2f(1, 1)
    GL.glVertex2f(WN_W, 0)

    # Bottom-right vertex
    GL.glTexCoord2f(1, 0)
    GL.glVertex2f(WN_W, WN_H)

    # Bottom-left vertex
    GL.glTexCoord2f(0, 0)
    GL.glVertex2f(0, WN_H)

    # Tell OpenGL that we are finished defining the quad.
    GL.glEnd()


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

    # Tell OpenGL not to interpolate the texture coordinates.
    # If it needs to be draw smaller (`GL_TEXTURE_MIN_FILTER`),
    # use nearest-neighbour (NN) interpolation (`GL_NEAREST`).
    GL.glTexParameteri(
        GL.GL_TEXTURE_2D,
        GL.GL_TEXTURE_MIN_FILTER,
        GL.GL_NEAREST,
    )

    # Same thing here: if we need to draw the texture at larger than
    # its native size (`GL_TEXTURE_MAG_FILTER`), use NN interpolation.
    GL.glTexParameteri(
        GL.GL_TEXTURE_2D,
        GL.GL_TEXTURE_MAG_FILTER,
        GL.GL_NEAREST,
    )

    # Tell OpenGL that when a texture coordinate goes outside of the texture
    # horizontally (the `S` coordinate = horizontal), use the nearest
    # edge pixel (`GL_CLAMP_TO_EDGE`).
    # We want to set this paramter for 2D textures (`GL_TEXTURE_2D`).
    GL.glTexParameteri(
        GL.GL_TEXTURE_2D,
        GL.GL_TEXTURE_WRAP_S,
        GL.GL_CLAMP_TO_EDGE,
    )

    # Same thing here, but for vertical wrapping instead of horizontal wrapping.
    # `T` is the vertical texture coordinate.
    GL.glTexParameteri(
        GL.GL_TEXTURE_2D,
        GL.GL_TEXTURE_WRAP_T,
        GL.GL_CLAMP_TO_EDGE,
    )

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

    pg.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting now.")
        sys.exit(0)
