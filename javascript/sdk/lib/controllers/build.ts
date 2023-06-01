import Client from "../client";
import type { RequestOptions } from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Create or update a test */
  async createTest(
    testId: string,
    name: string,
    unit: string,
    published?: string,
    advisory?: string,
    options: RequestOptions = {}
  ): Promise<void> {
    await this.#client.requestWithAuth(`/build/tests/${testId}`, {
      method: "POST",
      body: JSON.stringify({ name, unit, published, advisory }),
      ...options,
    });
  }

  /** Delete an existing test */
  async deleteTest(
    testId: string,
    options: RequestOptions = {}
  ): Promise<void> {
    await this.#client.requestWithAuth(`/build/tests/${testId}`, {
      method: "DELETE",
      ...options,
    });
  }

  /** Upload a test or attachment */
  async upload(
    testId: string,
    filename: string,
    data: BodyInit,
    options: RequestOptions = {}
  ): Promise<void> {
    await this.#client.requestWithAuth(`/build/tests/${testId}/${filename}`, {
      method: "POST",
      body: data,
      ...options,
    });
  }
}
