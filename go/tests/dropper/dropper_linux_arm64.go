//go:build linux && arm64

package Dropper

import (
	_ "embed"
)

//go:embed src/linux-arm64
var Dropper []byte
