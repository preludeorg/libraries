# Moonlight
A multiplatform etect probe written in [swift](https://www.swift.org/).

## Downloading Precompiled Binaries

To download precompiled moonlight binaries from our API endpoint, you'll need a detect 
token. You can provision your token by running `prelude iam create-account` 
(insructions [here](https://docs.prelude.org/docs/prelude-cli))

### m1 / m2 Mac Download

m1 / m2 chips are "ARM" processors. A majority of new macs are m1 / m2.

```
export PRELUDE_TOKEN='<INSERT TOKEN>'
curl -X GET -L "https://detect.prelude.org/download/moonlight?dos=darwin-arm64" -H "token:${PRELUDE_TOKEN}" > moonlight
chmod +x moonlight
./moonlight
```

### Intel Mac Download

Intel based Mac's are "x86_64" processors. A majority of usable macs bought before 2020 are Intel Bsed. 

```
export PRELUDE_TOKEN='<INSERT TOKEN>'
curl -X GET -L "https://detect.prelude.org/download/moonlight?dos=darwin-x86_64" -H "token:${PRELUDE_TOKEN}" > moonlight
chmod +x moonlight
./moonlight
```

## Compiling your own agent
### m1 / m2 Mac Compiling
m1 and m2 macs can compile for both x86_64 and ARM targets. 

* Install XCode (via the [App Store](https://apps.apple.com/us/app/xcode/id497799835?mt=12))
  * Note: You need the full xcode suite, not just the command line tools
* Compile for x86_64, and strip the binary:
  * The strip command is optional, but it will make the compile binary smaller, so it is recommended.V
```
swiftc -Osize ./Sources/Moonlight/moonlight.swift -o moonlight_darwin-x86_64 -target x86_64-apple-macos10.13
strip moonlight_darwin-x86_64
```
* Compile for ARM
```
swiftc -Osize ./Sources/Moonlight/moonlight.swift -o moonlight_darwin-arm64 -target arm64-apple-macos10.13
strip moonlight_darwin-arm64
```
* Export PRELUDE_TOKEN `export PRELUDE_TOKEN=<SECRET>`
* Next, test an executable: 
  * x86 mac: `./moonlight_darwin-x86_64`
  * m1 or m2 mac: `./moonlight_darwin-arm64`

### Intel Mac Compiling
m1 and m2 macs can compile for both x86_64 and ARM targets. 

* Install XCode (via the [App Store](https://apps.apple.com/us/app/xcode/id497799835?mt=12))
  * Note: You need the full xcode suite, not just the command line tools
* Compile for x86_64, and strip the binary:
  * The strip command is optional, but it will make the compiled binary smaller, so it is recommended.
```
swiftc -Osize ./Sources/Moonlight/moonlight.swift -o moonlight_darwin-x86_64 -target x86_64-apple-macos10.13
strip moonlight_darwin-x86_64
```
* Compile for ARM
```
swiftc -Osize ./Sources/Moonlight/moonlight.swift -o moonlight_darwin-arm64 -target arm64-apple-macos10.13
strip moonlight_darwin-arm64
```
* Export PRELUDE_TOKEN `export PRELUDE_TOKEN=<SECRET>`
* Next, test an executable: 
  * x86 mac: `./moonlight_darwin-x86_64`
  * m1 or m2 mac: `./moonlight_darwin-arm64`

### Building on linux

### Building for Linux on Docker on an ARM Mac

ARM macs can run both x86 and arm docker containers. To create linux binaries, you can specify a different 
"platform" for docker to run on. 
* _Note:_ The -slim images are runtime only images, and do not include the compiler.  

See also: 
* https://stackoverflow.com/questions/43007424/what-targets-are-available-for-the-swiftc-target-and-target-cpu-option
* https://github.com/apple/swift/blob/main/utils/swift_build_support/swift_build_support/targets.py#L151
git 

**ARM Instructions** 
```
docker run  --platform linux/aarch64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 swiftc -Osize /mnt/probe/Sources/Moonlight/moonlight.swift -o /mnt/probe/moonlight_linux-aarch64 -target aarch64-unknown-linux-gnu
docker run  --platform linux/aarch64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 strip /mnt/probe/moonlight_linux-aarch64
```

**x86_64 Instructions** 
```
docker run --platform linux/amd64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 swiftc -Osize /mnt/probe/Sources/Moonlight/moonlight.swift -o /mnt/probe/moonlight_linux-x86_64 -target x86_64-unknown-linux-gnu
docker run --platform linux/amd64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 strip /mnt/probe/moonlight_linux-x86_64
```


### Build for windows
Un-tested. It is a lot right now. If you have an x86 mac, you could probaly have a docker context for building widows instances. ARM mac users are in rough shape, https://github.com/StefanScherer/windows-docker-machine/issues/84 includes discussion on m1 support for window and docker. 