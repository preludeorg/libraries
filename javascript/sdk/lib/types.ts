export interface ServiceConfig {
  host: string;
  /** credentials is optional since some requests can be made without them */
  credentials?: Credentials;
  /** requestInterceptor allows you to modify the request before it is sent */
  requestInterceptor?: (request: Request) => Request;
  /** responseInterceptor allows you to modify the response before it is returned */
  responseInterceptor?: (request: Request, response: Response) => Response;
}

export interface Credentials {
  account: string;
  token: string;
}

export type RequestOptions = Omit<RequestInit, "method" | "body">;

export interface StatusResponse {
  status: true;
}

export interface CreateThreatProps {
  name: string;
  published: string;
  id?: string;
  source_id?: string;
  source?: string;
  tests?: string;
  ai_generated?: boolean;
}

export interface UpdateThreatProps {
  threat_id: string;
  name?: string;
  source_id?: string;
  source?: string;
  published?: string;
  tests?: string;
  ai_generated?: boolean;
}

export interface Threat {
  author: string | null;
  account_id: string;
  id: string;
  source_id: string | null;
  name: string;
  source: string | null;
  published: string | null;
  tests: string[];
  tombstoned: string | null;
  created: string;
}

export interface CreateTestProps {
  ai_generated?: boolean;
  intel_context?: string;
  name: string;
  technique?: string;
  testId?: string;
  unit: string;
}

export interface UpdateTestProps {
  intel_context?: string;
  name?: string,
  technique?: string,
  testId: string,
  unit?: string,
}

export interface Test {
  author: string | null;
  account_id: string;
  created: string;
  id: string;
  intel_context: string | null;
  name: string;
  technique: string | null;
  tombstoned: string | null;
  unit: string;
}

export type AttachedTest = Test & {
  attachments: string[];
};

export interface UploadProps {
  testId: string;
  filename: string;
  data: BodyInit;
  ai_generated?: boolean;
}

export interface UploadedAttachment {
  id: string;
  filename: string;
}

export interface Terms {
  threat_intel?: Record<string, string>;
}

export interface User {
  handle: string;
  permission: Permission;
  expires: string;
  name: string;
  oidc: boolean;
  subscriptions: string[];
  terms: Terms;
}

export interface Control {
  id: ControlCode;
  api: string;
}

export interface Account {
  account_id: string;
  whoami: string;
  users: User[];
  queue: Queue[];
  controls: Control[];
  mode: Mode;
  slug: string;
  company: string;
  probe_sleep: string;
  oidc?: OIDCSettings;
  features: {
    oidc: boolean;
    threat_intel: boolean;
    detections: boolean;
  };
}

export interface OIDCSettings {
  client_id: string;
  created: string;
  domain: string;
  issuer: OIDC;
  oidc_config_url: string;
}

export type ThreatIntel =
  | ThreatIntelComplete
  | ThreatIntelFailed
  | ThreatIntelRunning;

export type ThreatIntelRunning = ThreatIntelParsing | ThreatIntelGenerating;

export interface ThreatIntelParsing {
  status: "RUNNING";
  step: "PARSE";
}

export interface ThreatIntelGenerating {
  status: "RUNNING";
  step: "GENERATE";
  num_tasks: number;
  completed_tasks: number;
}

export interface ThreatIntelFailed {
  status: "FAILED";
  reason: "FAILED" | "TIMED_OUT" | "ABORTED";
}
export interface ThreatIntelComplete {
  status: "COMPLETE";
  output: ThreatIntelOutput[];
  title: string | null;
}

export interface ThreatIntelOutput {
  status: "SUCCEEDED" | "FAILED" | "SKIPPED";
  name: string;
  technique: string;
  ai_generated: AiGeneratedOutput | null;
  existing_test: ExistingTestOutput | null;
  excluded: ExcludedOutput | null;
}

export interface ExcludedOutput {
  classification: "EXCLUDED" | "TOO MANY TECHNIQUES";
}

