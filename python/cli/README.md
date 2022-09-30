# Detect CLI

This library can manage your Prelude Detect deployment via CLI. This CLI is a wrapper for the detect-sdk.

## Command line utility

There is a built-in command-line program that allows easy access to the Detect API. The CLI is modeled after the `aws-cli` 
package in terms of how it works.

First install the package with:
```bash
pip install detect-cli
```

Then view the available CLI tools with:
```bash
detect --help
```

#### Auto-complete

To add auto-completion to the detect CLI, add this line to your appropriate config:

~/.bashrc
```zsh
eval "$(_DETECT_COMPLETE=bash_source detect)"
```

~/.zshrc
```zsh
eval "$(_DETECT_COMPLETE=zsh_source detect)"
```