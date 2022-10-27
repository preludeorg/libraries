import { Credentials } from "./types";

function assertValidURL(url: URL) {
  const validScheme = url.protocol === "http:" || url.protocol === "https:";

  if (!validScheme) {
    throw new Error(`Invalid URL ${url.toString()}`);
  }
}
export default class Client {
  #host: URL;
  #credentials?: Credentials;
  #defaultHeaders: HeadersInit;

  constructor(host: string, credentials?: Credentials) {
    this.#host = new URL(host);
    assertValidURL(this.#host);

    this.#credentials = credentials;

    this.#defaultHeaders = {
      "Content-Type": "application/json",
    };
  }

  setCredentials(credentials: Credentials) {
    this.#credentials = credentials;
  }

  #assertCredentials() {
    if (typeof this.#credentials?.account !== "string") {
      throw new Error("Account ID credential not set");
    }

    if (typeof this.#credentials?.token !== "string") {
      throw new Error("Token credential not set");
    }
  }

  async #fetch(path: string, headers: HeadersInit, options: RequestInit) {
    const customHeaders = options.headers ?? {};
    const response = await fetch(`${this.#host.toString()}${path}`, {
      ...options,
      headers: {
        ...headers,
        ...customHeaders,
      },
    });

    if (!response.ok) {
      throw Error(await response.text());
    }

    return response;
  }

  async request(path: string, options: RequestInit = {}) {
    return this.#fetch(path, this.#defaultHeaders, options);
  }

  async requestWithAuth(path: string, options: RequestInit = {}) {
    this.#assertCredentials();
    return this.#fetch(
      path,
      { ...this.#credentials, ...this.#defaultHeaders },
      options
    );
  }
}
