import Client from "../client";
import type { ComputeResult, RequestOptions, Test, TestData } from "../types";

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

  async createTest(id: string, name: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/build/tests/${id}`, {
      method: "POST",
      body: JSON.stringify({ name }),
      ...options,
    });
  }

  async deleteTest(id: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/build/tests/${id}`, {
      method: "DELETE",
      ...options,
    });
  }

  async getTest(testId: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        ...options,
      }
    );

    return (await response.json()) as TestData;
  }

  async download(
    testId: string,
    filename: string,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}/${filename}`,
      {
        ...options,
        headers: {
          "Content-Type": "",
          ...(options.headers ?? {}),
        },
      }
    );
    return response.text();
  }

  async upload(
    testId: string,
    filename: string,
    code: string,
    options: RequestOptions = {}
  ) {
    await this.#client.requestWithAuth(`/build/tests/${testId}/${filename}`, {
      method: "POST",
      body: JSON.stringify({ code }),
      ...options,
    });
  }

  async createURL(attachment: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
      `/build/${attachment}/url`,
      {
        ...options,
      }
    );
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
