from enum import Enum, unique


class Colors(Enum):
    GREEN = 'green'
    RED = 'red'
    MAGENTA = 'magenta'


@unique
class RunCode(Enum):
    UNKNOWN = -1
    DEBUG = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    ONCE = 4

    @classmethod
    def _missing_(cls, value):
        return RunCode.UNKNOWN

@unique
class Permission(Enum):
    UNKNOWN = -1
    ADMIN = 0
    EXECUTIVE = 1
    BUILD = 2
    SERVICE = 3

    @classmethod
    def _missing_(cls, value):
        return Permission.UNKNOWN

@unique
class Lookup(Enum):
    Error = 1
    Passed = 100
    Failed = 101
    Timeout = 102
    CleanupError = 103
    NotRelevant = 104
    Quarantined_1 = 105
    Incompatible = 126
    Quarantined_2 = 127
    Unexpected = 256

    @classmethod
    def _missing_(cls, value):
        return Lookup.Unexpected
