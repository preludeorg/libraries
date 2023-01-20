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
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        return RunCode.UNKNOWN

@unique
class Permission(Enum):
    ADMIN = 0
    EXECUTIVE = 1
    BUILD = 2
    SERVICE = 3
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        return Permission.UNKNOWN
