// @ts-check
import Client from "../client";

/**
 * @class
 * @default
 * @property {Client} client
 */
export default class DetectController {
  #client;

  /**
   * @constructor
   * @param {Client} client
   */
  constructor(client) {
    this.#client = client;
  }

  /**
   * Register (or re-register) an endpoint to your account.
   *
   * @param {import("../types").RegisterEndpointParams} params - The parameters for registering an endpoint (host, serial_num, edr_id, tags).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<string>} - A Promise that resolves into the ID of the registered endpoint
   */
  async registerEndpoint(params, options = {}) {
    const { host, serial_num, edr_id = "", tags } = params;

    const response = await this.#client.requestWithAuth("/detect/endpoint", {
      method: "POST",
      body: JSON.stringify({
        id: `${host}:${serial_num}:${edr_id}`,
        tags,
      }),
      ...options,
    });

    return response.text();
  }

  /**
   * Update an endpoint in your account
   *
   * @param {import("../types").UpdateEndpointParams} params - The parameters for updating an endpoint (endpoint_id, host, edr_id, tags).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").UpdatedEndpoint>} - A Promise that resolves to the updated endpoint.
   */
  async updateEndpoint(params, options = {}) {
    const { endpoint_id, host, edr_id, tags } = params;

    const response = await this.#client.requestWithAuth(
      `/detect/endpoint/${endpoint_id}`,
      {
        method: "POST",
        body: JSON.stringify({
          host,
          edr_id,
          tags,
        }),
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Delete an endpoint from your account
   *
   * @param {string} endpoint_id - The id of the endpoint to delete.
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").StatusResponse>} - A Promise that resolves into a {status: True}.
   */
  async deleteEndpoint(endpoint_id, options = {}) {
    const response = await this.#client.requestWithAuth(`/detect/endpoint`, {
      method: "DELETE",
      body: JSON.stringify({ id: endpoint_id }),
      ...options,
    });

    return await response.json();
  }

  /**
   * List all endpoints on your account
   *
   * @param {number} [days=90] - The number of days from the current date to pull data from (optional).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").Probe[]>}
   */
  async listEndpoints(days = 90, options = {}) {
    const searchParams = new URLSearchParams({ days: days.toString() });
    const response = await this.#client.requestWithAuth(
      `/detect/endpoint?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * List advisories
   *
   * @param {number} [year] - The year to filter advisories (optional).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").Advisory[]>}
   */
  async listAdvisories(year, options = {}) {
    const searchParams = new URLSearchParams();
    if (year) {
      searchParams.set("year", year.toString());
    }

    const response = await this.#client.requestWithAuth(
      `/detect/advisories?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Get activity for an Account
   *
   * @param {import("../types").ActivityQuery & {
   *   view: import("../types").ActivityView;
   * }} query - The filter query (start, finish, tests, result_id, endpoints, dos, statuses, tags, and view).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<[]>} - A Promise that resolves to the activity.
   */
  async describeActivity(query, options = {}) {
    const searchParams = new URLSearchParams();
    searchParams.set("view", query.view);
    searchParams.set("start", query.start);
    searchParams.set("finish", query.finish);
    if (query.tests) searchParams.set("tests", query.tests);
    if (query.tags) searchParams.set("tags", query.tags);
    if (query.endpoints) searchParams.set("endpoints", query.endpoints);
    if (query.result_id) searchParams.set("result_id", query.result_id);
    if (query.dos) searchParams.set("dos", query.dos);

    const response = await this.#client.requestWithAuth(
      `/detect/activity?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * List all tests available to an account.
   *
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").Test[]>} - A promise that resolves to an array of Tests.
   */
  async listTests(options = {}) {
    const response = await this.#client.requestWithAuth("/detect/tests", {
      method: "GET",
      ...options,
    });

    return await response.json();
  }

  /**
   * Get properties of an existing test.
   *
   * @param {string} testId - The ID of the test to retrieve properties for.
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").AttachedTest>} - A Promise that resolves to the test.
   */
  async getTest(testId, options = {}) {
    const response = await this.#client.requestWithAuth(
      `/detect/tests/${testId}`,
      {
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Clone a test file or attachment.
   *
   * @param {string} testId - The ID of the test.
   * @param {string} filename - The name of the file or attachment to download.
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<string>} - A Promise that resolves to a URL location to download the test file or attachment.
   */
  async download(testId, filename, options = {}) {
    const response = await this.#client.requestWithAuth(
      `/detect/tests/${testId}/${filename}`,
      {
        ...options,
        headers: {
          "Content-Type": "",
          ...(options.headers ?? {}),
        },
      }
    );

    return response.text();
  }

  /**
   * Enable a test so endpoints will start running it.
   *
   * @param {import("../types").EnableTestParams} params - The parameters for enabling a test (test, runCode, tags).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").EnabledTest>} - A Promise that to the enabled test.
   */
  async enableTest(params, options = {}) {
    const { test, runCode, tags } = params;

    const response = await this.#client.requestWithAuth(
      `/detect/queue/${test}`,
      {
        method: "POST",
        body: JSON.stringify({ code: runCode, tags }),
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Disable a test so endpoints will stop running it.
   *
   * @param {import("../types").DisableTestParams} params - The parameters for disabling a test (tags, test).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").StatusResponse>} - A Promise that resolves into a {status: True}.
   */
  async disableTest(params, options = {}) {
    const { tags, test } = params;
    const searchParams = new URLSearchParams({ tags });

    const response = await this.#client.requestWithAuth(
      `/detect/queue/${test}?${searchParams.toString()}`,
      {
        method: "DELETE",
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Pull social statistics for a specific test.
   *
   * @param {string} test - The ID or name of the test to retrieve social statistics for.
   * @param {number} [days=30] - The number of days for which to retrieve social statistics. Default is 30 days (optional).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").Stats>} - A Promise that resolves to the social statistics for the test.
   */
  async socialStats(test, days = 30, options = {}) {
    const searchParams = new URLSearchParams({ days: days.toString() });
    const response = await this.#client.requestWithAuth(
      `/detect/${test}/social?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
  }
}
