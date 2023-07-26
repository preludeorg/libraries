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
   * @param {import("../types").DownloadParams} params - The parameters for downloading the probe executable.
   * @param {string} params.name - The name of the probe.
   * @param {import("../types").Platform} params.dos - The platform for the probe.
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<string>} A promise that resolves to the response text from the download request.
   */
  async download(params, options = {}) {
    const { name, dos } = params;

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
