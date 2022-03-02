from enum import Enum


class EventType(Enum):
    UnhandledException: int = 0
    PGDown: int = 1
    PGAlive: int = 2
    ESDown: int = 3
    ESAlive: int = 4
    AppUp: int = 5
    AppDown: int = 6
