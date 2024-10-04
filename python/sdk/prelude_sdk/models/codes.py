import logging

from enum import Enum, EnumMeta


class MissingItem(EnumMeta):
    def __getitem__(cls, name):
        try:
            return super().__getitem__(name.upper())
        except (AttributeError, KeyError):
            try:
                return cls(int(name))
            except ValueError:
                return cls(name)


class RunCode(Enum, metaclass=MissingItem):
    INVALID = -1
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    SMART = 4
    DEBUG = 5
    RUN_ONCE = 6
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
        return RunCode.DAILY


class Mode(Enum, metaclass=MissingItem):
    MANUAL = 0
    FROZEN = 1
    AUTOPILOT = 2

    @classmethod
    def _missing_(cls, value):
        return Mode.MANUAL


class Permission(Enum, metaclass=MissingItem):
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
    UNREPORTED = 3
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
    INSUFFICIENT_PRIVILEGES = 109
    INCORRECTLY_BLOCKED = 110
    PREVENTED_EXECUTION = 126
    STATIC_QUARANTINE = 127
    BLOCKED = 137
    UNEXPECTED_ERROR = 256

    @classmethod
    def _missing_(cls, value):
        if value and not isinstance(value, int):
            return cls(int(value))
        logging.warning('Unknown ExitCode: %s', str(value))
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
            State.ERROR: [
                ExitCode.FAILED_CLEANUP,
                ExitCode.INCORRECTLY_BLOCKED,
                ExitCode.MALFORMED_TEST,
                ExitCode.TIMED_OUT,
                ExitCode.UNEXPECTED_ERROR,
                ExitCode.UNKNOWN_ERROR,
                ExitCode.UNREPORTED,
            ],
            State.NONE: [ExitCode.MISSING],
            State.NOT_RELEVANT: [
                ExitCode.ENDPOINT_NOT_RELEVANT,
                ExitCode.INSUFFICIENT_PRIVILEGES,
                ExitCode.TEST_NOT_RELEVANT,
            ],
            State.PROTECTED: [
                ExitCode.BLOCKED,
                ExitCode.BLOCKED_AT_PERIMETER,
                ExitCode.DYNAMIC_QUARANTINE,
                ExitCode.EXPLOIT_PREVENTED,
                ExitCode.PREVENTED_EXECUTION,
                ExitCode.PROCESS_BLOCKED,
                ExitCode.PROCESS_BLOCKED_GRACEFULLY,
                ExitCode.PROTECTED,
                ExitCode.STATIC_QUARANTINE,
            ],
            State.UNPROTECTED: [
                ExitCode.UNPROTECTED,
            ],
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


class Control(Enum, metaclass=MissingItem):
    INVALID = -1
    NONE = 0
    CROWDSTRIKE = 1
    DEFENDER = 2
    SPLUNK = 3
    SENTINELONE = 4
    VECTR = 5
    S3 = 6
    INTUNE = 7
    SERVICENOW = 8

    @classmethod
    def _missing_(cls, value):
        return Control.INVALID

class PartnerSyncJobType(Enum, metaclass=MissingItem):
    INVALID = -1
    POLICY_EVALUATION = 1

    @classmethod
    def _missing_(cls, value):
        return Control.INVALID

class EDRResponse(Enum, metaclass=MissingItem):
    INVALID = -1
    OBSERVE = 1
    DETECT = 2
    PREVENT = 3

    @classmethod
    def _missing_(cls, value):
        return EDRResponse.INVALID

class AuditEvent(Enum, metaclass=MissingItem):
    INVALID = 0
    ATTACH_PARTNER = 1
    CREATE_DETECTION = 25
    CREATE_TEST = 2
    CREATE_THREAT = 18
    CREATE_USER = 3
    DELETE_DETECTION = 26
    DELETE_ENDPOINT = 4
    DELETE_TEST = 5
    DELETE_THREAT = 20
    DELETE_USER = 6
    DETACH_PARTNER = 7
    DISABLE_TEST = 8
    DOWNLOAD_TEST_ATTACHMENT = 9
    ENABLE_TEST = 10
    PARTNER_BLOCK_TEST = 11
    REGISTER_ENDPOINT = 12
    SCHEDULE = 23
    UNSCHEDULE = 24
    UPDATE_ACCOUNT = 13
    UPDATE_DETECTIONS = 27
    UPDATE_ENDPOINT = 14
    UPDATE_TEST = 15
    UPDATE_THREAT = 19
    UPDATE_USER = 17
    UPLOAD_TEST_ATTACHMENT = 16
    # Next value: 28

    @classmethod
    def _missing_(cls, value):
        return AuditEvent.INVALID
