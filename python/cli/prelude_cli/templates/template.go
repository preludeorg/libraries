/*
ID: $ID
NAME: $NAME
UNIT: $UNIT
GENERATED: $GENERATED
*/
package main

import (
	"github.com/preludeorg/test/endpoint"
)

func test() {
	Endpoint.Stop(100)
}

func clean() {
	println("[+] Cleaning up")
}

func main() {
	Endpoint.Start(test, clean)
}
