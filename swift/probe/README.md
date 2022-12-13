# Moonlight
A multiplatform etect probe written in [swift](https://www.swift.org/).

## Downloading Precompiled Binaries

To download precompiled moonlight binaries from our API endpoint, you'll need a detect 
token. You can provision your token by running `prelude iam create-account` 
(instructions [here](https://docs.prelude.org/docs/prelude-cli))

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
* Clone this repository, and change into the _libraries/swift/probe_ directory
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
* Next, test the executable: 
  * x86 mac: `./moonlight_darwin-x86_64`
  * m1 or m2 mac: `./moonlight_darwin-arm64`

### Building on linux

Building on linux was liberally cribbed from 
[compute's](https://github.com/preludeorg/compute/blob/master/Dockerfile) Dockerfile. 

*note:* binaries generated on Linux are dynamic as there are problems compiling static
swift code that uses FoundationNetworking (see: 
[forum post](https://forums.swift.org/t/linux-static-executable-linking-errors/54399/2))

* Install the dependencies of your distro
  * Debian: 
    ```
    apt update
    apt install \
              curl \
              binutils \
              libc6-dev \
              libcurl4 \
              libedit2 \
              libgcc-9-dev \
              libpython2.7 \
              libsqlite3-0 \
              libstdc++-9-dev \
              libxml2 \
              libz3-dev \
              pkg-config \
              tzdata \
              uuid-dev \
              zlib1g-dev  \
              libncurses6 
    ```
  * Centos
    ```
    dnf update
    dnf install ncurses-compat-libs glibc-headers gcc gcc-c++ kernel-devel libcurl-devel
    ```
  * Amzn Linux
    ```
    yum update
    yum install tar ncurses-compat-libs glibc-headers gcc gcc-c++ kernel-devel libcurl-devel
    ```
* Download swift upstream distribution: 
  * Debian `curl https://download.swift.org/swift-5.7.1-release/ubuntu2004/swift-5.7.1-RELEASE/swift-5.7.1-RELEASE-ubuntu20.04.tar.gz -o swift-5.7.1.tar.gz`
  * CentOS `curl https://download.swift.org/swift-5.7.1-release/centos7/swift-5.7.1-RELEASE/swift-5.7.1-RELEASE-centos7.tar.gz -o swift-5.7.1.tar.gz`
  * Amzn Linux `curl https://download.swift.org/swift-5.7.1-release/amazonlinux2/swift-5.7.1-RELEASE/swift-5.7.1-RELEASE-amazonlinux2.tar.gz -o swift-5.7.1.tar.gz`
  ```
* Unpack into the root of your machine
  ```
  tar -xf swift-5.7.1.tar.gz --strip-components=1 --directory /
  ```
* Test swiftc works `swiftc --version`
  * Should output 

    ```
    swiftc --version 
    Swift version 5.7.1 (swift-5.7.1-RELEASE)
    Target: x86_64-unknown-linux-gnu
    ```
* Cleanup tar: `rm swift-5.7.1.tar.gz`
* Clone this repository, and change into the _libraries/swift/probe_ directory
* Compile the application with dynamic libaries
  ```
  swiftc -Osize Sources/Moonlight/moonlight.swift -o moonlight_linux-x86_64 
  ```
* Compile the application with a static stdlib (still requires libcurl on system). Warning
  this binary will be ~50 megs, ~43 after stripping
  ```
  swiftc -static-stdlib -Osize Sources/Moonlight/moonlight.swift -o moonlight_linux-x86_64 
  strip moonlight_linux-x86_64 
  ```

### Building for Linux on Docker on an ARM Mac

ARM macs can run both x86 and arm docker containers. To create linux binaries, you can specify a different 
"platform" for docker to run on. 
* _Note:_ The -slim images are runtime only images, and do not include the compiler. 

See also: 
* https://stackoverflow.com/questions/43007424/what-targets-are-available-for-the-swiftc-target-and-target-cpu-option
* https://github.com/apple/swift/blob/main/utils/swift_build_support/swift_build_support/targets.py#L151
git 

**ARM Instructions** 
* Clone this repository, and change into the _libraries/swift/probe_ directory
* Run compile and stripe inside of docker container
  ```
  docker run  --platform linux/aarch64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 swiftc -Osize /mnt/probe/Sources/Moonlight/moonlight.swift -o /mnt/probe/moonlight_linux-aarch64 -target aarch64-unknown-linux-gnu
  docker run  --platform linux/aarch64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 strip /mnt/probe/moonlight_linux-aarch64
  ```

**x86_64 Instructions** 
* Clone this repository, and change into the _libraries/swift/probe_ directory
* Run compile and stripe inside of docker container
  ```
  docker run --platform linux/amd64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 swiftc -Osize /mnt/probe/Sources/Moonlight/moonlight.swift -o /mnt/probe/moonlight_linux-x86_64 -target x86_64-unknown-linux-gnu
  docker run --platform linux/amd64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 strip /mnt/probe/moonlight_linux-x86_64
  ```

### Build for windows
Un-tested. It is a lot right now. If you have an x86 mac, you could probaly have a docker context for building widows instances. ARM mac users are in rough shape, https://github.com/StefanScherer/windows-docker-machine/issues/84 includes discussion on m1 support for window and docker. 

## Running as Service on MacOS

To run moonlight as a service

* Get [prelude-detect-install.sh](./prelude-detect-install.sh)
* Check if moonlight is running: `ps aux | grep moonlight`
* Kill service if you are 
`launchctl unload -w ~/Library/LaunchAgents/org.prelude.detect.plist`
* Run installer `./prelude-detect-install.sh`