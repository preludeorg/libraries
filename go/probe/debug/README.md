# Debug probe

Compile the debug probe for any platform you want to run it on:

> GOOS can be darwin, linux or windows

```go
GOOS=darwin go build -o debug main.go
```

Copy ``debug`` to any computer and run any Detect test on demand:
```bash
./debug
[P] Detect API: https://api.preludesecurity.com
[P] Detect CA: prelude-account-us1-us-west-1.s3.amazonaws.com
[P] Enter a test ID:
```