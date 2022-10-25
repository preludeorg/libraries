export interface RequestConfig {
  host: string;
  account: string;
  token: string;
}

export type RequestOptions = Pick<RequestInit, "headers" | "signal">;

/** Dictionary to TTPs with
 * their id as the key
 * and question as the value */
export type ManifestList = Record<string, string>;

/** List of code files in the TTP Manifest */
export type Manifest = string[];

export interface BuildResults {}

export interface NewAccountResponse {}
