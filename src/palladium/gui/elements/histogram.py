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


from typing import Callable

import pygame as pg

from james import Element
from james.helpers.utils import get_text_surf
from james.elements.static_leaves.label import Label
from james.helpers.custom_types import SupportsGetItemColour

from palladium.core.custom_types import Colour
from palladium.core.utils import lerp_gradient
from palladium.gui.constants import BORDER_W, UI_MARGIN_XS, UI_MARGIN_S
from palladium.gui.themes import CLEAR
from palladium.core.utils import map_range


class HorizontalHistogram(Element):
    def __init__(
            self, *, flex: float = 0, shrink: float = 0,
            hover_tooltip: Label | None = None,
            data: dict[tuple[float, float], float],  # bin bounds, values - values can be float, e.g. percentage
            padding: int = UI_MARGIN_S,
            axis_label_font: pg.font.Font, data_label_font: pg.font.Font,
            axis_title_font: pg.font.Font,
            k_fg_bin_axis: str, bin_axis_title: str, k_fg_axis_value_labels: str,
            num_bin_axis_labels: int, gap: int = UI_MARGIN_XS,
            k_fg_data_value_labels: str, k_fg_data_value_gridlines: str,
            data_value_gridlines_interval: float,
            axis_thickness: int = BORDER_W, gridlines_thickness: int = BORDER_W,
            axis_formatter: Callable[[float], str] = lambda x: f"{x:,}",
            data_formatter: Callable[[float], str] = lambda x: f"{x:.2f}",
            bar_colour_scheme: dict[float, Colour]
        ) -> None:
        if num_bin_axis_labels <= 1:
            raise ValueError("Histogram requires at least two axis labels.")

        super().__init__(flex=flex, shrink=shrink, interactive=True, hover_tooltip=hover_tooltip)

        self.data = sorted(data.items(), key=lambda x: x[0][0])
        self.axis_label_font = axis_label_font
        self.data_label_font = data_label_font
        self.axis_title_font = axis_title_font

        self.k_fg_bin_axis = k_fg_bin_axis
        self.k_fg_data_value_gridlines = k_fg_data_value_gridlines
        self.k_fg_data_value_labels = k_fg_data_value_labels
        self.k_fg_axis_value_labels = k_fg_axis_value_labels

        self.bin_axis_title = bin_axis_title
        self.num_bin_axis_labels = num_bin_axis_labels
        self.data_value_gridlines_interval = data_value_gridlines_interval

        self.axis_thickness = axis_thickness
        self.gridlines_thickness = gridlines_thickness

        self.axis_formatter = axis_formatter
        self.data_formatter = data_formatter

        self.bar_colour_scheme = bar_colour_scheme

        self.gap = gap
        self.padding = padding

        self.work_surface = pg.Surface(self.rect.size, pg.SRCALPHA)

    def _min_and_max_bin(self) -> tuple[float, float]:
        min_bin = self.data[0][0][0]
        max_bin = self.data[-1][0][1]
        return min_bin, max_bin

    def _get_axis_label_values(self) -> list[float]:
        min_bin, max_bin = self._min_and_max_bin()
        increment = (max_bin - min_bin) / (self.num_bin_axis_labels - 1)
        return [min_bin + i * increment for i in range(self.num_bin_axis_labels)]

    def _get_axis_labels(self) -> list[str]:
        """Return axis labels in ascending order."""
        return [self.axis_formatter(val) for val in self._get_axis_label_values()]

    def _get_data_labels(self) -> list[str]:
        """Return value labels, sorted in ascending order by the lower bin bound for each bin. """
        return [self.data_formatter(value) for _, value in sorted(self.data, key=lambda x: x[0][0])]

    def set_data(self, data: dict[tuple[float, float], float]) -> None:
        self.data = sorted(data.items(), key=lambda x: x[0][0])

    def preferred_size(self) -> tuple[int, int]:
        # Total width
        max_axis_label_w = max(self.axis_label_font.size(label)[0] for label in self._get_axis_labels())
        max_data_label_w = max(self.data_label_font.size(label)[0] for label in self._get_data_labels())
        total_w = 3 * self.padding + self.axis_title_font.get_height() + max_axis_label_w + 2 * self.gap + max_data_label_w

        # Total height
        total_bar_h = self.data_label_font.get_height() * len(self.data)
        total_h = total_bar_h + self.axis_label_font.get_height() + 2 * self.padding

        return (total_w, total_h)

    def layout(self, rect: pg.Rect) -> None:
        self.assign_rect(rect)

        self.work_surface = pg.Surface(rect.size, pg.SRCALPHA)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        axis_labels = self._get_axis_labels()
        data_labels = self._get_data_labels()
        max_axis_label_w = max(self.axis_label_font.size(label)[0] for label in axis_labels)
        max_data_label_w = max(self.data_label_font.size(label)[0] for label in data_labels)

        # Calculate positions of axis text
        axis_label_right = self.rect.x + 2 * self.padding + max_axis_label_w + self.axis_label_font.get_height()

        min_bin, max_bin = self._min_and_max_bin()
        top_y = self.rect.y + self.padding + self.axis_label_font.get_height() // 2
        bottom_y = self.rect.bottom - self.padding - self.axis_label_font.get_height() // 2

        # Draw axis title
        axis_title_surf = get_text_surf(self.axis_label_font, self.bin_axis_title, theme[self.k_fg_bin_axis])
        rotated = pg.transform.rotate(axis_title_surf, 90)
        surface.blit(rotated, rotated.get_rect(
            centery=(top_y + bottom_y) / 2,
            left=self.rect.x + self.padding,
        ))

        # Draw axis text
        for axis_label_text, label_value in zip(axis_labels, self._get_axis_label_values()):
            text_surf = get_text_surf(self.axis_label_font, axis_label_text, theme[self.k_fg_axis_value_labels])
            surface.blit(text_surf, text_surf.get_rect(
                centery=map_range(label_value, min_bin, max_bin, bottom_y, top_y),
                right=axis_label_right
            ))

        # Draw bars
        bars_left = axis_label_right + self.gap
        bars_right = self.rect.right - self.padding - max_data_label_w - self.gap
        max_bar_w = bars_right - bars_left
        max_bin_val = max(b[1] for b in self.data)
        bar_h = self.data_label_font.get_height()

        for i, ((bin_lower, bin_upper), val) in enumerate(self.data[::-1]):
            # Colour the bars according to the midpoint of each bin
            bar_w = int(max_bar_w * (val / max_bin_val))
            bar_y = top_y + bar_h * i
            pg.draw.rect(
                surface, lerp_gradient((bin_lower + bin_upper) / 2, self.bar_colour_scheme),
                (bars_left, bar_y, bar_w, bar_h),
            )

            # Draw the labels
            label_left = bars_left + bar_w + self.gap
            label_surf = get_text_surf(self.data_label_font, data_labels[len(self.data) - i - 1], theme[self.k_fg_data_value_labels])
            surface.blit(label_surf, (label_left, bar_y))

        # Draw axis
        pg.draw.line(
            surface, theme[self.k_fg_bin_axis],
            (bars_left, top_y), (bars_left, bottom_y),
            width=self.axis_thickness
        )

        # Draw gridlines
        self.work_surface.fill(CLEAR)

        value = self.data_value_gridlines_interval
        while value < max_bin_val:
            gridline_x = bars_left + max_bar_w * value / max_bin_val
            pg.draw.line(
                self.work_surface, theme[self.k_fg_data_value_gridlines],
                (gridline_x - self.rect.x, top_y - self.rect.y),
                (gridline_x - self.rect.x, bottom_y - self.rect.y),
                width=self.axis_thickness
            )
            value += self.data_value_gridlines_interval

        surface.blit(self.work_surface, self.rect)