export interface AiGeneratedOutput {
  go_code: string;
  sigma_rules: string[];
  intel_context: string;
  threat_hunt_queries: ThreatHuntQueries[];
}

export interface ExistingTestOutput {
  go_code: string;
  sigma_rules: string[];
  test_id: string;
  test_name: string;
  threat_hunt_queries: ThreatHuntQueries[];
}

export interface ThreatHuntQueries {
  name: string;
  query: string;
  control: ControlCode;
}

export interface VerifiedUser {
  account_id: string;
  token: string;
  handle: string;
  permission: Permission;
  expires: string;
  name: string;
}

export interface CreateAccountParams {
  email: string;
  name?: string;
  company?: string;
  slug?: string;
  additionalFields?: Record<string, string>;
}

export interface CreateUserParams {
  permission: PermissionName;
  email: string;
  name?: string;
  expires?: string;
  oidc: boolean;
}

export interface UpdateUserParams {
  handle: string;
  permission?: PermissionName;
  expires?: string;
  name?: string;
  oidc?: boolean;
}

export interface CreatedUser {
  token: string;
}

export interface Queue {
  test: string | null;
  threat: string | null;
  run_code: RunCode;
  tag: string | null;
  started: string;
}

/**
 * Get the name of an enum value
 * @example,
 * getEnumName(RunCodes, RunCodes.DAILY) // => "DAILY"
 */
export function getEnumName<T extends Record<string, unknown>>(
  enumType: T,
  value: T[keyof T],
): keyof T {
  const key = Object.keys(enumType).find((k) => enumType[k] === value);
  if (key === undefined) {
    throw new Error(`Unknown enum value ${value}`);
  }
  return key;
}

export const RunCodes = {
  INVALID: -1,
  DAILY: 1,
  WEEKLY: 2,
  MONTHLY: 3,
  SMART: 4,
  DEBUG: 5,
  RUN_ONCE: 6,
  MONDAY: 10,
  TUESDAY: 11,
  WEDNESDAY: 12,
  THURSDAY: 13,
  FRIDAY: 14,
  SATURDAY: 15,
  SUNDAY: 16,
  MONTH_1: 20,
} as const;

export type RunCodeName = keyof typeof RunCodes;
export type RunCode = (typeof RunCodes)[keyof typeof RunCodes];

export const Permissions = {
  INVALID: -1,
  ADMIN: 0,
  EXECUTIVE: 1,
  BUILD: 2,
  SERVICE: 3,
  AUTO: 4,
} as const;

export type PermissionName = keyof typeof Permissions;
export type Permission = (typeof Permissions)[keyof typeof Permissions];

export const Modes = {
  MANUAL: 0,
  FROZEN: 1,
  AUTOPILOT: 2,
} as const;

export type ModeName = keyof typeof Modes;
export type Mode = (typeof Modes)[keyof typeof Modes];

export interface EnabledTest {
  id: string;
}

export interface Probe {
  endpoint_id: string;
  host: string;
  serial_num: string;
  edr_id: string | null;
  control: ControlCode;
  tags: string[];
  last_seen: string | null;
  created: string;
  dos: Platform | null;
  os?: string | null;
  policy?: string | null;
  policy_name?: string | null;
}

export const ExitCodes = {
  MISSING: -1,
  UNKNOWN_ERROR: 1,
  MALFORMED_TEST: 2,
  UNREPORTED: 3,
  PROCESS_BLOCKED: 9,
  PROCESS_BLOCKED_GRACEFULLY: 15,
  PROTECTED: 100,
  UNPROTECTED: 101,
  TIMED_OUT: 102,
  FAILED_CLEANUP: 103,
  TEST_NOT_RELEVANT: 104,
  DYNAMIC_QUARANTINE: 105,
  BLOCKED_AT_PERIMETER: 106,
  EXPLOIT_PREVENTED: 107,
  ENDPOINT_NOT_RELEVANT: 108,
  EXECUTION_PREVENTED: 126,
  STATIC_QUARANTINE: 127,
  BLOCKED: 137,
  UNEXPECTED_ERROR: 256,
} as const;

