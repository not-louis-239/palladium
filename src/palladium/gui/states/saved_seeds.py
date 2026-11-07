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

from james import HBox, VBox, SBox, Panel, ScrollableDisplay, Scrollbar, Label, Spacer, CircleButton, Element, GUI, PressAndHoldButton, InputBox

from palladium.core.constants import WN_W, Controls
from palladium.gui.utils import format_save_duration_ago, get_seed_messages
from palladium.gui.states.base import StateID
from palladium.gui.themes import ThemeKey
from palladium.gui.constants import UI_MARGIN_M, DEFAULT_ATTRS, DEFAULT_INPUT_BOX_ATTRS, UI_MARGIN_S, BORDER_W, SCREEN_RECT, ICON_SIZE
from palladium.generation.generators.star_system_gen import generate_star_system
from palladium.gui.states.base import State
from palladium.core.data_manager import SeedRecord


if TYPE_CHECKING:
    from palladium.game.game import Game


# TODO: add a setting to ScrollableDisplay where all its children inherit its width or height


from datetime import date, datetime, timezone


def _format_date(value: datetime) -> str:
    """
    Format a datetime, assuming the input is in UTC.

    Converts to the local timezone before formatting.

    - this year: "Sat 7 Nov at 8:00 am"
    - previous year: "Mon 1 Jan 2023 at 8:00 am"
    """

    value = value.astimezone(timezone.utc).astimezone()

    fmt = "%a {day} %b"
    if value.year != date.today().year:
        fmt += " %Y"

    date_str = value.strftime(fmt.format(day=value.day))
    time_str = value.strftime("%-I:%M %p").lower()

    return f"{date_str} at {time_str}"


