// @ts-check
import Client from "./client.js";
import BuildController from "./controllers/build.js";
import DetectController from "./controllers/detect.js";
import IAMController from "./controllers/iam.js";
import PartnerController from "./controllers/partner.js";
import ProbeController from "./controllers/probe.js";

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
    this.partner = new PartnerController(this.#client);
    this.probe = new ProbeController(this.#client);
  }

  /**
   * @param {import("./types.js").Credentials} credentials
   */
  setCredentials(credentials) {
    this.credentials = credentials;
    this.#client.setCredentials(credentials);
  }
}
