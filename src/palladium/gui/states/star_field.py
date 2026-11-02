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


import math

import numpy as np
import pygame as pg

from functools import lru_cache
from dataclasses import dataclass, field

from palladium.core.constants import WN_W, WN_H
from palladium.gui.utils import generate_bg_star_positions, star_surface, Camera


STAR_BG_WRAP_BOUNDS_AU = np.array([25_000, 25_000], dtype=np.float32)
STAR_DENSITY = 0.0000004  # per au^2 per layer
STAR_DENSITY_FACTOR_MULT = 250
STAR_BG_WRAP_BOUNDS_AU_ARR = np.asarray(
    STAR_BG_WRAP_BOUNDS_AU,
    dtype=np.float32,
)

HALF_WN_SIZE_ARR = np.array([WN_W / 2, WN_H / 2], dtype=np.float32)

PARALLAX_FACTORS = (
    0.02,
    0.05,
    0.10,
    0.18,
)

STAR_SURFACES = [
    pg.transform.smoothscale_by(star_surface, x / max(PARALLAX_FACTORS))
    for x in PARALLAX_FACTORS
]


@lru_cache(maxsize=16)
def generate_star_field(seed: int) -> Starfield:
    """Returns a list of star layers, each containing a set of star positions and parallax values."""
    star_positions = [
        _StarLayer(
            positions := generate_bg_star_positions(
                seed=(seed + i) % 2**63,
                wrap_bounds=(int(STAR_BG_WRAP_BOUNDS_AU[0]), int(STAR_BG_WRAP_BOUNDS_AU[1])),
                star_density_per_pix2=STAR_DENSITY
            ),
            parallax,
            STAR_SURFACES[i],
            indices=np.arange(len(positions), dtype=np.uint32)
        )
        for i, parallax in enumerate(PARALLAX_FACTORS)
    ]

    return Starfield(layers=star_positions)


@lru_cache(maxsize=1024)
def get_num_tiles(zoom_level: float) -> tuple[int, int]:
    """Returns the tile sizes for a given zoom level."""
    tile_size_pix = (STAR_BG_WRAP_BOUNDS_AU_ARR / zoom_level)
    tiles_x = int(np.ceil(WN_W / tile_size_pix[0] / 2)) + 1
    tiles_y = int(np.ceil(WN_H / tile_size_pix[1] / 2)) + 1
    return tiles_x, tiles_y


def _hash_stars(
        layer: _StarLayer,
        tile_x: int,
        tile_y: int,
    ) -> np.ndarray:
    tile_x_hash = np.uint32(tile_x % 2**32)
    tile_y_hash = np.uint32(tile_y % 2**32)

    values = (
        layer.indices
        + tile_x_hash * np.uint32(73856093)
        + tile_y_hash * np.uint32(19349663)
    )

    values ^= values >> np.uint32(13)
    values *= np.uint32(1274126177)
    values ^= values >> np.uint32(16)

    return values


def _get_star_hashes(
    layer: _StarLayer,
    tile_x: int,
    tile_y: int,
) -> np.ndarray:
    key = (tile_x, tile_y)

    if key not in layer.hash_cache:
        layer.hash_cache[key] = _hash_stars(
            layer,
            tile_x,
            tile_y,
        )

    return layer.hash_cache[key]


@dataclass
class _StarLayer:
    positions: np.ndarray
    parallax_value: float
    star_img: pg.Surface
    indices: np.ndarray
    hash_cache: dict[tuple[int, int], np.ndarray] = field(default_factory=dict)  # {(tile_x, tile_y): star_hashes}
    tile_cache: dict[tuple[int, int], np.ndarray] = field(default_factory=dict)  # {(tile_x, tile_y): star_positions}
    cache_zoom: int | None = None


@dataclass
class Starfield:
    layers: list[_StarLayer]

    def _draw_layer(self, screen: pg.Surface, camera: Camera, layer: _StarLayer) -> None:
        # Density factor needs to be quadratic as zooming out by a factor of N
        # shows N^2 more stars, so this compensates.

        # Camera / density factor
        # Density factor is >1 to intentionally increase the frequency of stars appearing
        # Somehow it doesn't tank performance that much so it can compensate for reducing the star density
        zoom = camera.zoom_au_per_pix
        density_factor = STAR_DENSITY_FACTOR_MULT / zoom ** 2
        density_threshold = np.uint32(min(1, density_factor) * (2**32 - 1))
        tiles_x, tiles_y = get_num_tiles(zoom_level=zoom)
        tile_size_pix = (STAR_BG_WRAP_BOUNDS_AU_ARR / zoom)  # size of 1 star tile in pixels

        # Scroll offset in tiles
        bg_scroll_offset = camera.pos * layer.parallax_value
        scroll_offset_tiles_x: int = math.floor(bg_scroll_offset.x / STAR_BG_WRAP_BOUNDS_AU_ARR[0])
        scroll_offset_tiles_y: int = math.floor(bg_scroll_offset.y / STAR_BG_WRAP_BOUNDS_AU_ARR[1])

        # Positioning - convert to screen space while we're at it
        screen_positions = (
            (layer.positions - (np.asarray(bg_scroll_offset) % STAR_BG_WRAP_BOUNDS_AU))
            / zoom
        )

        min_bound = -star_surface.get_width()

        for dx in range(-tiles_x, tiles_x + 1):
            # Calculate X-offsets and values
            offset_x = dx * tile_size_pix[0]

            x_positions = screen_positions[:, 0] + offset_x
            x_candidate = (
                (x_positions >= min_bound - HALF_WN_SIZE_ARR[0])
                & (x_positions <= WN_W - HALF_WN_SIZE_ARR[0])
            )

            if not x_candidate.size:
                continue

            tile_x = dx + scroll_offset_tiles_x
            x_indices = np.flatnonzero(x_candidate)
            y = screen_positions[x_indices, 1]

            for dy in range(-tiles_y, tiles_y + 1):
                # Calculate Y-offsets and values
                offset_y = dy * tile_size_pix[1]

                # Cull by screen bounds
                candidate_indices = x_indices[
                    (y >= min_bound - offset_y - HALF_WN_SIZE_ARR[1])
                    & (y <= WN_H - offset_y - HALF_WN_SIZE_ARR[1])
                ]

                if not candidate_indices.size:
                    continue

                # Pseudo-random hashing and density culling
                if density_factor < 1.0:
                    tile_y = dy + scroll_offset_tiles_y
                    hashes = _get_star_hashes(layer, tile_x, tile_y)
                    keep = hashes[candidate_indices] < density_threshold
                    candidate_indices = candidate_indices[keep]

                if not (tile_blits := screen_positions[candidate_indices]).size:
                    # No blits, so don't bother calculating offset.
                    continue

                # Account for tile offset
                tile_blits = tile_blits.copy()
                tile_blits[:, 0] += offset_x
                tile_blits[:, 1] += offset_y

                print(f"Tile blits shape: {tile_blits.shape}")
                print(f"Tile blits size: {tile_blits.size}")

                # Blit the star images
                # Compensate for the width of the star surface
                # and make sure that the positions converge at the centre
                screen.fblits([
                    (layer.star_img, b)
                    for b in (tile_blits + HALF_WN_SIZE_ARR - star_surface.get_width() / 2)
                ])

    def draw(self, screen: pg.Surface, camera: Camera) -> None:
        for layer in self.layers:
            self._draw_layer(screen, camera, layer)
