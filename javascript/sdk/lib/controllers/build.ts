import Client from "../client";
import type { Manifest, TTPTests, RequestOptions } from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async listManifest(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/manifest", options);
    return (await response.json()) as Manifest;
  }

  async getTTP(id: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/manifest/${id}`, {
      ...options,
    });

    return (await response.json()) as TTPTests;
  }

  async createTTP(id: string, question: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/manifest`, {
      method: "PUT",
      body: JSON.stringify({ id, question }),
      ...options,
    });
  }

  async deleteTTP(id: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/manifest/${id}`, {
      method: "DELETE",
      ...options,
    });
  }

  /**
   * Creates or updates a test
   */
  async putTest(
    name: string,
    code: string,
    create: boolean = false,
    options: RequestOptions = {}
  ) {
    await this.#client.requestWithAuth(`/code/${name}`, {
      method: "POST",
      body: JSON.stringify({ code, create: +create }),
      ...options,
    });
  }

  /**
   * Deletes a test
   */
  async deleteTest(name: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/code/${name}`, {
      method: "DELETE",
      ...options,
    });
  }

  /**
   * Gets the content of test
   */
  async getTest(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/code/${name}`, {
      ...options,
    });

    return response.text();
  }

  async deleteCompliedTests(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/code`, {
      method: "DELETE",
      ...options,
    });

    return response.text();
  }
}
