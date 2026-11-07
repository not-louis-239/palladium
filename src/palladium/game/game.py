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


import pygame as pg

from palladium.core.asset_manager import Assets
from palladium.core.constants import Controls
from palladium.core.profiler import Profiler
from palladium.core.data_manager import read_saved_seeds, write_saved_seeds
from palladium.generation.objects.planet import Planet
from palladium.generation.objects.star_system import StarSystem
from palladium.generation.generators.star_system_gen import generate_star_system
from palladium.gui.states import (
    BrowseStarState,
    BrowseSystemState,
    BrowseTerrainState,
    PlanetInfoState,
    PreferencesState,
    SavedSeedsState,
    SeedState,
    State,
    StateID,
    TitleState,
)
from palladium.gui.themes import THEMES, Theme


class Game:
    def __init__(self):
        self.assets = Assets()
        self.saved_seeds = read_saved_seeds()

        self.star_system: StarSystem | None = None
        self.planet_idx: int | None = None

        self.states: dict[StateID, State] = {
            StateID.TITLE: TitleState(self),
            StateID.ENTER_SEED: SeedState(self),
            StateID.BROWSE_SYSTEM: BrowseSystemState(self),
            StateID.BROWSE_STAR: BrowseStarState(self),
            StateID.BROWSE_TERRAIN: BrowseTerrainState(self),
            StateID.PLANET_INFO: PlanetInfoState(self),
            StateID.SAVED_SEEDS: SavedSeedsState(self),
            StateID.PREFS: PreferencesState(self)
        }
        self.state = StateID.TITLE

        self.theme_idx = 0
        self.profiler = Profiler(self)

    def quit(self) -> None:
        """Write data and cleanup."""
        write_saved_seeds(self.saved_seeds)

    def current_theme(self) -> Theme:
        return THEMES[self.theme_idx]

    def current_planet(self) -> Planet:
        """Do not call this until a star system and planet has been selected."""
        assert self.star_system is not None
        assert self.planet_idx is not None
        return self.star_system.planets[self.planet_idx]

    def refresh_seed_stats(self) -> None:
        """Regenerate each saved seed to refresh its generated statistics,
        including planet counts. Existing notes and metadata will be preserved."""

        for seed_record in self.saved_seeds:
            # Regenerate the system using the internal integer value
            integer_value = seed_record.seed_metadata.integer_value
            system = generate_star_system(integer_value)

            # Refresh properties
            seed_record.num_planets = len(system.planets)

    def enter_state(self, state: StateID) -> None:
        self.state = state
        self.states[self.state].on_entered()

    def update(self, dt_s: float) -> None:
        self.states[self.state].update(dt_s)

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.KEYDOWN and event.key == Controls.PROFILER_TOGGLE:
                self.profiler.visible = not self.profiler.visible

        self.states[self.state].take_input(keys, events, dt_s)

    def draw(self, screen: pg.Surface) -> None:
        self.states[self.state].draw(screen)
        self.profiler.show(screen)
