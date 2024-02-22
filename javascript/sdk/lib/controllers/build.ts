import Client from "../client";
import type {
  AttachedTest,
  RequestOptions,
  StatusResponse,
  Threat,
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
    technique?: string,
    testId?: string,
    options: RequestOptions = {}
  ): Promise<AttachedTest> {
    const response = await this.#client.requestWithAuth(`/build/tests`, {
      method: "POST",
      body: JSON.stringify({ name, unit, technique, id: testId }),
      ...options,
    });

    return (await response.json()) as AttachedTest;
  }

  /** Update a test */
  async updateTest(
    testId: string,
    name?: string,
    unit?: string,
    technique?: string,
    options: RequestOptions = {}
  ): Promise<AttachedTest> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        method: "POST",
        body: JSON.stringify({ name, unit, technique }),
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

  /** Create a threat */
  async createThreat(
    name: string,
    threat_id?: string,
    source_id?: string,
    source?: string,
    published?: string,
    tests?: string,
    options: RequestOptions = {}
  ): Promise<Threat> {
    const response = await this.#client.requestWithAuth(`/build/threats`, {
      method: "POST",
      body: JSON.stringify({
        name,
        threat_id,
        source_id,
        source,
        published,
        tests,
      }),
      ...options,
    });

    return (await response.json()) as Threat;
  }

  /** Update a threat */
  async updateThreat(
    threat_id: string,
    name?: string,
    source_id?: string,
    source?: string,
    published?: string,
    tests?: string,
    options: RequestOptions = {}
  ): Promise<Threat> {
    const response = await this.#client.requestWithAuth(
      `/build/threats/${threat_id}`,
      {
        method: "POST",
        body: JSON.stringify({
          name,
          threat_id,
          source_id,
          source,
          published,
          tests,
        }),
        ...options,
      }
    );

    return (await response.json()) as Threat;
  }

  /** Delete an existing threat */
  async deleteThreat(
    threat_id: string,
    options: RequestOptions = {}
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(
      `/build/threats/${threat_id}`,
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
