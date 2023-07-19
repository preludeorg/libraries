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
    UNKNOWN_ERROR = 1
    MALFORMED_TEST = 2
    BEHAVIOR_PREVENTED_1 = 9
    BEHAVIOR_PREVENTED_2 = 15
    CHECK_COMPLETED = 100
    NOT_PREVENTED = 101
    TIMED_OUT = 102
    FAILED_CLEANUP = 103
    NOT_RELEVANT = 104
    SIGNATURE_PREVENTED_1 = 105
    BLOCKED_AT_PERIMETER = 106
    BEHAVIOR_PREVENTED_3 = 107
    TEST_UNAVAILABLE = 108
    INCORRECTLY_BLOCKED = 110
    BEHAVIOR_PREVENTED_4 = 126
    SIGNATURE_PREVENTED_2 = 127
    OUT_OF_MEMORY = 137
    UNEXPECTED_ERROR = 256

    @classmethod
    def _missing_(cls, value):
        if value and not isinstance(value, int):
            return cls(int(value))
        return ExitCode.MISSING
    
    @classmethod
    def transform(self, test):
        if test.unit == 'health' and self != ExitCode.CHECK_COMPLETED:
            return ExitCode.INCORRECTLY_BLOCKED
        return self

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
                ExitCode.BEHAVIOR_PREVENTED_1,
                ExitCode.BEHAVIOR_PREVENTED_2,
                ExitCode.CHECK_COMPLETED,
                ExitCode.NOT_RELEVANT,
                ExitCode.SIGNATURE_PREVENTED_1,
                ExitCode.BLOCKED_AT_PERIMETER,
                ExitCode.BEHAVIOR_PREVENTED_3,
                ExitCode.TEST_UNAVAILABLE,
                ExitCode.BEHAVIOR_PREVENTED_4,
                ExitCode.SIGNATURE_PREVENTED_2
            ],
            State.UNPROTECTED: [
                ExitCode.NOT_PREVENTED,
            ],
            State.ERROR: [
                ExitCode.UNKNOWN_ERROR,
                ExitCode.MALFORMED_TEST,
                ExitCode.TIMED_OUT,
                ExitCode.FAILED_CLEANUP,
                ExitCode.INCORRECTLY_BLOCKED,
                ExitCode.OUT_OF_MEMORY,
                ExitCode.UNEXPECTED_ERROR
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
