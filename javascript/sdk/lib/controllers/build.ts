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
    techniques?: string,
    advisory?: string,
    testId?: string,
    options: RequestOptions = {}
  ): Promise<Test> {
    const response = await this.#client.requestWithAuth(`/build/tests`, {
      method: "POST",
      body: JSON.stringify({ name, unit, techniques, advisory, id: testId }),
      ...options,
    });

    return await response.json();
  }

  /** Update a test */
  async updateTest(
    testId: string,
    name?: string,
    unit?: string,
    techniques?: string,
    advisory?: string,
    options: RequestOptions = {}
  ): Promise<Test> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        method: "POST",
        body: JSON.stringify({ name, unit, techniques, advisory }),
        ...options,
      }
    );

    return await response.json();
  }

  /** Delete an existing test */
  async deleteTest(
    testId: string,
    options: RequestOptions = {}
  ): Promise<{ id: string }> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        method: "DELETE",
        ...options,
      }
    );

    return await response.json();
  }

  /** Upload a test or attachment */
  async upload(
    testId: string,
    filename: string,
    data: BodyInit,
    options: RequestOptions = {}
  ): Promise<{ id: string; filename: string }> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}/${filename}`,
      {
        method: "POST",
        body: data,
        ...options,
      }
    );

    return await response.json();
  }
}
