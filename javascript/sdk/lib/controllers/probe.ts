import Client from "../client";
import { DownloadParams, RequestOptions } from "../types";

export default class ProbeController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Download a probe executable */
  async download({ name, dos }: DownloadParams, options: RequestOptions = {}) {
    const response = await this.#client.request(`/download/${name}`, {
      method: "GET",
      ...options,
      headers: {
        dos,
        ...(options.headers ?? {}),
      },
    });

    return response.blob();
  }
}
