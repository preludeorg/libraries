import Client from "../client";
import {
  ComputeProps,
  ComputeResult,
  ComputeRoute,
  CreatedURL,
  RequestOptions,
} from "../types";

export default class ComputeController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async describeServer(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/compute", {
      ...options,
    });

    return response.text();
  }

  async computeProxy(
    route: ComputeRoute,
    data: ComputeProps,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth(
      `/compute/proxy/${route}`,
      {
        method: "POST",
        body: JSON.stringify(data),
        ...options,
      }
    );

    return (await response.json()) as ComputeResult[];
  }

  async createURL(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
      `/compute/url/${name}`,
      {
        ...options,
      }
    );

    return (await response.json()) as CreatedURL;
  }
}
