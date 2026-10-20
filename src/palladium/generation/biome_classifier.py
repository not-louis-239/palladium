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


import numpy as np
from palladium.generation.biomes import BiomeID
from palladium.generation.biome_rules import BIOME_RULES, CLASS_RULES, TerrainClass


def _classify_terrain(
        heights: np.ndarray,
        temps: np.ndarray,
        humidities: np.ndarray,
        geology: np.ndarray,
    ) -> np.ndarray:

    temps_c = temps - 273.15

    terrain_classes = np.full(
        heights.shape,
        TerrainClass.UNASSIGNED,
        dtype=np.uint8,
    )

    remaining = np.ones(heights.shape, dtype=bool)

    for rule in CLASS_RULES:
        matches = (
            remaining
            & rule.condition(
                heights,
                temps_c,
                humidities,
                geology,
            )
        )

        terrain_classes[matches] = rule.class_id
        remaining &= ~matches

        if not remaining.any():
            break

    return terrain_classes

def _classify_biomes(
        terrain_classes: np.ndarray,
        heights: np.ndarray,
        temps: np.ndarray,
        humidities: np.ndarray,
        geology: np.ndarray,
    ) -> np.ndarray:

    temps_c = temps - 273.15

    biomes = np.full(
        heights.shape,
        BiomeID.INVALID,
        dtype=np.uint8,
    )

    for terrain_class, rules in BIOME_RULES.items():
        class_mask = terrain_classes == terrain_class

        if not class_mask.any():
            continue

        remaining = class_mask.copy()

        for rule in rules:
            matches = (
                remaining
                & rule.condition(
                    heights,
                    temps_c,
                    humidities,
                    geology,
                )
            )

            biomes[matches] = rule.biome_id
            remaining &= ~matches

            if not remaining.any():
                break

    assert not np.any(biomes == BiomeID.INVALID), "Invalid biome detected due to failure to classify all biomes"
    return biomes

def stats_to_biome_array(
        heights: np.ndarray,
        temps: np.ndarray,
        humidities: np.ndarray,
        geology: np.ndarray,
    ) -> np.ndarray:
    """Accepts input `np.ndarray`s and returns an `np.ndarray` of `BiomeID`s."""

    classes = _classify_terrain(heights, temps, humidities, geology)
    biomes = _classify_biomes(classes, heights, temps, humidities, geology)
    return biomes
