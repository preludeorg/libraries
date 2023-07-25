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
   * Register (or re-register) an endpoint to your account
   *
   * @param {import("../types").RegisterEndpointParams} registerEndpoint - The register endpoint object.
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<string>} - A Promise that resolves into the ID of the registered endpoint
   */
  async registerEndpoint(registerEndpoint, options = {}) {
    const response = await this.#client.requestWithAuth("/detect/endpoint", {
      method: "POST",
      body: JSON.stringify({
        id: `${registerEndpoint.host}:${registerEndpoint.serial_num}:${registerEndpoint.edr_id}`,
        tags: registerEndpoint.tags,
      }),
      ...options,
    });

    return response.text();
  }

  /**
   * Update an endpoint in your account
   *
   * @param {import("../types").UpdateEndpointParams} updateEndpoint
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<void>}
   */
  async updateEndpoint(updateEndpoint, options = {}) {
    await this.#client.requestWithAuth(
      `/detect/endpoint/${updateEndpoint.endpoint_id}`,
      {
        method: "POST",
        body: JSON.stringify({
          host: updateEndpoint.host,
          edr_id: updateEndpoint.edr_id,
          tags: updateEndpoint.tags,
        }),
        ...options,
      }
    );
  }

  /**
   * Delete an endpoint from your account
   *
   * @param {string} endpoint_id - The id of the endpoint to delete.
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<void>}
   */
  async deleteEndpoint(endpoint_id, options = {}) {
    await this.#client.requestWithAuth(`/detect/endpoint`, {
      method: "DELETE",
      body: JSON.stringify({ id: endpoint_id }),
      ...options,
    });
  }

  /**
   * List all endpoints on your account
   *
   * @param {number} [days=90]
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
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
   * @param {number} [year]
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
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
   * }} query - The query object.
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
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
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<import("../types").Test[]>} - A promise that resolves to an array of Test objects.
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
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<import("../types").TestData>} - A Promise that resolves to the test data.
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
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<string>}
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
   * @param {import("../types").EnableTestParams} enableTest - The enable test object.
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<void>} - A Promise that resolves when the test is enabled.
   */
  async enableTest(enableTest, options = {}) {
    await this.#client.requestWithAuth(`/detect/queue/${enableTest.test}`, {
      method: "POST",
      body: JSON.stringify({ code: enableTest.runCode, tags: enableTest.tags }),
      ...options,
    });
  }

  /**
   * Disable a test so endpoints will stop running it.
   *
   * @param {import("../types").DisableTestParams} disableTest - The disable test object.
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<void>} - A Promise that resolves when the test is disabled.
   */
  async disableTest(disableTest, options = {}) {
    const params = new URLSearchParams({ tags: disableTest.tags });
    await this.#client.requestWithAuth(
      `/detect/queue/${disableTest.test}?${params.toString()}`,
      {
        method: "DELETE",
        ...options,
      }
    );
  }

  /**
   * Pull social statistics for a specific test.
   *
   * @param {string} test - The ID or name of the test to retrieve social statistics for.
   * @param {number} [days=30] - (Optional) The number of days for which to retrieve social statistics. Default is 30 days.
   * @param {import("../types").RequestOptions} [options={}] - Optional request options.
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
