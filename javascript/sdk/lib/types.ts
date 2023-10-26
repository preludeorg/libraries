export interface ServiceConfig {
  host: string;
  /** credentials is optional since some requests can be made without them */
  credentials?: Credentials;
  /** requestInterceptor allows you to modify the request before it is sent */
  requestInterceptor?: (request: Request) => Request;
}

export interface Credentials {
  account: string;
  token: string;
}

export type RequestOptions = Omit<RequestInit, "method" | "body">;

export interface StatusResponse {
  status: true;
}

export interface Test {
  account_id: string;
  id: string;
  name: string;
  unit: string;
  techniques: string[];
  advisory: string;
}

export type AttachedTest = Test & {
  attachments: string[];
};

export interface UploadedAttachment {
  id: string;
  filename: string;
}

export interface User {
  handle: string;
  permission: Permission;
  expires: string;
  name: string;
}

export interface Control {
  id: ControlCode;
  api: string;
}
export interface Account {
  account_id: string;
  whoami: string;
  users: User[];
  queue: Queue[];
  controls: Control[];
  mode: Mode;
  company: string;
}

export interface VerifiedUser {
  account_id: string;
  token: string;
  handle: string;
  permission: Permission;
  expires: string;
  name: string;
}

export interface CreateAccountParams {
  email: string;
  name?: string;
  company?: string;
}

export interface CreateUserParams {
  permission: PermissionName;
  email: string;
  name?: string;
  expires?: string;
}

export interface CreatedUser {
  token: string;
}

export interface Queue {
  test: string;
  run_code: RunCode;
  tag: string | null;
  started: string;
}

/**
 * Get the name of an enum value
 * @example,
 * getEnumName(RunCodes, RunCodes.DAILY) // => "DAILY"
 */
export function getEnumName<T extends Record<string, unknown>>(
  enumType: T,
  value: T[keyof T]
): keyof T {
  const key = Object.keys(enumType).find((k) => enumType[k] === value);
  if (key === undefined) {
    throw new Error(`Unknown enum value ${value}`);
  }
  return key;
}

export const RunCodes = {
  INVALID: -1,
  DAILY: 1,
  WEEKLY: 2,
  MONTHLY: 3,
  SMART: 4,
  DEBUG: 5,
  MONDAY: 10,
  TUESDAY: 11,
  WEDNESDAY: 12,
  THURSDAY: 13,
  FRIDAY: 14,
  SATURDAY: 15,
  SUNDAY: 16,
  MONTH_1: 20,
} as const;

export type RunCodeName = keyof typeof RunCodes;
export type RunCode = (typeof RunCodes)[keyof typeof RunCodes];

export const Permissions = {
  INVALID: -1,
  ADMIN: 0,
  EXECUTIVE: 1,
  BUILD: 2,
  SERVICE: 3,
  AUTO: 4,
} as const;

export type PermissionName = keyof typeof Permissions;
export type Permission = (typeof Permissions)[keyof typeof Permissions];

export const Modes = {
  MANUAL: 0,
  FROZEN: 1,
  AUTOPILOT: 2,
} as const;

export type ModeName = keyof typeof Modes;
export type Mode = (typeof Modes)[keyof typeof Modes];

export interface EnableTest {
  test: string;
  runCode: RunCodeName;
  tags?: string;
}

export interface EnabledTest {
  id: string;
}

export interface DisableTest {
  test: string;
  tags: string;
}

export interface Probe {
  endpoint_id: string;
  host: string;
  serial_num: string;
  edr_id: string | null;
  control: ControlCode;
  tags: string[];
  last_seen: string;
  created: string;
  dos: Platform | null;
  os?: string | null;
  policy?: string | null;
  policy_name?: string | null;
}

export const ExitCodes = {
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
  TEST_DISALLOWED: 126,
  STATIC_QUARANTINE: 127,
  BLOCKED: 137,
  UNEXPECTED_ERROR: 256,
} as const;

