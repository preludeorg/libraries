package Network

import (
	"bytes"
	"compress/gzip"
	"crypto/tls"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"strconv"
	"sync"
	"time"
)

type Requester struct {
	Client    *http.Client
	URL       string
	UserAgent string
}

type Authentication struct {
	Type       string
	Credential string
}

type RequestParameters struct {
	Headers     map[string][]string
	QueryParams url.Values
	Body        []byte
	Cookies     []*http.Cookie
	Auth        *Authentication
	Encoding    string
}

type RequestOptions struct {
	Timeout   time.Duration
	UserAgent string
}

type ResponseData struct {
	StatusCode int
	Headers    http.Header
	Body       []byte
}

func NewHTTPRequest(requestURL string, opts *RequestOptions) *Requester {

	timeout := time.Second * 1
	userAgent := "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"

	if opts != nil {
		if opts.Timeout != 0 {
			timeout = opts.Timeout
		}
		if opts.UserAgent != "" {
			userAgent = opts.UserAgent
		}
	}

	return &Requester{
		Client: &http.Client{
			Timeout: timeout,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
		URL:       requestURL,
		UserAgent: userAgent,
	}
}

func (r *Requester) prepareRequest(method string, params RequestParameters, bodyBuffer io.Reader) (*http.Request, error) {
	reqURL, err := url.Parse(r.URL)
	if err != nil {
		return nil, err
	}

	if params.QueryParams != nil {
		reqURL.RawQuery = params.QueryParams.Encode()
	}

	req, err := http.NewRequest(method, reqURL.String(), bodyBuffer)
	if err != nil {
		return nil, err
	}

	req.Header.Set("User-Agent", r.UserAgent)

	for key, values := range params.Headers {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	for _, cookie := range params.Cookies {
		req.AddCookie(cookie)
	}

	if params.Auth != nil {
		switch params.Auth.Type {
		case "Basic":
			req.SetBasicAuth(params.Auth.Credential, "")
		case "Bearer":
			req.Header.Add("Authorization", "Bearer "+params.Auth.Credential)
		}
	}

	return req, nil
}

func (r *Requester) GET(params RequestParameters) (response ResponseData, err error) {
	req, err := r.prepareRequest(http.MethodGet, params, nil)
	if err != nil {
		return response, err
	}

	resp, err := r.Client.Do(req)
	if err != nil {
		return response, err
	}
	defer resp.Body.Close()

	response.StatusCode = resp.StatusCode
	response.Headers = resp.Header

	response.Body, err = io.ReadAll(resp.Body)
	if err != nil {
		return response, err
	}

	return response, nil
}

func (r *Requester) POST(params RequestParameters) (response ResponseData, err error) {
	var bodyBuffer io.Reader
	if params.Encoding == "gzip" && params.Body != nil {
		var b bytes.Buffer
		gz := gzip.NewWriter(&b)
		if _, err := gz.Write(params.Body); err != nil {
			return response, err
		}
		if err := gz.Close(); err != nil {
			return response, err
		}
		bodyBuffer = &b
	} else {
		bodyBuffer = bytes.NewBuffer(params.Body)
	}

	req, err := r.prepareRequest(http.MethodPost, params, bodyBuffer)
	if err != nil {
		return response, err
	}

	if params.Encoding == "gzip" {
		req.Header.Add("Content-Encoding", "gzip")
	}

	resp, err := r.Client.Do(req)
	if err != nil {
		return response, err
	}
	defer resp.Body.Close()

	response.StatusCode = resp.StatusCode
	response.Headers = resp.Header

	response.Body, err = io.ReadAll(resp.Body)
	if err != nil {
		return response, err
	}

	return response, nil
}

func (r *Requester) HEAD(params RequestParameters) (response ResponseData, err error) {
	req, err := r.prepareRequest(http.MethodHead, params, nil)
	if err != nil {
		return response, err
	}

	resp, err := r.Client.Do(req)
	if err != nil {
		return response, err
	}
	defer resp.Body.Close()

	response.StatusCode = resp.StatusCode
	response.Headers = resp.Header

	response.Body, err = io.ReadAll(resp.Body)
	if err != nil {
		return response, err
	}

	return response, nil
}

func (r *Requester) DELETE(params RequestParameters) (response ResponseData, err error) {
	req, err := r.prepareRequest(http.MethodDelete, params, nil)
	if err != nil {
		return response, err
	}

	resp, err := r.Client.Do(req)
	if err != nil {
		return response, err
	}
	defer resp.Body.Close()

	response.StatusCode = resp.StatusCode
	response.Headers = resp.Header

	response.Body, err = io.ReadAll(resp.Body)
	if err != nil {
		return response, err
	}

	return response, nil
}

func TCP(host, port string, message []byte, timeouts ...time.Duration) error {
	timeout := time.Second * 1

	if len(timeouts) > 0 {
		timeout = timeouts[0]
	}

	target := fmt.Sprintf("%s:%s", host, port)

	conn, err := net.DialTimeout("tcp", target, timeout)
	if err != nil {
		return err
	}
	defer conn.Close()

	_, err = conn.Write(message)
	if err != nil {
		return err
	}

	return nil
}

func UDP(host, port string, message []byte, timeouts ...time.Duration) error {
	timeout := time.Second * 1

	if len(timeouts) > 0 {
		timeout = timeouts[0]
	}

	target := fmt.Sprintf("%s:%s", host, port)

	conn, err := net.DialTimeout("udp", target, timeout)
	if err != nil {
		return err
	}
	defer conn.Close()

	_, err = conn.Write(message)
	if err != nil {
		return err
	}

	return nil
}

type PortScan struct{}

func (s *PortScan) ScanPort(protocol, hostname string, port int, timeout ...time.Duration) bool {
	defaultTimeout := 2 * time.Second
	if len(timeout) > 0 {
		defaultTimeout = timeout[0]
	}

	address := hostname + ":" + strconv.Itoa(port)
	conn, err := net.DialTimeout(protocol, address, defaultTimeout)
	if err != nil {
		return false
	}
	defer conn.Close()
	return true
}

func (s *PortScan) ScanHosts(ports ...int) []string {
	hostArray := []string{}
	interfaces, err := net.Interfaces()
	if err != nil {
		println(err)
	}

	var wg sync.WaitGroup
	var mutex sync.Mutex

	for _, i := range interfaces {
		if i.Flags&net.FlagUp == 0 {
			continue
		}
		if i.Flags&net.FlagLoopback != 0 {
			continue
		}
		addrs, err := i.Addrs()
		if err != nil {
			println(err)
		}
		for _, addr := range addrs {
			ip, ok := addr.(*net.IPNet)
			if ok && ip.IP.To4() != nil {
				host := ip.IP.String()
				wg.Add(len(ports))
				for _, port := range ports {
					go func(host string, port int) {
						defer wg.Done()
						if s.ScanPort("tcp", host, port) {
							mutex.Lock()
							hostArray = append(hostArray, host)
							fmt.Printf("[+] Host: %s is up on port %d\n", host, port)
							mutex.Unlock()
						}
					}(host, port)
				}
			}
		}
	}
	wg.Wait()
	return hostArray
}

func InternalIP() (string, error) {
	interfaces, err := net.Interfaces()
	if err != nil {
		return "", err
	}

	for _, iface := range interfaces {
		addrs, err := iface.Addrs()
		if err != nil {
			return "", err
		}

		for _, addr := range addrs {
			if ipNet, ok := addr.(*net.IPNet); ok && !ipNet.IP.IsLoopback() && !ipNet.IP.IsLinkLocalUnicast() {
				if ipNet.IP.To4() != nil {
					return ipNet.IP.String(), nil
				}
			}
		}
	}

	return "", err
}
