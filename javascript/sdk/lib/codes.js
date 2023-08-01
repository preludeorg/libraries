//@ts-check
export const RunCode = /** @type {const}*/ ({
  INVALID: -1,
  DEBUG: 0,
  DAILY: 1,
  MONDAY: 10,
  TUESDAY: 11,
  WEDNESDAY: 12,
  THURSDAY: 13,
  FRIDAY: 14,
  SATURDAY: 15,
  SUNDAY: 16,
  FIRST_OF_MONTH: 20,
});

export const Mode = /** @type {const}*/ ({
  MANUAL: 0,
  FROZEN: 1,
  AUTOPILOT: 2,
});

export const Permission = /** @type {const}*/ ({
  INVALID: -1,
  ADMIN: 0,
  EXECUTIVE: 1,
  BUILD: 2,
  SERVICE: 3,
});

export const ExitCode = /** @type {const}*/ ({
  MISSING: -1,
  UNKNOWN_ERROR: 1,
  MALFORMED_TEST: 2,
  PROCESS_BLOCKED: 9,
  PROCESS_BLOCKED_GRACEFULLY: 15,
  PROTECTED: 100,
  UNPROTECTED: 101,
  TIMED_OUT: 102,
  FAILED_CLEANUP: 103,
  TEST_NOT_RELEVANT: 104,
  DYNAMIC_QUARANTINE: 105,
  BLOCKED_AT_PERIMETER: 106,
  EXPLOIT_PREVENTED: 107,
  ENDPOINT_NOT_RELEVANT: 108,
  FALSE_POSITIVE: 110,
  TEST_DISALLOWED: 126,
  STATIC_QUARANTINE: 127,
  OUT_OF_MEMORY: 137,
  UNEXPECTED_ERROR: 256,
});

export const ExitCodeGroup = /** @type {const}*/ ({
  NONE: [ExitCode.MISSING],
  PROTECTED: [
    ExitCode.PROCESS_BLOCKED,
    ExitCode.PROCESS_BLOCKED_GRACEFULLY,
    ExitCode.PROTECTED,
    ExitCode.DYNAMIC_QUARANTINE,
    ExitCode.BLOCKED_AT_PERIMETER,
    ExitCode.EXPLOIT_PREVENTED,
    ExitCode.TEST_DISALLOWED,
    ExitCode.STATIC_QUARANTINE,
    ExitCode.TEST_NOT_RELEVANT,
    ExitCode.ENDPOINT_NOT_RELEVANT,
  ],
  UNPROTECTED: [
    ExitCode.UNPROTECTED,
    ExitCode.FALSE_POSITIVE,
  ],
  ERROR: [
    ExitCode.UNKNOWN_ERROR,
    ExitCode.MALFORMED_TEST,
    ExitCode.TIMED_OUT,
    ExitCode.FAILED_CLEANUP,
    ExitCode.OUT_OF_MEMORY,
    ExitCode.UNEXPECTED_ERROR,
  ],
  NOT_RELEVANT: [
    ExitCode.TEST_NOT_RELEVANT,
    ExitCode.ENDPOINT_NOT_RELEVANT,
  ],
});

export const Control = /** @type {const}*/ ({
  INVALID: 0,
  CROWDSTRIKE: 1,
  DEFENDER: 2,
  SPLUNK: 3,
});
