import { RequestConfig } from "./types";

export default class Client {
  config: RequestConfig;
  #defaultHeaders: HeadersInit;

  constructor(config: RequestConfig) {
    this.config = config;

    this.#defaultHeaders = {
      "Content-Type": "application/json",
      account: this.config.account,
      token: this.config.token,
    };
  }

  async request(path: string, options: RequestInit = {}) {
    const headers = options.headers ?? {};
    const response = await fetch(`${this.config.host}${path}`, {
      ...options,
      headers: {
        ...this.#defaultHeaders,
        ...headers,
      },
    });

    if (!response.ok) {
      throw Error(await response.text());
    }

    return response;
  }
}
