import Client from "../client";
import type { ComputeResult, RequestOptions, Test } from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async listTests(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
      "/build/tests",
      options
    );
    return (await response.json()) as Test[];
  }

  async createTest(id: string, rule: string, code: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/build/tests`, {
      method: "POST",
      body: JSON.stringify({ id, rule, code }),
      ...options,
    });
  }

  async deleteTest(id: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/build/tests/${id}`, {
      method: "DELETE",
      ...options,
    });
  }

  async downloadTest(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
        `/build/source/${name}`,
        options
    );
    return response.text();
  }

  async uploadTest(name: string, code: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/build/source/${name}`, {
      method: "POST",
      body: JSON.stringify({ code }),
      ...options
    });
  }

  async createURL(vst: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/build/${vst}/url`, {
      ...options,
    });
    return (await response.json()) as { url: string };
  }

  async computeProxy(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/build/compute`, {
      method: "POST",
      body: JSON.stringify({ name }),
      ...options,
    });

    return (await response.json()) as ComputeResult[];
  }
}
