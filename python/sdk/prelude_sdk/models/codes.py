from enum import Enum, unique


class Colors(Enum):
    GREEN = 'green'
    RED = 'red'
    MAGENTA = 'magenta'


@unique
class RunCode(Enum):
    DEBUG = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    ONCE = 4

@unique
class Permission(Enum):
    ADMIN = 0
    EXECUTIVE = 1
    BUILD = 2
    SERVICE = 3
