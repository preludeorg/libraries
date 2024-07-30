//go:build darwin
// +build darwin

package Dropper

import (
	_ "embed"
)

//go:embed darwin
var Dropper []byte
