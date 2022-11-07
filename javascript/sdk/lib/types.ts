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
  question: string;
}

export interface Users {
  [id: string]: {
    handle: string;
    permission: Permission;
  };
}

export interface CreatedUser {
  token: string;
}

export interface AccountActivity {}

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
  OPERATOR: 2,
  SERVICE: 3,
  NONE: 4,
} as const;

export type Permission = typeof Permissions[keyof typeof Permissions];

export const ComputeRoutes = {
  TEST: "test",
  PUBLISH: "publish",
} as const;

export type ComputeRoute = typeof ComputeRoutes[keyof typeof ComputeRoutes];

export interface ComputeProps {
  /** test name */
  name: string;
}

export interface ComputeResult {
  architecture: string;
  platform: string;
  steps: {
    duration: string;
    name: string;
    output: string;
    status: number;
    step: string;
  }[];
}

export interface CreatedURL {}

export interface EnableTest {
  test: string;
  runCode: RunCode;
  tags: string[];
}
