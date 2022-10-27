import Client from "../client";
import {
  AccountActivity,
  AccountQueue,
  EndpointActivity,
  RequestOptions,
  RunCode,
} from "../types";

export default class DetectController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async registerEndpoint(
    { name, tag = "" }: { name: string; tag?: string },
    options: RequestOptions
  ) {
    const response = await this.#client.requestWithAuth("/account/endpoint", {
      method: "POST",
      body: JSON.stringify({ name, tag }),
      ...options,
    });

    return response.text();
  }

  async endpointActivity(
    { endpointId, days = 7 }: { endpointId: string; days?: number },
    options: RequestOptions
  ) {
    const response = await this.#client.requestWithAuth(
      "/account/endpoint/activity",
      {
        method: "GET",
        body: JSON.stringify({ endpoint_id: endpointId, days }),
        ...options,
      }
    );

    return (await response.json()) as EndpointActivity;
  }

  async accountActivity(
    { days = 7 }: { days?: number },
    options: RequestOptions
  ) {
    const response = await this.#client.requestWithAuth("/account/activity", {
      method: "GET",
      body: JSON.stringify({ days }),
      ...options,
    });

    return (await response.json()) as AccountActivity;
  }

  async printQueue(options: RequestOptions) {
    const response = await this.#client.requestWithAuth("/account/queue", {
      method: "GET",
      ...options,
    });

    return (await response.json()) as AccountQueue;
  }

  /** Activate a TTP so endpoints will start running it */
  async activateTTP(ttpId: string, runCode: RunCode, options: RequestOptions) {
    await this.#client.requestWithAuth(`/account/activation/${ttpId}`, {
      method: "POST",
      body: JSON.stringify({ run_code: runCode }),
      ...options,
    });
  }

  /** Deactivate a TTP so endpoints will stop running it */
  async deactivateTTP(ttpId: string, options: RequestOptions) {
    await this.#client.requestWithAuth(`/account/activation/${ttpId}`, {
      method: "DELETE",
      ...options,
    });
  }
}
