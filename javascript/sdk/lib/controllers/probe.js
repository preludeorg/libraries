import Client from "../client";

/**
 * @class
 * @default
 * @param {Client} client
 */
export default class ProbeController {
  #client;

  /**
   * @param {Client} client
   */
  constructor(client) {
    this.#client = client;
  }

  /**
   * Download a probe executable
   *
   * @param {import("../types").DownloadParams} download - The download params object
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns
   */
  async download(download, options = {}) {
    const response = await this.#client.request(`/download/${download.name}`, {
      method: "GET",
      ...options,
      headers: {
        dos: download.dos,
        "Content-Type": "",
        ...(options.headers ?? {}),
      },
    });

    return response.text();
  }
}
