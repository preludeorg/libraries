import Client from "../client";
import type { ComputeResult, RequestOptions, Test } from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async listTests(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/test", options);
    return (await response.json()) as Test[];
  }

  async getTest(id: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/test/${id}`, {
      ...options,
    });

    return (await response.json()) as string[];
  }

  async createTest(id: string, question: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/test`, {
      method: "PUT",
      body: JSON.stringify({ id, question }),
      ...options,
    });
  }

  async deleteTest(id: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/test/${id}`, {
      method: "DELETE",
      ...options,
    });
  }

  async createVariant(
    name: string,
    code: string,
    options: RequestOptions = {}
  ) {
    await this.#client.requestWithAuth(`/variant/${name}`, {
      method: "POST",
      body: JSON.stringify({ code }),
      ...options,
    });
  }

  async deleteVariant(name: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/variant/${name}`, {
      method: "DELETE",
      ...options,
    });
  }

  async getVariant(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/variant/${name}`, {
      ...options,
    });

    return response.text();
  }

  async createURL(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
      `/variant/${name}/url`,
      {
        ...options,
      }
    );

    return (await response.json()) as { url: string };
  }

  async computeProxy(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/compute`, {
      method: "POST",
      body: JSON.stringify({ name }),
      ...options,
    });

    return (await response.json()) as ComputeResult[];
  }

  async verifiedTests(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/verified`, {
      ...options,
    });

    return (await response.json()) as string[];
  }

  async deleteVerified(name: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/verified/${name}`, {
      method: "DELETE",
      ...options,
    });
  }
}
