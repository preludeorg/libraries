import Client from "../client";
import type {RequestOptions, Test, TestData} from "../types";

interface MapParams {
  testId: string;
  key: string;
}

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Create or update a test */
  async createTest(
    name: string,
    options: RequestOptions = {}
  ): Promise<Test> {
    const response = await this.#client.requestWithAuth(`/build/tests`, {
      method: "POST",
      body: JSON.stringify({ name }),
      ...options,
    });
    return await response.json()
  }

  /** Delete an existing test */
  async deleteTest(id: string, options: RequestOptions = {}): Promise<void> {
    await this.#client.requestWithAuth(`/build/tests/${id}`, {
      method: "DELETE",
      ...options,
    });
  }

  /** Get properties of an existing test */
  async getTest(
    testId: string,
    options: RequestOptions = {}
  ): Promise<TestData> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        ...options,
      }
    );

    return await response.json();
  }

  /** Clone a test file or attachment */
  async download(
    testId: string,
    filename: string,
    options: RequestOptions = {}
  ): Promise<string> {
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

  async map(params: MapParams, options: RequestOptions = {}): Promise<string> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${params.testId}/map/${params.key}`,
      {
        method: "POST",
        body: JSON.stringify({ id: params.testId }),
        ...options,
      }
    );

    return response.text();
  }

  async unmap(params: MapParams, options: RequestOptions = {}): Promise<void> {
    await this.#client.requestWithAuth(
      `/build/tests/${params.testId}/map/${params.key}`,
      {
        method: "DELETE",
        body: JSON.stringify({ id: params.testId }),
        ...options,
      }
    );
  }
}
