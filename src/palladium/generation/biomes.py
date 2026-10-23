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

import numpy as np

from palladium.core.custom_types import Colour


class BiomeID(IntEnum):
    INVALID = 0

    # Superheated / liquid biomes
    SUPER_PLASMA = auto()
    PLASMA = auto()
    VAPOUR = auto()
    MOLTEN_PEAKS = auto()
    MOLTEN = auto()

    # Very hot biomes
    PYRO = auto()
    LAVA = auto()
    BASALT = auto()
    MAGMA = auto()
    SCORCHED_MOUNTAINS = auto()
    SCORCHED_SLOPES = auto()
    SCORCHED_DESERT = auto()
    SCORCHED_PLAINS = auto()
    SULPHUR_MOUNTAINS = auto()
    SULPHUR_SLOPES = auto()
    SULPHUR_PLAINS = auto()
    VOLCANO = auto()
    VOLCANIC_PLAINS = auto()
    VOLCANIC_WASTES = auto()
    ASH_FOREST = auto()

    # Warm biomes
    WASTELAND = auto()
    SALT_FLATS = auto()
    ROCKY_DESERT = auto()
    BADLANDS = auto()
    HOT_DESERT = auto()
    DESERT = auto()
    COLD_DESERT = auto()
    TAR_PEAKS = auto()
    ASPHALT = auto()
    GEYSER = auto()
    HOT_SPRING = auto()
    SAVANNA = auto()
    TROPICAL_RAINFOREST = auto()
    SWAMP = auto()
    GRASSLAND = auto()
    TROPICAL_GRASS = auto()
    FOREST = auto()
    RAINFOREST = auto()

    # Cold biomes
    PINE_FOREST = auto()
    BOREAL_FOREST = auto()
    EXTREME_HILLS = auto()
    TUNDRA = auto()
    FROZEN_PLAINS = auto()
    FROZEN_PEAKS = auto()
    ALPINE = auto()

    # Cryogenic biomes
    CRYO_DESERT = auto()
    CRYO_PLAINS = auto()
    CRYO_SLOPES = auto()
    CRYO_PEAKS = auto()
    DRY_ICE_SLOPES = auto()
    DRY_ICE_PEAKS = auto()
    PERMAFROST_PLAINS = auto()
    SNOW_PLAINS = auto()
    ICY_SLOPES = auto()
    GLACIAL_MOUNTAINS = auto()
    GLACIER = auto()

    # Coastal biomes
    VOLCANIC_BEACH = auto()
    TROPICAL_BEACH = auto()
    RED_BEACH = auto()
    BEACH = auto()
    STONY_SHORE = auto()
    SNOWY_BEACH = auto()

    # Ocean biomes - ordered roughly by temp then depth
    SULPHUR_COAST = auto()
    SULPHUR = auto()
    REEF = auto()
    TROPICAL_OCEAN = auto()
    WARM_SEA = auto()
    COLD_SEA = auto()
    OCEAN = auto()
    ABYSS = auto()
    FROZEN_COAST = auto()
    FROZEN_OCEAN = auto()
    NITROGEN_ICE = auto()
    NITROGEN_OCEAN = auto()
    METHANE_ICE = auto()
    METHANE_OCEAN = auto()
    ETHANE_ICE = auto()
    ETHANE_OCEAN = auto()


@dataclass
class BiomeProfile:
    display_name: str
    colour: Colour


