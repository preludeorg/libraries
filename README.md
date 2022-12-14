# Prelude Libraries

Prelude maintains a collection of open-source libraries that interact with our products, [Build](https://docs.prelude.org/docs/build) and [Detect](https://docs.prelude.org/docs/the-basics).

You must have a [Prelude Account](https://docs.prelude.org/docs/prelude-account) to use these libraries. 

## Prelude Account

Create a free account by installing the [Prelude CLI](https://docs.prelude.org/docs/prelude-cli) and running the ``create-account`` command:
```bash
pip3 install prelude-cli
prelude iam create-account
```

> Alternatively, if you use [Build](https://build.preludesecurity.com) you can export your credentials from inside the application.

## Getting started

Libraries are organized by language and categorized into Probes and SDK(s).

> If you want to run security tests on your infrastructure, select a probe and follow the instructions. If you want to write your own client against the API, select an SDK.

### Probe

A [probe](https://docs.prelude.org/docs/probes) is an ephemeral endpoint process that requires no special privileges or installation. Probes have one duty: accept security tests from Detect, execute them, and respond with the result.

### SDK

A Software Development Kit (SDK) allows you to build your own tooling against the Prelude Service API. Additionally, some probes have [SDK implementations](https://docs.prelude.org/docs/probes#sdk-probes) allowing you to deploy them from inside your own applications.

## Probe compatibility 

| Name  | Supported | Runtime | SDK option
| ------------- | ------------- | ------------- | -------------
| Moonlight | MacOS | Swift | No
| Hades | Windows, MacOS, Linux | Go | Yes
| Presto | Windows, MacOS, Linux | Python | Yes
| Raindrop | Windows | PowerShell | No

