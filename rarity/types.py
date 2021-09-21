import enum
from dataclasses import dataclass


@dataclass
class SummonerNextAdventure:
    id: int
    remaining_time: int


class SummonerType(enum.Enum):
    Barbarian = 1
    Bard = 2
    Cleric = 3
    Druid = 4
    Fighter = 5
    Monk = 6
    Paladin = 7
    Ranger = 8
    Rogue = 9
    Sorcerer = 10
    Wizard = 11
