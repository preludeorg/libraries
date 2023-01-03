package main

import (
	"github.com/preludeorg/libraries/go/probe/internal/hades"
	"os"
)

func main() {
	var ok bool
	var hq string
	if hq, ok = os.LookupEnv("PRELUDE_API"); !ok {
		hq = "https://detect.preludesecurity.com"
	}
	probe := hades.CreateProbe(os.Getenv("PRELUDE_TOKEN"), hq)
	probe.Start()
}
