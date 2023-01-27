# Prelude Libraries

Prelude maintains a collection of open-source libraries that interact with our products, [Build](https://docs.preludesecurity.com/docs/build) and [Detect](https://docs.preludesecurity.com/docs/the-basics).

You must have a [Prelude Account](https://docs.preludesecurity.com/docs/prelude-account) to use these libraries. 

## Prelude Account

Create a free account by installing the [Prelude CLI](https://docs.preludesecurity.com/docs/prelude-cli) and running the ``create-account`` command:
```bash
pip3 install prelude-cli
prelude iam create-account
```

> Alternatively, if you use [Build](https://platform.preludesecurity.com) you can export your credentials from inside the application.

## Getting started

Libraries are organized by language and categorized into Probes and SDK(s).

> If you want to run security tests on your infrastructure, select a probe and follow the instructions. If you want to write your own client against the API, select an SDK.

### Probe

A [probe](https://docs.preludesecurity.com/docs/probes) is an ephemeral endpoint process that requires no special privileges or installation. Probes have one duty: accept security tests from Detect, execute them, and respond with the result.

### SDK

A Software Development Kit (SDK) allows you to build your own tooling against the Prelude Service API. 

## Probe compatibility 

Shell probes are the default choice when using a Prelude [installer](https://docs.preludesecurity.com/docs/individual-probe-deployment#installer). However, other probes are available, depending on your needs.

> A DOS is a platform and architecture combination

| Name  |  Runtime | Supported (DOS)
| ------------- | ------------- | -------------
| [Raindrop](https://github.com/preludeorg/libraries/tree/master/shell/probe) | PowerShell | windows-x86_64
| [Nocturnal](https://github.com/preludeorg/libraries/tree/master/shell/probe) | Bash | linux-x86_64, linux-arm64,darwin-x86_64, darwin-arm64
| [Moonlight](https://github.com/preludeorg/libraries/tree/master/swift/probe) | Swift | darwin-x86_64, darwin-arm64
| [Hades](https://github.com/preludeorg/libraries/tree/master/go/probe) | Go | windows-x86_64, linux-x86_64, linux-arm64, darwin-x86_64, darwin-arm64
