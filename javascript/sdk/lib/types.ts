export interface RequestConfig {
  host: string;
  account: string;
  token: string;
}

export type RequestOptions = Pick<RequestInit, "headers" | "signal">;

export interface Manifest {}

export interface BuildResults {}

export interface NewAccountResponse {}
