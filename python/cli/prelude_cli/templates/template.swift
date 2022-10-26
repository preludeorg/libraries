/*
NAME: $NAME
CREATED: $CREATED
*/
import Foundation

func test() {
    print("Run test")
    exit(103)
}

func clean() {
    print("Clean up")
    exit(103)
}

if CommandLine.arguments.contains("clean") {
    clean()
} else {
    test()
}
