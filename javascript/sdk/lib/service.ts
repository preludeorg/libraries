import Client from "./client";
import BuildController from "./controllers/build";
import IAMController from "./controllers/iam";
import { RequestConfig } from "./types";

export default class Service {
  build: BuildController;
  iam: IAMController;

  constructor(config: RequestConfig) {
    const client = new Client(config);

    this.build = new BuildController(client);
    this.iam = new IAMController(client);
  }
}
