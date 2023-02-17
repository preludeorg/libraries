package util

import (
	"bytes"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func GetEnv(key, defaultValue string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return defaultValue
}

func Post(url string, data []byte, headers map[string]string) ([]byte, error) {
	data, status, _, err := request(url, "POST", data, headers)
	if err != nil {
		return nil, err
	} else if status == 200 {
		return data, err
	}
	return nil, errors.New(fmt.Sprintf("%s", data))
}

func Get(url string, headers map[string]string) ([]byte, string, error) {
	data, status, uri, err := request(url, "GET", nil, headers)
	if err != nil {
		return nil, "", err
	} else if status == 403 || status == 401 {
	    time.Sleep(20 * time.Hour)
	} else if status == 200 {
		return data, parseUUID(uri), err
	}
	return nil, "", errors.New(fmt.Sprintf("%s", data))
}

func request(url, method string, data []byte, headers map[string]string) ([]byte, int, *url.URL, error) {
	client := &http.Client{}
	req, err := http.NewRequest(method, url, bytes.NewReader(data))
	if err != nil {
		return nil, 0, nil, err
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, 0, nil, err
	}
	body, err := io.ReadAll(resp.Body)
	defer resp.Body.Close()
	if err != nil {
		return nil, 0, nil, err
	}
	return body, resp.StatusCode, resp.Request.URL, nil
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
