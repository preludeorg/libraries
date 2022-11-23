# Moonlight
Probe written in [swift](https://www.swift.org/)

## Getting started

* Start by compiling:
```
swiftc -Osize ./Sources/moonlight.swift -o moonlight_darwin-x86_64 -target x86_64-apple-macos10.13 && strip moonlight_darwin-x86_64

swiftc -Osize ./Sources/moonlight.swift -o moonlight_darwin-arm64 -target arm64-apple-macos10.13 && strip moonlight_darwin-arm64
```
* Export PRELUDE_TOKEN `export PRELUDE_TOKEN=<SECRET>`
* Next, start an executable: 
  * x86 mac: `./moonlight_darwin-x86_64`
  * m1 or arm mac: `./moonlight_darwin-x86_64`

### My story

I was created by initializing a new package and opening in Xcode:
```
swift package init --name moonlight --type executable
open Package.swift
```
