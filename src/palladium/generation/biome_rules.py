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


from enum import IntEnum, auto
from dataclasses import dataclass

from palladium.generation.biomes import BiomeID
import palladium.generation.biome_descriptors as bd


class TerrainClass(IntEnum):
    UNASSIGNED = 0

    SUPERHEATED = auto()
    SUPER_HOT = auto()

    COASTAL = auto()
    SHALLOW_OCEANIC = auto()
    DEEP_OCEANIC = auto()

    VERY_HOT = auto()

    ARID = auto()

    HOT = auto()
    TEMPERATE = auto()
    COLD = auto()
    VERY_COLD = auto()
    CRYOGENIC = auto()


@dataclass
class BiomeRule:
    biome_id: BiomeID
    condition: bd.BiomeCondition

@dataclass
class ClassRule:
    class_id: TerrainClass
    condition: bd.BiomeCondition


# In order of how they should be applied.
# What determines each terrain class? (first match wins)
CLASS_RULES: list[ClassRule] = [
    ClassRule(
        TerrainClass.SUPERHEATED,
        lambda h, t, hum, g: t >= bd.T_SUPERHEATED,
    ),
    ClassRule(
        TerrainClass.SUPER_HOT,
        lambda h, t, hum, g: t >= bd.T_VOLCANIC
    ),
    ClassRule(
        TerrainClass.COASTAL,
        lambda h, t, hum, g: (h < bd.H_LAND) & (h >= bd.H_COASTAL)
    ),
    ClassRule(
        TerrainClass.SHALLOW_OCEANIC,
        lambda h, t, hum, g: (h < 0) & (h >= bd.H_SHALLOW)
    ),
    ClassRule(
        TerrainClass.DEEP_OCEANIC,
        lambda h, t, hum, g: h < bd.H_SHALLOW
    ),
    ClassRule(
        TerrainClass.VERY_HOT,
        lambda h, t, hum, g: t >= bd.T_SCORCHING
    ),
    ClassRule(
        TerrainClass.ARID,
        lambda h, t, hum, g: hum < bd.HUM_VERY_DRY
    ),
    ClassRule(
        TerrainClass.HOT,
        lambda h, t, hum, g: t >= bd.T_HOT
    ),
    ClassRule(
        TerrainClass.TEMPERATE,
        lambda h, t, hum, g: t >= bd.T_LUKEWARM
    ),
    ClassRule(
        TerrainClass.COLD,
        lambda h, t, hum, g: t >= bd.T_POLAR
    ),
    ClassRule(
        TerrainClass.VERY_COLD,
        lambda h, t, hum, g: t >= bd.T_CRYO
    ),
    ClassRule(
        TerrainClass.CRYOGENIC,
        bd.all_remaining
    )
]

