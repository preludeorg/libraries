import Client from "../client";
import {
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

  /** Get a list of endpoints from all partners */
  async endpoints(
    { partnerName, platform, hostname = "", offset = 0 }: EndpointsParams,
    options: RequestOptions = {}
  ): Promise<PartnerEndpoints> {
    const searchParams = new URLSearchParams({
      platform,
      hostname,
      offset: offset.toString(),
    });

    const response = await this.#client.requestWithAuth(
      `/partner/${partnerName}?${searchParams.toString()}`,
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
      `/partner/${partnerName}`,
      {
        method: "POST",
        body: JSON.stringify({ host_ids: hostIds }),
        ...options,
      }
    );

    return response.json();
  }
}
