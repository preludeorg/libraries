from enum import Enum


class Colors(Enum):
    GREEN = 'green'
    RED = 'red'
    MAGENTA = 'magenta'


class RunCode(Enum):
    UNKNOWN = -1
    DEBUG = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3

    @classmethod
    def _missing_(cls, value):
        return RunCode.UNKNOWN


class Permission(Enum):
    UNKNOWN = -1
    ADMIN = 0
    EXECUTIVE = 1
    BUILD = 2
    SERVICE = 3

    @classmethod
    def _missing_(cls, value):
        return Permission.UNKNOWN


class ExitCode(Enum):
    OTHER = -1
    ERROR = 1
    MALFORMED_VST = 2
    PROCESS_KILLED = 9
    PROTECTED = 100
    UNPROTECTED = 101
    TIMEOUT = 102
    CLEANUP_ERROR = 103
    NOT_RELEVANT = 104
    QUARANTINED_1 = 105
    INCOMPATIBLE_HOST = 126
    QUARANTINED_2 = 127
    UNEXPECTED = 256

    @classmethod
    def _missing_(cls, value):
        return ExitCode.OTHER

    @property
    def state(self):
        x = [k for k in ExitCodeGroup for v in k.value if self.value == v.value]
        return x[0] if x else ExitCodeGroup.NONE


class ExitCodeGroup(Enum):
    NONE = []
    PROTECTED = [
        ExitCode.PROTECTED,
        ExitCode.QUARANTINED_1,
        ExitCode.QUARANTINED_2,
        ExitCode.PROCESS_KILLED,
        ExitCode.NOT_RELEVANT
    ]
    UNPROTECTED = [
        ExitCode.UNPROTECTED
    ]
    ERROR = [
        ExitCode.ERROR,
        ExitCode.MALFORMED_VST,
        ExitCode.TIMEOUT,
        ExitCode.INCOMPATIBLE_HOST,
        ExitCode.UNEXPECTED
    ]
