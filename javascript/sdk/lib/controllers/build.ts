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

  async createTest(
    id: string,
    rule: string,
    code: string,
    options: RequestOptions = {}
  ) {
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

  async download(
    testId: string,
    filename: string,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth(
      `/build/attachment/${testId}/${filename}`,
      options
    );
    return response.text();
  }

  async upload(
    testId: string,
    filename: string,
    code: string,
    options: RequestOptions = {}
  ) {
    await this.#client.requestWithAuth(
      `/build/attachment/${testId}/${filename}`,
      {
        method: "POST",
        body: JSON.stringify({ code }),
        ...options,
      }
    );
  }

  async createURL(vst: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/build/${vst}/url`, {
      ...options,
    });
    return (await response.json()) as { url: string };
  }

  async computeProxy(id: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/build/compute`, {
      method: "POST",
      body: JSON.stringify({ id }),
      ...options,
    });

    return (await response.json()) as ComputeResult[];
  }
}
