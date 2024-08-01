//go:build darwin && amd64

package Dropper

import (
	_ "embed"
)

//go:embed darwin-amd64
var Dropper []byte
