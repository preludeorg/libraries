import Client from "../client";
import {
  AccountActivity,
  AccountQueue,
  RequestOptions,
  EnableTest,
} from "../types";

export default class DetectController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Register (or re-register) an endpoint to your account */
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

  async printQueue(options: RequestOptions) {
    const response = await this.#client.requestWithAuth("/account/queue", {
      method: "GET",
      ...options,
    });

    return (await response.json()) as AccountQueue;
  }

  /** Enable a test so endpoints will start running it */
  async enableTest(
    { test, runCode, tags }: EnableTest,
    options: RequestOptions
  ) {
    await this.#client.requestWithAuth(`/account/queue/${test}`, {
      method: "POST",
      body: JSON.stringify({ run_code: runCode, tags }),
      ...options,
    });
  }

  /** Disable a test so endpoints will stop running it */
  async disableTest(test: string, options: RequestOptions) {
    await this.#client.requestWithAuth(`/account/queue/${test}`, {
      method: "DELETE",
      ...options,
    });
  }

  /** Get report for an Account */
  async describeActivity(
    { days = 7, ident }: { days?: number; ident?: string },
    options: RequestOptions
  ) {
    let route = !!ident ? `/${ident}` : "";

    const response = await this.#client.requestWithAuth(
      `/account/report${route}`,
      {
        method: "GET",
        body: JSON.stringify({ days }),
        ...options,
      }
    );

    return (await response.json()) as AccountActivity;
  }

  /** Generate a redirect URL to a data dump */
  async exportReport({ days = 7 }: { days?: number }, options: RequestOptions) {
    const response = await this.#client.requestWithAuth(
      "/account/report-export",
      {
        method: "GET",
        body: JSON.stringify({ days }),
        ...options,
      }
    );

    return (await response.json()) as string;
  }

  /** Get all tags associated to an Account */
  async listTags(options: RequestOptions) {
    const response = await this.#client.requestWithAuth("/account/tag", {
      method: "GET",
      ...options,
    });

    return await response.json();
  }
}
