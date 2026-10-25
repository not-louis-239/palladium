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


from __future__ import annotations

import math
import statistics
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame as pg

from palladium.core.constants import WN_H, WN_W
from palladium.gui.constants import UI_MARGIN_S, UI_MARGIN_XS
from palladium.gui.themes import TRANSLUCENT_BLACK, ThemeKey
from palladium.gui.utils import draw_transparent_rect

if TYPE_CHECKING:
    from palladium.game.game import Game


FPS_MARKERS = [30, 60]
PIXELS_PER_SECOND = 5_000


MAX_HISTORY_LEN = 100
BAR_W = math.ceil(WN_W / MAX_HISTORY_LEN)


@dataclass
class Snapshot:
    # times are measured in absolute readings from `time.time()`
    t_i: float
    t_update: float
    t_input: float
    t_draw: float


class Profiler:
    def __init__(self, game: Game) -> None:
        self.visible = False
        self.snapshots: list[Snapshot] = []
        self.game = game

        self.back_overlay_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)
        self.front_overlay_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)
        self._populate_overlay_surfaces()

    def _populate_overlay_surfaces(self) -> None:
        # Draw background on the back overlay surface
        highest_marker_h = int(PIXELS_PER_SECOND / min(FPS_MARKERS))
        draw_transparent_rect(
            self.back_overlay_surface, TRANSLUCENT_BLACK,
            pg.Rect(0, WN_H - highest_marker_h, WN_W, highest_marker_h)
        )

        # Draw markers on the front overlay surface
        font = self.game.assets.fonts.tips
        font_colour = self.game.current_theme()[ThemeKey.FG_ELEMS]

        for marker in FPS_MARKERS:
            marker_h = WN_H - int(PIXELS_PER_SECOND / marker)
            pg.draw.line(self.front_overlay_surface, self.game.current_theme()[ThemeKey.FG_ELEMS], (0, marker_h), (WN_W, marker_h))
            text_left, text_top = UI_MARGIN_XS, marker_h + UI_MARGIN_XS
            text = f"{marker:.0f} fps"
            self.front_overlay_surface.blit(font.render(text, True, font_colour), (text_left, text_top))

    def record_snapshot(self, *, t_i: float, t_update: float, t_input: float, t_draw: float) -> None:
        self.snapshots.append(Snapshot(t_i=t_i, t_update=t_update, t_input=t_input, t_draw=t_draw))
        self.snapshots = self.snapshots[-MAX_HISTORY_LEN:]

    def fps(self) -> float:
        if not self.snapshots:
            return 0.0
        t_current = time.time()
        t_first = self.snapshots[0].t_i
        return len(self.snapshots) / (t_current - t_first)

    @property
    def update_times(self) -> list[float]:
        return [s.t_update - s.t_i for s in self.snapshots]

    @property
    def input_times(self) -> list[float]:
        return [s.t_input - s.t_update for s in self.snapshots]

    @property
    def draw_times(self) -> list[float]:
        return [s.t_draw - s.t_input for s in self.snapshots]

    def show(self, surface: pg.Surface) -> None:
        if not self.visible:
            return

        surface.blit(self.back_overlay_surface)

        col_update = self.game.current_theme()[ThemeKey.FG_PROFILER_UPDATE]
        col_input = self.game.current_theme()[ThemeKey.FG_PROFILER_INPUT]
        col_draw = self.game.current_theme()[ThemeKey.FG_PROFILER_DRAW]

        # draw bars, yadda yadda...
        for i, snap in enumerate(self.snapshots):
            update_top = int(WN_H - PIXELS_PER_SECOND * (snap.t_update - snap.t_i))
            input_top = int(update_top - PIXELS_PER_SECOND * (snap.t_input - snap.t_update))
            draw_top = int(input_top - PIXELS_PER_SECOND * (snap.t_draw - snap.t_input))

            # Draw the bars
            bar_left_x = i * WN_W / MAX_HISTORY_LEN
            pg.draw.rect(surface, col_draw, (bar_left_x, draw_top, BAR_W, input_top - draw_top))
            pg.draw.rect(surface, col_input, (bar_left_x, input_top, BAR_W, update_top - input_top))
            pg.draw.rect(surface, col_update, (bar_left_x, update_top, BAR_W, WN_H - update_top))

        surface.blit(self.front_overlay_surface)

        # Show aggregate statistics
        font = self.game.assets.fonts.tips
        colour = self.game.current_theme()[ThemeKey.FG_ELEMS]
        graph_top = WN_H - int(PIXELS_PER_SECOND / min(FPS_MARKERS))

        total_times = [snap.t_draw - snap.t_i for snap in self.snapshots]
        t_min, t_avg, t_max = min(total_times), statistics.mean(total_times), max(total_times)

        surface.blit(s := font.render(
            f"{t_min * 1_000:.2f} ms min", True, colour),
            s.get_rect(left=UI_MARGIN_XS, bottom=graph_top - UI_MARGIN_XS)
        )
        surface.blit(s := font.render(
            f"{t_avg * 1_000:.2f} ms avg", True, colour),
            s.get_rect(centerx=WN_W // 2, bottom=graph_top - UI_MARGIN_XS)
        )
        surface.blit(s := font.render(
            f"{t_max * 1_000:.2f} ms max", True, colour),
            s.get_rect(right=WN_W - UI_MARGIN_XS, bottom=graph_top - UI_MARGIN_XS)
        )

        bottom = graph_top - s.height - UI_MARGIN_S

        t_avg_update = statistics.mean(self.update_times)
        t_avg_input = statistics.mean(self.input_times)
        t_avg_draw = statistics.mean(self.draw_times)

        for val, label, k_fg in (
            (t_avg_draw, "draw", ThemeKey.FG_PROFILER_DRAW),
            (t_avg_input, "input", ThemeKey.FG_PROFILER_INPUT),
            (t_avg_update, "update", ThemeKey.FG_PROFILER_UPDATE),
        ):
            text_surf = font.render(f"{val * 1_000:.3g} ms {label}", True, self.game.current_theme()[k_fg])
            surface.blit(text_surf, text_surf.get_rect(left=UI_MARGIN_XS, bottom=bottom))
            bottom -= text_surf.height + UI_MARGIN_XS

        # FPS summary
        surface.blit(
            s := font.render(f"{self.fps():.2f} fps", True, self.game.current_theme()[ThemeKey.FG_ELEMS]),
            s.get_rect(bottom=bottom, left=UI_MARGIN_XS)
        )
