import Client from "../client";
import type {
  Account,
  CreateAccountParams,
  CreateUserParams,
  CreatedUser,
  Credentials,
  Mode,
  RequestOptions,
} from "../types";

export default class IAMController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async newAccount(
    { email, name }: CreateAccountParams,
    options: RequestOptions = {}
  ): Promise<Credentials> {
    const response = await this.#client.request("/iam/account", {
      method: "POST",
      body: JSON.stringify({ handle: email, user_name: name }),
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

  async updateAccount(mode: Mode, options: RequestOptions = {}) {
    await this.#client.requestWithAuth("/iam/account", {
      method: "PUT",
      body: JSON.stringify({ mode }),
      ...options,
    });

    return true;
  }

  async getAccount(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "GET",
      ...options,
    });

    return (await response.json()) as Account;
  }

  async createUser(
    { permission, handle, name, expires }: CreateUserParams,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth("/iam/user", {
      method: "POST",
      body: JSON.stringify({ permission, handle, name, expires }),
      ...options,
    });

    return (await response.json()) as CreatedUser;
  }

  async deleteUser(handle: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth("/iam/user", {
      method: "DELETE",
      body: JSON.stringify({ handle }),
      ...options,
    });

    return true;
  }

  async purgeAccount(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "DELETE",
      ...options,
    });

    return response.text();
  }
}
