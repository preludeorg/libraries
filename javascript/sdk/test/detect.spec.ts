import fs from "fs/promises";
import { ChildProcess, spawn } from "node:child_process";
import path from "node:path";
import {
  afterAll,
  beforeAll,
  describe,
  expect,
  expectTypeOf,
  it,
} from "vitest";
import { RunCodes, Service } from "../lib/main";

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function downloadFile(url: string, headers: Record<string, string>) {
  const response = await fetch(url, { method: "GET", headers });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.arrayBuffer();
}

describe("detect", () => {
  let service = new Service({ host: "https://detect.dev.prelude.org" });
  let probePath = path.resolve("./moonlight");
  let probeToken = "";
  let probeProcess: ChildProcess | null = null;
  beforeAll(async () => {
    const credentials = await service.iam.newAccount("internal-tester-detect");
    service.setCredentials(credentials);
  });

  afterAll(async () => {
    await service.iam.purgeAccount();
    // await fs.unlink(probePath);
    // probeProcess?.kill();
  });

  it("registers an endpoint", async () => {
    const token = await service.detect.registerEndpoint({
      id: "test",
      tags: [],
    });

    expectTypeOf(token).toBeString();
    probeToken = token;
  });

  it("lists probes", async () => {
    const probes = await service.detect.listProbes();
    expect(probes[0].endpoint_id).toEqual("test");
    expect(probes[0].tags).toEqual([]);
  }, 10_000);

  describe("moonlight probe", () => {
    it("downloads", async () => {
      const file = await downloadFile(
        "https://detect.dev.prelude.org/download/moonlight?dos=darwin-arm64",
        { token: probeToken }
      );
      await fs.writeFile(probePath, Buffer.from(file));
      await fs.chmod(probePath, "755");
    });

    it.skip("starts", async () => {
      return new Promise((res, rej) => {
        probeProcess = spawn(probePath, {
          env: {
            PRELUDE_TOKEN: probeToken,
            PRELUDE_API: "https://detect.dev.prelude.org",
          },
        });

        // probeProcess?.on("spawn", () => {

        // });

        probeProcess?.stdout?.on("readable", () => {
          const buff = probeProcess?.stdout?.read(100);

          console.log(probeProcess?.stdout?.read(100));
          res(buff);
        });

        probeProcess?.on("error", (data) => {
          rej(data);
        });

        probeProcess?.on("close", (code) => {
          rej(code);
        });
      });
    }, 10_000);
  });

  it("compiles health check test", async () => {
    await sleep(5000);
    const compute = await service.build.computeProxy(
      "39de298a-911d-4a3b-aed4-1e8281010a9a.c"
    );
    expect(
      compute.every((r) => r.steps.every((s) => s.status === 0)),
      `Expected all variants to pass. Got ${JSON.stringify(compute, null, 2)}`
    ).toBeTruthy();
  }, 60_000);

  it("enables the health check test", async () => {
    await service.detect.enableTest({
      test: "39de298a-911d-4a3b-aed4-1e8281010a9a",
      runCode: RunCodes.DEBUG,
      tags: [],
    });

    console.log(probeToken);

    await sleep(60_000);
  }, 60_000);
});
