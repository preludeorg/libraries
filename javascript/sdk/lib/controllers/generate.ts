import Client from "../client";
import type { GeneratedTechnique, RequestOptions, ThreatIntel } from "../types";

export default class GenerateController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Upload a threat intel pdf */
  async uploadThreatIntel(
    file: File,
    force_ai: boolean,
    options: RequestOptions = {},
  ): Promise<{ job_id: string }> {
    const searchParams = new URLSearchParams();
    searchParams.set("force_ai", force_ai ? "true" : "false");
    const headers = {
      "Content-Type": "application/pdf",
      ...options.headers,
    };

    const response = await this.#client.requestWithAuth(
      `/generate/threat-intel?${searchParams.toString()}`,
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

  /** Generate a technique from threat intel build process */
  async generateTechnique(
    technique: string,
    parent_job_id?: string,
    intel_context?: string,
    options: RequestOptions = {},
  ): Promise<GeneratedTechnique> {
    const response = await this.#client.requestWithAuth(`/generate/technique`, {
      method: "POST",
      body: JSON.stringify({ technique, parent_job_id, intel_context }),
      ...options,
    });

    return (await response.json()) as GeneratedTechnique;
  }
}
