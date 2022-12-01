# Moonlight
Probe written in [swift](https://www.swift.org/)

## Getting started

Compile Moonlight, replacing ```<TARGET>``` with a supported operating system:

* x86_64-apple-macos10.13
* arm64-apple-macos10.13
* x86_64-unknown-linux-gnu
* x86_64-unknown-windows-msvc

> The strip command is optional, but it will make the compile binary smaller, so it is recommended.
```
swiftc -Osize ./Sources/moonlight.swift -o moonlight -target <TARGET> && strip moonlight
```
