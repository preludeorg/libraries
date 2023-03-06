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

export interface Test {
  account_id: string;
  id: string;
  name: string;
}

export interface User {
  handle: string;
  permission: Permission;
}

export interface Control {
  name: string;
  api?: string;
  username?: string;
  secret?: string;
}

export interface Account {
  whoami: string;
  controls: Control[];
  users: User[];
}

export interface CreatedUser {
  token: string;
}

export interface Queue {
  test: string;
  run_code: RunCode;
  tag: string[] | null;
  started: string;
}

export const RunCodes = {
  DEBUG: 0,
  DAILY: 1,
  WEEKLY: 2,
  MONTHLY: 3,
  ONCE: 4,
} as const;

export type RunCode = typeof RunCodes[keyof typeof RunCodes];

export const Permissions = {
  ADMIN: 0,
  EXECUTIVE: 1,
  BUILD: 2,
  SERVICE: 3,
  NONE: 4,
} as const;

export type Permission = typeof Permissions[keyof typeof Permissions];

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
  tags: string[];
}

export interface Probe {
  endpoint_id: string;
  edr_id: string;
  host: string;
  last_beacon: string;
  serial_num: string;
  tags: string[];
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
  ERROR: 1,
  MALFORMED_VST: 2,
  PROCESS_KILLED_1: 9,
  PROCESS_KILLED_2: 15,
  PROTECTED: 100,
  UNPROTECTED: 101,
  TIMEOUT: 102,
  CLEANUP_ERROR: 103,
  NOT_RELEVANT: 104,
  QUARANTINED_1: 105,
  OUTBOUND_SECURE: 106,
  EXPLOIT_PREVENTED: 107,
  INCOMPATIBLE_HOST: 126,
  QUARANTINED_2: 127,
  UNEXPECTED: 256,
} as const;

export type ExitCodeName = keyof typeof ExitCodes;
export type ExitCode = typeof ExitCodes[ExitCodeName];
export const ExitCodeNames = Object.keys(ExitCodes) as ExitCodeName[];
export const ExitCodeGroup = {
  NONE: [ExitCodes.MISSING],
  PROTECTED: [
    ExitCodes.PROTECTED,
    ExitCodes.QUARANTINED_1,
    ExitCodes.QUARANTINED_2,
    ExitCodes.PROCESS_KILLED_1,
    ExitCodes.PROCESS_KILLED_2,
    ExitCodes.NOT_RELEVANT,
    ExitCodes.OUTBOUND_SECURE,
    ExitCodes.EXPLOIT_PREVENTED,
  ],
  UNPROTECTED: [ExitCodes.UNPROTECTED],
  ERROR: [
    ExitCodes.ERROR,
    ExitCodes.MALFORMED_VST,
    ExitCodes.TIMEOUT,
    ExitCodes.INCOMPATIBLE_HOST,
    ExitCodes.UNEXPECTED,
  ],
} as const;

export const ActionCodes = {
  NONE: 0,
  IGNORE: 1,
  IMPORTANT: 2,
} as const;

export type ActionCodeName = keyof typeof ActionCodes;
export type ActionCode = typeof ActionCodes[ActionCodeName];

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

export interface TestData {
  attachments: string[];
  mappings: string[];
}

export interface Rule {
  label: string;
  published: string;
  description: string;
  long_description: string;
}

export interface RuleUsage {
  tests: string[];
  count: number;
  unprotected: number;
}

export interface RuleInfo {
  rule: Rule | null;
  usage: RuleUsage;
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
  date: string;
  unprotected: number;
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
  event: RecommendationEvent[];
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
