package util

import (
	"bytes"
	"errors"
	"io"
	"io/fs"
	"net/http"
	"os"
	"path/filepath"
)

func GetEnv(key, defaultValue string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return defaultValue
}

func Request(url string, data []byte, headers map[string]string) ([]byte, error) {
	client := &http.Client{}
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(data))
	if err != nil {
		return nil, err
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	body, err := io.ReadAll(resp.Body)
	defer resp.Body.Close()
	if err != nil {
		return nil, err
	}
	return body, nil
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
