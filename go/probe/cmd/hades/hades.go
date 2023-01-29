package main

import (
	"github.com/preludeorg/libraries/go/probe/internal/hades"
	"os"
)

func main() {
	hq := os.Getenv("PRELUDE_API")
	if hq == "" {
		hq = "https://api.preludesecurity.com"
	}
	probe := hades.CreateProbe(os.Getenv("PRELUDE_TOKEN"), hq)
	probe.Start()
}
