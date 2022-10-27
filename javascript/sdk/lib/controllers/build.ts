import Client from "../client";
import type {
  BuildResults,
  Manifest,
  ManifestList,
  RequestOptions,
} from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async listManifest(options: RequestOptions) {
    const response = await this.#client.requestWithAuth("/manifest", options);
    return (await response.json()) as ManifestList;
  }

  async getTTP(id: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(`/manifest/${id}`, {
      ...options,
    });

    return (await response.json()) as Manifest;
  }

  async createTTP(id: string, question: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/manifest`, {
      method: "PUT",
      body: JSON.stringify({ id, question }),
      ...options,
    });
  }

  async deleteTTP(id: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/manifest/delete/${id}`, {
      method: "DELETE",
      ...options,
    });
  }

  /**
   * Creates or updates a code file
   */
  async putCodeFile(name: string, code: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/code/${name}`, {
      method: "POST",
      body: JSON.stringify({ code }),
      ...options,
    });
  }

  /**
   * Deletes a code file
   */
  async deleteCodeFile(name: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/code/${name}`, {
      method: "DELETE",
      ...options,
    });
  }

  async getCodeFile(name: string, options: RequestOptions = {}) {
    const response = await this.#client.request(`/code/${name}`, {
      ...options,
    });

    return response.text();
  }

  async deploy(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
      `/build/deploy/${name}`,
      {
        ...options,
      }
    );

    return (await response.json()) as BuildResults;
  }
}
