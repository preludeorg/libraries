import Client from "../client";
import type { RequestOptions, Test } from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Create or update a test */
  async createTest(
    name: string,
    unit: string,
    advisory?: string,
    testId?: string,
    options: RequestOptions = {}
  ): Promise<Test> {
    const response = await this.#client.requestWithAuth(`/build/tests`, {
      method: "POST",
      body: JSON.stringify({ name, unit, advisory, testId }),
      ...options,
    });

    return await response.json();
  }

  /** Update a test */
  async updateTest(
    testId: string,
    name?: string,
    unit?: string,
    advisory?: string,
    options: RequestOptions = {}
  ): Promise<Test> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        method: "POST",
        body: JSON.stringify({ name, unit, advisory }),
        ...options,
      }
    );

    return await response.json();
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
