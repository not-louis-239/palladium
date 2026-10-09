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


import numpy as np


def generate_bins(data: list[float], num_bins: int) -> dict[float, int]:
    """
    Generate histogram bins from a list of data.

    Args:
        data (list[float]): The input data to be binned.
        num_bins (int): The number of bins to create.

    Returns:
        dict[float, int]: A dictionary where keys are bin minimums and values are counts.
    """
    hist, bin_edges = np.histogram(data, bins=num_bins)
    return {bin_edges[i]: hist[i] for i in range(len(hist))}
