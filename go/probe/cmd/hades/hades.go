package main

import (
	"github.com/preludeorg/libraries/go/probe/internal/hades"
	"os"
)

func main() {
	probe := hades.CreateProbe(os.Getenv("PRELUDE_TOKEN"), os.Getenv("PRELUDE_HQ"))
	probe.Start()
}
