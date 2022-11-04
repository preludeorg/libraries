from enum import Enum, unique


class Colors(Enum):
    GREEN = 'green'
    RED = 'red'
    MAGENTA = 'magenta'


@unique
class RunCode(Enum):
    DEBUG = 0
    DAILY = 1
    WEEKLY = 3
    MONTHLY = 4
    ONCE = 5


@unique
class Permission(Enum):
    ADMIN = 0
    EXECUTIVE = 1
    BUILD = 2
    SERVICE = 3
