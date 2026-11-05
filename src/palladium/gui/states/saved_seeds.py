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
from typing import TYPE_CHECKING
from datetime import date, datetime, timezone

import pygame as pg

from james import HBox, VBox, Panel, ScrollableDisplay, Scrollbar, Label, Spacer, CircleButton, Element, GUI

from palladium.core.constants import WN_W
from palladium.gui.utils import format_save_duration_ago, get_seed_messages
from palladium.gui.states.base import StateID
from palladium.gui.themes import ThemeKey
from palladium.gui.constants import UI_MARGIN_M, DEFAULT_ATTRS, UI_MARGIN_S, UI_MARGIN_XS, SCREEN_RECT, ICON_SIZE
from palladium.gui.states.base import State
from palladium.core.data_manager import SeedRecord


if TYPE_CHECKING:
    from palladium.game.game import Game


# TODO: add a setting to ScrollableDisplay where all its children inherit its width or height


def _format_date(value: date) -> str:
    """
    Format a date string, e.g.:

    - this year: "Mon 1 Jan"
    - if it's a previous year, includes the year: "Mon 1 Jan 2023"
    """

    # TODO: include the time

    fmt = "%a {day} %b"
    if value.year != date.today().year:
        fmt += " %Y"

    return value.strftime(fmt.format(day=value.day))


class SavedSeedsState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.setup_ui()

    def setup_ui(self) -> None:
        self.seeds_vbox: VBox = VBox(
            gap=UI_MARGIN_S,
        )

        self.panel = Panel(
            VBox(
                HBox(
                    back_button := CircleButton(
                        r=ICON_SIZE // 2,
                        img_path=self.images.back,
                        **DEFAULT_ATTRS,
                    ),
                    Spacer(),
                    Label(
                        text="saved seeds",
                        font=self.fonts.heading,
                        k_fg=ThemeKey.FG_ELEMS
                    ),
                    Spacer(),
                    world_count_label := Label(
                        k_fg=ThemeKey.FG_ACCENT,
                        inset=UI_MARGIN_S,
                        font=self.fonts.text,
                    ),
                    CircleButton(
                        r=ICON_SIZE // 2,
                        k_fg_colour=ThemeKey.FG_ACCENT,
                        img_inset=UI_MARGIN_S,
                        img_path=self.images.trees
                    ),
                ),
                HBox(
                    seeds_scrollable := ScrollableDisplay(
                        flex=1.0,
                        shrink=1.0,
                        min_internal_w=WN_W - 3 * UI_MARGIN_M - UI_MARGIN_S,
                        child=self.seeds_vbox
                    ),
                    Scrollbar(
                        tied_to=seeds_scrollable,
                        bar_thickness=UI_MARGIN_S,
                        groove_thickness=UI_MARGIN_S,
                        k_bar=ThemeKey.FG_ELEMS,
                        k_bar_hovered=ThemeKey.FG_HOVERED,
                        k_bar_pressed=ThemeKey.FG_PRESSED,
                        k_groove=ThemeKey.FG_SENTINEL,
                    ),
                ),
                gap=UI_MARGIN_S
            ),
            horiz_padding=UI_MARGIN_M,
            vert_padding=UI_MARGIN_M,
        )

        self.back_button = back_button
        self.seed_count_label = world_count_label
        self.seeds_scrollable = seeds_scrollable
        self.hovered_panel = None

        # Make a triplet of action buttons that can be subbed in anywhere
        self.action_buttons = HBox(
            # Load seed
            CircleButton(
                r=ICON_SIZE // 2,
                k_fg_colour=ThemeKey.FG_ACCENT,
                img_path=self.images.play
            ),
            # Edit seed
            CircleButton(
                r=ICON_SIZE // 2,
                k_fg_colour=ThemeKey.FG_ACCENT,
                img_path=self.images.pencil
            ),
            # Delete seed
            CircleButton(
                r=ICON_SIZE // 2,
                k_fg_colour=ThemeKey.FG_ACCENT,
                img_path=self.images.garbage_bin
            ),
        )


        self.gui = GUI(
            self.panel
        )

    def _make_seed_panel(self, seed_record: SeedRecord) -> Panel:
        """Returns a `Panel` to display a `SeedRecord`."""

        seed_text, offset_text, seed_int_text = get_seed_messages(seed_record.seed_metadata)

        panel = Panel(
            HBox(
                VBox(
                    HBox(
                        Label(
                            text=seed_text,
                            font=self.fonts.text,
                            k_fg=ThemeKey.FG_ACCENT,
                            shrink=1.0,
                        ),
                        Label(
                            text=offset_text,
                            font=self.fonts.text,
                            k_fg=ThemeKey.FG_ACCENT2
                        ),
                        Label(
                            text=seed_int_text,
                            font=self.fonts.text,
                            k_fg=ThemeKey.FG_SENTINEL
                        ),
                        Spacer(),
                    ),
                    HBox(
                        CircleButton(
                            r=self.fonts.tips.get_height() // 2,
                            k_fg_colour=ThemeKey.FG_SENTINEL,
                            img_path=self.images.clock,
                        ),
                        Label(
                            text=format_save_duration_ago(
                                (datetime.now(timezone.utc) - seed_record.added).total_seconds()
                            ),
                            font=self.fonts.tips,
                            k_fg=ThemeKey.FG_SENTINEL
                        ),
                        Label(
                            text=seed_record.notes,
                            font=self.fonts.tips,
                            k_fg=ThemeKey.FG_ELEMS,
                            shrink=1.0,  # to avoid overflow
                        ),
                        Spacer(),
                        gap=UI_MARGIN_S,
                    ),
                    gap=UI_MARGIN_S,
                ),
                gap=UI_MARGIN_S,
            ),
            k_bg=ThemeKey.BG_DARK_HOVERED,
            horiz_padding=UI_MARGIN_S,
            vert_padding=UI_MARGIN_S,
        )

        return panel

    def _refresh_gui(self) -> None:
        self.seed_count_label.text = str(len(self.game.saved_seeds))

        self.seeds_vbox.clear_children()
        for record in self.game.saved_seeds:
            panel = self._make_seed_panel(record)
            self.seeds_vbox.add_child(panel)

        self.gui.layout([SCREEN_RECT])

    def _get_hovered_seed_panel(self, hovered_elem: Element | None) -> Panel | None:
        if not hovered_elem:
            return None

        panels: list[Panel] = self.seeds_vbox.children  # type: ignore

        for panel in panels:
            if (
                hovered_elem is panel
                or panel in hovered_elem.parents
            ):
                return panel

        return None

    def on_entered(self) -> None:
        self._refresh_gui()

    def update(self, dt_s: float) -> None:
        self.gui.update(dt_s)

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        elem = self.gui.hit_test(pg.mouse.get_pos())

        # Update hovered panel with buttons
        self.hovered_panel = self._get_hovered_seed_panel(elem)


        # Process events
        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if elem is self.back_button:
                    self.game.enter_state(StateID.ENTER_SEED)

            if event.type == pg.MOUSEWHEEL:
                if (
                    elem is not None
                    and (
                        elem is self.seeds_scrollable
                        or self.seeds_scrollable in elem.parents
                    )
                ):
                    self.seeds_scrollable.handle_scroll(event)


    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])
        self.gui.draw(screen, self.game.current_theme())
