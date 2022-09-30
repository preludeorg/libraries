# Hades

> One of Chopin's 24 Preludes. Hades is considered by many to be the most difficult of the Chopin preludes.[2] Hans von Bülow dubbed this prelude "Hades." It was composed between 1836 and 1839, published in 1839 and dedicated to Camille Pleyel who commissioned the opus 28 preludes for 2,000 francs.

# Usage

Install with:

```bash
go get github.com/preludorg/detect-clients/go/probe
```

Include Hades in a project with:

```golang
package main

import (
    hades "github.com/preludorg/detect-clients/go/probe/pkg/service"
)

func main() {
    ps := hades.CreateService()
    if err := ps.Register(); err == nil {
        ps.Start()
    }
}
```

## Development

For local testing you can use:
```bash
go run cmd/hades/hades.go
```