export type ExitCodeName = keyof typeof ExitCodes;
export type ExitCode = (typeof ExitCodes)[ExitCodeName];
export const ExitCodeNames = Object.keys(ExitCodes) as ExitCodeName[];
export const ExitCodeGroup = {
  NONE: [ExitCodes.MISSING],
  PROTECTED: [
    ExitCodes.BLOCKED,
    ExitCodes.BLOCKED_AT_PERIMETER,
    ExitCodes.DYNAMIC_QUARANTINE,
    ExitCodes.EXPLOIT_PREVENTED,
    ExitCodes.EXECUTION_PREVENTED,
    ExitCodes.PROCESS_BLOCKED,
    ExitCodes.PROCESS_BLOCKED_GRACEFULLY,
    ExitCodes.PROTECTED,
    ExitCodes.STATIC_QUARANTINE,
  ],
  UNPROTECTED: [ExitCodes.UNPROTECTED],
  ERROR: [
    ExitCodes.FAILED_CLEANUP,
    ExitCodes.MALFORMED_TEST,
    ExitCodes.TIMED_OUT,
    ExitCodes.UNEXPECTED_ERROR,
    ExitCodes.UNKNOWN_ERROR,
    ExitCodes.UNREPORTED,
  ],
  NOT_RELEVANT: [ExitCodes.TEST_NOT_RELEVANT, ExitCodes.ENDPOINT_NOT_RELEVANT],
} as const;

export const ActionCodes = {
  NONE: 0,
  IGNORE: 1,
  IMPORTANT: 2,
} as const;

export type ActionCodeName = keyof typeof ActionCodes;
export type ActionCode = (typeof ActionCodes)[ActionCodeName];

export const ControlCodes = {
  INVALID: -1,
  NONE: 0,
  CROWDSTRIKE: 1,
  DEFENDER: 2,
  SPLUNK: 3,
  SENTINELONE: 4,
  VECTR: 5,
} as const;

export type ControlCodeName = keyof typeof ControlCodes;
export type ControlCode = (typeof ControlCodes)[ControlCodeName];

export const EDRResponses = {
  INVALID: -1,
  OBSERVE: 1,
  DETECT: 2,
  PREVENT: 3,
} as const;

export type EDRResponseName = keyof typeof EDRResponses;
export type EDRResponse = (typeof EDRResponses)[EDRResponseName];

export type NonArchPlatform = "darwin" | "linux" | "windows";
export type Architecture = "arm64" | "x86_64";

export const Platforms = [
  "linux-arm64",
  "linux-x86_64",
  "windows-arm64",
  "windows-x86_64",
  "darwin-arm64",
  "darwin-x86_64",
  "unknown",
] as const;

export type Platform = (typeof Platforms)[number];

export interface Activity {
  date: string;
  endpoint_id: string;
  id: string;
  status: ExitCode;
  test: string;
  threat: string | null;
  dos: Platform;
  control: ControlCode;
  policy: string | null;
  os: string | null;
}

export interface PersonalActivity {
  detected: number;
  observed: number;
  prevented: number;
  total: number;
}

export interface ExpectedActivity {
  crowdstrike: EDRResponse | null;
}

export interface TestsActivity {
  id: string;
  /** @deprecated */
  protected: number | null;
  social: number | null;
  personal: PersonalActivity;
  expected: ExpectedActivity;
}

export interface TechniquesActivity {
  id: string;
  name: string | null;
  /** @deprecated */
  protected: number | null;
  social: number | null;
  personal: PersonalActivity;
  expected: ExpectedActivity;
}

export interface ThreatsActivity {
  id: string;
  /** @deprecated */
  protected: number | null;
  social: number | null;
  personal: PersonalActivity;
}

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "APIError";
  }
}

