import Client from "../client";
import {
  Activity,
  ActivityQuery,
  CreateRecommendation,
  DayResult,
  EnableTest,
  Insight,
  Probe,
  ProbeActivity,
  Queue,
  Recommendation,
  RegisterEndpointParams,
  RequestOptions,
  RuleInfo,
  SearchResults,
  Stats,
  Test,
} from "../types";

export default class DetectController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Register (or re-register) an endpoint to your account */
  async registerEndpoint(
    { id, tags = "" }: RegisterEndpointParams,
    options: RequestOptions = {}
  ): Promise<string> {
    const response = await this.#client.requestWithAuth("/detect/endpoint", {
      method: "POST",
      body: JSON.stringify({ id, tags }),
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
    days: number = 7,
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

  async listQueue(options: RequestOptions = {}): Promise<Queue[]> {
    const response = await this.#client.requestWithAuth("/detect/queue", {
      method: "GET",
      ...options,
    });

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
    { test, runCode, tags }: EnableTest,
    options: RequestOptions = {}
  ) {
    await this.#client.requestWithAuth(`/detect/queue/${test}`, {
      method: "POST",
      body: JSON.stringify({ code: runCode, tags }),
      ...options,
    });
  }

  /** Disable a test so endpoints will stop running it */
  async disableTest(test: string, options: RequestOptions = {}) {
    await this.#client.requestWithAuth(`/detect/queue/${test}`, {
      method: "DELETE",
      ...options,
    });
  }

  /** Search the NVD for a keyword  */
  async search(
    identifier: string,
    options: RequestOptions = {}
  ): Promise<SearchResults> {
    const searchParams = new URLSearchParams({ identifier });
    const response = await this.#client.requestWithAuth(
      `/detect/search?${searchParams.toString()}`,
      {
        method: "GET",
        ...options,
      }
    );

    return await response.json();
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
    query: ActivityQuery & { view: "rules" },
    options?: RequestOptions
  ): Promise<RuleInfo[]>;
  async describeActivity(
    query: ActivityQuery & {
      view: "days" | "logs" | "insights" | "probes" | "rules";
    },
    options: RequestOptions = {}
  ) {
    const searchParams = new URLSearchParams();
    searchParams.set("start", query.start);
    searchParams.set("finish", query.finish);
    searchParams.set("view", query.view);
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

  /** Return a list of recommendations associated to an Account */
  async getRecommendations(options: RequestOptions = {}) {
    const response = await this.#client.requestWithAuth(
      `/detect/recommendations`,
      {
        method: "GET",
        ...options,
      }
    );

    return (await response.json()) as Recommendation[];
  }

  /** Create a new security recommendation */
  async createRecommendation(
    request: CreateRecommendation,
    options: RequestOptions = {}
  ): Promise<string> {
    const response = await this.#client.requestWithAuth(
      `/detect/recommendations`,
      {
        method: "POST",
        body: JSON.stringify(request),
        ...options,
      }
    );

    return await response.text();
  }
}
