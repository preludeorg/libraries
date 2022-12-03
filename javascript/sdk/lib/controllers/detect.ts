import Client from "../client";
import {
  AccountActivity,
  AccountQueue,
  EnableTest,
  Probe,
  RequestOptions,
} from "../types";

export default class DetectController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Register (or re-register) an endpoint to your account */
  async registerEndpoint(
    { id, tags = [] }: { id: string; tags?: string[] },
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth("/account/endpoint", {
      method: "POST",
      body: JSON.stringify({ id, tags }),
      ...options,
    });

    return response.text();
  }

  async printQueue(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/account/queue", {
      method: "GET",
      ...options,
    });

    return (await response.json()) as AccountQueue[];
  }

  /** Enable a test so endpoints will start running it */
  async enableTest(
    { test, runCode, tags }: EnableTest,
    options: RequestOptions = {}
  ) {
    await this.#client.requestWithAuth(`/account/queue/${test}`, {
      method: "POST",
      body: JSON.stringify({ code: runCode, tags }),
      ...options,
    });
  }

  /** Disable a test so endpoints will stop running it */
  async disableTest(test: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/account/queue/${test}`, {
      method: "DELETE",
      ...options,
    });
  }

  /** Get report for an Account */
  async describeActivity(days: number = 7, options: RequestOptions = {}) {
    const searchParams = new URLSearchParams({ days: days.toString() });
    const response = await this.#client.requestWithAuth(
      `/account/report?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return (await response.json()) as AccountActivity;
  }

  /** Generate a redirect URL to a data dump */
  async exportReport(days: number = 7, options: RequestOptions = {}) {
    const searchParams = new URLSearchParams({ days: days.toString() });
    const response = await this.#client.requestWithAuth(
      `/account/report/export?${searchParams.toString()}`,
      {
        method: "GET",
        redirect: "manual",
        ...options,
      }
    );

    const location = response.headers.get("location");

    return location ?? "";
  }

  /** Get all probes associated to an Account */
  async listProbes(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/account/probes", {
      method: "GET",
      ...options,
    });

    return (await response.json()) as Probe[];
  }
}
