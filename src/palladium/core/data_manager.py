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


# Module to manage user data


from __future__ import annotations

import json
from datetime import datetime
from dataclasses import dataclass, asdict

from palladium.generation.objects.star_system import SeedMetadata
from palladium.core.paths import DATA_DIR


@dataclass(kw_only=True)
class SeedRecord:
    seed_metadata: SeedMetadata
    notes: str = ""
    added: datetime

    def to_json(self) -> dict:
        return {
            "seed_metadata": asdict(self.seed_metadata),
            "notes": self.notes,
            "added": self.added.isoformat()
        }

    @classmethod
    def from_json(cls, json_data: dict) -> SeedRecord:
        metadata = SeedMetadata(**json_data["seed_metadata"])
        return cls(
            seed_metadata=metadata,
            notes=json_data["notes"],
            added=datetime.fromisoformat(json_data["added"])
        )


DATA_DIR.mkdir(parents=True, exist_ok=True)
SAVED_SEEDS_FP = DATA_DIR / "saved_seeds.json"


def read_saved_seeds() -> list[SeedRecord]:
    if not SAVED_SEEDS_FP.exists():
        return []

    try:
        with open(SAVED_SEEDS_FP, "r") as file:
            json_data = json.load(file)
    except json.JSONDecodeError:
        print(f"JSON is invalid. Resetting saved seeds.")
        return []
    except Exception as e:
        print(f"An error occurred while reading saved seeds: {e}. Resetting saved seeds.")
        return []

    seed_records = [SeedRecord.from_json(seed_record) for seed_record in json_data]
    return seed_records


def write_saved_seeds(seed_records: list[SeedRecord]) -> None:
    json_data = [seed_record.to_json() for seed_record in seed_records]

    try:
        with open(SAVED_SEEDS_FP, "w") as file:
            json.dump(json_data, file, indent=4)
    except PermissionError:
        print(f"Cannot write saved seeds. Permission denied.")
    except Exception as e:
        print(f"An error occurred while writing saved seeds: {e}")
