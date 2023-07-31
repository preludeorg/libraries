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
  BEHAVIOR_PREVENTED_1: 9,
  BEHAVIOR_PREVENTED_2: 15,
  CHECK_COMPLETED: 100,
  NOT_PREVENTED: 101,
  TIMED_OUT: 102,
  FAILED_CLEANUP: 103,
  NOT_RELEVANT: 104,
  SIGNATURE_PREVENTED_1: 105,
  BLOCKED_AT_PERIMETER: 106,
  BEHAVIOR_PREVENTED_3: 107,
  TEST_UNAVAILABLE: 108,
  INCORRECTLY_BLOCKED: 110,
  BEHAVIOR_PREVENTED_4: 126,
  SIGNATURE_PREVENTED_2: 127,
  OUT_OF_MEMORY: 137,
  UNEXPECTED_ERROR: 256,
});

export const ExitCodeGroup = /** @type {const}*/ ({
  NONE: [ExitCode.MISSING],
  PROTECTED: [
    ExitCode.BEHAVIOR_PREVENTED_1,
    ExitCode.BEHAVIOR_PREVENTED_2,
    ExitCode.CHECK_COMPLETED,
    ExitCode.NOT_RELEVANT,
    ExitCode.SIGNATURE_PREVENTED_1,
    ExitCode.BLOCKED_AT_PERIMETER,
    ExitCode.BEHAVIOR_PREVENTED_3,
    ExitCode.TEST_UNAVAILABLE,
    ExitCode.BEHAVIOR_PREVENTED_4,
    ExitCode.SIGNATURE_PREVENTED_2,
  ],
  UNPROTECTED: [ExitCode.NOT_PREVENTED],
  ERROR: [
    ExitCode.UNKNOWN_ERROR,
    ExitCode.MALFORMED_TEST,
    ExitCode.TIMED_OUT,
    ExitCode.FAILED_CLEANUP,
    ExitCode.INCORRECTLY_BLOCKED,
    ExitCode.OUT_OF_MEMORY,
    ExitCode.UNEXPECTED_ERROR,
  ],
  NOT_RELEVANT: [ExitCode.NOT_RELEVANT, ExitCode.TEST_UNAVAILABLE],
});

export const Control = /** @type {const}*/ ({
  INVALID: 0,
  CROWDSTRIKE: 1,
  DEFENDER: 2,
  SPLUNK: 3,
});
