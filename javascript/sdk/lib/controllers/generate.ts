import Client from "../client";
import type { RequestOptions, ThreatIntel } from "../types";

export default class GenerateController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Upload a threat intel pdf */
  async uploadThreatIntel(
    file: File,
    options: RequestOptions = {},
  ): Promise<{ job_id: string }> {
    const headers = {
      "Content-Type": "application/pdf",
      ...options.headers,
    };

    const response = await this.#client.requestWithAuth(
      `/generate/threat-intel`,
      {
        method: "POST",
        body: await file.arrayBuffer(),
        headers,
        ...options,
      },
    );

    return (await response.json()) as { job_id: string };
  }

  /** Get a threat intel build process */
  async getThreatIntel(
    id: string,
    options: RequestOptions = {},
  ): Promise<ThreatIntel> {
    const response = await this.#client.requestWithAuth(
      `/generate/threat-intel/${id}`,
      {
        method: "GET",
        ...options,
      },
    );

    return (await response.json()) as ThreatIntel;
  }
}
