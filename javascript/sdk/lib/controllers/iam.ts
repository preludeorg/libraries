import Client from "../client";
import type {
  CreatedUser,
  Credentials,
  Permission,
  RequestOptions,
  Users,
} from "../types";

export default class IAMController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async newAccount(
    email: string,
    options: RequestOptions = {}
  ): Promise<Credentials> {
    const response = await this.#client.request("/account", {
      method: "POST",
      body: JSON.stringify({ email }),
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

    return (await response.json()) as Users;
  }

  async createUser(
    permission: Permission,
    email: string,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth("/account/user", {
      method: "POST",
      body: JSON.stringify({ permission, email }),
      ...options,
    });

    return (await response.json()) as CreatedUser;
  }

  async deleteUser(email: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth("/account/user", {
      method: "DELETE",
      body: JSON.stringify({ email }),
      ...options,
    });

    return true;
  }

  async updateToken(token: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth("/account", {
      method: "PUT",
      body: JSON.stringify({ token }),
      ...options,
    });
  }
}
