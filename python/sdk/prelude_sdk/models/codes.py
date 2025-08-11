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
    SUPPORT = 5

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
        logging.warning("Unknown ExitCode: %s", str(value))
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
    none = "none"
    arm64 = "arm64"
    x86_64 = "x86_64"
    aarch64 = "arm64"
    amd64 = "x86_64"
    x86 = "x86_64"

    @classmethod
    def normalize(cls, dos: str):
        try:
            arch = dos.split("-", 1)[-1]
            return dos[: -len(arch)].lower() + cls[arch.lower()].value
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
    OKTA = 9
    M365 = 10
    ENTRA = 11
    JAMF = 12
    GMAIL = 14
    GOOGLE_IDENTITY = 15
    DEFENDER_DISCOVERY = 16
    TENABLE = 17
    EC2 = 18
    AWS_SSM = 19
    AZURE_VM = 20
    GITHUB = 21
    TENABLE_DISCOVERY = 22
    QUALYS = 23
    QUALYS_DISCOVERY = 24
    RAPID7 = 25
    RAPID7_DISCOVERY = 26
    INTEL_INTUNE = 28
    CISCO_MERAKI = 29
    CISCO_MERAKI_IDENTITY = 30

    @classmethod
    def _missing_(cls, value):
        return Control.INVALID

    @property
    def control_category(self):
        for k, v in ControlCategory.mapping().items():
            if self in v:
                return k
        return ControlCategory.NONE

    @property
    def scm_category(self):
        for k, v in SCMCategory.control_mapping().items():
            if self in v:
                return k
        return SCMCategory.NONE

    @property
    def parent(self):
        match self:
            case Control.CISCO_MERAKI_IDENTITY:
                return Control.CISCO_MERAKI
            case Control.DEFENDER_DISCOVERY:
                return Control.DEFENDER
            case Control.QUALYS_DISCOVERY:
                return Control.QUALYS
            case Control.RAPID7_DISCOVERY:
                return Control.RAPID7
            case Control.TENABLE_DISCOVERY:
                return Control.TENABLE

    @property
    def children(self):
        match self:
            case Control.CISCO_MERAKI:
                return [Control.CISCO_MERAKI_IDENTITY]
            case Control.DEFENDER:
                return [Control.DEFENDER_DISCOVERY]
            case Control.QUALYS:
                return [Control.QUALYS_DISCOVERY]
            case Control.RAPID7:
                return [Control.RAPID7_DISCOVERY]
            case Control.TENABLE:
                return [Control.TENABLE_DISCOVERY]
            case _:
                return []


class ControlCategory(Enum, metaclass=MissingItem):
    INVALID = -1
    NONE = 0
    CLOUD = 1
    EMAIL = 2
    IDENTITY = 3
    NETWORK = 4
    XDR = 5
    ASSET_MANAGER = 6
    DISCOVERED_DEVICES = 7
    VULN_MANAGER = 8
    SIEM = 9
    PRIVATE_REPO = 10
    HARDWARE = 11

    @classmethod
    def _missing_(cls, value):
        return ControlCategory.INVALID

    @classmethod
    def mapping(cls):
        return {
            ControlCategory.ASSET_MANAGER: [
                Control.AWS_SSM,
                Control.INTUNE,
                Control.JAMF,
            ],
            ControlCategory.CLOUD: [],
            ControlCategory.DISCOVERED_DEVICES: [
                Control.AZURE_VM,
                Control.DEFENDER_DISCOVERY,
                Control.EC2,
                Control.QUALYS_DISCOVERY,
                Control.RAPID7_DISCOVERY,
                Control.SERVICENOW,
                Control.TENABLE_DISCOVERY,
            ],
            ControlCategory.EMAIL: [
                Control.GMAIL,
                Control.M365,
            ],
            ControlCategory.HARDWARE: [
                Control.INTEL_INTUNE,
            ],
            ControlCategory.IDENTITY: [
                Control.CISCO_MERAKI_IDENTITY,
                Control.ENTRA,
                Control.GOOGLE_IDENTITY,
                Control.OKTA,
            ],
            ControlCategory.NETWORK: [Control.CISCO_MERAKI],
            ControlCategory.PRIVATE_REPO: [
                Control.GITHUB,
            ],
            ControlCategory.SIEM: [
                Control.S3,
                Control.SPLUNK,
                Control.VECTR,
            ],
            ControlCategory.VULN_MANAGER: [
                Control.QUALYS,
                Control.RAPID7,
                Control.TENABLE,
            ],
            ControlCategory.XDR: [
                Control.CROWDSTRIKE,
                Control.DEFENDER,
                Control.SENTINELONE,
            ],
        }


