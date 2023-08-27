# Debug probe

Compile the debug probe on the same platform you want to run it against:
```go
go build -o debug main.go
```

Copy ``debug`` to any computer and run any Detect test on demand:
```bash
./debug
```