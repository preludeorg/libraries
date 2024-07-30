//go:build windows
// +build windows

package Dropper

import (
	_ "embed"
)

//go:embed windows
var Dropper []byte