class SCMCategory(Enum, metaclass=MissingItem):
    INVALID = -1
    NONE = 0
    ENDPOINT = 1
    INBOX = 2
    USER = 3
    NETWORK_DEVICE = 4

    @classmethod
    def _missing_(cls, value):
        return SCMCategory.INVALID

    @classmethod
    def control_mapping(cls):
        return {
            SCMCategory.ENDPOINT: [
                Control.AWS_SSM,
                Control.AZURE_VM,
                Control.CROWDSTRIKE,
                Control.DEFENDER,
                Control.DEFENDER_DISCOVERY,
                Control.EC2,
                Control.INTEL_INTUNE,
                Control.INTUNE,
                Control.JAMF,
                Control.QUALYS,
                Control.QUALYS_DISCOVERY,
                Control.RAPID7,
                Control.RAPID7_DISCOVERY,
                Control.SENTINELONE,
                Control.SERVICENOW,
                Control.TENABLE,
                Control.TENABLE_DISCOVERY,
            ],
            SCMCategory.INBOX: [
                Control.GMAIL,
                Control.M365,
            ],
            SCMCategory.NETWORK_DEVICE: [
                Control.CISCO_MERAKI,
            ],
            SCMCategory.USER: [
                Control.CISCO_MERAKI_IDENTITY,
                Control.ENTRA,
                Control.GOOGLE_IDENTITY,
                Control.OKTA,
            ],
        }

    @classmethod
    def category_mapping(cls):
        return {
            SCMCategory.ENDPOINT: [
                ControlCategory.ASSET_MANAGER,
                ControlCategory.DISCOVERED_DEVICES,
                ControlCategory.HARDWARE,
                ControlCategory.VULN_MANAGER,
                ControlCategory.XDR,
            ],
            SCMCategory.INBOX: [ControlCategory.EMAIL],
            SCMCategory.NETWORK_DEVICE: [ControlCategory.NETWORK],
            SCMCategory.USER: [ControlCategory.IDENTITY],
        }


class BackgroundJobTypes(Enum, metaclass=MissingItem):
    INVALID = -1
    UPDATE_SCM = 1
    DEPLOY_PROBE = 2
    OBSERVED_DETECTED = 3
    PRELUDE_ENDPOINT_SYNC = 4
    EXPORT_SCM = 5
    PARTNER_GROUPS = 6

    @classmethod
    def _missing_(cls, value):
        return BackgroundJobTypes.INVALID


class EDRResponse(Enum, metaclass=MissingItem):
    INVALID = -1
    OBSERVE = 1
    DETECT = 2
    PREVENT = 3

    @classmethod
    def _missing_(cls, value):
        return EDRResponse.INVALID


class PartnerEvents(Enum, metaclass=MissingItem):
    INVALID = -1
    REDUCED_FUNCTIONALITY_MODE = 1
    NO_EDR = 2
    MISSING_EDR_POLICY = 3
    MISSING_AV_POLICY = 4
    MISSING_MFA = 5
    NO_ASSET_MANAGER = 6
    MISCONFIGURED_POLICY_SETTING = 7
    MISSING_SCAN = 8
    OUT_OF_DATE_SCAN = 9
    NO_VULN_MANAGER = 10
    USER_MISSING_ASSET_MANAGER = 11
    USER_MISSING_EDR = 12
    USER_MISSING_VULN_MANAGER = 13
    NO_SERVER_MANAGER = 14
    MISSING_HOST_FIREWALL_POLICY = 16
    OUT_OF_DATE_FIRMWARE = 18

    @classmethod
    def _missing_(cls, value):
        return PartnerEvents.INVALID

    @classmethod
    def control_category_mapping(cls):
        return {
            PartnerEvents.MISCONFIGURED_POLICY_SETTING: [
                ControlCategory.ASSET_MANAGER,
                ControlCategory.EMAIL,
                ControlCategory.IDENTITY,
                ControlCategory.XDR,
            ],
            PartnerEvents.MISSING_AV_POLICY: [ControlCategory.XDR],
            PartnerEvents.MISSING_EDR_POLICY: [ControlCategory.XDR],
            PartnerEvents.MISSING_HOST_FIREWALL_POLICY: [ControlCategory.ASSET_MANAGER],
            PartnerEvents.MISSING_MFA: [ControlCategory.IDENTITY],
            PartnerEvents.MISSING_SCAN: [ControlCategory.VULN_MANAGER],
            PartnerEvents.NO_ASSET_MANAGER: [ControlCategory.ASSET_MANAGER],
            PartnerEvents.NO_EDR: [ControlCategory.XDR],
            PartnerEvents.NO_SERVER_MANAGER: [ControlCategory.ASSET_MANAGER],
            PartnerEvents.NO_VULN_MANAGER: [ControlCategory.VULN_MANAGER],
            PartnerEvents.OUT_OF_DATE_FIRMWARE: [ControlCategory.NETWORK],
            PartnerEvents.OUT_OF_DATE_SCAN: [ControlCategory.VULN_MANAGER],
            PartnerEvents.REDUCED_FUNCTIONALITY_MODE: [ControlCategory.XDR],
            PartnerEvents.USER_MISSING_ASSET_MANAGER: [ControlCategory.IDENTITY],
            PartnerEvents.USER_MISSING_EDR: [ControlCategory.IDENTITY],
            PartnerEvents.USER_MISSING_VULN_MANAGER: [ControlCategory.IDENTITY],
        }


