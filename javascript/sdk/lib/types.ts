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
  state: "PROTECTED" | "UNPROTECTED" | "ERROR" | "REGISTERED" | null;
  endpoint_id: string;
  tags: string[];
  updated: string;
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
  PROCESS_KILLED: 9,
  PROTECTED: 100,
  UNPROTECTED: 101,
  TIMEOUT: 102,
  CLEANUP_ERROR: 103,
  NOT_RELEVANT: 104,
  QUARANTINED_1: 105,
  OUTBOUND_SECURE: 106,
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
    ExitCodes.PROCESS_KILLED,
    ExitCodes.NOT_RELEVANT,
    ExitCodes.OUTBOUND_SECURE,
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
  | "windows-arm64";

export interface Activity {
  date: string;
  endpoint_id: string;
  id: string;
  observed: 0 | 1;
  status: ExitCode;
  test: string;
  dos: Platform;
  tags: string[] | null;
}

export interface TestData {
  attachments: string[];
  mappings: string[];
}

export interface Rule {
  label: string;
  published: string;
  description: string;
}

export type RuleList = Record<string, Rule>;

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

export type DayResults = Record<
  string,
  {
    PROTECTED?: number;
    UNPROTECTED?: number;
    ERROR?: number;
  }
>;

export interface Insight {
  dos: string | null;
  tag: string | null;
  test: string | null;
  volume: { error: number; protected: number; unprotected: number };
}

export type RuleVolume = Record<
  string,
  {
    PROTECTED?: number;
    UNPROTECTED?: number;
    ERROR?: number;
  }
>;
