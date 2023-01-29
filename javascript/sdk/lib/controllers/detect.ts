import Client from "../client";
import {
  AccountQueue,
  Activity,
  EnableTest,
  Probe,
  RequestOptions,
  SearchResults,
  Stats,
} from "../types";

export default class DetectController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Register (or re-register) an endpoint to your account */
  async registerEndpoint(
    { id, tags = "" }: { id: string; tags?: string },
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth("/detect/endpoint", {
      method: "POST",
      body: JSON.stringify({ id, tags }),
      ...options,
    });

    return response.text();
  }

  async printQueue(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/detect/queue", {
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
    await this.#client.requestWithAuth(`/detect/queue/${test}`, {
      method: "POST",
      body: JSON.stringify({ code: runCode, tags }),
      ...options,
    });
  }

  /** Disable a test so endpoints will stop running it */
  async disableTest(test: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/detect/queue/${test}`, {
      method: "DELETE",
      ...options,
    });
  }

  /** Get report for an Account */
  async describeActivity(
    start: string,
    finish: string,
    options: RequestOptions = {}
  ) {
    const searchParams = new URLSearchParams({ start, finish });
    const response = await this.#client.requestWithAuth(
      `/detect/activity?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return (await response.json()) as Activity[];
  }

  /** Get all probes associated to an Account */
  async listProbes(days: number = 7, options: RequestOptions = {}) {
    const searchParams = new URLSearchParams({ days: days.toString() });
    const response = await this.#client.requestWithAuth(
      `/detect/probes?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return (await response.json()) as Probe[];
  }

  /** Pull social statistics for a specific test */
  async stats(test: string, days: number = 30, options: RequestOptions = {}) {
    const searchParams = new URLSearchParams({ days: days.toString() });
    const response = await this.#client.requestWithAuth(
      `/detect/${test}/stats?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return (await response.json()) as Stats;
  }

  /** Mark a result as observed */
  async observe(rowId: string, value: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/detect/observe`, {
      method: "POST",
      body: JSON.stringify({ row_id: rowId, value }),
      ...options,
    });

    return await response.text();
  }

  /** Delete an endpoint */
  async deleteProbe(endpoint_id: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/detect/endpoint`, {
      method: "DELETE",
      body: JSON.stringify({ id: endpoint_id }),
      ...options,
    });
  }

  /** Search the NVD for a keyword  */
  async search(identifier: string, options: RequestOptions = {}) {
    const searchParams = new URLSearchParams({ identifier });
    const response = await this.#client.requestWithAuth(
      `/detect/search?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return (await response.json()) as SearchResults;
  }
}