class SavedSeedsState(State):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        # this is only safe if we don't allow any other actions
        # while a record is being edited.
        self.record_idx_to_edit = None
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
                        k_fg=ThemeKey.FG
                    ),
                    Spacer(),
                    SBox(
                        seed_count_label := Label(
                            k_fg=ThemeKey.FG_ACCENT,
                            font=self.fonts.text,
                        ),
                    ),
                    CircleButton(
                        r=ICON_SIZE // 2,
                        k_fg_colour=ThemeKey.FG_ACCENT,
                        img_inset=UI_MARGIN_S,
                        img_path=self.images.trees
                    ),
                    refresh_seed_stats_button := PressAndHoldButton(
                        r=ICON_SIZE // 2,
                        k_border_colour=ThemeKey.FG_DIM,
                        k_border_hovered=ThemeKey.FG_DIM_HOVERED,
                        k_border_pressed=ThemeKey.FG_DIM_PRESSED,
                        k_fg_colour=ThemeKey.FG_DIM,
                        k_fg_hovered=ThemeKey.FG_DIM_HOVERED,
                        k_fg_pressed=ThemeKey.FG_DIM_PRESSED,
                        k_bg_colour=ThemeKey.BG_DIM,
                        k_bg_hovered=ThemeKey.BG_DIM_HOVERED,
                        k_bg_pressed=ThemeKey.BG_DIM_PRESSED,
                        k_fg_arc=ThemeKey.FG_PROGRESS_ARC,
                        img_path=self.images.refresh,
                        img_inset=UI_MARGIN_S,
                        border_w=BORDER_W,
                        hover_tooltip=Panel(
                            VBox(
                                Label(
                                    text="refresh seed stats",
                                    font=self.fonts.ui,
                                    inset=UI_MARGIN_S,
                                    k_fg=ThemeKey.FG,
                                ),
                                Label(
                                    text="Regenerate each saved seed to refresh its generated statistics, ",
                                    font=self.fonts.text,
                                    inset=UI_MARGIN_S,
                                    k_fg=ThemeKey.FG,
                                ),
                                Spacer(flex=0, min_h=-UI_MARGIN_S),  # yes, this is weird, but the negative margin works to counteract spacing
                                Label(
                                    text="including planet counts. Existing notes and metadata will be preserved.",
                                    font=self.fonts.text,
                                    inset=UI_MARGIN_S,
                                    k_fg=ThemeKey.FG,
                                ),
                            ),
                            k_bg=ThemeKey.BG_DARK,
                            horiz_padding=UI_MARGIN_S,
                            vert_padding=UI_MARGIN_S,
                        )
                    )
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
                        k_bar=ThemeKey.FG,
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
        self.seed_count_label = seed_count_label
        self.seeds_scrollable = seeds_scrollable
        self.hovered_panel = None  # the seed panel that is currently being hovered over
        self.refresh_seed_stats_button = refresh_seed_stats_button

        # Make a triplet of action buttons that can be subbed in anywhere
        self.action_buttons = HBox(
            # Load seed
            CircleButton(
                r=ICON_SIZE // 2,
                k_border_colour=ThemeKey.FG_ACCENT,
                k_border_hovered=ThemeKey.FG_ACCENT_HOVERED,
                k_border_pressed=ThemeKey.FG_ACCENT_PRESSED,
                k_fg_colour=ThemeKey.FG_ACCENT,
                k_fg_hovered=ThemeKey.FG_ACCENT_HOVERED,
                k_fg_pressed=ThemeKey.FG_ACCENT_PRESSED,
                k_bg_colour=ThemeKey.BG_ACCENT,
                k_bg_hovered=ThemeKey.BG_ACCENT_HOVERED,
                k_bg_pressed=ThemeKey.BG_ACCENT_PRESSED,
                img_path=self.images.play,
                img_inset=UI_MARGIN_S,
                border_w=BORDER_W,
                hover_tooltip=Label(
                    text="load seed",
                    font=self.fonts.text,
                    inset=UI_MARGIN_S,
                    k_bg=ThemeKey.BG_DARK,
                    k_fg=ThemeKey.FG,
                )
            ),
            # Edit seed
            CircleButton(
                r=ICON_SIZE // 2,
                k_border_colour=ThemeKey.FG,
                k_border_hovered=ThemeKey.FG_HOVERED,
                k_border_pressed=ThemeKey.FG_PRESSED,
                k_fg_colour=ThemeKey.FG,
                k_fg_hovered=ThemeKey.FG_HOVERED,
                k_fg_pressed=ThemeKey.FG_PRESSED,
                k_bg_colour=ThemeKey.BG_TRANSLUCENT,
                k_bg_hovered=ThemeKey.BG_TRANSLUCENT_HOVERED,
                k_bg_pressed=ThemeKey.BG_TRANSLUCENT_PRESSED,
                img_path=self.images.pencil,
                img_inset=UI_MARGIN_S,
                border_w=BORDER_W,
                hover_tooltip=Label(
                    text="edit seed notes",
                    font=self.fonts.text,
                    inset=UI_MARGIN_S,
                    k_bg=ThemeKey.BG_DARK,
                    k_fg=ThemeKey.FG,
                )
            ),
            # Delete seed
            PressAndHoldButton(
                r=ICON_SIZE // 2,
                k_border_colour=ThemeKey.FG_ERROR,
                k_border_hovered=ThemeKey.FG_ERROR_HOVERED,
                k_border_pressed=ThemeKey.FG_ERROR_PRESSED,
                k_fg_colour=ThemeKey.FG_ERROR,
                k_fg_hovered=ThemeKey.FG_ERROR_HOVERED,
                k_fg_pressed=ThemeKey.FG_ERROR_PRESSED,
                k_bg_colour=ThemeKey.BG_ERROR,
                k_bg_hovered=ThemeKey.BG_ERROR_HOVERED,
                k_bg_pressed=ThemeKey.BG_ERROR_PRESSED,
                k_fg_arc=ThemeKey.FG_PROGRESS_ARC,
                img_path=self.images.garbage_bin,
                img_inset=UI_MARGIN_S,
                border_w=BORDER_W,
                hover_tooltip=Label(
                    text="delete seed",
                    font=self.fonts.text,
                    inset=UI_MARGIN_S,
                    k_bg=ThemeKey.BG_DARK,
                    k_fg=ThemeKey.FG,
                )
            ),
            gap=UI_MARGIN_S
        )

        self.edit_seed_prompt = Panel(
            VBox(
                Spacer(),
                Panel(
                    VBox(
                        SBox(
                            Label(
                                text="edit seed notes",
                                font=self.fonts.heading,
                                k_fg=ThemeKey.FG,
                            ),
                        ),
                        edit_notes_input_box := InputBox(
                            font=self.fonts.text,
                            **DEFAULT_INPUT_BOX_ATTRS,
                        ),
                        gap=UI_MARGIN_S
                    ),
                    k_bg=ThemeKey.BG_DARK,
                    horiz_padding=UI_MARGIN_M,
                    vert_padding=UI_MARGIN_M,
                ),
                Spacer(),
            ),
            horiz_padding=UI_MARGIN_M,
            vert_padding=UI_MARGIN_M,
        )

        self.edit_seed_prompt.hide()
        self.edit_notes_input_box = edit_notes_input_box

        self.gui = GUI(
            self.panel,
            self.edit_seed_prompt,
        )

    def _make_seed_label(self, seed_record: SeedRecord) -> tuple[Label, Label, Label]:
        seed_text, offset_text, seed_int_text = get_seed_messages(seed_record.seed_metadata)

        return (
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
            )
        )

    def _make_seed_panel(self, seed_record: SeedRecord) -> Panel:
        """Returns a `Panel` to display a `SeedRecord`."""

        panel = Panel(
            HBox(
                VBox(
                    HBox(
                        *self._make_seed_label(seed_record),
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
                            k_fg=ThemeKey.FG,
                            shrink=1.0,  # to avoid overflow
                        ),
                        Spacer(),
                        gap=UI_MARGIN_S,
                    ),
                    gap=UI_MARGIN_S,
                ),
                Spacer(),
                gap=UI_MARGIN_S,
            ),
            hover_tooltip=Panel(
                VBox(
                    HBox(
                        *self._make_seed_label(seed_record),
                    ),
                    HBox(
                        CircleButton(
                            r=self.fonts.tips.get_height() // 2,
                            k_fg_colour=ThemeKey.FG_SENTINEL,
                            img_path=self.images.clock,
                        ),
                        Label(
                            text=_format_date(seed_record.added),
                            font=self.fonts.tips,
                            k_fg=ThemeKey.FG_SENTINEL
                        ),
                        gap=UI_MARGIN_S,
                    ),
                    HBox(
                        CircleButton(
                            r=self.fonts.tips.get_height() // 2,
                            k_fg_colour=ThemeKey.FG_SENTINEL,
                            img_path=self.images.planet,
                        ),
                        Label(
                            text=str(seed_record.num_planets),
                            font=self.fonts.tips,
                            k_fg=ThemeKey.FG_SENTINEL
                        ),
                        gap=UI_MARGIN_S,
                    ),
                    gap=UI_MARGIN_S,
                ),
                k_bg=ThemeKey.BG_DARK,
                horiz_padding=UI_MARGIN_S,
                vert_padding=UI_MARGIN_S,
            ),
            k_bg=ThemeKey.BG_DARK_HOVERED,
            horiz_padding=UI_MARGIN_S,
            vert_padding=UI_MARGIN_S,
        )

        return panel

    def _refresh_gui(self) -> None:
        """Refreshes the GUI to reflect the current state of the saved seeds list,
        by making a panel for each saved seed."""

        self.seed_count_label.text = str(len(self.game.saved_seeds))

        self.seeds_vbox.clear_children()
        for record in self.game.saved_seeds:
            panel = self._make_seed_panel(record)
            self.seeds_vbox.add_child(panel)

        self.gui.layout([SCREEN_RECT, SCREEN_RECT])

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

    def _delete_seed(self, idx: int) -> None:
        # Remove the seed panel for the seed
        self.seeds_vbox.rm_child(self.seeds_vbox.children[idx])
        # Delete the seed itself
        self.game.saved_seeds.pop(idx)
        self._refresh_gui()

    def _submit_edit(self) -> None:
        self.edit_seed_prompt.hide()
        assert self.record_idx_to_edit is not None
        self.game.saved_seeds[self.record_idx_to_edit].notes = self.edit_notes_input_box.text
        self.record_idx_to_edit = None
        self._refresh_gui()

    def on_entered(self) -> None:
        self._refresh_gui()

    def update(self, dt_s: float) -> None:
        self.gui.update(dt_s)

    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.Event], dt_s: float) -> None:
        elem = self.gui.hit_test(pg.mouse.get_pos())

        # Update hovered panel with buttons
        old_hovered_panel = self.hovered_panel
        self.hovered_panel = self._get_hovered_seed_panel(elem)

        # .child refers to the child of the `Panel`s, i.e. the `HBox` that contains
        # the `Panel` contents.
        if self.hovered_panel is not old_hovered_panel:
            if old_hovered_panel is not None:
                assert old_hovered_panel.child is not None
                old_hovered_panel.k_bg = ThemeKey.BG_DARK_HOVERED
                old_hovered_panel.child.rm_child(self.action_buttons)
                old_hovered_panel.layout(old_hovered_panel.rect)

            if self.hovered_panel is not None:
                assert self.hovered_panel.child is not None
                self.hovered_panel.k_bg = ThemeKey.BG_DARK_PRESSED
                self.hovered_panel.child.add_child(self.action_buttons)
                self.hovered_panel.layout(self.hovered_panel.rect)

        # Process events
        for event in events:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.edit_notes_input_box.on_mouse_up()

                if elem is self.back_button:
                    self.game.enter_state(StateID.ENTER_SEED)

                if elem is self.refresh_seed_stats_button and self.refresh_seed_stats_button.is_full:
                    self.game.refresh_seed_stats()
                    self._refresh_gui()

                load, edit, delete = self.action_buttons.children
                assert isinstance(delete, PressAndHoldButton)  # silences the type checker

                if elem is load:
                    assert self.hovered_panel is not None
                    idx = self.seeds_vbox.children.index(self.hovered_panel)
                    record = self.game.saved_seeds[idx]
                    self.game.star_system = generate_star_system(
                        seed=int(record.seed_metadata.display_str) if not record.seed_metadata.is_string else record.seed_metadata.display_str,
                        offset=record.seed_metadata.offset
                    )
                    self.game.enter_state(StateID.BROWSE_SYSTEM)

                elif elem is edit:
                    assert self.hovered_panel is not None
                    idx = self.seeds_vbox.children.index(self.hovered_panel)
                    record = self.game.saved_seeds[idx]
                    self.record_idx_to_edit = idx
                    self.edit_seed_prompt.show()
                    self.edit_notes_input_box.text = record.notes

                elif elem is delete and delete.is_full:
                    assert self.hovered_panel is not None
                    idx = self.seeds_vbox.children.index(self.hovered_panel)
                    self._delete_seed(idx)

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.edit_notes_input_box.on_mouse_down(event)

            elif event.type == pg.MOUSEWHEEL:
                if (
                    elem is not None
                    and (
                        elem is self.seeds_scrollable
                        or self.seeds_scrollable in elem.parents
                    )
                ):
                    self.seeds_scrollable.handle_scroll(event)

            elif (
                event.type == pg.KEYDOWN
            ):
                if self.edit_notes_input_box.visible:
                    if event.key == Controls.GENERIC_SUBMIT:
                        self._submit_edit()

                    elif event.key == Controls.GENERIC_ESCAPE:
                        self.edit_seed_prompt.visible = False

        self.edit_notes_input_box.handle_input(events=events, dt_s=dt_s)

    def draw(self, screen: pg.Surface) -> None:
        screen.fill(self.game.current_theme()[ThemeKey.BG_SCREEN])
        self.gui.draw(screen, self.game.current_theme())
