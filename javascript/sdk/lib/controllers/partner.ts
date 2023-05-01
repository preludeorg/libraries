import Client from "../client";
import {
  AttachPartnerParams,
  DeployParams,
  DeployedEnpoint,
  EndpointsParams,
  PartnerEndpoints,
  RequestOptions,
} from "../types";

export default class PartnerController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async attachPartner(
    { name, api, user, secret = "" }: AttachPartnerParams,
    options: RequestOptions = {}
  ) {
    const response = await this.#client.requestWithAuth(
      `/partner/${name}`,
      {
        method: "POST",
        body: JSON.stringify({ api, user, secret }),
        ...options,
      }
    );

    return response.text();
  }

  async detachPartner(name: string, options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
      `/partner/${name}`,
      {
        method: "DELETE",
        ...options,
      }
    );

    return response.text();
  }

  /** Get a list of endpoints from all partners */
  async endpoints(
    {
      partnerName,
      platform,
      hostname = "",
      offset = 0,
      count = 100,
    }: EndpointsParams,
    options: RequestOptions = {}
  ): Promise<PartnerEndpoints> {
    const searchParams = new URLSearchParams({
      platform,
      hostname,
      offset: offset.toString(),
      count: count.toString(),
    });

    const response = await this.#client.requestWithAuth(
      `/partner/endpoints/${partnerName}?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return response.json();
  }

  /** Deploy probes on all specified partner endpoints */
  async deploy(
    { partnerName, hostIds }: DeployParams,
    options: RequestOptions = {}
  ): Promise<DeployedEnpoint[]> {
    const response = await this.#client.requestWithAuth(
      `/partner/deploy/${partnerName}`,
      {
        method: "POST",
        body: JSON.stringify({ host_ids: hostIds }),
        ...options,
      }
    );

    return response.json();
  }
}
