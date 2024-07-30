//go:build linux
// +build linux

package Dropper

import (
	_ "embed"
)

//go:embed linux
var Dropper []byte
