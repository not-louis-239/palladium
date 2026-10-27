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



import pygame as pg

from palladium.core.custom_types import AColour
from palladium.generation.objects.star_system import SeedMetadata


def draw_transparent_rect(surface: pg.Surface, colour: AColour, rect: pg.Rect) -> None:
    """Draws a transparent rectangle. This function is dedicated
    to this purpose because `pg.draw.rect` doesn't work well: it overwrites
    alpha values on the destination surface instead of layering colours
    depending on opacity."""
    rect_surface = pg.Surface(rect.size, pg.SRCALPHA)
    rect_surface.fill(colour)
    surface.blit(rect_surface, rect)


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
