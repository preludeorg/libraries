//go:build linux && amd64

package Dropper

import (
	_ "embed"
)

//go:embed linux-amd64
var Dropper []byte
