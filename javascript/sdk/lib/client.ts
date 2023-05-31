import { Credentials } from "./types";

function assertValidURL(url: URL) {
  const validScheme = url.protocol === "http:" || url.protocol === "https:";

  if (!validScheme) {
    throw new Error(`Invalid URL ${url.toString()}`);
  }
}

const defaultHeaders: HeadersInit = {
  "Content-Type": "application/json",
  _product: "js-sdk",
};

function combineHeaders(...headers: HeadersInit[]): HeadersInit {
  return headers.reduce((acc, h) => ({ ...acc, ...h }), {});
}

class APIError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = "APIError";
  }
}
export default class Client {
  #host: URL;
  #credentials?: Credentials;
  #requestInterceptor?: (request: Request) => Request;

  constructor(
    host: string,
    credentials?: Credentials,
    requestInterceptor?: (request: Request) => Request
  ) {
    this.#host = new URL(host);
    assertValidURL(this.#host);

    this.#credentials = credentials;
    this.#requestInterceptor = requestInterceptor;
  }

  setCredentials(credentials: Credentials) {
    this.#credentials = credentials;
  }

  #ensureCredentials() {
    if (typeof this.#credentials?.account !== "string") {
      throw new Error("Account ID not set");
    }

    if (typeof this.#credentials?.token !== "string") {
      throw new Error("Token not set");
    }

    return this.#credentials;
  }

  async #fetch(request: Request, options: RequestInit = {}) {
    const response = await fetch(request);

    if (options.redirect === "manual" && response.status === 302) {
      return response;
    }

    if (!response.ok) {
      throw new APIError(await response.text(), response.status);
    }

    return response;
  }

  async request(path: string, options: RequestInit = {}) {
    let req = new Request(new URL(path, this.#host), {
      ...options,
      headers: combineHeaders(defaultHeaders, options.headers ?? {}),
    });

    if (this.#requestInterceptor) {
      req = this.#requestInterceptor(req);
    }

    return this.#fetch(req, options);
  }

  async requestWithAuth(path: string, options: RequestInit = {}) {
    const credentials = this.#ensureCredentials();

    let req = new Request(new URL(path, this.#host), {
      ...options,
      headers: combineHeaders(
        defaultHeaders,
        { ...credentials },
        options.headers ?? {}
      ),
    });

    if (this.#requestInterceptor) {
      req = this.#requestInterceptor(req);
    }

    return this.#fetch(req, options);
  }
}
