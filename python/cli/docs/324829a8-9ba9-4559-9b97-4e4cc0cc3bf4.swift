func test() {
    print("testing")
}

func clean() {
    print("cleaning up")
}

if CommandLine.arguments.contains("clean") {
    clean()
} else {
    test()
}