export type ExitCodeName = keyof typeof ExitCodes;
export type ExitCode = (typeof ExitCodes)[ExitCodeName];
export const ExitCodeNames = Object.keys(ExitCodes) as ExitCodeName[];
export const ExitCodeGroup = {
  NONE: [ExitCodes.MISSING],
  PROTECTED: [
    ExitCodes.PROCESS_BLOCKED,
    ExitCodes.PROCESS_BLOCKED_GRACEFULLY,
    ExitCodes.PROTECTED,
    ExitCodes.DYNAMIC_QUARANTINE,
    ExitCodes.BLOCKED_AT_PERIMETER,
    ExitCodes.BLOCKED,
    ExitCodes.EXPLOIT_PREVENTED,
    ExitCodes.TEST_DISALLOWED,
    ExitCodes.STATIC_QUARANTINE,
    ExitCodes.TEST_NOT_RELEVANT,
    ExitCodes.ENDPOINT_NOT_RELEVANT,
  ],
  UNPROTECTED: [ExitCodes.UNPROTECTED],
  ERROR: [
    ExitCodes.UNKNOWN_ERROR,
    ExitCodes.MALFORMED_TEST,
    ExitCodes.TIMED_OUT,
    ExitCodes.FAILED_CLEANUP,
    ExitCodes.UNEXPECTED_ERROR,
  ],
  NOT_RELEVANT: [ExitCodes.TEST_NOT_RELEVANT, ExitCodes.ENDPOINT_NOT_RELEVANT],
} as const;

export const ActionCodes = {
  NONE: 0,
  IGNORE: 1,
  IMPORTANT: 2,
} as const;

export type ActionCodeName = keyof typeof ActionCodes;
export type ActionCode = (typeof ActionCodes)[ActionCodeName];

export const ControlCodes = {
  INVALID: -1,
  NONE: 0,
  CROWDSTRIKE: 1,
  DEFENDER: 2,
  SPLUNK: 3,
  SENTINELONE: 4,
  VECTR: 5,
} as const;

export type ControlCodeName = keyof typeof ControlCodes;
export type ControlCode = (typeof ControlCodes)[ControlCodeName];

export type NonArchPlatform = "darwin" | "linux" | "windows";

export type Platform =
  | "darwin-arm64"
  | "darwin-x86_64"
  | "linux-x86_64"
  | "linux-arm64"
  | "windows-x86_64"
  | "windows-arm64"
  | "unknown";

export interface Activity {
  date: string;
  endpoint_id: string;
  id: string;
  status: ExitCode;
  test: string;
  dos: Platform;
  control: ControlCode;
  policy: string | null;
  os: string | null;
}

export interface TestsActivity {
  id: string;
  protected: number;
}

export interface Advisory {
  id: string;
  name: string;
  source: string;
  published: string;
}

export interface AdvisoriesActivity {
  id: string;
  protected: number;
}

export interface ActivityQuery {
  start: string;
  finish: string;
  tests?: string;
  endpoints?: string;
  dos?: string;
  statuses?: string;
  control?: string;
  impersonate?: string;
  os?: string;
  policy?: string;
}

export interface DayActivity {
  datetime: string;
  unprotected: number;
  volume: number;
}

export interface Insight {
  dos: string | null;
  test: string | null;
  volume: { error: number; protected: number; unprotected: number };
}

export interface ProbeActivity {
  dos: Platform;
  endpoint_id: string;
  state: "PROTECTED" | "UNPROTECTED" | "ERROR";
  control: ControlCode;
}

export type EndpointActivity = Record<string, number>;

export interface MetricsActivity {
  account_id: string;
  endpoints: number;
  tests: number;
  company: string;
  unique_tests: number;
}

export interface Finding {
  key: string;
  value: string | ControlCode | null;
  improvement: number;
}

export interface FindingsActivity {
  protected: number;
  dos: Platform;
  control: ControlCode;
  policy: string | null;
  os: string | null;
  finding?: Finding;
}

export interface RegisterEndpointParams {
  host: string;
  serial_num: string;
  tags?: string;
}

export interface UpdateEndpointParams {
  endpoint_id: string;
  tags?: string;
}

export interface UpdatedEndpoint {
  id: string;
}

export interface DownloadParams {
  name: string;
  dos: Platform;
}

export interface AttachPartnerParams {
  partnerCode: ControlCode;
  api: string;
  user: string;
  secret?: string;
}

export interface AttachedPartner {
  api: string;
  connected: boolean;
}

export interface EndpointsParams {
  partner: ControlCodeName;
  platform: string;
  hostname?: string;
  offset?: number;
  count?: number;
}

export interface DeployParams {
  partnerCode: ControlCode;
  hostIds: string[];
}

export interface DeployedEndpoints {
  id: ControlCode;
  host_ids: string[];
}

export type PartnerEndpoints = Record<
  string,
  {
    hostname: string;
    os: string;
    policy?: string | null;
    policy_name?: string | null;
  }
>;

export interface AuditLog {
  event: string;
  account_id: string;
  user_id: string;
  values: AuditLogValues;
  status: string;
  timestamp: string;
}

export type AuditLogValues = Record<string, unknown>;

export interface BlockResponse {
  file: string;
  already_reported?: boolean;
  ioc_id?: string;
}
