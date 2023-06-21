export interface DockerContainer {
  Id: string;
  Names: string[];
  Image: string;
  ImageID: string;
  Command: string;
  Created: number;
  Ports: Ports[];
  Labels: Record<string, string>;
  State: string;
  Status: string;
  HostConfig: HostConfig;
  NetworkSettings: NetworkSettings;
  Mounts: Mounts[];
  SizeRw: number;
  SizeRootFs: number;
  ProbeStatus: ProbeStatus | ProbeStatus.Unsupported;
}

export enum ProbeStatus {
  Unsupported = 0,
  NotInstalled = 1,
  Running = 2,
}

export interface ActionAlert {
  title: string;
  message: string;
  level: string;
}

interface Ports {
  PrivatePort: number;
  PublicPort: number;
  Type: string;
}
interface HostConfig {
  NetworkMode: string;
}
interface NetworkSettings {
  Networks: Record<string, Network>;
}
interface Network {
  NetworkID: string;
  EndpointID: string;
  Gateway: string;
  IPAddress: string;
  IPPrefixLen: number;
  IPv6Gateway: string;
  GlobalIPv6Address: string;
  GlobalIPv6PrefixLen: number;
  MacAddress: string;
}
interface Mounts {
  Name: string;
  Source: string;
  Destination: string;
  Mode: string;
  RW: boolean;
  Propagation: string;
}
