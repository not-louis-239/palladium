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


from dataclasses import dataclass
from enum import IntEnum, auto

import palladium.generation.biomes.biome_descriptors as bd
from palladium.generation.biomes.biomes import BiomeID
from palladium.generation.objects.field_types import FieldType


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
        lambda fields: fields[FieldType.TEMP] >= bd.T_SUPERHEATED,
    ),
    ClassRule(
        TerrainClass.SUPER_HOT,
        lambda fields: fields[FieldType.TEMP] >= bd.T_VOLCANIC
    ),
    ClassRule(
        TerrainClass.COASTAL,
        lambda fields: (fields[FieldType.HEIGHT] < bd.H_LAND) & (fields[FieldType.HEIGHT] >= bd.H_COASTAL)
    ),
    ClassRule(
        TerrainClass.SHALLOW_OCEANIC,
        lambda fields: (fields[FieldType.HEIGHT] < 0) & (fields[FieldType.HEIGHT] >= bd.H_SHALLOW)
    ),
    ClassRule(
        TerrainClass.DEEP_OCEANIC,
        lambda fields: fields[FieldType.HEIGHT] < bd.H_SHALLOW
    ),
    ClassRule(
        TerrainClass.VERY_HOT,
        lambda fields: fields[FieldType.TEMP] >= bd.T_SCORCHING
    ),
    ClassRule(
        TerrainClass.CRYOGENIC,
        lambda fields: fields[FieldType.TEMP] < bd.T_CRYO
    ),
    ClassRule(
        TerrainClass.VERY_COLD,
        lambda fields: fields[FieldType.TEMP] < bd.T_POLAR
    ),
    ClassRule(
        TerrainClass.ARID,
        lambda fields: fields[FieldType.HUMIDITY] < bd.HUM_VERY_DRY
    ),
    ClassRule(
        TerrainClass.HOT,
        lambda fields: fields[FieldType.TEMP] >= bd.T_HOT
    ),
    ClassRule(
        TerrainClass.TEMPERATE,
        lambda fields: fields[FieldType.TEMP] >= bd.T_LUKEWARM
    ),
    ClassRule(
        TerrainClass.COLD,
        bd.all_remaining
    ),
]

