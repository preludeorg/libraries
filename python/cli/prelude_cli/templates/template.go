/*
ID: $ID
NAME: $NAME
UNIT: $UNIT
CREATED: $CREATED
*/
package main

import (
	"github.com/preludeorg/test/endpoint"
)

func test() {
	Endpoint.Stop(100)
}

func clean() {
	Endpoint.Stop(100)
}

func main() {
	Endpoint.Start(test, clean)
}
