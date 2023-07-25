// @ts-check
import Client from "./client.js";
import BuildController from "./controllers/build";
import DetectController from "./controllers/detect";

/**
 * Serves as a wrapper for API requests
 *
 * @class
 */
export class Service {
  /**
   * @type {Client}
   */
  #client;

  /**
   * @param {import("./types.js").ServiceConfig} config
   */
  constructor(config) {
    this.#client = new Client(
      config.host,
      config.credentials,
      config.requestInterceptor
    );

    this.build = new BuildController(this.#client);
    this.iam = new IAMController(this.#client);
    this.detect = new DetectController(this.#client);
    this.probe = new ProbeController(this.#client);
    this.partner = new PartnerController(this.#client);
  }

  /**
   * @param {import("./types.js").Credentials} credentials
   */
  setCredentials(credentials) {
    this.credentials = credentials;
    this.#client.setCredentials(credentials);
  }
}
