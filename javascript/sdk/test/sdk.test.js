import {Service, RunCodes, } from "@theprelude/sdk";
import { expect, assert } from "chai";
import { describe } from "mocha";
import fetch, { Headers, Request, Response } from 'node-fetch';
import readline from 'readline';
import { stdin as input, stdout as output } from 'node:process';
import {randomUUID} from "crypto";
import path from 'path';
import { fileURLToPath } from 'url';
import {readFileSync} from "fs";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
    host: process.env.API,
  });

  describe("IAM Controller", function () {
    this.timeout(60000);
    it("newAccount should return a new account", async function (){
      const account = await service.iam.newAccount(process.env.EMAIL);
      expect(account).to.have.property("account");
      expect(account).to.have.property("token");
      service.setCredentials(account);
      await waitForUserInput();
    });
    
    it("getAccount should return the account", async function () {
      const account = await service.iam.getAccount();
      expect(account).to.have.property("whoami");
      assert.equal(account.whoami, process.env.EMAIL, "whoami is correct");
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
    this.timeout(60000);
    const testId = randomUUID();
    const testName = "test";
    const templateName = `${testId}.go`;
    
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
      const file = readFileSync(`${__dirname}/templates/template.go`, "utf8");
      let data = file.toString();
      data = data.replaceAll('$ID', testId);
      data = data.replaceAll('$NAME', testName);
      data = data.replaceAll('$CREATED', new Date().toISOString());
      await service.build.upload(testId, templateName, data);
      const test = await service.build.getTest(testId);
      expect(test.attachments).to.have.lengthOf(1);
      expect(test.attachments[0]).to.be.equal(templateName);
    });
    
    it("download should return the same data as the upload", async function () {
      const data = await service.build.download(testId, templateName);
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
  
  describe("Probe Controller", function () {
    it("download should return a string");
  });
  
  describe("Detect Controller", function () {
    const host = 'test_host';
    const serial = 'test_serial';
    const edrId = 'test_edr_id';
    const tags = 'test_tag';
    const healthCheck = '39de298a-911d-4a3b-aed4-1e8281010a9a';
    const recommendation = 'Test';
    let endpointToken = '';
    let endpointId = '';
    let activeTest = '';
    let recommendationId = '';
    
    it("registerEndpoint should return a string with length 32", async function () {
      const result = await service.detect.registerEndpoint({host, serial_num: serial, edr_id: edrId, tags});
      expect(result).to.have.lengthOf(32);
      endpointToken = result;
    });
    
    it("listEndpoints should return an array with length 1", async function () {
      const result = await service.detect.listEndpoints();
      expect(result).to.have.lengthOf(1);
      assert.equal(result[0].host, host);
      endpointId = result[0].endpoint_id;
    });
    
    it("listTests should return an array with length greater that 1", async function () {
      const result = await service.detect.listTests();
      expect(result).to.have.length.greaterThan(1);
      const tests = result.filter((test) => test.id !==  healthCheck);
      activeTest = tests[0].id;
    });
    
    it("listQueue should return an array with length 1", async function () {
      const result = await service.detect.listQueue();
      expect(result).to.have.lengthOf(1);
      assert.equal(result[0].test, healthCheck);
    });
    
    it("enableTest should add a new test to the queue", async function () {
      await service.detect.enableTest({test: activeTest, runCode: RunCodes.DEBUG, tags: [tags]});
      const result = await service.detect.listQueue();
      expect(result).to.have.lengthOf(2);
      expect(result).to.have.deep.property('[1].test', activeTest);
    });
    
    it("disableTest should remove the test from the queue", async function () {
      await service.detect.disableTest(activeTest);
      const result = await service.detect.listQueue();
      expect(result).to.have.lengthOf(1);
    });
    
    it("deleteEndpoint should remove the endpoint from the list", async function () {
      await service.detect.deleteEndpoint(endpointId);
      const result = await service.detect.listEndpoints();
      expect(result).to.have.lengthOf(0);
    });
    
    it("putRecommendation should assert true", async function () {
      await service.detect.putRecommendation({title: recommendation, description: recommendation});
      assert.equal(true, true);
    });
    
    it("getRecommendations should return an array with length 1", async function () {
      const result = await service.detect.getRecommendations();
      expect(result).to.have.lengthOf(1);
      assert.equal(result[0].title, recommendation);
      recommendationId = result[0].id;
    });
    
    it("makeDecision should make a decision on the recommendation", async function () {
      await service.detect.makeDecision({id: recommendationId, decision: 1});
      const result = await service.detect.getRecommendations();
      expect(result).to.have.lengthOf(1);
      assert.equal(result[0].events[0].decision, 1);
    });
  });
  
  describe("IAM Controller - Purge", function () {
    it("purgeAccount should return an empty string", async function () {
      const result = await service.iam.purgeAccount();
      expect(result).to.equal("");
    });
  });
});
