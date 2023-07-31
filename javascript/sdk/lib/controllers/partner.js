//@ts-check
import Client from "../client";

/**
 * @class
 * @default
 * @param {Client} client
 */
export default class PartnerController {
  #client;

  /**
   * @param {Client} client
   */
  constructor(client) {
    this.#client = client;
  }

  /**
   * Attaches a partner to an account.
   *
   * @param {import("../types").AttachPartnerParams} params - The parameters for attaching a partner (partnerCode, api, user, secret).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").AttachedPartner>} A promise that resolves to the attached partner.
   */
  async attachPartner(params, options = {}) {
    const { partnerCode, api, user, secret = "" } = params;

    const response = await this.#client.requestWithAuth(
      `/partner/${partnerCode}`,
      {
        method: "POST",
        body: JSON.stringify({ api, user, secret }),
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Detaches a partner from an account
   *
   * @param {import("../types").ControlCode} partnerCode - The partner code, with options: INVALID (0), CROWDSTRIKE (1), DEFENDER (2), SPLUNK (3).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").StatusResponse>} - A Promise that resolves into a {status: True}.
   */
  async detachPartner(partnerCode, options = {}) {
    const response = await this.#client.requestWithAuth(
      `/partner/${partnerCode}`,
      {
        method: "DELETE",
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Get a list of endpoints from all partners.
   *
   * @param {import("../types").EndpointsParams} params - The parameters for fetching endpoints (partnerCode, platform, hostname, offset, count).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").PartnerEndpoints>} A promise that resolves to the list of endpoints from partners.
   */
  async endpoints(params, options = {}) {
    const {
      partnerCode,
      platform,
      hostname = "",
      offset = 0,
      count = 100,
    } = params;

    const searchParams = new URLSearchParams({
      platform,
      hostname,
      offset: offset.toString(),
      count: count.toString(),
    });

    const response = await this.#client.requestWithAuth(
      `/partner/endpoints/${partnerCode}?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
  }

  /**
   * Deploy probes on all specified partner endpoints.
   *
   * @param {import("../types").DeployParams} params - The parameters for deploying probes (partnerCode, hostIds).
   * @param {import("../types").RequestOptions} [options={}] - Additional request options (optional).
   * @returns {Promise<import("../types").DeployedEndpoints>} A promise that resolves to a list of deployed endpoints.
   */
  async deploy(params, options = {}) {
    const { partnerCode, hostIds } = params;

    const response = await this.#client.requestWithAuth(
      `/partner/deploy/${partnerCode}`,
      {
        method: "POST",
        body: JSON.stringify({ host_ids: hostIds }),
        ...options,
      }
    );

    return await response.json();
  }
}
