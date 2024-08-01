//go:build darwin && arm64

package Dropper

import (
	_ "embed"
)

//go:embed src/darwin-arm64
var Dropper []byte
