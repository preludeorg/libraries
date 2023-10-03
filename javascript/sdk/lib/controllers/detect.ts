import Client from "../client";
import {
  Activity,
  ActivityQuery,
  AdvisoriesActivity,
  Advisory,
  AttachedTest,
  DayActivity,
  DisableTest,
  EnableTest,
  EnabledTest,
  EndpointActivity,
  Insight,
  MetricsActivity,
  FindingsActivity,
  Probe,
  ProbeActivity,
  RegisterEndpointParams,
  RequestOptions,
  StatusResponse,
  Test,
  TestsActivity,
  UpdateEndpointParams,
  UpdatedEndpoint,
} from "../types";

export default class DetectController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Register (or re-register) an endpoint to your account */
  async registerEndpoint(
    { host, serial_num, tags }: RegisterEndpointParams,
    options: RequestOptions = {}
  ): Promise<string> {
    const response = await this.#client.requestWithAuth("/detect/endpoint", {
      method: "POST",
      body: JSON.stringify({
        id: `${host}:${serial_num}`,
        tags,
      }),
      ...options,
    });

    return response.text();
  }

  /** Update an endpoint in your account */
  async updateEndpoint(
    { endpoint_id, tags }: UpdateEndpointParams,
    options: RequestOptions = {}
  ): Promise<UpdatedEndpoint> {
    const response = await this.#client.requestWithAuth(
      `/detect/endpoint/${endpoint_id}`,
      {
        method: "POST",
        body: JSON.stringify({
          tags,
        }),
        ...options,
      }
    );

    return (await response.json()) as UpdatedEndpoint;
  }

  /** Delete an endpoint from your account */
  async deleteEndpoint(
    endpoint_id: string,
    options: RequestOptions = {}
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(`/detect/endpoint`, {
      method: "DELETE",
      body: JSON.stringify({ id: endpoint_id }),
      ...options,
    });

    return (await response.json()) as StatusResponse;
  }

  /** List all endpoints on your account */
  async listEndpoints(
    days: number = 90,
    options: RequestOptions = {}
  ): Promise<Probe[]> {
    const searchParams = new URLSearchParams({ days: days.toString() });
    const response = await this.#client.requestWithAuth(
      `/detect/endpoint?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return (await response.json()) as Probe[];
  }

  /** List advisories */
  async listAdvisories(
    options: RequestOptions = {},
  ): Promise<Advisory[]> {
    const searchParams = new URLSearchParams();
    const response = await this.#client.requestWithAuth(
      `/detect/advisories?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );
    return (await response.json()) as Advisory[];
  }

  /** Get logs for an Account */
  async describeActivity(
    query: ActivityQuery & { view: "logs" },
    options?: RequestOptions
  ): Promise<Activity[]>;
  /** Get daily activity for an Account */
  async describeActivity(
    query: ActivityQuery & { view: "days" },
    options?: RequestOptions
  ): Promise<DayActivity[]>;
  async describeActivity(
    query: ActivityQuery & { view: "insights" },
    options?: RequestOptions
  ): Promise<Insight[]>;
  async describeActivity(
    query: ActivityQuery & { view: "probes" },
    options?: RequestOptions
  ): Promise<ProbeActivity[]>;
  async describeActivity(
    query: ActivityQuery & { view: "endpoints" },
    options?: RequestOptions
  ): Promise<EndpointActivity>;
  async describeActivity(
    query: ActivityQuery & { view: "metrics" },
    options?: RequestOptions
  ): Promise<MetricsActivity[]>;
  async describeActivity(
    query: ActivityQuery & { view: "advisories" },
    options?: RequestOptions
  ): Promise<AdvisoriesActivity[]>;
  async describeActivity(
    query: ActivityQuery & { view: "tests" },
    options?: RequestOptions
  ): Promise<TestsActivity[]>;
  async describeActivity(
    query: ActivityQuery & { view: "findings" },
    options?: RequestOptions
  ): Promise<FindingsActivity[]>;
  async describeActivity(
    query: ActivityQuery & { view: "protected" },
    options?: RequestOptions
  ): Promise<number>;
  async describeActivity(
    query: ActivityQuery & {
      view:
        | "days"
        | "logs"
        | "insights"
        | "probes"
        | "endpoints"
        | "metrics"
        | "advisories"
        | "tests"
        | "findings"
        | "protected";
    },
    options: RequestOptions = {}
  ) {
    const searchParams = new URLSearchParams();
    searchParams.set("view", query.view);
    searchParams.set("start", query.start);
    searchParams.set("finish", query.finish);
    if (query.tests) searchParams.set("tests", query.tests);
    if (query.endpoints) searchParams.set("endpoints", query.endpoints);
    if (query.dos) searchParams.set("dos", query.dos);
    if (query.statuses) searchParams.set("statuses", query.statuses);
    if (query.control) searchParams.set("control", query.control);
    if (query.impersonate) searchParams.set("impersonate", query.impersonate);
    if (query.os) searchParams.set("os", query.os);
    if (query.policy) searchParams.set("policy", query.policy);

    const response = await this.#client.requestWithAuth(
      `/detect/activity?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
  }

  /** List all tests available to an account */
  async listTests(options: RequestOptions = {}): Promise<Test[]> {
    const response = await this.#client.requestWithAuth("/detect/tests", {
      method: "GET",
      ...options,
    });

    return await response.json();
  }

  /** Get properties of an existing test */
  async getTest(
    testId: string,
    options: RequestOptions = {}
  ): Promise<AttachedTest> {
    const response = await this.#client.requestWithAuth(
      `/detect/tests/${testId}`,
      {
        ...options,
      }
    );

    return (await response.json()) as AttachedTest;
  }

  /**
   * Clone a test file or attachment
   *
   * @returns {string} - A URL location to download the test file or attachment
   */
  async download(
    testId: string,
    filename: string,
    options: RequestOptions = {}
  ): Promise<string> {
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

  /** Enable a test so endpoints will start running it */
  async enableTest(
    { test, runCode, tags = "" }: EnableTest,
    options: RequestOptions = {}
  ): Promise<EnabledTest> {
    const response = await this.#client.requestWithAuth(
      `/detect/queue/${test}`,
      {
        method: "POST",
        body: JSON.stringify({ code: runCode, tags }),
        ...options,
      }
    );

    return (await response.json()) as EnabledTest;
  }

  /** Disable a test so endpoints will stop running it */
  async disableTest(
    { test, tags }: DisableTest,
    options: RequestOptions = {}
  ): Promise<StatusResponse> {
    const params = new URLSearchParams({ tags });
    const response = await this.#client.requestWithAuth(
      `/detect/queue/${test}?${params.toString()}`,
      {
        method: "DELETE",
        ...options,
      }
    );

    return (await response.json()) as StatusResponse;
  }
}
