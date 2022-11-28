# Moonlight
Probe written in [swift](https://www.swift.org/)

## Mac Getting started

Assuming you are on an ARM mac.

* Start by compiling:
```
swiftc -Osize ./Sources/moonlight.swift -o moonlight_darwin-x86_64 -target x86_64-apple-macos10.13 && strip moonlight_darwin-x86_64

swiftc -Osize ./Sources/moonlight.swift -o moonlight_darwin-arm64 -target arm64-apple-macos10.13 && strip moonlight_darwin-arm64
```
  * This may require XCode to be installed in addition to the XCode CLI tools. 
  * The strip command is optional, but it will make the compile binary smaller, so it is recommended.
* Export PRELUDE_TOKEN `export PRELUDE_TOKEN=<SECRET>`
* Next, start an executable: 
  * x86 mac: `./moonlight_darwin-x86_64`
  * m1 or arm mac: `./moonlight_darwin-arm64`

## Building linux clients
Assuming you're on an m1 mac, which can run both x86 and arm docker containers, you can use the following steps.

* _Note:_ The -slim images are runtime only images, and do not include the compiler.  

See also: 
* https://stackoverflow.com/questions/43007424/what-targets-are-available-for-the-swiftc-target-and-target-cpu-option
* https://github.com/apple/swift/blob/main/utils/swift_build_support/swift_build_support/targets.py#L151
git 

### Build for arm64 (aka aarch64): 
```
docker run  --platform linux/aarch64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 swiftc -Osize /mnt/probe/Sources/moonlight.swift -o /mnt/probe/moonlight_linux-aarch64 -target aarch64-unknown-linux-gnu
docker run  --platform linux/aarch64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 strip /mnt/probe/moonlight_linux-aarch64
```

### Build for x86_64: 
```
docker run --platform linux/amd64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 swiftc -Osize /mnt/probe/Sources/moonlight.swift -o /mnt/probe/moonlight_linux-x86_64 -target x86_64-unknown-linux-gnu
docker run --platform linux/amd64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 strp /mnt/probe/moonlight_linux-x86_64
```


## Build for windows
Un-tested. It is a lot right now. If you have an x86 mac, you could probaly have a docker context for building widows instances. ARM mac users are in rough shape, https://github.com/StefanScherer/windows-docker-machine/issues/84 includes discussion on m1 support for window and docker. 