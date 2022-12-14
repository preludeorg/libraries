# Moonlight

A probe written in Swift.

## Quick start

Compile Moonlight, replacing ```<TARGET>``` with your desired operating system:

* x86_64-apple-macos10.13
* arm64-apple-macos10.13

> The strip command is optional, but it will make the compile binary smaller, so we recommended it.

```
swiftc -Osize ./Sources/moonlight.swift -o moonlight -target <TARGET> && strip moonlight
```

Ensure your binary is executable:
```bash
chmod +x moonlight
```

Start the probe:

> [Register an endpoint](https://docs.prelude.org/docs/probes#registering-endpoints) to get a token

```bash
export PRELUDE_TOKEN=<TOKEN>
./moonlight
```
