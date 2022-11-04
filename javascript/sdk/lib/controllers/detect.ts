import Client from "../client";
import {
  AccountActivity,
  AccountQueue,
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

  async enableTest(test: string, runCode: RunCode, options: RequestOptions) {
    await this.#client.requestWithAuth(`/account/activation/${test}`, {
      method: "POST",
      body: JSON.stringify({ run_code: runCode }),
      ...options,
    });
  }

  async disableTest(test: string, options: RequestOptions) {
    await this.#client.requestWithAuth(`/account/activation/${test}`, {
      method: "DELETE",
      ...options,
    });
  }
}
