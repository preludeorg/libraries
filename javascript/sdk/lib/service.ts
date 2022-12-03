import Client from "./client";
import BuildController from "./controllers/build";
import DetectController from "./controllers/detect";
import IAMController from "./controllers/iam";
import { Credentials, ServiceConfig } from "./types";

export class Service {
  #client: Client;
  credentials?: Credentials;
  build: BuildController;
  iam: IAMController;
  detect: DetectController;

  constructor(config: ServiceConfig) {
    this.#client = new Client(config.host, config.credentials);

    this.build = new BuildController(this.#client);
    this.iam = new IAMController(this.#client);
    this.detect = new DetectController(this.#client);
  }

  setCredentials(credentials: Credentials) {
    this.credentials = credentials;
    this.#client.setCredentials(credentials);
  }
}
