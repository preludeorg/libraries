/*
RULE: hello world
CREATED: 2023-01-20 11:10:48.336675
*/
package main

import (
	"fmt"
	"os"
)

func test() {
	fmt.Println("Run test")
	os.Exit(100)
}

func clean() {
	fmt.Println("Clean up")
	os.Exit(100)
}

func main() {
	args := os.Args[1:]
	if len(args) > 0 {
		clean()
	} else {
		test()
	}
}
