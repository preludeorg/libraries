type RequestInterceptor = (request: Request) => Request;

export interface ServiceConfig {
  host: string;
  /** credentials is optional since some requests can be made without them */
  credentials?: Credentials;
  /** requestInterceptor allows you to modify the request before it is sent */
  requestInterceptor?: RequestInterceptor;
}

export interface Credentials {
  account: string;
  token: string;
}

export type RequestOptions = Omit<RequestInit, "method" | "body">;

export interface Test {
  account_id: string;
  id: string;
  name: string;
  unit: string;
  techniques: string[];
  advisory: string;
}

export interface User {
  handle: string;
  permission: Permission;
  expires: string;
  name: string;
}

export interface Control {
  id: ControlCode;
  api: string;
}
export interface Account {
  account_id: string;
  whoami: string;
  controls: Control[];
  users: User[];
  mode: Mode;
  queue: Queue[];
  company: string;
}

export interface CreateAccountParams {
  email: string;
  name?: string;
  company?: string;
}

export interface CreateUserParams {
  permission: Permission;
  email: string;
  name?: string;
  expires?: string;
}

export interface CreatedUser {
  token: string;
}

export interface Queue {
  test: string;
  run_code: RunCode;
  tag: string | null;
  started: string;
}

export interface ComputeResult {
  name: string;
  steps: {
    output: string | unknown[];
    status: number;
    step: string;
    duration: string;
  }[];
}

export interface EnableTestParams {
  test: string;
  runCode: RunCode;
  tags?: string;
}

export interface DisableTestParams {
  test: string;
  tags: string;
}

export interface Probe {
  endpoint_id: string;
  edr_id: string | null;
  host: string;
  last_beacon: string;
  serial_num: string;
  tags: string[];
  created: string;
}

export interface SearchResults {
  info: {
    published: string;
    description: string;
  };
  tests: string[];
}

export type RunCode = (typeof RunCodes)[keyof typeof RunCodes];

export type Permission = (typeof Permissions)[keyof typeof Permissions];

export type Mode = (typeof Modes)[keyof typeof Modes];

export type ExitCodeName = keyof typeof ExitCodes;
export type ExitCode = (typeof ExitCodes)[ExitCodeName];

export type ActionCodeName = keyof typeof ActionCodes;
export type ActionCode = (typeof ActionCodes)[ActionCodeName];

export type ControlCodeName = keyof typeof ControlCodes;
export type ControlCode = (typeof ControlCodes)[ControlCodeName];

export type Platform =
  | "darwin-arm64"
  | "darwin-x86_64"
  | "linux-x86_64"
  | "linux-arm64"
  | "windows-x86_64"
  | "windows-arm64"
  | "unknown";

export interface Activity {
  date: string;
  endpoint_id: string;
  id: string;
  observed: 0 | 1;
  status: ExitCode;
  test: string;
  dos: Platform;
  tags: string[] | null;
  edr_id: string | null;
}

export interface TestData {
  attachments: string[];
  mappings: string[];
}

export interface TestUsage {
  count: number;
  not_relevant: number;
  failed: number;
}

export interface TestActivity {
  id: string;
  usage: TestUsage;
}

export interface AdvisoryUsage {
  count: number;
  not_relevant: number;
  failed: number;
}

export interface AdvisoryInfo {
  id: string;
  usage: AdvisoryUsage;
}

export interface Advisory {
  id: string;
  name: string;
  source: string;
  published: string;
}

export type Stats = Record<Platform, Record<`${ExitCode}`, number>>;

export type ActivityView =
  | "days"
  | "logs"
  | "insights"
  | "probes"
  | "advisories"
  | "tests"
  | "metrics";

export interface ActivityQuery {
  start: string;
  finish: string;
  tests?: string;
  result_id?: string;
  endpoints?: string;
  dos?: string;
  statuses?: string;
  tags?: string;
}

export interface DayResult {
  count: number;
  datetime: string;
  failed: number;
}

export interface Insight {
  dos: string | null;
  tag: string | null;
  test: string | null;
  volume: { error: number; protected: number; unprotected: number };
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  handle: string;
  created: string;
  events: RecommendationEvent[];
}
export interface RecommendationEvent {
  /**
   * 0 = NONE
   * 1 = APPROVE
   * 2 = DENY
   */
  decision: number;
  handle: string;
  created: string;
}
export type RuleVolume = Record<
  string,
  {
    PROTECTED?: number;
    UNPROTECTED?: number;
    ERROR?: number;
  }
>;

export interface ProbeActivity {
  dos: Platform;
  endpoint_id: string;
  state: "PROTECTED" | "UNPROTECTED" | "ERROR";
  tags: string[];
  edr_id: string | null;
}

export interface MetricsActivity {
  account_id: string;
  endpoints: number;
  tests: number;
  company: string;
  unique_tests: number;
  custom_tests: number;
}

export interface CreateRecommendation {
  title: string;
  description: string;
}

export interface DecideRecommendation {
  id: string;
  /**
   * 1 = APPROVE
   * 2 = DENY
   */
  decision: 1 | 2;
}

export interface RegisterEndpointParams {
  host: string;
  serial_num: string;
  edr_id?: string;
  tags?: string;
}

export interface UpdateEndpointParams {
  endpoint_id: string;
  host?: string;
  edr_id?: string;
  tags?: string;
}

export interface DownloadParams {
  name: string;
  dos: Platform;
}

export interface AttachPartnerParams {
  partnerCode: ControlCode;
  api: string;
  user: string;
  secret?: string;
}

export interface EndpointsParams {
  partnerCode: ControlCode;
  platform: string;
  hostname?: string;
  offset?: number;
  count?: number;
}

export interface DeployParams {
  partnerCode: ControlCode;
  hostIds: string[];
}

export type PartnerEndpoints = Record<
  string,
  {
    hostname: string;
    version: string;
    state: string;
  }
>;
