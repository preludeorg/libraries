package main

import "fmt"

import (
	"os"
)

func test() {
    fmt.Println("Run test")
	os.Exit(100)
}

func cleanup() {
    fmt.Println("Clean up")
	os.Exit(100)
}

func main() {
	args := os.Args[1:]
	if len(args) > 0 {
		cleanup()
	} else {
		test()
	}
}