# run with bash -e on an m1 mac
swiftc -Osize ./Sources/Moonlight/moonlight.swift -o moonlight_darwin-x86_64 -target x86_64-apple-macos10.13 && strip moonlight_darwin-x86_64

swiftc -Osize ./Sources/Moonlight/moonlight.swift -o moonlight_darwin-arm64 -target arm64-apple-macos10.13 && strip moonlight_darwin-arm64

docker run  --platform linux/aarch64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 swiftc -Osize /mnt/probe/Sources/Moonlight/moonlight.swift -o /mnt/probe/moonlight_linux-aarch64 -target aarch64-unknown-linux-gnu
docker run  --platform linux/aarch64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 strip /mnt/probe/moonlight_linux-aarch64

docker run --platform linux/amd64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 swiftc -Osize /mnt/probe/Sources/Moonlight/moonlight.swift -o /mnt/probe/moonlight_linux-x86_64 -target x86_64-unknown-linux-gnu
docker run --platform linux/amd64 -it --rm -v $PWD:/mnt/probe swift:5.7.1 strip /mnt/probe/moonlight_linux-x86_64

