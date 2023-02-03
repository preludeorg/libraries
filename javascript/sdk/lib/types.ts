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

export const PassCodes = [100, 9, 17, 18, 105, 127, 106] as const;
export const FailCodes = [101] as const;
export const ErrorCodes = [1, 2, 15, 102, 103, 126, 256] as const;

const StatusCodes = [...PassCodes, ...FailCodes, ...ErrorCodes] as const;
export type StatusCode = typeof StatusCodes[number];

export interface Activity {
  date: string;
  endpoint_id: string;
  id: string;
  observed: 0 | 1;
  status: StatusCode;
  test: string;
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

export type Platform =
  | "darwin-arm64"
  | "darwin-x86_64"
  | "linux-x86_64"
  | "linux-arm64"
  | "windows-x86_64"
  | "windows-arm64";
export type StatusCodeAsStr = `${StatusCode}`;
export type Stats = Record<Platform, Record<StatusCodeAsStr, number>>;

export interface Insight {
  name: string;
  test: string;
  created: string;
}

export interface ActivityQuery {
  start: string;
  finish: string;
  view: "days" | "probes" | "logs" | "insights";
  test?: string;
  result_id?: string;
  endpoint_id?: string;
  dos?: string;
  status?: unknown;
  tags?: string;
}
