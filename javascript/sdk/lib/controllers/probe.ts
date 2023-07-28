import Client from "../client";
import { DownloadParams, RequestOptions } from "../types";

export default class ProbeController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /**
   * Download a probe executable
   *
   * @returns {string} - A URL location to download the probe.
   */
  async download(
    { name, dos }: DownloadParams,
    options: RequestOptions = {}
  ): Promise<string> {
    const response = await this.#client.request(`/download/${name}`, {
      method: "GET",
      ...options,
      headers: {
        dos,
        "Content-Type": "",
        ...(options.headers ?? {}),
      },
    });

    return response.text();
  }
}
