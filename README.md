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

### Probe

A [probe](https://docs.prelude.org/docs/probes) is an ephemeral endpoint process that requires no special privileges or installation. Probes have one duty: accept security tests from Detect, execute them, and respond with the result.

### SDK

A Software Development Kit (SDK) allows you to build your own tooling against the Prelude Service API. Additionally, some probes have [SDK implementations](https://docs.prelude.org/docs/probes#sdk-probes) allowing you to deploy them from inside other applications.
