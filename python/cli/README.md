# Prelude CLI

Standardize how you write, compile, validate and deploy security tests (TTPs).

The prelude-cli utility allows you to:

* Store security tests in a cloud account
* Register endpoints and deploy probes on them
* Enable tests to run continuously against your probes
* Monitor results

There are four modules inside the CLI:

> This library wraps around the prelude-sdk utility, which can be used standalone to interact with the Prelude API.

1. iam: Prelude account management
2. configure: establish a local keychain on your computer
3. build: manage the security tests in your account
4. detect: run continuous security tests against your endpoints

## Install

```bash
pip install prelude-cli
prelude --help
```

### Auto-complete

To add auto-completion to the Prelude CLI, add this line to your appropriate config:

~/.bashrc
```zsh
eval "$(_DETECT_COMPLETE=bash_source prelude)"
```

~/.zshrc
```zsh
eval "$(_DETECT_COMPLETE=zsh_source prelude)"
```

## Quick start

Start by registering a new Prelude account and configuring your local keychain. Skip this step if you've done it before.
```zsh
prelude iam create-account
prelude configure
```

Every new account is provisioned with Prelude's collection of open-source TTPs, known as your initial manifest.
It helps to [understand how Prelude stores security tests](#security-tests).
You can view your manifest, then clone all associated code files locally, using the following commands:
```zsh
prelude build list-manifest
prelude build clone
```

Add or remove TTPs from your account using:
```zsh
prelude build create-ttp '<TTP NAME>'
prelude build delete-ttp <TTP IDENTIFIER>
```

Create and upload new code files:
```zsh
prelude build create-test <TTP ID>
prelude build put-test <PATH>
```

## Security tests

TTP is a generally overloaded acronym standing for Tactics, Techniques and Procedures. At Prelude, TTPs represent individual 
security tests and are broken into two components: metadata and code files.

### Metadata

TTP metadata is stored in your manifest and hosted in Prelude's cloud. Metadata includes properties such as name
and last updated time. Each TTP has a unique UUID-4 identifier.

### Code files

Code files are individual source files which can be compiled into executables. Each code file is associated to a TTP 
through the logical naming convention: ```TTP_ID_platform-architecture.ext```, where platform and architecture are optional and extension can be any supported programming language.

> The supported programming languages are: C, C# and Swift. [Review the templates](prelude_cli/templates).

Code files - after compilation - must be capable of the following options. The first executes the test and the 
second runs any cleanup activities:
```zsh
./code
./code clean
```

While stdout/stderr may print to console, the primary goal of each code file is to output a single number representing
the state of the test. 

Both the test and clean options must return an applicable status code from this list:

* 1: unexpected test failure (think catch block)
* 2: incorrect arguments used
* 3-8: internal issue with test
* 9: OS killed test
* 10-14: internal issue with test
* 15: probe killed the process
* 17-18: outside program killed test
* 24-25: used too many OS resources
* 100: test was a "yes"
* 101: test was a "no"
* 102: test timed out
* 103: test was negative
* 104: file could not write to disk
* 105: file deleted on writing to disk
* 256: binary execution error
