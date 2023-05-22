from enum import Enum 


class RunCode(Enum):
    INVALID = -1
    DEBUG = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3

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
    PRELUDE = 4

    @classmethod
    def _missing_(cls, value):
        return Permission.INVALID


class ExitCode(Enum):
    MISSING = -1
    REMOVED = 0
    ERROR = 1
    MALFORMED_VST = 2
    PROCESS_KILLED_1 = 9
    PROCESS_KILLED_2 = 15
    PROTECTED = 100
    UNPROTECTED = 101
    TIMEOUT = 102
    CLEANUP_ERROR = 103
    NOT_RELEVANT = 104
    QUARANTINED_1 = 105
    OUTBOUND_SECURE = 106
    EXPLOIT_PREVENTED = 107
    ENDPOINT_BLOCKED = 126
    QUARANTINED_2 = 127
    PROCESS_KILLED_3 = 137
    UNEXPECTED = 256

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

    @classmethod
    def mapping(self):
        return {
            State.NONE: [ExitCode.MISSING],
            State.PROTECTED: [
                ExitCode.REMOVED,
                ExitCode.PROTECTED,
                ExitCode.QUARANTINED_1,
                ExitCode.QUARANTINED_2,
                ExitCode.PROCESS_KILLED_1,
                ExitCode.PROCESS_KILLED_2,
                ExitCode.NOT_RELEVANT,
                ExitCode.OUTBOUND_SECURE,
                ExitCode.ENDPOINT_BLOCKED,
                ExitCode.EXPLOIT_PREVENTED,
                ExitCode.PROCESS_KILLED_3
            ],
            State.UNPROTECTED: [ExitCode.UNPROTECTED],
            State.ERROR: [
                ExitCode.ERROR,
                ExitCode.MALFORMED_VST,
                ExitCode.TIMEOUT,
                ExitCode.UNEXPECTED
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
        except (KeyError, IndexError) as e:
            return cls.none.value
