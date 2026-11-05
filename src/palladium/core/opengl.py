from OpenGL import GL

from palladium.core.constants import WN_H, WN_W


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


def set_opengl_tex_params() -> None:
    # Set OpenGL's texture parameters.

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
