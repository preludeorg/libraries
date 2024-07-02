/*
ID: $ID
NAME: $NAME
TECHNIQUE: $TECHNIQUE
UNIT: $UNIT
CREATED: $TIME
*/
package main

import (
	Endpoint "github.com/preludeorg/libraries/go/tests/endpoint"
)

func test() {
	Endpoint.Stop(Endpoint.TestCompletedNormally)
}

func clean() {
	Endpoint.Say("Cleaning up")
}

func main() {
	Endpoint.Start(test, clean)
}
