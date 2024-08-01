//go:build darwin && amd64

package Dropper

import (
	_ "embed"
)

//go:embed darwin-x86_64
var Dropper []byte
