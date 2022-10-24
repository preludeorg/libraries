import Client from "../client";
import type { BuildResults, Manifest, RequestOptions } from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async listTTP(options: RequestOptions) {
    const response = await this.#client.request("/manifest", options);
    return (await response.json()) as Manifest[];
  }

  async getTTP(id: string, options: RequestOptions = {}) {
    const response = await this.#client.request(`/manifest/${id}`, {
      ...options,
    });

    return (await response.json()) as Manifest;
  }

  async createTTP(id: string, question: string, options: RequestOptions = {}) {
    await this.#client.request(`/manifest`, {
      method: "PUT",
      body: JSON.stringify({ id, question }),
      ...options,
    });
  }

  async deleteTTP(id: string, options: RequestOptions = {}) {
    await this.#client.request(`/manifest/delete/${id}`, {
      method: "DELETE",
      ...options,
    });
  }

  /**
   * Creates or updates a code file
   */
  async putCodeFile(name: string, code: string, options: RequestOptions = {}) {
    await this.#client.request(`/code/${name}`, {
      method: "POST",
      body: JSON.stringify({ code }),
      ...options,
    });
  }

  /**
   * Deletes a code file
   */
  async deleteCodeFile(name: string, options: RequestOptions = {}) {
    await this.#client.request(`/code/${name}`, {
      method: "DELETE",
      ...options,
    });
  }

  async getCodeFile(name: string, options: RequestOptions = {}) {
    await this.#client.request(`/code/${name}`, {
      ...options,
    });
  }

  async deploy(name: string, options: RequestOptions = {}) {
    const response = await this.#client.request(`/build/deploy/${name}`, {
      ...options,
    });

    return (await response.json()) as BuildResults;
  }
}