class AlertTypes(Enum, metaclass=MissingItem):
    INVALID = -1
    NEW_REDUCED_FUNCTIONALITY_MODE_ENDPOINTS = 1
    NEW_NO_EDR_ENDPOINTS = 2
    NEW_MISSING_EDR_POLICY_ENDPOINTS = 3
    NEW_MISSING_AV_POLICY_ENDPOINTS = 4
    NEW_MISSING_MFA_USERS = 5
    NEW_NO_ASSET_MANAGER_ENDPOINTS = 6
    NEW_POLICY_SETTING_FAILURE = 7
    NEW_POLICY_SETTING_PASS = 8
    NEW_MISSING_SCAN_ENDPOINTS = 9
    NEW_NO_VULN_MANAGER_ENDPOINTS = 10
    NEW_OUT_OF_DATE_SCAN_ENDPOINTS = 11
    NEW_USER_MISSING_ASSET_MANAGER = 12
    NEW_USER_MISSING_EDR = 13
    NEW_USER_MISSING_VULN_MANAGER = 14
    NEW_NO_SERVER_MANAGER_ENDPOINTS = 15
    NEW_MISSING_HOST_FIREWALL_POLICY_ENDPOINTS = 17
    NEW_OUT_OF_DATE_FIRMWARE_NETWORK_DEVICES = 19

    @classmethod
    def _missing_(cls, value):
        return AlertTypes.INVALID


class PolicyType(Enum, metaclass=MissingItem):
    INVALID = 0
    EDR = 1
    AV = 2
    IDENTITY_PASSWORD = 3
    EMAIL_ANTIPHISH = 4
    EMAIL_OUTBOUND = 5
    EMAIL_CONTENT = 6
    EMAIL_MALWARE = 7
    EMAIL_ATTACHMENT = 8
    EMAIL_LINKS = 9
    EMAIL_DKIM = 10
    DEVICE_COMPLIANCE = 11
    IDENTITY_MFA = 12
    HOST_FIREWALL = 13
    NETWORK_FIREWALL = 15
    INTEL_BELOW_OS = 16
    INTEL_OS = 17
    INTEL_TDT = 18
    INTEL_CHIP = 19

    @classmethod
    def _missing_(cls, value):
        return PolicyType.INVALID


class Platform(Enum, metaclass=MissingItem):
    INVALID = 0
    WINDOWS = 1
    DARWIN = 2
    LINUX = 3
    ALL = 4

    @classmethod
    def _missing_(cls, value):
        return Platform.INVALID


class NotationType(Enum, metaclass=MissingItem):
    INVALID = -1
    OBJECT_EXCEPTION_CREATED = 1
    OBJECT_EXCEPTION_DELETED = 2
    OBJECT_EXCEPTION_UPDATED = 3
    OBJECT_EXCEPTION_EXPIRED = 4
    POLICY_EXCEPTION_CREATED = 10
    POLICY_EXCEPTION_DELETED = 11
    POLICY_EXCEPTION_UPDATED = 5
    POLICY_EXCEPTION_EXPIRED = 6
    PARTNER_ATTACHED = 7
    PARTNER_DETACHED = 8
    PARTNER_UPDATED = 9
    # Next value: 12

    @classmethod
    def _missing_(cls, value):
        return NotationType.INVALID
