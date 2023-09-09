from enum import Enum


class RunCode(Enum):
    INVALID = -1
    DAILY = 1
    SMART = 2
    MONDAY = 10
    TUESDAY = 11
    WEDNESDAY = 12
    THURSDAY = 13
    FRIDAY = 14
    SATURDAY = 15
    SUNDAY = 16
    MONTH_1 = 20

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
    AUTO = 4

    @classmethod
    def _missing_(cls, value):
        return Permission.INVALID


class ExitCode(Enum):
    MISSING = -1
    UNKNOWN_ERROR = 1
    MALFORMED_TEST = 2
    PROCESS_BLOCKED = 9
    PROCESS_BLOCKED_GRACEFULLY = 15
    PROTECTED = 100
    UNPROTECTED = 101
    TIMED_OUT = 102
    FAILED_CLEANUP = 103
    TEST_NOT_RELEVANT = 104
    DYNAMIC_QUARANTINE = 105
    BLOCKED_AT_PERIMETER = 106
    EXPLOIT_PREVENTED = 107
    ENDPOINT_NOT_RELEVANT = 108
    TEST_DISALLOWED = 126
    STATIC_QUARANTINE = 127
    BLOCKED = 137
    UNEXPECTED_ERROR = 256

    @classmethod
    def _missing_(cls, value):
        if value and not isinstance(value, int):
            return cls(int(value))
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
                ExitCode.PROCESS_BLOCKED,
                ExitCode.PROCESS_BLOCKED_GRACEFULLY,
                ExitCode.PROTECTED,
                ExitCode.DYNAMIC_QUARANTINE,
                ExitCode.BLOCKED_AT_PERIMETER,
                ExitCode.BLOCKED,
                ExitCode.EXPLOIT_PREVENTED,
                ExitCode.TEST_DISALLOWED,
                ExitCode.STATIC_QUARANTINE,
                ExitCode.TEST_NOT_RELEVANT,
                ExitCode.ENDPOINT_NOT_RELEVANT
            ],
            State.UNPROTECTED: [
                ExitCode.UNPROTECTED,
            ],
            State.ERROR: [
                ExitCode.UNKNOWN_ERROR,
                ExitCode.MALFORMED_TEST,
                ExitCode.TIMED_OUT,
                ExitCode.FAILED_CLEANUP,
                ExitCode.UNEXPECTED_ERROR
            ],
            State.NOT_RELEVANT: [
                ExitCode.TEST_NOT_RELEVANT,
                ExitCode.ENDPOINT_NOT_RELEVANT
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
    INVALID = -1
    NONE = 0
    CROWDSTRIKE = 1
    DEFENDER = 2
    SPLUNK = 3
    SENTINELONE = 4
    VECTR = 5

    @classmethod
    def _missing_(cls, value):
        return Control.INVALID
