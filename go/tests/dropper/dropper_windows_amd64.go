//go:build windows && amd64

package Dropper

import (
	_ "embed"
)

//go:embed windows-amd64
var Dropper []byte
