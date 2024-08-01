//go:build linux && amd64

package Dropper

import (
	_ "embed"
)

//go:embed src/linux-amd64
var Dropper []byte
