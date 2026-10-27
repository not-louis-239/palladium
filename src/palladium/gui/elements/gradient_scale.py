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


from collections.abc import Callable
from typing import Literal

import numpy as np
import pygame as pg
from james import Element
from james.elements.static_leaves.label import Label
from james.helpers.custom_types import SupportsGetItemColour
from james.helpers.utils import get_text_surf

from palladium.core.custom_types import Colour
from palladium.core.utils import map_range


class GradientScale(Element):
    def __init__(
            self, *,
            flex: float = 0, shrink: float = 0,
            hover_tooltip: Label | None = None,
            inset: int, gradient_w: int, gap: int,
            max_val: float, min_val: float, labels: dict[float, str],
            label_font: pg.font.Font, title_font: pg.font.Font,
            title_text: str, gradient_anchors: dict[float, Colour],
            k_bg: str, k_fg: str, value_transform: Callable[[float], float] | Literal["equidistant"] | None = None
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, interactive=True, hover_tooltip=hover_tooltip)

        if value_transform == "equidistant":
            if not (max_val in labels and min_val in labels):
                raise ValueError("If labels are equidistant, max_val and min_val must both be labels.")

        self.inset = inset
        self.gradient_w = gradient_w
        self.gap = gap

        self.max_val = max_val
        self.min_val = min_val

        self.label_font = label_font
        self.title_font = title_font

        self.title_text = title_text
        self.labels = labels
        self.gradient_anchors = gradient_anchors
        self.value_transform = value_transform

        self.k_bg = k_bg
        self.k_fg = k_fg

    def _equidistant_position(self, value: float) -> float:
        label_values = np.array(
            sorted(self.labels),
            dtype=np.float32,
        )

        label_positions = np.arange(
            len(label_values),
            dtype=np.float32,
        )

        return float(np.interp(
            value,
            label_values,
            label_positions,
        ))

    def _refresh_gradient_surf(self) -> None:
        height = (
            self.rect.height
            - 3 * self.inset
            - self.title_font.get_height()
            - self.label_font.get_height()
        )
        width = self.gradient_w

        anchors = sorted(self.gradient_anchors.items())

        anchor_values = np.array(
            [value for value, _ in anchors],
            dtype=np.float32,
        )

        if self.value_transform == "equidistant":
            label_values = list(self.labels)

            anchor_values = np.array([
                self._equidistant_position(value)
                for value in anchor_values
            ], dtype=np.float32)

            min_val = 0
            max_val = len(label_values) - 1

        elif callable(self.value_transform):
            anchor_values = np.array(
                [self.value_transform(value) for value in anchor_values],
                dtype=np.float32,
            )

            min_val = self.value_transform(self.min_val)
            max_val = self.value_transform(self.max_val)
        else:
            min_val = self.min_val
            max_val = self.max_val

        anchor_colours = np.array(
            [colour[:3] for _, colour in anchors],
            dtype=np.float32,
        )

        anchor_y = np.interp(
            anchor_values,
            [min_val, max_val],
            [height - 1, 0],
        )

        # Pixel coordinate for every row, from top to bottom.
        y = np.arange(height, dtype=np.float32)

        # Interpolate RGB independently between gradient anchors.
        rgb = np.column_stack([
            np.interp(
                y,
                anchor_y[::-1],
                anchor_colours[::-1, channel],
            )
            for channel in range(3)
        ])

        rgb = np.clip(rgb, 0, 255).astype(np.uint8)

        # Expand each row across the gradient's width.
        pixels = np.broadcast_to(
            rgb[:, None, :],
            (height, width, 3),
        )

        # surfarray expects the first dimension to be X.
        self.gradient_surf = pg.surfarray.make_surface(
            pixels.swapaxes(0, 1)
        )

    def preferred_size(self) -> tuple[int, int]:
        max_label_width = max(
            self.label_font.size(text)[0]
            for text in self.labels.values()
        )

        gradient_and_label_w = (
            self.gradient_w
            + self.gap
            + max_label_width
        )

        title_w = self.title_font.size(self.title_text)[0]

        width = (
            2 * self.inset
            + max(title_w, gradient_and_label_w)
        )

        height = (
            3 * self.inset
            + self.title_font.get_height()
            + self.label_font.get_height()
        )

        return (width, height)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
        self.layout_dirty = False

        self._refresh_gradient_surf()

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        # Draw background
        pg.draw.rect(surface, theme[self.k_bg], self.rect)

        # Draw title
        text_surf = get_text_surf(self.title_font, self.title_text, theme[self.k_fg])

        text_rect = text_surf.get_rect(
            top=self.rect.y + self.inset,
            centerx=self.rect.x + self.rect.width / 2
        )

        surface.blit(
            text_surf, text_rect
        )

        # Draw gradient
        gradient_top = text_rect.bottom + self.inset + self.label_font.get_height() // 2
        gradient_height = self.gradient_surf.get_height()
        gradient_left = self.rect.x + self.inset
        surface.blit(self.gradient_surf, (gradient_left, gradient_top))

        # Draw labels
        label_left = gradient_left + self.gradient_surf.width + self.gap

        if self.value_transform == "equidistant":
            if self.min_val not in self.labels or self.max_val not in self.labels:
                raise ValueError(
                    "value_transform='equidistant' requires "
                    "min_val and max_val to be labels"
                )

            positions = [
                map_range(
                    i,
                    0,
                    len(self.labels) - 1,
                    gradient_top + gradient_height,
                    gradient_top,
                )
                for i in range(len(self.labels))
            ]

        elif callable(self.value_transform):
            transformed_vals = [
                self.value_transform(value)
                for value in self.labels
            ]

            transformed_min = self.value_transform(self.min_val)
            transformed_max = self.value_transform(self.max_val)

            positions = [
                map_range(
                    value,
                    transformed_min,
                    transformed_max,
                    gradient_top + gradient_height,
                    gradient_top,
                )
                for value in transformed_vals
            ]

        else:
            positions = [
                map_range(
                    value,
                    self.min_val,
                    self.max_val,
                    gradient_top + gradient_height,
                    gradient_top,
                )
                for value in self.labels
            ]

        for text, y_pos in zip(self.labels.values(), positions):
            label_surf = get_text_surf(self.label_font, text, theme[self.k_fg])
            label_rect = label_surf.get_rect(centery=y_pos, left=label_left)
            surface.blit(label_surf, label_rect)
