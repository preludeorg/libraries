import Client from "../client";
import {
  AttachPartnerParams,
  AttachedPartner,
  BlockResponse,
  ControlCode,
  ControlCodeName,
  DeployParams,
  DeployedEndpoints,
  EndpointsParams,
  PartnerEndpoints,
  RequestOptions,
  StatusResponse,
} from "../types";

export default class PartnerController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  async attachPartner(
    { partnerCode, api, user, secret = "" }: AttachPartnerParams,
    options: RequestOptions = {}
  ): Promise<AttachedPartner> {
    const response = await this.#client.requestWithAuth(
      `/partner/${partnerCode}`,
      {
        method: "POST",
        body: JSON.stringify({ api, user, secret }),
        ...options,
      }
    );

    return (await response.json()) as AttachedPartner;
  }

  async block(
    partnerCode: ControlCode,
    test_id: string,
    options: RequestOptions = {}
  ): Promise<BlockResponse[]> {
    const response = await this.#client.requestWithAuth(
      `/partner/block/${partnerCode}`,
      {
        method: "POST",
        body: JSON.stringify({ test_id }),
        ...options,
      }
    );

    return (await response.json()) as BlockResponse[];
  }

  async detachPartner(
    partner: ControlCodeName,
    options: RequestOptions = {}
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(`/partner/${partner}`, {
      method: "DELETE",
      ...options,
    });

    return (await response.json()) as StatusResponse;
  }

  /** Get a list of endpoints from all partners */
  async endpoints(
    {
      partner,
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
      `/partner/endpoints/${partner}?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return response.json();
  }

  /** Deploy probes on all specified partner endpoints */
  async deploy(
    { partnerCode, hostIds }: DeployParams,
    options: RequestOptions = {}
  ): Promise<DeployedEndpoints> {
    const response = await this.#client.requestWithAuth(
      `/partner/deploy/${partnerCode}`,
      {
        method: "POST",
        body: JSON.stringify({ host_ids: hostIds }),
        ...options,
      }
    );

    return (await response.json()) as DeployedEndpoints;
  }

  /** Generate webhook authenication information for specified partner */
  async webhookGenerate(
    partnerCode: ControlCode,
    options: RequestOptions = {}
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(
      `/partner/suppress/${partnerCode}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
  }
}
