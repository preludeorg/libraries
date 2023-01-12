export interface ServiceConfig {
  host: string;
  /** credentials is optional since some requests can be made without them */
  credentials?: Credentials;
}

export interface Credentials {
  account: string;
  token: string;
}

export type RequestOptions = Omit<RequestInit, "method" | "body">;

export interface Test {
  account_id: string;
  id: string;
  filename: string;
  rule: string;
  vst: string[];
}

export interface User {
  handle: string;
  permission: Permission;
}

export interface Range {
  url: string;
  token: string;
}

export interface CreatedUser {
  token: string;
}

export type AccountActivity = Record<string, any>;

export interface AccountQueue {}

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
