# Copyright 2026 Louis Masarei-Boulton

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import random

import numpy as np
import pygame as pg

from palladium.core.custom_types import AColour
from palladium.generation.objects.star_system import SeedMetadata

# Set up star surface for drawing a single star
STAR_GLOW_FIDELITY = 30
STAR_GLOW_RADIUS = 30
STAR_STARTING_BRIGHTNESS = 12
STAR_DRAW_LAYERS = [  # (radius, brightness)
    (
        int(STAR_GLOW_RADIUS * (1 - x / STAR_GLOW_FIDELITY)),
        int(STAR_STARTING_BRIGHTNESS * (x / STAR_GLOW_FIDELITY) ** 2)
    ) for x in range(STAR_GLOW_FIDELITY)
]

star_surface = pg.Surface((STAR_GLOW_RADIUS * 2, STAR_GLOW_RADIUS * 2), pg.SRCALPHA)

for radius, brightness in STAR_DRAW_LAYERS:
    pg.draw.circle(star_surface, (255, 255, 255, brightness), (STAR_GLOW_RADIUS, STAR_GLOW_RADIUS), radius)
pg.draw.circle(star_surface, (255, 255, 255, 255), (STAR_GLOW_RADIUS, STAR_GLOW_RADIUS), 1)


def draw_transparent_rect(surface: pg.Surface, colour: AColour, rect: pg.Rect) -> None:
    """Draws a transparent rectangle. This function is dedicated
    to this purpose because `pg.draw.rect` doesn't work well: it overwrites
    alpha values on the destination surface instead of layering colours
    depending on opacity."""
    rect_surface = pg.Surface(rect.size, pg.SRCALPHA)
    rect_surface.fill(colour)
    surface.blit(rect_surface, rect)


def draw_bg_star(surface: pg.Surface, centre_pos: tuple[int, int]) -> None:
    surface.blit(star_surface, star_surface.get_rect(center=centre_pos))


def generate_bg_star_positions(seed: int, wrap_bounds: tuple[int, int], star_density_per_pix2: float) -> np.ndarray:
    """Based on an integer seed and a wrap width which dictates
    the bounds for the star positions, generate a list of (x, y)
    coordinates at which to draw stars.

    Also, apparently NumPy hates negative integers, so only pass positive
    `seeds`, please!"""

    total_area_px2 = wrap_bounds[0] * wrap_bounds[1]
    num_stars = int(star_density_per_pix2 * total_area_px2)

    # Generate random positions within the wrap bounds
    rng = np.random.default_rng(seed)
    star_positions = rng.random((num_stars, 2), dtype=np.float32)
    star_positions *= np.asarray(wrap_bounds, dtype=np.float32)

    return star_positions


def get_seed_messages(seed_metadata: SeedMetadata) -> tuple[str, str, str]:
    """Returns: seed text, offset, internal integer value
    in the form of strings designed to be joined together visually."""

    # Seed text
    seed_str = seed_metadata.display_str

    # Offset text
    offset = seed_metadata.offset
    if not offset:
        offset_text = ""
    elif offset > 0:
        offset_text = f" + {offset}"
    else:
        offset_text = f" - {-offset}"

    # Internal integer
    if seed_metadata.is_string:
        seed_int_label = f" ({seed_metadata.integer_value})"
    else:
        seed_int_label = ""

    return (seed_str, offset_text, seed_int_label)
