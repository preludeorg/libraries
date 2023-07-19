from enum import Enum 


class RunCode(Enum):
    INVALID = -1
    DEBUG = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    MONDAY = 10
    TUESDAY = 11
    WEDNESDAY = 12
    THURSDAY = 13
    FRIDAY = 14
    SATURDAY = 15
    SUNDAY = 16
    FIRST_OF_MONTH = 20

    @classmethod
    def _missing_(cls, value):
        return RunCode.INVALID


class Mode(Enum):
    MANUAL = 0
    FROZEN = 1
    AUTOPILOT = 2

    @classmethod
    def _missing_(cls, value):
        return Mode.MANUAL
 

class Permission(Enum):
    INVALID = -1
    ADMIN = 0
    EXECUTIVE = 1
    BUILD = 2
    SERVICE = 3

    @classmethod
    def _missing_(cls, value):
        return Permission.INVALID


class ExitCode(Enum):
    MISSING = -1
    REMOVED = 0
    ERROR_OCCURED = 1
    MALFORMED_TEST = 2
    FORCE_KILLED = 9
    GRACEFULLY_KILLED = 15
    PROTECTED = 100
    UNPROTECTED = 101
    TIMED_OUT = 102
    FAILED_CLEANUP = 103
    NOT_RELEVANT = 104
    BEHAVIOR_QUARANTINED = 105
    BLOCKED_AT_PERIMETER = 106
    EXPLOIT_PREVENTED = 107
    TEST_UNAVAILABLE = 108
    IS_RELEVANT = 109
    FALSE_POSITIVE = 110
    EXECUTION_DISALLOWED = 126
    FILE_QUARANTINED = 127
    OUT_OF_MEMORY = 137
    UNEXPECTED_ERROR = 256

    @classmethod
    def _missing_(cls, value):
        return ExitCode.MISSING

    @property
    def state(self):
        for k, v in State.mapping().items():
            if self in v:
                return k
        return State.NONE


class State(Enum):
    NONE = 0
    PROTECTED = 1
    UNPROTECTED = 2
    ERROR = 3
    NOT_RELEVANT = 4

    @classmethod
    def mapping(cls):
        return {
            State.NONE: [ExitCode.MISSING],
            State.PROTECTED: [
                ExitCode.REMOVED,
                ExitCode.PROTECTED,
                ExitCode.BEHAVIOR_QUARANTINED,
                ExitCode.FILE_QUARANTINED,
                ExitCode.FORCE_KILLED,
                ExitCode.GRACEFULLY_KILLED,
                ExitCode.NOT_RELEVANT,
                ExitCode.TEST_UNAVAILABLE,
                ExitCode.BLOCKED_AT_PERIMETER,
                ExitCode.EXECUTION_DISALLOWED,
                ExitCode.EXPLOIT_PREVENTED,
                ExitCode.OUT_OF_MEMORY
            ],
            State.UNPROTECTED: [
                ExitCode.UNPROTECTED,
                ExitCode.IS_RELEVANT,
            ],
            State.ERROR: [
                ExitCode.ERROR_OCCURED,
                ExitCode.MALFORMED_TEST,
                ExitCode.TIMED_OUT,
                ExitCode.UNEXPECTED_ERROR,
                ExitCode.FALSE_POSITIVE
            ],
            State.NOT_RELEVANT: [
                ExitCode.NOT_RELEVANT,
                ExitCode.TEST_UNAVAILABLE
            ]
        }


class DOS(Enum):
    none = 'none'
    arm64 = 'arm64'
    x86_64 = 'x86_64'
    aarch64 = 'arm64'
    amd64 = 'x86_64'
    x86 = 'x86_64'

    @classmethod
    def normalize(cls, dos: str):
        try:
            arch = dos.split('-', 1)[-1]
            return dos[:-len(arch)].lower() + cls[arch.lower()].value
        except (KeyError, IndexError, AttributeError):
            return cls.none.value


class Control(Enum):
    INVALID = 0
    CROWDSTRIKE = 1
    DEFENDER = 2
    SPLUNK = 3

    @classmethod
    def _missing_(cls, value):
        return Control.INVALID
