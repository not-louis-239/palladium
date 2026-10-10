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
from james import Element, InputBox, RectButton, SupportsGetItemColour


def draw_elem(surface: pg.Surface, elem: Element, theme: SupportsGetItemColour) -> None:
    # Custom overrides in the renderer to add specialised behaviour to specific element types
    if isinstance(elem, RectButton):
        elem.draw_primitive(surface, theme)

        # bottom-only border
        pg.draw.line(
            surface, theme[elem.k_border],
            (elem.rect.left, elem.rect.bottom),
            (elem.rect.right, elem.rect.bottom),
            elem.border_w
        )

        return

    if isinstance(elem, InputBox):
        elem.draw_primitive(surface, theme)
        elem.draw_cursor(surface, theme)

        # bottom-only border
        pg.draw.line(
            surface, theme[elem.k_border],
            (elem.rect.left, elem.rect.bottom),
            (elem.rect.right, elem.rect.bottom),
            elem.border_w
        )

        elem.draw_tooltip_with_default_border(surface, theme)

        return

    elem.draw_default(surface, theme)
