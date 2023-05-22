import Client from "../client";
import {
  Activity,
  ActivityQuery,
  Advisory,
  AdvisoryInfo,
  DayResult,
  DisableTest,
  EnableTest,
  Insight,
  Probe,
  ProbeActivity,
  RegisterEndpointParams,
  RequestOptions,
  Stats,
  Test,
  TestData,
} from "../types";

export default class DetectController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Get properties of an existing test */
  async getTest(
    testId: string,
    options: RequestOptions = {}
  ): Promise<TestData> {
    const response = await this.#client.requestWithAuth(
      `/detect/tests/${testId}`,
      {
        ...options,
      }
    );

    return await response.json();
  }

  /** Clone a test file or attachment */
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

  /** Register (or re-register) an endpoint to your account */
  async registerEndpoint(
    {
      host,
      serial_num,
      edr_id = "",
      tags = "",
      endpoint_id = "",
    }: RegisterEndpointParams,
    options: RequestOptions = {}
  ): Promise<string> {
    const params = endpoint_id
      ? { endpoint_id, tags, edr_id, host }
      : { id: `${host}:${serial_num}:${edr_id}`, tags };
    const response = await this.#client.requestWithAuth("/detect/endpoint", {
      method: "POST",
      body: JSON.stringify(params),
      ...options,
    });

    return response.text();
  }

  /** Delete an endpoint from your account */
  async deleteEndpoint(
    endpoint_id: string,
    options: RequestOptions = {}
  ): Promise<void> {
    await this.#client.requestWithAuth(`/detect/endpoint`, {
      method: "DELETE",
      body: JSON.stringify({ id: endpoint_id }),
      ...options,
    });
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
    year?: number
  ): Promise<Advisory[]> {
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

  /** Get logs for an Account */
  async describeActivity(
    query: ActivityQuery & { view: "logs" },
    options?: RequestOptions
  ): Promise<Activity[]>;
  /** Get daily activity for an Account */
  async describeActivity(
    query: ActivityQuery & { view: "days" },
    options?: RequestOptions
  ): Promise<DayResult[]>;
  async describeActivity(
    query: ActivityQuery & { view: "insights" },
    options?: RequestOptions
  ): Promise<Insight[]>;
  async describeActivity(
    query: ActivityQuery & { view: "probes" },
    options?: RequestOptions
  ): Promise<ProbeActivity[]>;
  async describeActivity(
    query: ActivityQuery & { view: "advisories" },
    options?: RequestOptions
  ): Promise<AdvisoryInfo[]>;
  async describeActivity(
    query: ActivityQuery & {
      view: "days" | "logs" | "insights" | "probes" | "advisories";
    },
    options: RequestOptions = {}
  ) {
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

  /** List all tests available to an account */
  async listTests(options: RequestOptions = {}): Promise<Test[]> {
    const response = await this.#client.requestWithAuth("/detect/tests", {
      method: "GET",
      ...options,
    });

    return await response.json();
  }

  /** Enable a test so endpoints will start running it */
  async enableTest(
    { test, runCode, tags = "" }: EnableTest,
    options: RequestOptions = {}
  ) {
    await this.#client.requestWithAuth(`/detect/queue/${test}`, {
      method: "POST",
      body: JSON.stringify({ code: runCode, tags }),
      ...options,
    });
  }

  /** Disable a test so endpoints will stop running it */
  async disableTest({ test, tags }: DisableTest, options: RequestOptions = {}) {
    const params = new URLSearchParams({ tags });
    await this.#client.requestWithAuth(
      `/detect/queue/${test}?${params.toString()}`,
      {
        method: "DELETE",
        ...options,
      }
    );
  }

  /** Pull social statistics for a specific test */
  async socialStats(
    test: string,
    days: number = 30,
    options: RequestOptions = {}
  ): Promise<Stats> {
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
