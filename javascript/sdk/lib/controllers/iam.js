import Client from "../client";

/**
 * @class
 * @default
 * @property {Client} client
 */
export default class IAMController {
  #client;

  /**
   * @param {Client} client
   */
  constructor(client) {
    this.#client = client;
  }

  /**
   *
   * @param {import("../types").CreateAccountParams} createAccount - the createAccount object
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<import("../types").Credentials} - A Promise that resolves into account credentials
   */
  async newAccount(createAccount, options = {}) {
    const response = await this.#client.request("/iam/account", {
      method: "POST",
      body: JSON.stringify({
        handle: createAccount.email,
        user_name: createAccount.name,
        company: createAccount.company,
      }),
      ...options,
    });

    return await response.json();
  }

  /**
   * Delete an account and all things in it
   *
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   */
  async purgeAccount(options = {}) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "DELETE",
      ...options,
    });

    return response.text();
  }

  /**
   * Update properties on an account
   *
   * @param {import("../types").Mode} [mode] - Optional the updated Mode for the account
   * @param {string} [company] - Optional the updated company for the account
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {import("../types").Account} - A Promise that resolves with the Account
   */
  async updateAccount(mode, company, options = {}) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "PUT",
      body: JSON.stringify({ mode, company }),
      ...options,
    });

    return await response.json();
  }

  /**
   * Get account properties
   *
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {import("../types").Account} - A Promise that resolves with the Account
   */
  async getAccount(options = {}) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "GET",
      ...options,
    });

    return await response.json();
  }

  /**
   * Create a new user inside an account
   *
   * @param {import("../types").CreateUserParams} createUser - The createUser object
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {import("../types").CreatedUser} - A Promise that resolves with the created User
   */
  async createUser(createUser, options = {}) {
    const response = await this.#client.requestWithAuth("/iam/user", {
      method: "POST",
      body: JSON.stringify({
        permission: createUser.permission,
        handle: createUser.email,
        name: createUser.name,
        expires: createUser.expires,
      }),
      ...options,
    });

    return await response.json();
  }

  /**
   * Delete a user from an account
   *
   * @param {string} handle - The handle of the user to delete.
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<boolean>} - A Promise that resolves to true if the user is successfully deleted.
   */
  async deleteUser(handle, options = {}) {
    await this.#client.requestWithAuth("/iam/user", {
      method: "DELETE",
      body: JSON.stringify({ handle }),
      ...options,
    });

    return true;
  }

  /**
   * Get audit logs from the last X days.
   *
   * @param {number} [days=7] - The number of days for which to retrieve audit logs. Default is 7 days.
   * @param {number} [limit=1000] - The maximum number of audit logs to retrieve. Default is 1000 logs.
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<Object>} - A Promise that resolves to the retrieved audit logs as an object.
   */
  async auditLogs(days = 7, limit = 1000, options = {}) {
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
