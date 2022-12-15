import Client from "../client";
import type {
  CreatedUser,
  Credentials,
  Permission,
  RequestOptions,
  User,
} from "../types";

export default class IAMController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async newAccount(
    handle: string,
    options: RequestOptions = {}
  ): Promise<Credentials> {
    const response = await this.#client.request("/account", {
      method: "POST",
      body: JSON.stringify({ handle }),
      ...options,
    });

    const json = (await response.json()) as {
      account_id: string;
      token: string;
    };

    return {
      account: json.account_id,
      token: json.token,
    };
  }

  async getUsers(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/account/user", {
      method: "GET",
      ...options,
    });

    return (await response.json()) as User[];
  }

  async createUser(
    permission: Permission,
    handle: string,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth("/account/user", {
      method: "POST",
      body: JSON.stringify({ permission, handle }),
      ...options,
    });

    return (await response.json()) as CreatedUser;
  }

  async deleteUser(handle: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth("/account/user", {
      method: "DELETE",
      body: JSON.stringify({ handle }),
      ...options,
    });

    return true;
  }

  async purgeAccount(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/account/purge", {
      method: "DELETE",
      ...options,
    });

    return response.text();
  }
}
