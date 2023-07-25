import { ServiceConfig } from "./types";
import Client from "./client.js";
import BuildController from "./controllers/build.js";

/**
 * @class
 * @property {Client} client
 * @property {Credentials} [credentials]
 * @property {BuildController} build
 * @property {IAMController} iam
 * @property {DetectController} detect
 * @property {ProbeController} probe
 * @property {PartnerController} partner
 */
export class Service {
  #client;
  credentials;
  build;
  iam;
  detect;
  probe;
  partner;

  /**
   * @constructor
   * @param {ServiceConfig} config
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
   *
   * @param {Credentials} credentials
   */
  setCredentials(credentials) {
    this.credentials = credentials;
    this.#client.setCredentials(credentials);
  }
}
