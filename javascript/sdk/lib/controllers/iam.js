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
   * Create a new account
   *
   * @param {import("../types").CreateAccountParams} params - The parameters for creating a new account.
   * @param {string} params.email - The email for the new account.
   * @param {string} params.name - The name of the user associated with the new account.
   * @param {string} params.company - The company name for the new account.
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").Credentials>} A promise that resolves to the Credentials for the new account.
   */
  async newAccount(params, options = {}) {
    const { email, name, company } = params;

    const response = await this.#client.request("/iam/account", {
      method: "POST",
      body: JSON.stringify({
        handle: email,
        user_name: name,
        company,
      }),
      ...options,
    });

    return await response.json();
  }

  /**
   * Delete an account and all things in it
   *
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<string>} A promise that resolves to the response text from the request.
   */
  async purgeAccount(options = {}) {
    const response = await this.#client.requestWithAuth("/iam/account", {
      method: "DELETE",
      ...options,
    });

    return response.text();
  }

  /**
   * Update properties on an account.
   *
   * @param {import("../types").Mode} [mode] - The Mode for the account (optional).
   * @param {string} [company] - The company name for the account (optional).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").Account>} A promise that resolves to the updated account.
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
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
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
   * @param {import("../types").CreateUserParams} params - The parameters for creating a new user.
   * @param {import("../types").Permission} params.permission - The permission level for the new user.
   * @param {string} params.email - The email address of the new user.
   * @param {string} [params.name] - The name of the new user (optional).
   * @param {string} [params.expires] - The expiration date for the new user (optional).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").CreatedUser>} A promise that resolves to the details of the created user.
   */
  async createUser(params, options = {}) {
    const { permission, email, name, expires } = params;

    const response = await this.#client.requestWithAuth("/iam/user", {
      method: "POST",
      body: JSON.stringify({
        permission,
        handle: email,
        name,
        expires,
      }),
      ...options,
    });

    return await response.json();
  }

  /**
   * Delete a user from an account
   *
   * @param {string} handle - The handle of the user to delete.
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
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
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
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
