//go:build windows && amd64

package Dropper

import (
	_ "embed"
)

//go:embed windows-x86_64
var Dropper []byte
