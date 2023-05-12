import { randomUUID } from "crypto";
import { addDays, subDays } from "date-fns";
import { readFileSync, unlinkSync, writeFileSync } from "fs";
import { spawnSync } from "node:child_process";
import path from "path";
import { fileURLToPath } from "url";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { RunCodes, Service } from "../lib/main";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

declare module "vitest" {
  export interface TestContext {
    service: Service;
  }
}

const testEmail =
  process.env.EMAIL ?? "test@auto-accept.developer.preludesecurity.com";
const host = process.env.API_HOST ?? "https://api.staging.preludesecurity.com";

const createAccount = async () => {
  const service = new Service({
    host,
  });
  const creds = await service.iam.newAccount({
    email: testEmail,
    name: "test",
  });
  await sleep(5000);
  return creds;
};

describe("SDK Test", () => {
  let probeName = "nocturnal";
  let probeExists = false;

  describe("IAM Controller", () => {
    const service = new Service({
      host,
    });

    beforeAll(async () => {
      const account = await service.iam.newAccount({
        email: testEmail,
        name: "test",
      });
      expect(account).toHaveProperty("account");
      expect(account).toHaveProperty("token");
      await sleep(4000);
      service.setCredentials(account);
    });

    afterAll(async () => {
      await service.iam.purgeAccount();
    });

    it("updateAccount should update the account", async () => {
      const result = await service.iam.updateAccount(1);
      expect(result).to.be.true;
      const account = await service.iam.getAccount();
      expect(account).toHaveProperty("mode");
      expect(account.mode).eq(1);
    });

    it("getAccount should return the account", async () => {
      const account = await service.iam.getAccount();
      expect(account).toHaveProperty("whoami");
      expect(account.whoami).eq(testEmail);
    });

    it("createUser should return an object with a value token that is a UUID4", async () => {
      const result = await service.iam.createUser({
        permission: 3,
        handle: "registration",
        name: "registration",
        expires: addDays(new Date(), 1).toISOString(),
      });
      expect(result.token).toMatch(
        /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/
      );
      const account = await service.iam.getAccount();
      expect(account).toHaveProperty("users");
      expect(account.users).toHaveLength(2);
    });

    it("deleteUser should return a boolean true", async () => {
      const result = await service.iam.deleteUser("registration");
      expect(result).to.be.true;
      const account = await service.iam.getAccount();
      expect(account).toHaveProperty("users");
      expect(account.users).to.have.lengthOf(1);
    });
  });

  describe("Build Controller", async () => {
    const testId = randomUUID();
    const testName = "test";
    const templateName = `${testId}.go`;
    const testUnit = "AV";

    const service = new Service({
      host,
    });

    beforeAll(async () => {
      const credentials = await createAccount();
      service.setCredentials(credentials);
    });

    afterAll(async () => {
      await service.iam.purgeAccount();
    });

    it("createTest should not throw an error", async () => {
      await service.build.createTest(testId, testName, testUnit);
    });

    it("getTest should return a test object", async () => {
      const test = await service.build.getTest(testId);
      expect(test).toHaveProperty("attachments");
      expect(test).toHaveProperty("unit");
    });

    it("upload should have an attachment in the getTest call", async () => {
      const file = readFileSync(`${__dirname}/templates/template.go`, "utf8");
      let data = file.toString();
      data = data.replace("$ID", testId);
      data = data.replace("$NAME", testName);
      data = data.replace("$CREATED", new Date().toISOString());
      await service.build.upload(testId, templateName, data);
      const test = await service.build.getTest(testId);
      expect(test.attachments).to.have.lengthOf(1);
      expect(test.attachments[0]).to.be.equal(templateName);
    });

    it("download should return the same data as the upload", async () => {
      const data = await service.build.download(testId, templateName);
      expect(data).toContain(testId);
      expect(data).toContain(testName);
    });

    it("deleteTest should not throw an error", async () => {
      await service.build.deleteTest(testId);
    });
  });

  describe("Detect Controller", () => {
    const hostName = "test_host";
    const serial = "test_serial";
    const edrId = "test_edr_id";
    const tags = "test_tag";
    const healthCheck = "39de298a-911d-4a3b-aed4-1e8281010a9a";
    const recommendation = "Test";
    let endpointToken = "";
    let endpointId = "";
    let activeTest = "";
    let recommendationId = "";
    let unitId = "";
    let start = subDays(new Date(), 7).toISOString();
    let finish = addDays(new Date(), 1).toISOString();

    const service = new Service({
      host,
    });

    beforeAll(async () => {
      const credentials = await createAccount();
      service.setCredentials(credentials);
    });

    afterAll(async () => {
      await service.iam.purgeAccount();
    });

    it("registerEndpoint should return a string with length 32", async () => {
      const result = await service.detect.registerEndpoint({
        host: hostName,
        serial_num: serial,
        edr_id: edrId,
        tags,
      });
      expect(result).toHaveLength(32);
      endpointToken = result;
    });

    it("listEndpoints should return an array with length 1", async () => {
      const result = await service.detect.listEndpoints();
      expect(result).toHaveLength(1);
      expect(result[0].host).eq(hostName);
      endpointId = result[0].endpoint_id;
    });

    it("listTests should return an array with length greater that 1", async () => {
      const result = await service.detect.listTests();
      expect(result).to.have.length.greaterThan(1);
      const tests = result.filter((test) => test.id !== healthCheck);
      activeTest = tests[0].id;
      unitId = tests[0].unit;
    });

    it("listQueue should return an array with length 1", async () => {
      const result = await service.detect.listQueue();
      expect(result).to.have.lengthOf(1);
      expect(result[0].test).eq(healthCheck);
    });

    it("enableTest should add a new test to the queue", async function () {
      await service.detect.enableTest({
        test: activeTest,
        runCode: RunCodes.DEBUG,
        tags: tags,
      });

      const result = await service.detect.listQueue();

      expect(result).toHaveLength(2);
      expect(result).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            test: activeTest,
            run_code: RunCodes.DEBUG,
          }),
        ])
      );
    });

    describe("with probe", () => {
      afterAll(async () => {
        await unlinkSync(`${probeName}.sh`);
      });

      it("download should return a string", async () => {
        const service = new Service({
          host,
        });
        const result = await service.probe.download({
          name: probeName,
          dos: "linux-arm64",
        });
        expect(result).to.be.a("string");
        await writeFileSync(`${probeName}.sh`, result, { mode: 0o755 });
      });

      it("spawns the probe", async () => {
        spawnSync(`./${probeName}.sh`, {
          env: {
            PRELUDE_TOKEN: endpointToken,
          },
          timeout: 20000,
        });
      });

      it("describeActivity should spawn a probe and run 2 tests", async function () {
        const result = await service.detect.describeActivity({
          start,
          finish,
          view: "logs",
        });
        expect(result).toHaveLength(2);
      });

      it(
        "describeActivity units view should return 2 tests",
        async function () {
          const result = await service.detect.describeActivity({
            start,
            finish,
            view: "units",
          });

          const unit = result.find((u) => u.unit.id === unitId);
          expect(unit).toBeDefined();
          expect(unit?.usage?.count).toBe(1);
        },
        { retry: 5 }
      );
    });

    it("disableTest should remove the test from the queue", async function () {
      await service.detect.disableTest({
        test: activeTest,
        tags: tags,
      });
      const result = await service.detect.listQueue();
      expect(result).toHaveLength(1);
    });

    it("socialStats should return an object with a non-empty aray of values", async function () {
      const result = await service.detect.socialStats(activeTest);
      expect(Object.values(result)).to.have.length.greaterThan(1);
    });

    it("deleteEndpoint should remove the endpoint from the list", async function () {
      await service.detect.deleteEndpoint(endpointId);
      const result = await service.detect.listEndpoints();
      expect(result).to.have.lengthOf(0);
    });
  });

  describe.runIf(
    Boolean(process.env.PARTNER_USER) && Boolean(process.env.PARTNER_SECRET)
  )("PartnerController", () => {
    let deployEndpoint = "";
    const service = new Service({
      host,
    });

    beforeAll(async () => {
      const credentials = await createAccount();
      service.setCredentials(credentials);
      await service.partner.attachPartner({
        name: "crowdstrike",
        api: "https://api.us-2.crowdstrike.com",
        user: process.env.PARTNER_USER as string,
        secret: process.env.PARTNER_SECRET as string,
      });
    });

    afterAll(async () => {
      await service.iam.purgeAccount();
    });

    it("attachControl should add a new control", async () => {
      const result = await service.partner.attachPartner({
        name: "crowdstrike",
        api: "https://api.us-2.crowdstrike.com",
        user: "test",
        secret: "test",
      });
      expect(result).to.be.a("string");
      const account = await service.iam.getAccount();
      expect(account).toHaveProperty("controls");
      expect(account.controls).toHaveLength(1);
      expect(account.controls).toEqual(expect.arrayContaining(["crowdstrike"]));
    });

    it("endpoints should return an object", async () => {
      const result = await service.partner.endpoints({
        partnerName: "crowdstrike",
        platform: "linux",
      });

      expect(result).to.be.a("object");
      deployEndpoint = Object.keys(result)[0];
    });

    it(
      "endpoints should limit results by count and offset",
      async () => {
        const result = await service.partner.endpoints({
          partnerName: "crowdstrike",
          platform: "linux",
          count: 1,
          offset: 0,
        });

        expect(result).to.be.a("object");
        expect(Object.keys(result)).to.have.lengthOf(1);

        const result2 = await service.partner.endpoints({
          partnerName: "crowdstrike",
          platform: "linux",
          count: 1,
          offset: 1,
        });

        expect(result2).to.be.a("object");
        expect(Object.keys(result2)).to.have.lengthOf(1);
        expect(Object.keys(result2)[0]).not.eq(Object.keys(result)[0]);
      },
      { timeout: 10_000 }
    );

    it("deploy should return and array", async () => {
      const result = await service.partner.deploy({
        partnerName: "crowdstrike",
        hostIds: [deployEndpoint],
      });

      expect(result).to.be.a("array");
      expect(result).to.have.lengthOf(1);
      expect(result[0].aid).eq(deployEndpoint);
    });

    it("detachControl should remove a control", async () => {
      const result = await service.partner.detachPartner("crowdstrike");
      expect(result).to.be.a("string");
      const account = await service.iam.getAccount();
      expect(account).toHaveProperty("controls");
      expect(account.controls).toHaveLength(0);
    });
  });
});
