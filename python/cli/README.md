# Prelude CLI

Want to standardize how you write, compile, validate and deploy security tests (TTPs)?

The prelude-cli utility allows you to:

* Write security tests (TTPs) in any language
* Store tests in a cloud account for quick access and easy sharing
* Automatically compile tests for every platform your chosen language supports
* Add your tests to a continuous testing pipeline to track their efficacy
* Generate a download link for any test in your collection

> This library wraps around the prelude-sdk utility, which can be used standalone to interact with the Prelude API.

Each security test uses an exit status to provide an objective analysis of its efficacy.

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
prelude build create-code-file <TTP ID>
prelude build put-code-file <PATH>
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

* 0: success
* 1: unexpected failure; something went wrong (think catch block)
* 2: expected failure 
* 3: the system under test is not applicable (think skipped)
