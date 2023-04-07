import {Service} from "@theprelude/sdk";
import { expect, assert } from "chai";
import { describe } from "mocha";
import fetch, { Headers, Request, Response } from 'node-fetch';
import readline from 'readline';
import { stdin as input, stdout as output } from 'node:process';
import {randomUUID} from "crypto";
import {readFileSync} from "fs";

if (!globalThis.fetch) {
  globalThis.fetch = fetch;
  globalThis.Headers = Headers;
  globalThis.Request = Request;
  globalThis.Response = Response;
}

// create a function that periodically checks if the service is authorized. Check every 5 seconds for 30 seconds.
const waitForUserInput = function () {
  return new Promise((resolve, reject) => {
    const rl = readline.createInterface({ input, output });
    rl.question("Press ENTER to continue testing after verifying the account...", () => {
      rl.close();
      resolve();
    });
  });
}

describe("SDK Test", function () {
  let service = new Service({
    host: "https://api.staging.preludesecurity.com",
  });

  describe("IAM Controller - Core", function () {
    it("newAccount should return a new account", async function (){
      this.timeout(60000);
      const account = await service.iam.newAccount("alex+testingframework@preludesecurity.com");
      expect(account).to.have.property("account");
      expect(account).to.have.property("token");
      service.setCredentials(account);
      await waitForUserInput();
    });
    
    it("getAccount should return the account", async function () {
      const account = await service.iam.getAccount();
      expect(account).to.have.property("whoami");
      assert.equal(account.whoami, "alex+testingframework@preludesecurity.com", "whoami is correct");
    });
    
    it("createUser should return an object with a value token that is a UUID4", async function () {
      const result = await service.iam.createUser(3, "registration");
      expect(result.token).to.match(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
      const account = await service.iam.getAccount();
      expect(account).to.have.property("users");
      expect(account.users).to.have.lengthOf(2);
    });
    
    it("deleteUser should return a boolean true", async function () {
      const result = await service.iam.deleteUser("registration");
      expect(result).to.be.true;
      const account = await service.iam.getAccount();
      expect(account).to.have.property("users");
      expect(account.users).to.have.lengthOf(1);
    });
  });
  
  describe("Build Controller", function () {
    const testId = randomUUID();
    const testName = "test";
    
    it("createTest should not throw an error", async function () {
      await service.build.createTest(testId, testName);
      assert.equal(true, true);
    });
    
    it("getTest should return a test object", async function () {
      const test = await service.build.getTest(testId);
      expect(test).to.have.property("attachments");
      expect(test).to.have.property("mappings");
    });
    
    it("upload should have an attachment in the getTest call", async function () {
      const file = readFileSync("./templates/template.go", "utf8");
      let data = file.toString();
      data.replace('$ID', testId);
      data.replace('$NAME', testName);
      data.replace('$CREATED', new Date().toISOString());
      await service.build.upload(testId, 'template.go', data);
      const test = await service.build.getTest(testId);
      expect(test.attachments).to.have.lengthOf(1);
      expect(test.attachments[0]).to.be.equal(`${testId}.go`);
    });
    
    it("download should return the same data as the upload", async function () {
      const data = await service.build.download(testId, `${testId}.go`);
      expect(data).to.have.string(testId);
      expect(data).to.have.string(testName);
    });
    
    it("map should add a mapping to the test", async function () {
      await service.build.map({testId, key: 'test'});
      const test = await service.build.getTest(testId);
      expect(test.mappings).to.have.lengthOf(1);
    });
    
    it("unmap should remove the mapping from the test", async function () {
      await service.build.unmap({testId, key: 'test'});
      const test = await service.build.getTest(testId);
      expect(test.mappings).to.have.lengthOf(0);
    });
    
    it("deleteTest should not throw an error", async function () {
      await service.build.deleteTest(testId);
      assert.equal(true, true);
    });
  });
  
  describe("IAM Controller - Purge", function () {
    it("purgeAccount should return an empty string", async function () {
      const result = await service.iam.purgeAccount();
      expect(result).to.equal("");
    });
  });
});
