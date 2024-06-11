import Client from "../client";
import type {
  AttachedTest,
  CompiledResponse,
  ControlCode,
  CreateDetectionRule,
  CreateTestProps,
  CreateThreatProps,
  RequestOptions,
  StatusResponse,
  Threat,
  ThreatHunt,
  UpdateThreatProps,
  UploadProps,
  UploadedAttachment,
} from "../types";

export default class BuildController {
  #client: Client;

  constructor(client: Client) {
    this.#client = client;
  }

  /** Create or update a test */
  async createTest(
    { name, unit, technique, testId, ai_generated = false }: CreateTestProps,
    options: RequestOptions = {},
  ): Promise<AttachedTest> {
    const response = await this.#client.requestWithAuth(`/build/tests`, {
      method: "POST",
      body: JSON.stringify({
        name,
        unit,
        technique,
        id: testId,
        ai_generated,
      }),
      ...options,
    });

    return (await response.json()) as AttachedTest;
  }

  /** Update a test */
  async updateTest(
    testId: string,
    name?: string,
    unit?: string,
    technique?: string,
    options: RequestOptions = {},
  ): Promise<AttachedTest> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}`,
      {
        method: "POST",
        body: JSON.stringify({ name, unit, technique }),
        ...options,
      },
    );

    return (await response.json()) as AttachedTest;
  }

  /** Delete an existing test */
  async deleteTest(
    { test_id, purge = false }: { test_id: string; purge?: boolean },
    options: RequestOptions = {},
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(
      `/build/tests/${test_id}`,
      {
        method: "DELETE",
        body: JSON.stringify({ purge }),
        ...options,
      },
    );

    return (await response.json()) as StatusResponse;
  }

  /** Create a threat */
  async createThreat(
    {
      name,
      published,
      id,
      source_id,
      source,
      tests,
      ai_generated = false,
    }: CreateThreatProps,
    options: RequestOptions = {},
  ): Promise<Threat> {
    const response = await this.#client.requestWithAuth(`/build/threats`, {
      method: "POST",
      body: JSON.stringify({
        name,
        published,
        id,
        source_id,
        source,
        tests,
        ai_generated,
      }),
      ...options,
    });

    return (await response.json()) as Threat;
  }

  /** Update a threat */
  async updateThreat(
    {
      threat_id,
      name,
      source_id,
      source,
      published,
      tests,
      ai_generated = false,
    }: UpdateThreatProps,
    options: RequestOptions = {},
  ): Promise<Threat> {
    const response = await this.#client.requestWithAuth(
      `/build/threats/${threat_id}`,
      {
        method: "POST",
        body: JSON.stringify({
          name,
          threat_id,
          source_id,
          source,
          published,
          tests,
          ai_generated,
        }),
        ...options,
      },
    );

    return (await response.json()) as Threat;
  }

  /** Delete an existing threat */
  async deleteThreat(
    { threat_id, purge = false }: { threat_id: string; purge?: boolean },
    options: RequestOptions = {},
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(
      `/build/threats/${threat_id}`,
      {
        method: "DELETE",
        body: JSON.stringify({ purge }),
        ...options,
      },
    );

    return (await response.json()) as StatusResponse;
  }

  /** Upload a test or attachment */
  async upload(
    { testId, filename, data, ai_generated = false }: UploadProps,
    options: RequestOptions = {},
  ): Promise<UploadedAttachment> {
    if (data.toString().length > 1000000) {
      throw new Error(`File size must be under 1MB (${filename})`);
    }

    const headers = {
      "Content-Type": "application/octet-stream",
      ...options.headers,
    };

    const searchParams = new URLSearchParams();
    if (ai_generated) {
      searchParams.set("ai_generated", "true");
    }

    const response = await this.#client.requestWithAuth(
      `/build/tests/${testId}/${filename}?${searchParams}`,
      {
        method: "POST",
        body: data,
        headers,
        ...options,
      },
    );

    return (await response.json()) as UploadedAttachment;
  }

  /** Create a detection */
  async createDetection(
    { rule, ruleId, testId, detectionId }: CreateDetectionRule,
    options: RequestOptions = {},
  ) {
    const response = await this.#client.requestWithAuth(`/build/detections`, {
      method: "POST",
      body: JSON.stringify({
        rule,
        test_id: testId,
        detection_id: detectionId,
        rule_id: ruleId,
      }),
      ...options,
    });

    return (await response.json()) as StatusResponse;
  }

  /** Update a detection */
  async updateDetection(
    {
      detectionId,
      rule,
      testId,
    }: { detectionId: string; rule: string; testId?: string },
    options: RequestOptions = {},
  ) {
    const response = await this.#client.requestWithAuth(
      `/build/detections/${detectionId}`,
      {
        method: "POST",
        body: JSON.stringify({ rule, test_id: testId }),
        ...options,
      },
    );

    return (await response.json()) as StatusResponse;
  }

  /** Delete an existing detection */
  async deleteDetection(
    detectionId: string,
    options: RequestOptions = {},
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(
      `/build/detections/${detectionId}`,
      {
        method: "DELETE",
        ...options,
      },
    );

    return (await response.json()) as StatusResponse;
  }

  /** Compile code (returns jobId) */
  async compile(
    code: string,
    filename?: string,
    options: RequestOptions = {},
  ): Promise<{ job_id: string }> {
    const response = await this.#client.requestWithAuth(`/build/compile`, {
      method: "POST",
      body: JSON.stringify({ code, filename }),
      ...options,
    });

    return (await response.json()) as { job_id: string };
  }

  /** Get compile process */
  async getCompile(
    id: string,
    options: RequestOptions = {},
  ): Promise<CompiledResponse> {
    const response = await this.#client.requestWithAuth(
      `/build/compile/${id}`,
      {
        method: "GET",
        ...options,
      },
    );

    return (await response.json()) as CompiledResponse;
  }

  /** Create a threat hunt query */
  async createThreatHunt(
    {
      control,
      name,
      query,
      test_id,
      threat_hunt_id,
    }: {
      control: ControlCode;
      name: string;
      query: string;
      test_id: string;
      threat_hunt_id?: string;
    },
    options: RequestOptions = {},
  ): Promise<ThreatHunt> {
    const response = await this.#client.requestWithAuth(`/build/threat_hunts`, {
      method: "POST",
      body: JSON.stringify({
        control,
        name,
        query,
        test_id,
        threat_hunt_id,
      }),
      ...options,
    });

    return (await response.json()) as ThreatHunt;
  }

  /** Update a threat hunt query */
  async updateThreatHunt(
    {
      threat_hunt_id,
      name,
      query,
      test_id,
    }: {
      threat_hunt_id: string;
      name?: string;
      query?: string;
      test_id?: string;
    },
    options: RequestOptions = {},
  ): Promise<ThreatHunt> {
    const response = await this.#client.requestWithAuth(
      `/build/threat_hunts/${threat_hunt_id}`,
      {
        method: "POST",
        body: JSON.stringify({ name, query, test_id }),
        ...options,
      },
    );

    return (await response.json()) as ThreatHunt;
  }

  /** Delete an existing threat hunt query */
  async deleteThreatHunt(
    threat_hunt_id: string,
    options: RequestOptions = {},
  ): Promise<StatusResponse> {
    const response = await this.#client.requestWithAuth(
      `/build/threat_hunts/${threat_hunt_id}`,
      {
        method: "DELETE",
        ...options,
      },
    );

    return (await response.json()) as StatusResponse;
  }
}
