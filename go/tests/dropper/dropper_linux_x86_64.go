//go:build linux && amd64

package Dropper

import (
	_ "embed"
)

//go:embed linux-x86_64
var Dropper []byte
