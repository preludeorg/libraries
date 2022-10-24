import Client from "../client";
import type { NewAccountResponse, RequestOptions } from "../types";

export default class IAMController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async newAccount(email: string, options: RequestOptions = {}) {
    const response = await this.#client.request("/account", {
      method: "POST",
      body: JSON.stringify({ email }),
      ...options,
    });
    return (await response.json()) as NewAccountResponse;
  }
}
