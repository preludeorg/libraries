import {Service} from "@theprelude/sdk";
import { expect, assert } from "chai";
import { describe } from "mocha";
import fetch, { Headers, Request, Response } from 'node-fetch';
import readline from 'readline';
import { stdin as input, stdout as output } from 'node:process';

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
    
    it("createUser should return a string that is a UUID4", async function () {
      const result = await service.iam.createUser(3, "registration");
      expect(result.token).to.match(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
      const account = await service.iam.getAccount();
      expect(account).to.have.property("users");
      expect(account.users).to.have.lengthOf(2);
    });
  });
  
  describe("IAM Controller - Purge", function () {
    it("purgeAccount should return an empty string", async function () {
      const result = await service.iam.purgeAccount();
      expect(result).to.equal("");
    });
  });
});
