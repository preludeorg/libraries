import Client from "./client.js";
import { RequestOptions, Test } from "../types.js";

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
   * @param {string} name - The name of the test.
   * @param {string} unit - The unit of the test.
   * @param {string} [techniques] - Optional techniques for the test (TXXXX.XX format).
   * @param {string} [advisory] - Optional advisory for the test.
   * @param {string} [testId] - Optional UUID of the test.
   * @param {RequestOptions} [options={}] - Optional request options.
   * @returns {Promise<Test>} A promise that resolves to the created test.
   */
  async createTest(name, unit, techniques, advisory, testId, options) {
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
   * @param {string} testId - The UUID of the test to update
   * @param {string} [name] - Optional updated name of the test
   * @param {string} [unit] - Optional updated unit of the test
   * @param {string} [techniques] - Optional updated techniques used in the test
   * @param {string} [advisory] - Optional updated advisory for the test
   * @param {RequestOptions} [options={}] - The request options
   * @returns {Promise<Test>} A promise that resolves to the updated test
   */
  async updateTest(testId, name, unit, techniques, advisory, options) {
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
   * @param {string} testId - The UUID of the test to delete
   * @param {RequestOptions} [options={}] - Optional request options
   * @returns {Promise<void>}
   */
  async deleteTest(testId, options) {
    await this.#client.requestWithAuth(`/build/tests/${testId}`, {
      method: "DELETE",
      ...options,
    });
  }

  /**
   * Upload a test or attachment
   *
   * @param {string} testId - The UUID of the test to upload the attachment to
   * @param {string} filename - The filename of the attachment
   * @param {BodyInit} data - The data of the attachment
   * @param {RequestOptions} [options={}] - Optional request options
   * @returns {Promise<void>}
   */
  async upload(testId, filename, data, options) {
    await this.#client.requestWithAuth(`/build/tests/${testId}/${filename}`, {
      method: "POST",
      body: data,
      ...options,
    });
  }
}
