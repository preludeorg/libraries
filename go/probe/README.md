# Hades

A probe written in Go.

## Quick start | Standalone

Compile Hades for each supported operating system:
```
GOOS=darwin go build -ldflags="-s -w" -o hades main.go;
GOOS=linux go build -ldflags="-s -w" -o hades main.go;
GOOS=windows go build -ldflags="-s -w" -o hades.exe main.go;
```

Start the probe:

> [Register an endpoint](https://docs.prelude.org/docs/probes#registering-endpoints) to get a token

```bash
export PRELUDE_TOKEN=<TOKEN>
./hades
```

## Quick start | SDK

```bash
go get github.com/preludeorg/libraries/go/probe
```

Include Hades in a project with:

```golang
package main

import (
    hades "github.com/preludeorg/libraries/go/probe/pkg/service"
)

func main() {
    ps := hades.CreateService()
    if err := ps.Register(); err == nil {
        ps.Start()
    }
}
```
