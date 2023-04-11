import { BeforeAll, setDefaultTimeout } from "@cucumber/cucumber";
import fetch, { Headers, Request, Response } from "node-fetch";

BeforeAll(function () {
  if (!globalThis.fetch) {
    globalThis.fetch = fetch;
    globalThis.Headers = Headers;
    globalThis.Request = Request;
    globalThis.Response = Response;
  }
  setDefaultTimeout(10 * 1000);
});
