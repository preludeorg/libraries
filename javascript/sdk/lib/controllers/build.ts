import Client from "../client";
import type {
  AttachedTest,
  RequestOptions,
  StatusResponse,
  UploadedAttachment,
} from "../types";

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
  ): Promise<AttachedTest> {
    const response = await this.#client.requestWithAuth(`/build/tests`, {
      method: "POST",
      body: JSON.stringify({ name, unit, techniques, advisory, id: testId }),
      ...options,
    });

    return (await response.json()) as AttachedTest;
  }

  /** Update a test */
  async updateTest(
    testId: string,
    name?: string,
    unit?: string,
    techniques?: string,
    advisory?: string,
    options: RequestOptions = {}
  ): Promise<AttachedTest> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        method: "POST",
        body: JSON.stringify({ name, unit, techniques, advisory }),
        ...options,
      }
    );

    return (await response.json()) as AttachedTest;
  }

  /** Delete an existing test */
  async deleteTest(
    testId: string,
    options: RequestOptions = {}
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        method: "DELETE",
        ...options,
      }
    );

    return (await response.json()) as StatusResponse;
  }

  /** Upload a test or attachment */
  async upload(
    testId: string,
    filename: string,
    data: BodyInit,
    options: RequestOptions = {}
  ): Promise<UploadedAttachment> {
    if (data.toString().length > 1000000) {
      throw new Error(`File size must be under 1MB (${filename})`);
    }

    const headers = {
      "Content-Type": "application/octet-stream",
      ...options.headers,
    };

    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}/${filename}`,
      {
        method: "POST",
        body: data,
        headers,
        ...options,
      }
    );

    return (await response.json()) as UploadedAttachment;
  }
}
