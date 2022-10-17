from enum import Enum, unique


class Colors(Enum):
    GREEN = 'green'
    RED = 'red'


@unique
class RunCode(Enum):
    DEBUG = 0
    DAILY = 1
    MONTHLY = 2
    ONCE = 3


@unique
class Permission(Enum):
    ADMIN = 0
    OUTPOST = 1
    EXECUTIVE = 2
    SERVICE = 3
