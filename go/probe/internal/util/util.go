package util

import (
	"errors"
	"io"
	"io/fs"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
)

func Request(url string, headers map[string]string) ([]byte, string, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, "", err
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, "", err
	}
	body, err := io.ReadAll(resp.Body)
	defer resp.Body.Close()
	if err != nil {
		return nil, "", err
	}

	return body, parseUUID(url), nil
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
			defer os.Remove(f.Name())
			if err != nil {
				return nil
			}
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

func parseUUID(str string) string {
	uri, err := url.Parse(str)
	if err == nil {
		path := uri.EscapedPath()
		components := strings.Split(path, "/")
		if len(components) > 2 {
			return components[2]
		}
	}
	return ""
}
