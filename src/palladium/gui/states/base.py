


from abc import ABC, abstractmethod
from enum import StrEnum

import pygame as pg



class StateID(StrEnum):
    MAIN_MENU = "main_menu"
    TERRAIN_GEN = "terrain_gen"
    INSPECT = "inspect"

class State(ABC):
    @abstractmethod
    def update(self, dt_s: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def take_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw(self, screen: pg.Surface) -> None:
        raise NotImplementedError
