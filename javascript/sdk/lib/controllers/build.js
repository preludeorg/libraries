// @ts-check
import Client from "../client";

/**
 * @class
 * @default
 * @property {Client} client
 */
export default class BuildController {
  #client;

  /**
   * @constructor
   * @param {Client} client
   */
  constructor(client) {
    this.#client = client;
  }

  /**
   * Create or update a test
   *
   * @param {import("../types").CreateTestParams} params - The parameters for creating a test (name, unit, techniques, advisory, testId).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").Test>} A promise that resolves to the created test.
   */
  async createTest(params, options = {}) {
    const { name, unit, techniques, advisory, testId } = params;

    const response = await this.#client.requestWithAuth(`/build/tests`, {
      method: "POST",
      body: JSON.stringify({ name, unit, techniques, advisory, id: testId }),
      ...options,
    });

    return await response.json();
  }

  /**
   * Update a test
   *
   * @param {import("../types").UpdateTestParams} params - The parameters for updating a test (name, unit, techniques, advisory, testId).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").Test>} A promise that resolves to the updated test.
   */
  async updateTest(params, options = {}) {
    const { testId, name, unit, techniques, advisory } = params;

    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        method: "POST",
        body: JSON.stringify({ name, unit, techniques, advisory }),
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Delete an existing test
   *
   * @param {string} testId - The UUID of the test to delete.
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<void>}
   */
  async deleteTest(testId, options = {}) {
    await this.#client.requestWithAuth(`/build/tests/${testId}`, {
      method: "DELETE",
      ...options,
    });
  }

  /**
   * Upload a test or attachment
   *
   * @param {string} testId - The UUID of the test to upload the attachment to.
   * @param {string} filename - The filename of the attachment.
   * @param {BodyInit} data - The data of the attachment.
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<void>}
   */
  async upload(testId, filename, data, options = {}) {
    await this.#client.requestWithAuth(`/build/tests/${testId}/${filename}`, {
      method: "POST",
      body: data,
      ...options,
    });
  }
}
