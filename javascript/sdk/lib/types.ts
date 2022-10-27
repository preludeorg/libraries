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

/** Dictionary to TTPs with
 * their id as the key
 * and question as the value */
export type ManifestList = Record<string, string>;

/** List of code files in the TTP Manifest */
export type Manifest = string[];

export interface BuildResults {}

export interface Users {}

export interface CreatedUser {}

export interface EndpointActivity {}

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
