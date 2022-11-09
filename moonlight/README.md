# Moonlight

## Getting started

Start by compiling:
```
swiftc -Osize Sources/main.swift -o moonlight && strip moonlight
```

Next, start as an executable:
```
./moonlight
```

### My story

I was created by initializing a new package and opening in Xcode:
```
swift package init --name moonlight --type executable
open Package.swift
```
