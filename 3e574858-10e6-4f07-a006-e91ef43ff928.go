/*
NAME: 3e574858-10e6-4f07-a006-e91ef43ff928.go
QUESTION: $QUESTION
CREATED: 2022-12-30 19:28:04.982606
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