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
    { email, name, company }: CreateAccountParams,
    options: RequestOptions = {}
  ): Promise<Credentials> {
    const response = await this.#client.request("/iam/account", {
      method: "POST",
      body: JSON.stringify({ handle: email, user_name: name, company }),
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

  /** Delete an account and all things in it */
  async purgeAccount(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "DELETE",
      ...options,
    });

    return response.text();
  }

  /** Update properties on an account */
  async updateAccount(
    mode?: Mode,
    company?: string,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "PUT",
      body: JSON.stringify({ mode, company }),
      ...options,
    });

    return (await response.json()) as Account;
  }

  /** Get account properties */
  async getAccount(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "GET",
      ...options,
    });

    return (await response.json()) as Account;
  }

  /** Create a new user inside an account */
  async createUser(
    { permission, email, name, expires }: CreateUserParams,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth("/iam/user", {
      method: "POST",
      body: JSON.stringify({ permission, handle: email, name, expires }),
      ...options,
    });

    return (await response.json()) as CreatedUser;
  }

  /** Delete a user from an account */
  async deleteUser(handle: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth("/iam/user", {
      method: "DELETE",
      body: JSON.stringify({ handle }),
      ...options,
    });

    return true;
  }

  /** Get audit logs from the last X days */
  async auditLogs(
    days: number = 7,
    limit: number = 1000,
    options: RequestOptions = {}
  ) {
    const searchParams = new URLSearchParams({
      days: days.toString(),
      limit: limit.toString(),
    });
    const response = await this.#client.requestWithAuth(
      `iam/audit?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
  }
}
