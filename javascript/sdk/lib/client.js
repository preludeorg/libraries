// @ts-check

/**
 * Asserts that the provided URL is valid.
 *
 * @param {URL} url - The URL to validate.
 */
function assertValidURL(url) {
  const validScheme = url.protocol === "http:" || url.protocol === "https:";

  if (!validScheme) {
    throw new Error(`Invalid URL ${url.toString()}`);
  }
}

/**
 * Default headers used in HTTP requests.
 *
 * @type {HeadersInit}
 */
const defaultHeaders = {
  "Content-Type": "application/json",
  _product: "js-sdk",
};

/**
 * Combines multiple sets of headers into a single headers object.
 *
 * @param {HeadersInit[]} headers - The headers to combine.
 * @returns {HeadersInit} The combined headers.
 */
function combineHeaders(...headers) {
  return headers.reduce((acc, h) => ({ ...acc, ...h }), {});
}

/**
 * Custom error class for API errors.
 *
 * @class
 * @extends Error
 */
export class APIError extends Error {
  /**
   * Constructs a new instance of the APIError class.
   *
   * @constructor
   * @param {string} message - The error message.
   * @param {number} status - The HTTP status code associated with the error.
   */
  constructor(message, status) {
    super(message);
    this.name = "APIError";
    this.status = status;
  }
}

/**
 * Client class for making HTTP requests.
 *
 * @class
 * @default
 */
export default class Client {
  #host;
  #credentials;
  #requestInterceptor;

  /**
   * Create a new instance of the Client class.
   *
   * @constructor
   * @param {string} host - The host URL.
   * @param {import("./types").Credentials} [credentials] - The authentication credentials.
   * @param {import("./types").RequestInterceptor} [requestInterceptor] - The request interceptor function.
   */
  constructor(host, credentials, requestInterceptor) {
    /**
     * The host URL.
     *
     * @type {URL}
     * @private
     */
    this.#host = new URL(host);
    assertValidURL(this.#host);

    /**
     * The authentication credentials.
     *
     * @type {import("./types").Credentials}
     * @private
     */
    this.#credentials = credentials;

    /**
     * The request interceptor function.
     *
     * @type {import("./types").RequestInterceptor}
     * @private
     */
    this.#requestInterceptor = requestInterceptor;
  }

  /**
   * Sets the credentials for the API client.
   *
   * @param {import("./types").Credentials} credentials - The authentication credentials to set.
   */
  setCredentials(credentials) {
    this.#credentials = credentials;
  }

  /**
   * Ensures that the credentials are properly set and returns them.
   *
   * @private
   * @returns {import("./types").Credentials} The validated credentials.
   * @throws {Error} If the account ID or token is not set.
   */
  #ensureCredentials() {
    if (typeof this.#credentials?.account !== "string") {
      throw new Error("Account ID not set");
    }

    if (typeof this.#credentials?.token !== "string") {
      throw new Error("Token not set");
    }

    return this.#credentials;
  }

  /**
   * Fetches the specified request.
   *
   * @private
   * @async
   * @param {Request} request - The request object to fetch.
   * @param {RequestInit} [options={}] - Optional request options.
   * @returns {Promise<Response>} A promise that resolves to the response.
   * @throws {APIError}
   */
  async #fetch(request, options = {}) {
    const response = await fetch(request);

    if (options.redirect === "manual" && response.status === 302) {
      return response;
    }

    if (!response.ok) {
      throw new APIError(await response.text(), response.status);
    }

    return response;
  }

  /**
   * Sends an HTTP request to the specified path.
   *
   * @async
   * @param {string} path - The path to send the request to.
   * @param {RequestInit} [options={}] - Optional request options.
   * @returns {Promise<Response>} A promise that resolves to the response.
   */
  async request(path, options = {}) {
    let req = new Request(new URL(path, this.#host), {
      ...options,
      headers: combineHeaders(defaultHeaders, options.headers ?? {}),
    });

    if (this.#requestInterceptor) {
      req = this.#requestInterceptor(req);
    }

    return this.#fetch(req, options);
  }

  /**
   * Sends an authenticated HTTP request to the specified path.
   *
   * @async
   * @param {string} path - The path to send the request to.
   * @param {RequestInit} [options={}] - Optional request options.
   * @returns {Promise<Response>} A promise that resolves to the response.
   * @throws {Error} If the account ID or token is not set.
   */
  async requestWithAuth(path, options = {}) {
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
