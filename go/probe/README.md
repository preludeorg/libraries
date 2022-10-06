# Hades

> One of Chopin's 24 Preludes. Hades is considered by many to be the most difficult of the Chopin preludes.[2] Hans von Bülow dubbed this prelude "Hades." It was composed between 1836 and 1839, published in 1839 and dedicated to Camille Pleyel who commissioned the opus 28 preludes for 2,000 francs.

# Usage

Install with:

```bash
go get github.com/preludeorg/detect-clients/go/probe
```

Include Hades in a project with:

```golang
package main

import (
    hades "github.com/preludeorg/detect-clients/go/probe/pkg/service"
)

func main() {
    ps := hades.CreateService()
    if err := ps.Register(); err == nil {
        ps.Start()
    }
}
```

You can also manually load configurations from a keychain file and specify a name with:

Include Hades in a project with:

```golang
package main

import (
    hades "github.com/preludeorg/detect-clients/go/probe/pkg/service"
)

func main() {
    ps := hades.CreateService()
	err := ps.LoadKeychain("/path/to/keychain.ini")
	if err != nil {
		panic(err)
    }
    if err = ps.Register("my-amazing-probe"); err == nil {
        ps.Start()
    }
}
```

## Development

For local testing you can use:
```bash
go run cmd/hades/hades.go
```