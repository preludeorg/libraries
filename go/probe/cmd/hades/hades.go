package main

import (
	"github.com/preludorg/detect-clients/go/probe/internal/hades"
	"os"
)

func main() {
	probe := hades.CreateProbe(os.Getenv("PRELUDE_TOKEN"))
	probe.Start()
}