export interface ActivityQuery {
  start: string;
  finish: string;
  tests?: string;
  threats?: string;
  endpoints?: string;
  dos?: Platform;
  control?: string;
  impersonate?: string;
  os?: string;
  policy?: string;
  statuses?: string;
}

export type ActivityQueryKey = keyof ActivityQuery;

export type EndpointActivity = {
  id: string;
  protected: number;
};

export interface MetricsActivity {
  account_id: string;
  endpoints: number;
  tests: number;
  company: string;
  unique_tests: number;
}

export interface Finding {
  key: string;
  value: string | ControlCode | null;
  improvement: number;
}

export interface FindingsActivity {
  protected: number;
  dos: Platform;
  control: ControlCode;
  policy: string | null;
  os: string | null;
  finding?: Finding;
}

export interface RegisterEndpointParams {
  host: string;
  serial_num: string;
  tags?: string;
}

export interface UpdateEndpointParams {
  endpoint_id: string;
  tags?: string;
}

export interface UpdatedEndpoint {
  id: string;
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

export interface AttachedPartner {
  api: string;
  connected: boolean;
}

export interface EndpointsParams {
  partner: ControlCodeName;
  platform: string;
  hostname?: string;
  offset?: number;
  count?: number;
}

export interface DeployParams {
  partnerCode: ControlCode;
  hostIds: string[];
}

export interface DeployedEndpoints {
  id: ControlCode;
  host_ids: string[];
}

export type PartnerEndpoints = Record<
  string,
  {
    hostname: string;
    os: string;
    policy?: string | null;
    policy_name?: string | null;
  }
>;

export interface AuditLog {
  event: string;
  account_id: string;
  user_id: string;
  values: AuditLogValues;
  status: string;
  timestamp: string;
}

export type AuditLogValues = Record<string, unknown>;

export interface BlockResponseRule {
  name: string;
  status: "CREATED" | "ALREADY_EXISTS" | "ERROR";
  created?: string;
  error?: string;
}

export interface BlockResponse {
  platform: "windows" | "linux" | "macos";
  rules: BlockResponseRule[];
}

export interface ProtectedActivity {
  date: string;
  observed: number;
  detected: number;
  protected: number;
}

export const OIDCOptions = ["google", "okta", "azure"] as const;
export type OIDC = (typeof OIDCOptions)[number];

export interface AttachOIDC {
  issuer: OIDC;
  client_id: string;
  client_secret: string;
  oidc_config_url: string;
}

export interface AttachedOIDC {
  issuer: OIDC;
  domain: string;
}

export interface ScheduleItem {
  id: string;
  type: "test" | "threat";
  runCode: RunCodeName;
  tags: string;
}

export interface UnscheduleItem {
  id: string;
  type: "test" | "threat";
  tags: string;
}

export interface DetectionRules {
  name: string;
  ruletype_id: string;
}

export interface CreateDetectionRule {
  testId: string;
  rule: string;
  detectionId?: string;
  ruleId?: string;
}

export interface Detection {
  account_id: string;
  created: string;
  id: string;
  name: string;
  rule_id: string;
  test: string;
  rule: Record<string, unknown>;
}

export interface DetectionReport {
  platform: "windows" | "linux" | "macos";
  created: string;
}

export interface GeneratedTechnique {
  parent_job_id: string | null;
  job_id: string;
}

export interface CompiledResponse {
  status: "COMPLETE" | "FAILED" | "RUNNING";
  results?: CompiledResponseResult[];
}

export interface CompiledResponseResult {
  platform: NonArchPlatform;
  architecture: Architecture;
  status: "SUCCEEDED" | "FAILED" | "SKIPPED";
  reason: string | null;
}

export interface ThreatHunt {
  control: ControlCode;
  name: string;
  query: string;
  test_id: string;
  threat_hunt_id: string;
}

export interface ThreatHuntActivity {
  non_prelude_origin: number;
  prelude_origin: number;
  test_id: string;
}

export interface ThreatHuntResult {
  account_id: string;
  non_prelude_origin: number;
  prelude_origin: number;
  threat_hunt_id: string;
}