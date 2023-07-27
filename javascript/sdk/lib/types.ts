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

export interface CreateAccountParams {
  email: string;
  name?: string;
  company?: string;
}

export interface CreateUserParams {
  permission: Permission;
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

export const RunCodes = {
  INVALID: -1,
  DEBUG: 0,
  DAILY: 1,
  WEEKLY: 2,
  MONTHLY: 3,
  MONDAY: 10,
  TUESDAY: 11,
  WEDNESDAY: 12,
  THURSDAY: 13,
  FRIDAY: 14,
  SATURDAY: 15,
  SUNDAY: 16,
  FIRST_OF_MONTH: 20,
} as const;

export type RunCode = (typeof RunCodes)[keyof typeof RunCodes];

export const Permissions = {
  INVALID: -1,
  ADMIN: 0,
  EXECUTIVE: 1,
  BUILD: 2,
  SERVICE: 3,
} as const;

export type Permission = (typeof Permissions)[keyof typeof Permissions];

export const Modes = {
  MANUAL: 0,
  FROZEN: 1,
  AUTOPILOT: 2,
} as const;

export type Mode = (typeof Modes)[keyof typeof Modes];

export interface ComputeResult {
  name: string;
  steps: {
    output: string | unknown[];
    status: number;
    step: string;
    duration: string;
  }[];
}

export interface EnableTest {
  test: string;
  runCode: RunCode;
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
  tags: string[];
  last_beacon: string;
  created: string;
}

export interface SearchResults {
  info: {
    published: string;
    description: string;
  };
  tests: string[];
}

export const ExitCodes = {
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
} as const;

export type ExitCodeName = keyof typeof ExitCodes;
export type ExitCode = (typeof ExitCodes)[ExitCodeName];
export const ExitCodeNames = Object.keys(ExitCodes) as ExitCodeName[];
export const ExitCodeGroup = {
  NONE: [ExitCodes.MISSING],
  PROTECTED: [
    ExitCodes.BEHAVIOR_PREVENTED_1,
    ExitCodes.BEHAVIOR_PREVENTED_2,
    ExitCodes.CHECK_COMPLETED,
    ExitCodes.NOT_RELEVANT,
    ExitCodes.SIGNATURE_PREVENTED_1,
    ExitCodes.BLOCKED_AT_PERIMETER,
    ExitCodes.BEHAVIOR_PREVENTED_3,
    ExitCodes.TEST_UNAVAILABLE,
    ExitCodes.BEHAVIOR_PREVENTED_4,
    ExitCodes.SIGNATURE_PREVENTED_2,
  ],
  UNPROTECTED: [ExitCodes.NOT_PREVENTED],
  ERROR: [
    ExitCodes.UNKNOWN_ERROR,
    ExitCodes.MALFORMED_TEST,
    ExitCodes.TIMED_OUT,
    ExitCodes.FAILED_CLEANUP,
    ExitCodes.INCORRECTLY_BLOCKED,
    ExitCodes.OUT_OF_MEMORY,
    ExitCodes.UNEXPECTED_ERROR,
  ],
  NOT_RELEVANT: [ExitCodes.NOT_RELEVANT, ExitCodes.TEST_UNAVAILABLE],
} as const;

export const ActionCodes = {
  NONE: 0,
  IGNORE: 1,
  IMPORTANT: 2,
} as const;

export type ActionCodeName = keyof typeof ActionCodes;
export type ActionCode = (typeof ActionCodes)[ActionCodeName];

export const ControlCodes = {
  INVALID: 0,
  CROWDSTRIKE: 1,
  DEFENDER: 2,
  SPLUNK: 3,
} as const;

export type ControlCodeName = keyof typeof ControlCodes;
export type ControlCode = (typeof ControlCodes)[ControlCodeName];

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
  observed: 0 | 1;
  status: ExitCode;
  test: string;
  dos: Platform;
  tags: string[] | null;
  edr_id: string | null;
}

export interface TestUsage {
  count: number;
  not_relevant: number;
  failed: number;
}

export interface TestActivity {
  id: string;
  usage: TestUsage;
}

export interface AdvisoryUsage {
  count: number;
  not_relevant: number;
  failed: number;
}

export interface AdvisoryInfo {
  id: string;
  usage: AdvisoryUsage;
}

export interface Advisory {
  id: string;
  name: string;
  source: string;
  published: string;
}

export type Stats = Record<Platform, Record<`${ExitCode}`, number>>;

export interface ActivityQuery {
  start: string;
  finish: string;
  tests?: string;
  result_id?: string;
  endpoints?: string;
  dos?: string;
  statuses?: string;
  tags?: string;
}

export interface DayResult {
  count: number;
  datetime: string;
  failed: number;
}

export interface Insight {
  dos: string | null;
  tag: string | null;
  test: string | null;
  volume: { error: number; protected: number; unprotected: number };
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  handle: string;
  created: string;
  events: RecommendationEvent[];
}
export interface RecommendationEvent {
  /**
   * 0 = NONE
   * 1 = APPROVE
   * 2 = DENY
   */
  decision: number;
  handle: string;
  created: string;
}
export type RuleVolume = Record<
  string,
  {
    PROTECTED?: number;
    UNPROTECTED?: number;
    ERROR?: number;
  }
>;

export interface ProbeActivity {
  dos: Platform;
  endpoint_id: string;
  state: "PROTECTED" | "UNPROTECTED" | "ERROR";
  tags: string[];
  edr_id: string | null;
}

export interface MetricsActivity {
  account_id: string;
  endpoints: number;
  tests: number;
  company: string;
  unique_tests: number;
  custom_tests: number;
}

export interface CreateRecommendation {
  title: string;
  description: string;
}

export interface DecideRecommendation {
  id: string;
  /**
   * 1 = APPROVE
   * 2 = DENY
   */
  decision: 1 | 2;
}

export interface RegisterEndpointParams {
  host: string;
  serial_num: string;
  edr_id?: string;
  tags?: string;
}

export interface UpdateEndpointParams {
  endpoint_id: string;
  host?: string;
  edr_id?: string;
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
  partnerCode: ControlCode;
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
  id: string;
  host_ids: string[];
}

export type PartnerEndpoints = Record<
  string,
  {
    hostname: string;
    version: string;
    state: string;
  }
>;

export interface AuditLog {
  event: string;
  account_id: string;
  user_id: string;
  values: AuditLogValues;
  status: ExitCode;
  timestamp: string;
}

export type AuditLogValues = Record<string, unknown>;
