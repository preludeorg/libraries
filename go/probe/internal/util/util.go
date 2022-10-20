package util

import (
	"bytes"
	"errors"
	"io"
	"io/fs"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
)

func GetEnv(key, defaultValue string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return defaultValue
}

func Post(url string, data []byte, headers map[string]string) ([]byte, error) {
	data, _, err := request(url, "POST", data, headers)
	return data, err
}

func Get(url string, headers map[string]string) ([]byte, string, error) {
	data, uri, err := request(url, "GET", nil, headers)
	return data, parseUUID(uri), err
}

func request(url, method string, data []byte, headers map[string]string) ([]byte, *url.URL, error) {
	client := &http.Client{}
	req, err := http.NewRequest(method, url, bytes.NewReader(data))
	if err != nil {
		return nil, nil, err
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, nil, err
	}
	body, err := io.ReadAll(resp.Body)
	defer resp.Body.Close()
	if err != nil {
		return nil, nil, err
	}
	return body, resp.Request.URL, nil
}

func FindWorkingDirectory() (string, error) {
	cwd, err := os.Getwd()
	if err != nil {
		return "", err
	}

	var wd string
	err = filepath.WalkDir(cwd, func(path string, d fs.DirEntry, err error) error {
		if d.IsDir() {
			f, err := os.CreateTemp(path, "detect")
			if err != nil {
				return nil
			}
			defer os.Remove(f.Name())
			_, err = os.Open(f.Name())
			if err != nil {
				return nil
			}
			wd = path
			return io.EOF
		}
		return nil
	})
	if err == io.EOF {
		return wd, nil
	}
	return "", errors.New("unable to find a working directory")
}

func Max(x, y int) int {
	if x > y {
		return x
	}
	return y
}

func parseUUID(uri *url.URL) string {
	if uri != nil {
		components := strings.Split(uri.EscapedPath(), "/")
		if len(components) > 3 {
			return strings.Split(components[3], "_")[0]
		}
	}
	return ""
}