# For each `TerrainClass`, what are the
# `BiomeRule`s that should be applied?
# Rules are applied in order in their respective lists. First match wins.
BIOME_RULES: dict[TerrainClass, list[BiomeRule]] = {
    TerrainClass.SUPERHEATED: [
        BiomeRule(
            BiomeID.SUPER_PLASMA,
            lambda h, t, hum, g: t >= 10_000,
        ),
        BiomeRule(
            BiomeID.PLASMA,
            lambda h, t, hum, g: t >= 8_000,
        ),
        BiomeRule(
            BiomeID.VAPOUR,
            lambda h, t, hum, g:
                (t >= 6_000)
                & (hum >= bd.HUM_SLIGHTLY_HUMID),
        ),
        BiomeRule(
            BiomeID.MOLTEN_PEAKS,
            lambda h, t, hum, g:
                (t >= 3_500)
                & (h >= bd.H_HIGHLANDS),
        ),
        BiomeRule(
            BiomeID.MOLTEN,
            lambda h, t, hum, g: t >= 3_500,
        ),
        BiomeRule(
            BiomeID.PYRO,
            lambda h, t, hum, g: t >= 2_500,
        ),
        BiomeRule(
            BiomeID.LAVA,
            lambda h, t, hum, g: t >= 800,
        ),
        BiomeRule(
            BiomeID.BASALT,
            lambda h, t, hum, g: h >= bd.H_HIGHLANDS,
        ),
        BiomeRule(
            BiomeID.MAGMA,
            bd.all_remaining
        )
    ],

    TerrainClass.SUPER_HOT: [
        BiomeRule(
            BiomeID.GEYSER,
            lambda h, t, hum, g:
                (hum > bd.HUM_VERY_HUMID) & bd.rare(g)
        ),
        BiomeRule(
            BiomeID.SULPHUR_MOUNTAINS,
            lambda h, t, hum, g:
                (h >= bd.H_MOUNTAINS) & bd.rare(g)
        ),
        BiomeRule(
            BiomeID.VOLCANO,
            lambda h, t, hum, g:
                h > bd.H_MOUNTAINS
        ),
        BiomeRule(
            BiomeID.SULPHUR_SLOPES,
            lambda h, t, hum, g:
                (h >= bd.H_ELEVATED) & bd.rare(g)
        ),
        BiomeRule(
            BiomeID.SULPHUR_PLAINS,
            lambda h, t, hum, g:
                bd.rare(g)
        ),
        BiomeRule(
            BiomeID.VOLCANIC_WASTES,
            lambda h, t, hum, g:
                hum < bd.HUM_DRY
        ),
        BiomeRule(
            BiomeID.VOLCANIC_PLAINS,
            bd.all_remaining
        )
    ],

    TerrainClass.COASTAL: [
        BiomeRule(
            BiomeID.VOLCANIC_BEACH,
            lambda h, t, hum, g:
                t > bd.T_VERY_HOT
        ),
        BiomeRule(
            BiomeID.TROPICAL_BEACH,
            lambda h, t, hum, g:
                t > bd.T_WARM
        ),
        BiomeRule(
            BiomeID.RED_BEACH,
            lambda h, t, hum, g:
                (t > bd.T_COOL) & bd.rare(g)
        ),
        BiomeRule(
            BiomeID.BEACH,
            lambda h, t, hum, g:
                t > bd.T_COOL
        ),
        BiomeRule(
            BiomeID.STONY_SHORE,
            lambda h, t, hum, g:
                t > bd.T_SUBARCTIC
        ),
        BiomeRule(
            BiomeID.SNOWY_BEACH,
            bd.all_remaining
        )
    ],

    TerrainClass.SHALLOW_OCEANIC: [
        # Hot liquids
        BiomeRule(
            BiomeID.SULPHUR_COAST,
            lambda h, t, hum, g: t >= bd.T_VERY_HOT,
        ),
        BiomeRule(
            BiomeID.REEF,
            lambda h, t, hum, g: t >= bd.T_VERY_WARM,
        ),
        BiomeRule(
            BiomeID.WARM_SEA,
            lambda h, t, hum, g: t >= bd.T_ROOM,
        ),
        BiomeRule(
            BiomeID.COLD_SEA,
            lambda h, t, hum, g: t >= bd.T_FREEZING,
        ),
        BiomeRule(
            BiomeID.FROZEN_COAST,
            bd.all_remaining
        )
    ],

    TerrainClass.DEEP_OCEANIC: [
        # Hot liquids
        BiomeRule(
            BiomeID.SULPHUR,
            lambda h, t, hum, g: t >= bd.T_VERY_HOT,
        ),

        BiomeRule(
            BiomeID.TROPICAL_OCEAN,
            lambda h, t, hum, g: t >= bd.T_WARM,
        ),

        # Nitrogen
        BiomeRule(
            BiomeID.NITROGEN_ICE,
            lambda h, t, hum, g:
                (t < bd.T_NITROGEN_MELTING_PT)
                & bd.super_rare(g),
        ),

        BiomeRule(
            BiomeID.NITROGEN_OCEAN,
            lambda h, t, hum, g:
                (t < bd.T_NITROGEN_BOILING_PT)
                & bd.super_rare(g),
        ),

        # Methane
        BiomeRule(
            BiomeID.METHANE_ICE,
            lambda h, t, hum, g:
                (t < bd.T_METHANE_MELTING_PT)
                & ~bd.alternate(g),
        ),

        BiomeRule(
            BiomeID.METHANE_OCEAN,
            lambda h, t, hum, g:
                (t < bd.T_METHANE_BOILING_PT)
                & ~bd.alternate(g),
        ),

        # Ethane
        BiomeRule(
            BiomeID.ETHANE_ICE,
            lambda h, t, hum, g:
                t < bd.T_ETHANE_MELTING_PT,
        ),

        BiomeRule(
            BiomeID.ETHANE_OCEAN,
            lambda h, t, hum, g:
                t < bd.T_ETHANE_BOILING_PT,
        ),

        # Generic frozen water
        BiomeRule(
            BiomeID.FROZEN_OCEAN,
            lambda h, t, hum, g: t < bd.T_FREEZING,
        ),

        # Other ocean
        BiomeRule(
            BiomeID.ABYSS,
            lambda h, t, hum, g:
                (t < bd.T_LUKEWARM) & (h < bd.H_DEEP)
                | (t < bd.T_VERY_COLD) & (h < bd.H_SHALLOW)
        ),

        BiomeRule(
            BiomeID.OCEAN,
            bd.all_remaining
        )
    ],

    TerrainClass.VERY_HOT: [
        BiomeRule(
            BiomeID.TAR_PEAKS,
            lambda h, t, hum, g: bd.asphalt(t, hum, g) & (h >= bd.H_MOUNTAINS)
        ),
        BiomeRule(
            BiomeID.ASPHALT,
            lambda h, t, hum, g: bd.asphalt(t, hum, g)
        ),
        BiomeRule(
            BiomeID.HOT_SPRING,
            lambda h, t, hum, g: bd.anti_rare(g) & (hum > bd.HUM_HUMID)
        ),
        BiomeRule(
            BiomeID.SCORCHED_MOUNTAINS,
            lambda h, t, hum, g: h >= bd.H_MOUNTAINS
        ),
        BiomeRule(
            BiomeID.SCORCHED_SLOPES,
            lambda h, t, hum, g: h >= bd.H_ELEVATED
        ),
        BiomeRule(
            BiomeID.SCORCHED_DESERT,
            lambda h, t, hum, g: hum < bd.HUM_SLIGHTLY_DRY
        ),
        BiomeRule(
            BiomeID.ASH_FOREST,
            lambda h, t, hum, g: hum >= bd.HUM_SLIGHTLY_HUMID
        ),
        BiomeRule(
            BiomeID.SCORCHED_PLAINS,
            bd.all_remaining
        )
    ],

    TerrainClass.ARID: [
        BiomeRule(
            BiomeID.SALT_FLATS,
            lambda h, t, hum, g: hum < bd.HUM_EXTREMELY_DRY
        ),
        BiomeRule(
            BiomeID.ALPINE,
            lambda h, t, hum, g: h > bd.H_HIGHLANDS
        ),
        BiomeRule(
            BiomeID.HOT_DESERT,
            lambda h, t, hum, g: t > bd.T_VERY_WARM
        ),
        BiomeRule(
            BiomeID.DESERT,
            lambda h, t, hum, g: t > bd.T_COOL
        ),
        BiomeRule(
            BiomeID.COLD_DESERT,
            bd.all_remaining
        ),
    ],

    TerrainClass.HOT: [
        BiomeRule(
            BiomeID.SWAMP,
            lambda h, t, hum, g: hum >= bd.HUM_EXTREMELY_HUMID
        ),
        BiomeRule(
            BiomeID.TROPICAL_RAINFOREST,
            lambda h, t, hum, g: hum >= bd.HUM_HUMID
        ),
        BiomeRule(
            BiomeID.SAVANNA,
            bd.all_remaining
        ),
    ],

    TerrainClass.TEMPERATE: [
        BiomeRule(
            BiomeID.TROPICAL_GRASS,
            lambda h, t, hum, g: hum < bd.HUM_SLIGHTLY_DRY
        ),
        BiomeRule(
            BiomeID.FOREST,
            lambda h, t, hum, g: hum < bd.HUM_HUMID
        ),
        BiomeRule(
            BiomeID.RAINFOREST,
            bd.all_remaining
        ),
    ],

    TerrainClass.COLD: [
        BiomeRule(
            BiomeID.GLACIAL_MOUNTAINS,
            lambda h, t, hum, g: (t < bd.T_FREEZING) & (h > bd.H_MOUNTAINS) & bd.rare(g)
        ),
        BiomeRule(
            BiomeID.GLACIER,
            lambda h, t, hum, g: (t < bd.T_FREEZING) & (h > bd.H_ELEVATED) & bd.rare(g)
        ),
        BiomeRule(
            BiomeID.ICY_SLOPES,
            lambda h, t, hum, g: (t < bd.T_FREEZING) & (h > bd.H_ELEVATED)
        ),
        BiomeRule(
            BiomeID.TUNDRA,
            lambda h, t, hum, g: (t < bd.T_FREEZING)
        ),
        BiomeRule(
            BiomeID.EXTREME_HILLS,
            lambda h, t, hum, g: bd.boreal(t, hum) & (h > bd.H_MOUNTAINS)
        ),
        BiomeRule(
            BiomeID.FOREST,
            lambda h, t, hum, g: (t > bd.T_COOL) & (hum < bd.HUM_HUMID)
        ),
        BiomeRule(
            BiomeID.BOREAL_FOREST,
            lambda h, t, hum, g: bd.boreal(t, hum)
        ),
        BiomeRule(
            BiomeID.GRASSLAND,
            lambda h, t, hum, g: hum < bd.HUM_SLIGHTLY_DRY
        ),
        BiomeRule(
            BiomeID.PINE_FOREST,
            bd.all_remaining
        )
    ],

    TerrainClass.VERY_COLD: [
        BiomeRule(
            BiomeID.FROZEN_PEAKS,
            lambda h, t, hum, g: h > bd.H_MOUNTAINS
        ),
        BiomeRule(
            BiomeID.PERMAFROST_PLAINS,
            lambda h, t, hum, g: t < bd.T_PERMAFROST
        ),
        BiomeRule(
            BiomeID.SNOW_PLAINS,
            lambda h, t, hum, g: bd.anti_alternate(g)
        ),
        BiomeRule(
            BiomeID.FROZEN_PLAINS,
            bd.all_remaining
        )
    ],

    TerrainClass.CRYOGENIC: [
        BiomeRule(
            BiomeID.DRY_ICE_PEAKS,
            lambda h, t, hum, g: (h > bd.H_MOUNTAINS) & bd.rare(g)
        ),
        BiomeRule(
            BiomeID.CRYO_PEAKS,
            lambda h, t, hum, g: (h > bd.H_MOUNTAINS)
        ),
        BiomeRule(
            BiomeID.DRY_ICE_SLOPES,
            lambda h, t, hum, g: (h > bd.H_ELEVATED) & bd.rare(g)
        ),
        BiomeRule(
            BiomeID.CRYO_SLOPES,
            lambda h, t, hum, g: (h > bd.H_ELEVATED)
        ),
        BiomeRule(
            BiomeID.CRYO_DESERT,
            lambda h, t, hum, g: hum < bd.HUM_DRY
        ),
        BiomeRule(
            BiomeID.CRYO_PLAINS,
            bd.all_remaining
        )
    ],
}


# Terrain classes without specified biome rules
unspecified = {cl for cl in TerrainClass if cl not in BIOME_RULES} - {TerrainClass.UNASSIGNED}
if unspecified:
    raise RuntimeError(f"Unspecified terrain class(es): {", ".join(u.name for u in unspecified)}")

# Unused terrain classes
unused = {cl for cl in TerrainClass if not any(c.class_id == cl for c in CLASS_RULES)} - {TerrainClass.UNASSIGNED}
if unused:
    print(f"Warning: {len(unused)} TerrainClasses have no class rule set.")
    for cl in unused:
        print(f"  - {cl.name}")

# Biome IDs that are not assigned to any biome rule
unassigned = {
    b for b in BiomeID
    if not any(
        br.biome_id == b for rule_list in BIOME_RULES.values()
        for br in rule_list
    )
} - {BiomeID.INVALID}

if unassigned:
    print(f"Warning: {len(unassigned)} BiomeIDs are not assigned to any biome rules:")
    for biome_id in unassigned:
        print(f"  - {biome_id.name}")
