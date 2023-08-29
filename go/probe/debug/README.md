# Debug probe

Compile the debug probe for any platform you want to run it on:

> GOOS can be darwin, linux or windows

```go
GOOS=darwin go build -o debug main.go
```

Copy ``debug`` to any computer and run any Detect test on demand:
```bash
./debug
[P] Enter a test ID:
```