# For each `TerrainClass`, what are the
# `BiomeRule`s that should be applied?
# Rules are applied in order in their respective lists. First match wins.
BIOME_RULES: dict[TerrainClass, list[BiomeRule]] = {
    TerrainClass.SUPERHEATED: [
        BiomeRule(
            BiomeID.SUPER_PLASMA,
            lambda fields: fields[FieldType.TEMP] >= 10_000,
        ),
        BiomeRule(
            BiomeID.PLASMA,
            lambda fields: fields[FieldType.TEMP] >= 8_000,
        ),
        BiomeRule(
            BiomeID.VAPOUR,
            lambda fields:
                (fields[FieldType.TEMP] >= 6_000)
                & (fields[FieldType.HUMIDITY] >= bd.HUM_SLIGHTLY_HUMID),
        ),
        BiomeRule(
            BiomeID.MOLTEN_PEAKS,
            lambda fields:
                (fields[FieldType.TEMP] >= 3_500)
                & (fields[FieldType.HEIGHT] >= bd.H_HIGHLANDS),
        ),
        BiomeRule(
            BiomeID.MOLTEN,
            lambda fields: fields[FieldType.TEMP] >= 3_500,
        ),
        BiomeRule(
            BiomeID.PYRO,
            lambda fields: fields[FieldType.TEMP] >= 2_500,
        ),
        BiomeRule(
            BiomeID.LAVA,
            lambda fields: fields[FieldType.TEMP] >= 800,
        ),
        BiomeRule(
            BiomeID.BASALT,
            lambda fields: fields[FieldType.HEIGHT] >= bd.H_ELEVATED,
        ),
        BiomeRule(
            BiomeID.MAGMA,
            bd.all_remaining
        )
    ],

    TerrainClass.SUPER_HOT: [
        BiomeRule(
            BiomeID.GEYSER,
            lambda fields:
                (fields[FieldType.HUMIDITY] > bd.HUM_VERY_HUMID) & bd.rare(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.SULPHUR_MOUNTAINS,
            lambda fields:
                (fields[FieldType.HEIGHT] >= bd.H_MOUNTAINS) & bd.rare(fields[FieldType.SPECIAL_1])
        ),
        BiomeRule(
            BiomeID.VOLCANO,
            lambda fields:
                fields[FieldType.HEIGHT] > bd.H_MOUNTAINS
        ),
        BiomeRule(
            BiomeID.SULPHUR_SLOPES,
            lambda fields:
                (fields[FieldType.HEIGHT] >= bd.H_ELEVATED) & bd.rare(fields[FieldType.SPECIAL_1])
        ),
        BiomeRule(
            BiomeID.SULPHUR_PLAINS,
            lambda fields:
                bd.rare(fields[FieldType.SPECIAL_1])
        ),
        BiomeRule(
            BiomeID.VOLCANIC_WASTES,
            lambda fields:
                fields[FieldType.HUMIDITY] < bd.HUM_DRY
        ),
        BiomeRule(
            BiomeID.VOLCANIC_PLAINS,
            bd.all_remaining
        )
    ],

    TerrainClass.COASTAL: [
        BiomeRule(
            BiomeID.VOLCANIC_BEACH,
            lambda fields:
                fields[FieldType.TEMP] > bd.T_VERY_HOT
        ),
        BiomeRule(
            BiomeID.TROPICAL_BEACH,
            lambda fields:
                fields[FieldType.TEMP] > bd.T_WARM
        ),
        BiomeRule(
            BiomeID.RED_BEACH,
            lambda fields:
                (fields[FieldType.TEMP] > bd.T_COOL) & bd.rare(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.BEACH,
            lambda fields:
                fields[FieldType.TEMP] > bd.T_COOL
        ),
        BiomeRule(
            BiomeID.STONY_SHORE,
            lambda fields:
                fields[FieldType.TEMP] > bd.T_SUBARCTIC
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
            lambda fields: fields[FieldType.TEMP] >= bd.T_VERY_HOT,
        ),
        BiomeRule(
            BiomeID.REEF,
            lambda fields: fields[FieldType.TEMP] >= bd.T_VERY_WARM,
        ),
        BiomeRule(
            BiomeID.WARM_SEA,
            lambda fields: fields[FieldType.TEMP] >= bd.T_ROOM,
        ),
        BiomeRule(
            BiomeID.COLD_SEA,
            lambda fields: fields[FieldType.TEMP] >= bd.T_FREEZING,
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
            lambda fields: fields[FieldType.TEMP] >= bd.T_VERY_HOT,
        ),

        BiomeRule(
            BiomeID.TROPICAL_OCEAN,
            lambda fields: fields[FieldType.TEMP] >= bd.T_WARM,
        ),

        # Nitrogen
        BiomeRule(
            BiomeID.NITROGEN_ICE,
            lambda fields:
                (fields[FieldType.TEMP] < bd.T_NITROGEN_MELTING_PT)
                & bd.super_rare(fields[FieldType.SPECIAL_0]),
        ),

        BiomeRule(
            BiomeID.NITROGEN_OCEAN,
            lambda fields:
                (fields[FieldType.TEMP] < bd.T_NITROGEN_BOILING_PT)
                & bd.super_rare(fields[FieldType.SPECIAL_0]),
        ),

        # Methane
        BiomeRule(
            BiomeID.METHANE_ICE,
            lambda fields:
                (fields[FieldType.TEMP] < bd.T_METHANE_MELTING_PT)
                & ~bd.alternate(fields[FieldType.SPECIAL_1]),
        ),

        BiomeRule(
            BiomeID.METHANE_OCEAN,
            lambda fields:
                (fields[FieldType.TEMP] < bd.T_METHANE_BOILING_PT)
                & ~bd.alternate(fields[FieldType.SPECIAL_1]),
        ),

        # Ethane
        BiomeRule(
            BiomeID.ETHANE_ICE,
            lambda fields:
                fields[FieldType.TEMP] < bd.T_ETHANE_MELTING_PT,
        ),

        BiomeRule(
            BiomeID.ETHANE_OCEAN,
            lambda fields:
                fields[FieldType.TEMP] < bd.T_ETHANE_BOILING_PT,
        ),

        # Generic frozen water
        BiomeRule(
            BiomeID.FROZEN_OCEAN,
            lambda fields: fields[FieldType.TEMP] < bd.T_FREEZING,
        ),

        # Other ocean
        BiomeRule(
            BiomeID.ABYSS,
            lambda fields:
                (fields[FieldType.TEMP] < bd.T_LUKEWARM) & (fields[FieldType.HEIGHT] < bd.H_DEEP)
                | (fields[FieldType.TEMP] < bd.T_VERY_COLD) & (fields[FieldType.HEIGHT] < bd.H_SHALLOW)
        ),

        BiomeRule(
            BiomeID.OCEAN,
            bd.all_remaining
        )
    ],

    TerrainClass.VERY_HOT: [
        BiomeRule(
            BiomeID.TAR_PEAKS,
            lambda fields: bd.asphalt(fields) & (fields[FieldType.HEIGHT] >= bd.H_MOUNTAINS)
        ),
        BiomeRule(
            BiomeID.ASPHALT,
            lambda fields: bd.asphalt(fields)
        ),
        BiomeRule(
            BiomeID.HOT_SPRING,
            lambda fields: bd.anti_rare(fields[FieldType.SPECIAL_0]) & (fields[FieldType.HUMIDITY] > bd.HUM_HUMID)
        ),
        BiomeRule(
            BiomeID.SCORCHED_MOUNTAINS,
            lambda fields: fields[FieldType.HEIGHT] >= bd.H_MOUNTAINS
        ),
        BiomeRule(
            BiomeID.SCORCHED_SLOPES,
            lambda fields: fields[FieldType.HEIGHT] >= bd.H_ELEVATED
        ),
        BiomeRule(
            BiomeID.SCORCHED_DESERT,
            lambda fields: fields[FieldType.HUMIDITY] < bd.HUM_SLIGHTLY_DRY
        ),
        BiomeRule(
            BiomeID.ASH_FOREST,
            lambda fields: fields[FieldType.HUMIDITY] >= bd.HUM_SLIGHTLY_HUMID
        ),
        BiomeRule(
            BiomeID.SCORCHED_PLAINS,
            bd.all_remaining
        )
    ],

    TerrainClass.ARID: [
        BiomeRule(
            BiomeID.WASTELAND,
            lambda fields: (fields[FieldType.HUMIDITY] < bd.HUM_VERY_DRY) & bd.rare(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.SALT_FLATS,
            lambda fields: fields[FieldType.HUMIDITY] < bd.HUM_EXTREMELY_DRY
        ),
        BiomeRule(
            BiomeID.ALPINE,
            lambda fields: fields[FieldType.HEIGHT] > bd.H_HIGHLANDS
        ),
        BiomeRule(
            BiomeID.BADLANDS,
            lambda fields: (fields[FieldType.TEMP] > bd.T_VERY_WARM) & bd.alternate(fields[FieldType.SPECIAL_1])
        ),
        BiomeRule(
            BiomeID.OASIS,
            lambda fields: (fields[FieldType.TEMP] > bd.T_COOL) & bd.rare(fields[FieldType.SPECIAL_2])
        ),
        BiomeRule(
            BiomeID.HOT_DESERT,
            lambda fields: fields[FieldType.TEMP] > bd.T_VERY_WARM
        ),
        BiomeRule(
            BiomeID.ROCKY_DESERT,
            lambda fields: (fields[FieldType.TEMP] > bd.T_COOL) & bd.alternate(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.DESERT,
            lambda fields: fields[FieldType.TEMP] > bd.T_COOL
        ),
        BiomeRule(
            BiomeID.COLD_DESERT,
            bd.all_remaining
        ),
    ],

    TerrainClass.HOT: [
        BiomeRule(
            BiomeID.SWAMP,
            lambda fields: fields[FieldType.HUMIDITY] >= bd.HUM_EXTREMELY_HUMID
        ),
        BiomeRule(
            BiomeID.TROPICAL_RAINFOREST,
            lambda fields: fields[FieldType.HUMIDITY] >= bd.HUM_HUMID
        ),
        BiomeRule(
            BiomeID.SAVANNA,
            bd.all_remaining
        ),
    ],

    TerrainClass.TEMPERATE: [
        BiomeRule(
            BiomeID.TROPICAL_GRASS,
            lambda fields: fields[FieldType.HUMIDITY] < bd.HUM_SLIGHTLY_DRY
        ),
        BiomeRule(
            BiomeID.FOREST,
            lambda fields: fields[FieldType.HUMIDITY] < bd.HUM_HUMID
        ),
        BiomeRule(
            BiomeID.RAINFOREST,
            bd.all_remaining
        ),
    ],

    TerrainClass.COLD: [
        BiomeRule(
            BiomeID.GLACIAL_MOUNTAINS,
            lambda fields: (fields[FieldType.TEMP] < bd.T_FREEZING) & (fields[FieldType.HEIGHT] > bd.H_MOUNTAINS) & bd.rare(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.GLACIER,
            lambda fields: (fields[FieldType.TEMP] < bd.T_FREEZING) & (fields[FieldType.HEIGHT] > bd.H_ELEVATED) & bd.rare(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.ICY_SLOPES,
            lambda fields: (fields[FieldType.TEMP] < bd.T_FREEZING) & (fields[FieldType.HEIGHT] > bd.H_ELEVATED)
        ),
        BiomeRule(
            BiomeID.TUNDRA,
            lambda fields: (fields[FieldType.TEMP] < bd.T_FREEZING)
        ),
        BiomeRule(
            BiomeID.EXTREME_HILLS,
            lambda fields: bd.boreal(fields) & (fields[FieldType.HEIGHT] > bd.H_MOUNTAINS)
        ),
        BiomeRule(
            BiomeID.FOREST,
            lambda fields: (fields[FieldType.TEMP] > bd.T_COOL) & (fields[FieldType.HUMIDITY] < bd.HUM_HUMID)
        ),
        BiomeRule(
            BiomeID.BOREAL_FOREST,
            lambda fields: bd.boreal(fields)
        ),
        BiomeRule(
            BiomeID.GRASSLAND,
            lambda fields: fields[FieldType.HUMIDITY] < bd.HUM_SLIGHTLY_DRY
        ),
        BiomeRule(
            BiomeID.PINE_FOREST,
            bd.all_remaining
        )
    ],

    TerrainClass.VERY_COLD: [
        BiomeRule(
            BiomeID.FROZEN_PEAKS,
            lambda fields: fields[FieldType.HEIGHT] > bd.H_MOUNTAINS
        ),
        BiomeRule(
            BiomeID.PERMAFROST_PLAINS,
            lambda fields: fields[FieldType.TEMP] < bd.T_PERMAFROST
        ),
        BiomeRule(
            BiomeID.SNOW_PLAINS,
            lambda fields: bd.anti_alternate(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.FROZEN_PLAINS,
            bd.all_remaining
        )
    ],

    TerrainClass.CRYOGENIC: [
        BiomeRule(
            BiomeID.DRY_ICE_PEAKS,
            lambda fields: (fields[FieldType.HEIGHT] > bd.H_MOUNTAINS) & bd.rare(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.CRYO_PEAKS,
            lambda fields: (fields[FieldType.HEIGHT] > bd.H_MOUNTAINS)
        ),
        BiomeRule(
            BiomeID.DRY_ICE_SLOPES,
            lambda fields: (fields[FieldType.HEIGHT] > bd.H_ELEVATED) & bd.rare(fields[FieldType.SPECIAL_0])
        ),
        BiomeRule(
            BiomeID.CRYO_SLOPES,
            lambda fields: (fields[FieldType.HEIGHT] > bd.H_ELEVATED)
        ),
        BiomeRule(
            BiomeID.CRYO_DESERT,
            lambda fields: fields[FieldType.HUMIDITY] < bd.HUM_DRY
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