BIOME_PROFILES: dict[BiomeID, BiomeProfile] = {
    BiomeID.INVALID: BiomeProfile("Invalid", (255, 0, 0)),

    # Superheated / liquid biomes
    BiomeID.SUPER_PLASMA: BiomeProfile("Super Plasma", (255, 255, 230)),
    BiomeID.PLASMA: BiomeProfile("Plasma", (255, 252, 199)),
    BiomeID.VAPOUR: BiomeProfile("Vapour", (255, 242, 175)),
    BiomeID.MOLTEN_PEAKS: BiomeProfile("Molten Peaks", (255, 234, 150)),
    BiomeID.BASALT: BiomeProfile("Basalt", (78, 78, 64)),
    BiomeID.MOLTEN: BiomeProfile("Molten", (255, 226, 110)),

    # Very hot biomes
    BiomeID.PYRO: BiomeProfile("Pyro", (255, 207, 76)),
    BiomeID.LAVA: BiomeProfile("Lava", (255, 170, 23)),
    BiomeID.MAGMA: BiomeProfile("Magma", (255, 105, 0)),
    BiomeID.SCORCHED_MOUNTAINS: BiomeProfile("Scorched Mountains", (29, 26, 26)),
    BiomeID.SCORCHED_SLOPES: BiomeProfile("Scorched Slopes", (52, 47, 45)),
    BiomeID.SCORCHED_DESERT: BiomeProfile("Scorched Desert", (188, 170, 137)),
    BiomeID.SCORCHED_PLAINS: BiomeProfile("Scorched Plains", (208, 190, 157)),
    BiomeID.SULPHUR_MOUNTAINS: BiomeProfile("Sulphur Mountains", (116, 91, 44)),
    BiomeID.SULPHUR_SLOPES: BiomeProfile("Sulphur Slopes", (139, 116, 54)),
    BiomeID.SULPHUR_PLAINS: BiomeProfile("Sulphur Plains", (161, 142, 68)),
    BiomeID.VOLCANO: BiomeProfile("Volcano", (128, 0, 0)),
    BiomeID.VOLCANIC_PLAINS: BiomeProfile("Volcanic Plains", (137, 77, 77)),
    BiomeID.VOLCANIC_WASTES: BiomeProfile("Volcanic Wastes", (83, 47, 25)),
    BiomeID.ASH_FOREST: BiomeProfile("Ash Forest", (53, 50, 44)),

    # Warm biomes
    BiomeID.WASTELAND: BiomeProfile("Wasteland", (189, 172, 155)),
    BiomeID.SALT_FLATS: BiomeProfile("Salt Flats", (192, 192, 192)),
    BiomeID.ROCKY_DESERT: BiomeProfile("Rocky Desert", (204, 195, 186)),
    BiomeID.BADLANDS: BiomeProfile("Badlands", (176, 71, 26)),
    BiomeID.HOT_DESERT: BiomeProfile("Hot Desert", (255, 210, 127)),
    BiomeID.DESERT: BiomeProfile("Desert", (255, 234, 198)),
    BiomeID.COLD_DESERT: BiomeProfile("Cold Desert", (255, 250, 239)),
    BiomeID.TAR_PEAKS: BiomeProfile("Tar Peaks", (66, 62, 59)),
    BiomeID.ASPHALT: BiomeProfile("Asphalt", (45, 45, 45)),
    BiomeID.GEYSER: BiomeProfile("Geyser", (255, 101, 211)),
    BiomeID.HOT_SPRING: BiomeProfile("Hot Spring", (0, 255, 172)),
    BiomeID.SAVANNA: BiomeProfile("Savanna", (198, 218, 117)),
    BiomeID.TROPICAL_RAINFOREST: BiomeProfile("Tropical Rainforest", (0, 69, 0)),
    BiomeID.SWAMP: BiomeProfile("Swamp", (108, 129, 55)),
    BiomeID.GRASSLAND: BiomeProfile("Grassland", (255, 219, 73)),
    BiomeID.TROPICAL_GRASS: BiomeProfile("Tropical Grass", (201, 189, 11)),
    BiomeID.FOREST: BiomeProfile("Forest", (83, 220, 23)),
    BiomeID.RAINFOREST: BiomeProfile("Rainforest", (0, 142, 0)),

    # Cold biomes
    BiomeID.PINE_FOREST: BiomeProfile("Pine Forest", (88, 175, 141)),
    BiomeID.BOREAL_FOREST: BiomeProfile("Boreal Forest", (156, 217, 192)),
    BiomeID.EXTREME_HILLS: BiomeProfile("Extreme Hills", (149, 166, 158)),
    BiomeID.TUNDRA: BiomeProfile("Tundra", (207, 255, 255)),
    BiomeID.FROZEN_PLAINS: BiomeProfile("Frozen Plains", (207, 200, 255)),
    BiomeID.FROZEN_PEAKS: BiomeProfile("Frozen Peaks", (227, 220, 255)),
    BiomeID.ALPINE: BiomeProfile("Alpine", (167, 197, 209)),

    # Cryogenic biomes
    BiomeID.CRYO_DESERT: BiomeProfile("Cryo Desert", (180, 190, 200)),
    BiomeID.CRYO_PLAINS: BiomeProfile("Cryo Plains", (210, 225, 235)),
    BiomeID.CRYO_SLOPES: BiomeProfile("Cryo Slopes", (155, 180, 195)),
    BiomeID.CRYO_PEAKS: BiomeProfile("Cryo Peaks", (125, 155, 180)),
    BiomeID.DRY_ICE_SLOPES: BiomeProfile("Dry Ice Slopes", (230, 255, 255)),
    BiomeID.DRY_ICE_PEAKS: BiomeProfile("Dry Ice Peaks", (248, 255, 255)),
    BiomeID.PERMAFROST_PLAINS: BiomeProfile("Permafrost Plains", (224, 207, 179)),
    BiomeID.SNOW_PLAINS: BiomeProfile("Snow Plains", (247, 254, 255)),
    BiomeID.ICY_SLOPES: BiomeProfile("Icy Slopes", (207, 236, 255)),
    BiomeID.GLACIAL_MOUNTAINS: BiomeProfile("Glacial Mountains", (200, 189, 206)),
    BiomeID.GLACIER: BiomeProfile("Glacier", (143, 212, 255)),

    # Coastal biomes
    BiomeID.VOLCANIC_BEACH: BiomeProfile("Volcanic Beach", (131, 91, 80)),
    BiomeID.TROPICAL_BEACH: BiomeProfile("Tropical Beach", (255, 248, 157)),
    BiomeID.RED_BEACH: BiomeProfile("Red Beach", (186, 99, 73)),
    BiomeID.BEACH: BiomeProfile("Beach", (255, 250, 187)),
    BiomeID.STONY_SHORE: BiomeProfile("Stony Shore", (195, 195, 195)),
    BiomeID.SNOWY_BEACH: BiomeProfile("Snowy Beach", (228, 221, 255)),

    # Ocean biomes
    BiomeID.SULPHUR_COAST: BiomeProfile("Sulphur Coast", (226, 255, 153)),
    BiomeID.SULPHUR: BiomeProfile("Sulphur", (208, 255, 84)),
    BiomeID.REEF: BiomeProfile("Reef", (0, 255, 235)),
    BiomeID.TROPICAL_OCEAN: BiomeProfile("Tropical Ocean", (0, 116, 148)),
    BiomeID.WARM_SEA: BiomeProfile("Warm Sea", (0, 214, 255)),
    BiomeID.COLD_SEA: BiomeProfile("Cold Sea", (0, 155, 255)),
    BiomeID.OCEAN: BiomeProfile("Ocean", (0, 76, 112)),
    BiomeID.ABYSS: BiomeProfile("Abyss", (15, 0, 33)),
    BiomeID.FROZEN_COAST: BiomeProfile("Frozen Coast", (123, 212, 255)),
    BiomeID.FROZEN_OCEAN: BiomeProfile("Frozen Ocean", (177, 230, 255)),
    BiomeID.NITROGEN_ICE: BiomeProfile("Nitrogen Ice", (185, 225, 255)),
    BiomeID.NITROGEN_OCEAN: BiomeProfile("Nitrogen Ocean", (160, 210, 240)),
    BiomeID.METHANE_ICE: BiomeProfile("Methane Ice", (150, 190, 230)),
    BiomeID.METHANE_OCEAN: BiomeProfile("Methane Ocean", (135, 175, 215)),
    BiomeID.ETHANE_ICE: BiomeProfile("Ethane Ice", (178, 255, 227)),
    BiomeID.ETHANE_OCEAN: BiomeProfile("Ethane Ocean", (163, 255, 212)),
}

missing = set(BiomeID) - set(BIOME_PROFILES.keys())
if missing:
    raise RuntimeError(f"The following BiomeIDs are missing profiles:{"".join(f"\n  - {m.name}" for m in missing)}")


BIOME_COLOURS = np.array([
    BIOME_PROFILES[biome].colour
    for biome in BiomeID
], dtype=np.uint8)


def _test():
    print("Biomes:")

    for biome_profile in BIOME_PROFILES.values():
        colour = biome_profile.colour
        print(
            f"  - \033[38;2;{colour[0]};{colour[1]};{colour[2]}m██\033[0m"
            f" {biome_profile.display_name}"
        )


if __name__ == "__main__":
    _test()

