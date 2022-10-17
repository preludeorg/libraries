# Detect CLI

Want to standardize how you write, compile, validate and deploy security tests (TTPs)?

Prelude's detect-cli utility allows you to:

* Write security tests (TTPs) in any language
* Store tests in a cloud account for quick access and easy sharing
* Automatically compile tests for every platform your chosen language supports
* Add your tests to a continuous testing pipeline to track their efficacy
* Generate a download link for any test in your collection

> This library wraps around the detect-sdk utility, which can be used standalone to interact with the Prelude API.

Each security test uses an exit status to provide an objective analysis of its efficacy.

## Install

```bash
pip install detect-cli
detect --help
```

### Auto-complete

To add auto-completion to the detect CLI, add this line to your appropriate config:

~/.bashrc
```zsh
eval "$(_DETECT_COMPLETE=bash_source detect)"
```

~/.zshrc
```zsh
eval "$(_DETECT_COMPLETE=zsh_source detect)"
```

## Quick start

Set up your keychain. Follow the prompts to add your account credentials, which saves to 
~/.prelude/keychain.ini, and is used to authenticate all future requests.
```zsh
detect configure
```

Every new account is provisioned with Prelude's collection of open-source TTPs, known as your initial manifest.
It helps to [understand how Prelude stores security tests](#security-tests).
You can view your manifest, then clone all associated code files locally, using the following commands:
```zsh
detect database view
detect database clone
```

Add or remove TTPs from your account using:
```zsh
detect database create '<TTP NAME>'
detect database delete <TTP IDENTIFIER>
```

Upload new code files:
```zsh
detect database upload <PATH>
```

## Security tests

TTP is a generally overloaded acronym standing for Tactics, Techniques and Procedures. At Prelude, TTPs represent individual 
security tests and are broken into two components: metadata and code files.

### Metadata

TTP metadata is stored in your manifest and hosted in Prelude's cloud. Metadata includes properties such as name
and last updated time. Each TTP has a unique UUID-4 identifier.

### Code files

Code files are individual source files which can be compiled into executables. Each code file is associated to a TTP 
through the logical naming convention: ```TTP_ID.ext```, where extension can be any supported programming language. 

> The supported programming languages are: C, C# and Swift. [Review the templates](docs).

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
