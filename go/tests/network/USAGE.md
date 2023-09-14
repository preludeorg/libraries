# Network Package Usage

### 1. Creating a new HTTP requester with default options:
```go
requester := Network.NewHTTPRequest("https://example.com", nil)
```

### 2. Creating a new HTTP requester with custom options:
```go
opts := &Network.RequestOptions{
    Timeout:   5 * time.Second,
    UserAgent: "CustomUserAgent/1.0",
}
requester := Network.NewHTTPRequest("https://example.com", opts)
```

### 3. Sending a GET request:
```go
params := Network.RequestParameters{
    Headers: map[string]string{
        "Accept": "application/json",
    },
}
statusCode, body, err := requester.GET(params)
if err != nil {
    fmt.Println("Error:", err)
} else {
    fmt.Println("Status Code:", statusCode)
    fmt.Println("Response Body:", string(body))
}
```

### 4. Sending a POST request with body data and gzip encoding:
```go
params := Network.RequestParameters{
    Headers: map[string]string{
        "Content-Type": "application/json",
    },
    Body:     []byte(`{"key": "value"}`),
    Encoding: "gzip",
}
statusCode, body, err := requester.POST(params)
if err != nil {
    fmt.Println("Error:", err)
} else {
    fmt.Println("Status Code:", statusCode)
    fmt.Println("Response Body:", string(body))
}
```

### 5. Sending a TCP message:
```go
err := Network.TCP("localhost", "8080", []byte("Hello, Server!"), 2*time.Second)
if err != nil {
    fmt.Println("Error:", err)
}
```

### 6. Scanning a port:
```go
scanner := &Network.PortScan{}
isOpen := scanner.ScanPort("tcp", "example.com", 80)
if isOpen {
    fmt.Println("Port 80 is open!")
} else {
    fmt.Println("Port 80 is closed!")
}
```

### 7. Scanning multiple ports on local network hosts:
```go
hosts := scanner.ScanHosts(22, 80, 443)
for _, host := range hosts {
    fmt.Println("Host with open port:", host)
}
```

### 8. Retrieving the internal IP address:
```go
ip, err := Network.InternalIP()
if err != nil {
    fmt.Println("Error:", err)
} else {
    fmt.Println("Internal IP:", ip)
}
```
