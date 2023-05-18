import Client from "../client";
import type { RequestOptions } from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Create or update a test */
  async createTest(
    id: string,
    name: string,
    unit: string,
    options: RequestOptions = {}
  ): Promise<void> {
    await this.#client.requestWithAuth(`/build/tests/${id}`, {
      method: "POST",
      body: JSON.stringify({ name, unit }),
      ...options,
    });
  }

  /** Delete an existing test */
  async deleteTest(id: string, options: RequestOptions = {}): Promise<void> {
    await this.#client.requestWithAuth(`/build/tests/${id}`, {
      method: "DELETE",
      ...options,
    });
  }

  /** Upload a test or attachment */
  async upload(
    testId: string,
    filename: string,
    code: string,
    options: RequestOptions = {}
  ): Promise<void> {
    await this.#client.requestWithAuth(`/build/tests/${testId}/${filename}`, {
      method: "POST",
      body: JSON.stringify({ code }),
      ...options,
    });
  }
}
