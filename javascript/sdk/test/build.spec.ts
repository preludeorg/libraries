import fs from "fs/promises";
import path from "path";
import * as uuid from "uuid";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { Service } from "../lib/main";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const getTemplate = async (ext: string) => {
  return fs.readFile(
    path.resolve(`../../python/cli/prelude_cli/templates/template.${ext}`),
    "utf-8"
  );
};

describe("build", async () => {
  let service = new Service({ host: "https://detect.dev.prelude.org" });
  beforeAll(async () => {
    const credentials = await service.iam.newAccount("internal-tester");
    service.setCredentials(credentials);
  });

  afterAll(async () => {
    await service.iam.purgeAccount();
  });

  it("list initial tests for new account", async () => {
    const tests = await service.build.listTests();
    expect(tests.length).toBeGreaterThan(1);
  });

  describe.each([
    { lang: "c", template: await getTemplate("c") },
    { lang: "cs", template: await getTemplate("cs") },
    { lang: "swift", template: await getTemplate("swift") },
    { lang: "go", template: await getTemplate("go") },
  ])("$lang language", ({ lang, template }) => {
    const testId = uuid.v4();
    const question = `This is a test for ${lang}`;

    it("creates a new test", async () => {
      await service.build.createTest(testId, question);
    });

    it("list tests to include new test", async () => {
      const tests = await service.build.listTests();
      expect(tests).toContainEqual(
        expect.objectContaining({
          id: testId,
          question,
        })
      );
    });

    it("gets a new tests variants", async () => {
      const variants = await service.build.getTest(testId);
      expect(variants).toHaveLength(0);
    });

    const variantName = `${testId}.${lang}`;
    it("creates a new variant", async () => {
      await service.build.createVariant(variantName, template);
    });

    it("gets the new variant", async () => {
      /** waiting for files to hit s3 */
      await sleep(1000);
      const variants = await service.build.getTest(testId);
      expect(variants).toContain(variantName);
      const code = await service.build.getVariant(variantName);
      expect(code).toEqual(template);
    });

    it("computes the variant", async () => {
      const compute = await service.build.computeProxy(variantName);
      expect(compute.length).toBeGreaterThan(0);
      /* Checks that all steps have a status true */
      expect(
        compute.every((r) => r.steps.every((s) => s.status === 0)),
        `Expected all variants to pass. Got ${JSON.stringify(compute, null, 2)}`
      ).toBeTruthy();
    }, 60_000);

    it("gets the verified security tests", async () => {
      const vsts = await service.build.verifiedTests();
      expect(vsts.length).toBeGreaterThan(1);
    });

    it("generates deploy url for first vst", async () => {
      const [firstVST] = await service.build.verifiedTests();
      const { url } = await service.build.createURL(firstVST);
      /* should be a url */
      expect(url).toMatch(
        /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi
      );
    });

    it("deletes a verified security test", async () => {
      const [firstVST] = await service.build.verifiedTests();
      await service.build.deleteVerified(firstVST);
      const vsts = await service.build.verifiedTests();
      expect(vsts).not.toContain(firstVST);
    });

    it("deletes the variant", async () => {
      await service.build.deleteVariant(variantName);
      const variants = await service.build.getTest(testId);
      expect(variants).not.toContain(variantName);
    });

    it("deletes the test", async () => {
      await service.build.deleteTest(testId);
      const tests = await service.build.listTests();
      expect(tests).not.toContainEqual(
        expect.objectContaining({
          id: testId,
          question,
        })
      );
    });
  });
});
