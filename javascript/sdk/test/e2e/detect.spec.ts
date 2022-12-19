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
import { RunCodes, Service } from "../../lib/main";

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

const serviceURL = import.meta.env.VITE_PRELUDE_SERVICE_URL;

describe("detect", () => {
  let service = new Service({ host: serviceURL });
  let probePath = path.resolve("./moonlight");
  let probeToken = "";
  let probeProcess: ChildProcess | null = null;
  beforeAll(async () => {
    const credentials = await service.iam.newAccount("internal-tester-detect");
    service.setCredentials(credentials);
  });

  afterAll(async () => {
    await service.iam.purgeAccount();
    await fs.unlink(probePath);
    probeProcess?.kill();
  });

  it("registers an endpoint", async () => {
    const token = await service.detect.registerEndpoint({
      id: "test",
      tags: ["test-tag"],
    });

    expectTypeOf(token).toBeString();
    probeToken = token;
  });

  it("prints an empty the queue", async () => {
    const queue = await service.detect.printQueue();
    expectTypeOf(queue).toBeArray();
  });

  it.skip("lists probes", async () => {
    const probes = await service.detect.listProbes();

    console.log(probes);
    expect(probes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          endpoint_id: "test",
          tags: ["test-tag"],
        }),
      ])
    );
  });

  it(
    "compiles Can I run sudo with no password? test",
    async () => {
      await sleep(3000);
      const compute = await service.build.computeProxy(
        "082e2303-cc14-4854-b72f-b77ea1e1acd8.c"
      );
      expect(
        compute.every((r) => r.steps.every((s) => s.status === 0)),
        `Expected all variants to pass. Got ${JSON.stringify(compute, null, 2)}`
      ).toBeTruthy();
    },
    { timeout: 30_000, retry: 2 }
  );

  it("enables Can I run sudo with no password? test", async () => {
    await service.detect.enableTest({
      test: "082e2303-cc14-4854-b72f-b77ea1e1acd8",
      runCode: RunCodes.DEBUG,
      tags: ["test-tag"],
    });
  });

  it("prints a queue with Can I run sudo with no password", async () => {
    const queue = await service.detect.printQueue();
    expect(queue).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          test: "082e2303-cc14-4854-b72f-b77ea1e1acd8",
          run_code: RunCodes.DEBUG,
          tag: "test-tag",
        }),
      ])
    );
  });
  describe("moonlight probe", () => {
    it("downloads", async () => {
      const arch = process.arch === "x64" ? "x86_64" : process.arch;
      const platform = ["win32", "win64"].includes(process.platform)
        ? "windows"
        : process.platform;
      const file = await downloadFile(
        `${serviceURL}/download/moonlight?dos=${platform}-${arch}`,
        { token: probeToken }
      );
      await fs.writeFile(probePath, Buffer.from(file));
      await fs.chmod(probePath, "755");
    });

    it("starts", async () => {
      return new Promise((res, rej) => {
        probeProcess = spawn(probePath, {
          env: {
            PRELUDE_TOKEN: probeToken,
            PRELUDE_API: serviceURL,
          },
        });

        /* after 3 seconds without an stderr assume it started successfully.
         * Reason: On Macos probes doesn't talk on stdout
         */
        setTimeout(() => {
          res("ok");
        }, 3_000);

        probeProcess?.stdout?.on("data", () => {
          res("ok");
        });

        probeProcess?.stderr?.on("data", (data) => {
          rej(`stderr: ${data}`);
        });

        probeProcess?.on("error", (data) => {
          rej(`closed with error: ${data}`);
        });

        probeProcess?.on("close", (code) => {
          rej(`closed with code: ${code}`);
        });
      });
    });
  });

  it(
    "gets the activity",
    async () => {
      await sleep(4000);
      const activity = await service.detect.describeActivity();
      expect(activity).toEqual(
        expect.objectContaining({
          "082e2303-cc14-4854-b72f-b77ea1e1acd8": { OK: 1 },
        })
      );
    },
    { retry: 2 }
  );

  it("disables Can I run sudo with no password? test", async () => {
    await service.detect.disableTest("082e2303-cc14-4854-b72f-b77ea1e1acd8");
  });

  it("prints a queue without Can I run sudo with no password", async () => {
    const queue = await service.detect.printQueue();
    expect(queue).not.toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          test: "082e2303-cc14-4854-b72f-b77ea1e1acd8",
        }),
      ])
    );
  });
});
