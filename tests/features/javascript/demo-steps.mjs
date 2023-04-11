import { Given, Then, When } from "@cucumber/cucumber";
import { Service } from "../../../javascript/sdk/dist/sdk.js";
import assert from "assert";

Given("I am signed in as a demo user", function () {
  this.controller = new Service({
    host: "https://api.staging.preludesecurity.com",
    credentials: {
      account: "prelude-demo",
      token: "executive-demo",
    },
  }).detect;
});

/* --- Activity data scenarios --- */

Given(
  "I want to request activity data from the {string} view",
  function (view) {
    this.view = view;
    this.options = {};
  }
);

Given("I specify a test ID {string}", function (test) {
  this.options.tests = [test];
});

Given("I specify a DOS {string}", function (dos) {
  this.options.dos = [dos];
});

Given("I specify a tag {string}", function (tag) {
  this.options.tags = [tag];
});

When("I retrieve the activity data", async function () {
  this.response = await this.controller.describeActivity({
    ...this.options,
    view: this.view,
  });
});

Then("the response should contain logs", async function () {
  assert(Array.isArray(this.response));
  assert(this.response.length > 0);
  assert("id" in this.response[0], "no id in response");
  assert("date" in this.response[0], "no date in response");
  assert("test" in this.response[0], "no test in response");
  assert("endpoint_id" in this.response[0], "no endpoint_id in response");
  assert("status" in this.response[0], "no status in response");
  assert("dos" in this.response[0], "no dos in response");
  assert("tags" in this.response[0], "no tags in response");
  assert("edr_id" in this.response[0], "no edr_id in response");
});

Then("the response should contain data only for that test ID", function () {
  assert(
    this.response.every(
      (data) => data.test === this.options.tests[0],
      "response contains tests not specified"
    )
  );
});

Then("the response should contain data only for that tag", function () {
  assert(
    this.response.every(
      (data) => data.tags[0] === this.options.tags[0],
      "response contains tag not specified"
    )
  );
});

Then("the response should contain data only for that DOS", function () {
  assert(
    this.response.every(
      (data) => data.dos === this.options.dos[0],
      "response contains DOS not specified"
    )
  );
});

Then("the response should contain insights", function () {
  assert(Array.isArray(this.response));
  assert(this.response.length > 0);
  assert("dos" in this.response[0], "no dos in response");
  assert("test" in this.response[0], "no test in response");
  assert("volume" in this.response[0], "no volume in response");
  assert("error" in this.response[0].volume, "no error in volume response");
  assert(
    "protected" in this.response[0].volume,
    "no protected in volume response"
  );
  assert(
    "unprotected" in this.response[0].volume,
    "no unprotected in volume response"
  );
});

Then("the response should contain probes", function () {
  assert(Array.isArray(this.response));
  assert(this.response.length > 0);
  assert("endpoint_id" in this.response[0], "no endpoint_id in response");
  assert("dos" in this.response[0], "no dos in response");
  assert("tags" in this.response[0], "no tags in response");
  assert("state" in this.response[0], "no state in response");
  assert("edr_id" in this.response[0], "no edr_id in response");
});

Then("the response should contain rules", function () {
  assert(Array.isArray(this.response));
  assert(this.response.length > 0);
  assert("rule" in this.response[0], "no rule in response");
  assert("id" in this.response[0].rule, "no id in rule response");
  assert("label" in this.response[0].rule, "no label in rule response");
  assert("published" in this.response[0].rule, "no published in rule response");
  assert(
    "description" in this.response[0].rule,
    "no description in rule response"
  );
  assert(
    "long_description" in this.response[0].rule,
    "no long_description in rule response"
  );
});

/* --- Scenario: Get tests --- */

When("I retrieve tests", async function () {
  this.response = await this.controller.listTests();
});

Then("the response should contain tests", function () {
  assert(Array.isArray(this.response), "response is not an array");
  assert(this.response.length > 0, "response is empty");
  assert("id" in this.response[0], "id not in response");
  assert("name" in this.response[0], "name not in response");
  assert("account_id" in this.response[0], "account not in response");
});

/* --- Scenario: Search the NVD for a keyword --- */

Given("I have a keyword to search for {string}", function (keyword) {
  this.keyword = keyword;
});

When("I search for the keyword", async function () {
  this.response = await this.controller.search(this.keyword);
});

Then("the response should contain search results", function () {
  assert("info" in this.response);
  assert("tests" in this.response);
});
