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


import time


segment_time = time.perf_counter()

def log_segment(name: str | None = None) -> None:
    """Log the time taken between the current call and the last
    call of log_segment(). If no `name` is provided, resets
    the segment clock without logging anything."""

    global segment_time

    if name is None:
        print(f"Resetting segment clock...")
        segment_time = time.perf_counter()
        return

    new_segment_time = time.perf_counter()
    print(f"Segment '{name}' completed in {1_000.0 * (new_segment_time - segment_time):,.4f} ms.")
    segment_time = new_segment_time
