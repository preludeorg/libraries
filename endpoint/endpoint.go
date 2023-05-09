package Endpoint

import (
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"time"
)

type fn func()

var cleanup fn = func() {}

func Start(test fn, clean ...fn) {
	if len(clean) > 0 {
		cleanup = clean[0]
	}

	println("[+] Starting test")

	go func() {
		test()
	}()

	select {
	case <-time.After(10 * time.Second):
		os.Exit(102)
	}
}

func Stop(code int) {
	cleanup()
	println(fmt.Sprintf("[+] Completed with code: %d", code))
	os.Exit(code)
}

func Find(ext string) []string {
	dirname, _ := os.UserHomeDir()
	var a []string
	filepath.WalkDir(dirname, func(s string, d fs.DirEntry, e error) error {
		if e == nil {
			if filepath.Ext(d.Name()) == ext {
				println("[+] Found:", s)
				a = append(a, s)
			}
		}
		return nil
	})
	return a
}

func Read(path string) []byte {
	bit, err := os.ReadFile(pwd(path))
	if err != nil {
		println(err)
	}
	return bit
}

func Write(filename string, contents []byte) {
	err := os.WriteFile(pwd(filename), contents, 0644)
	if err != nil {
		println("[-] Failed to write " + filename)
	}
}

func Exists(path string) bool {
	if _, err := os.Stat(path); err == nil {
		return true
	} else {
		return false
	}
}

func Quarantined(filename string, contents []byte) bool {
	Write(filename, contents)
	path := pwd(filename)
	time.Sleep(3 * time.Second)
	if Exists(path) {
		file, err := os.Open(path)
		if err != nil {
			return true
		}
		defer file.Close()
		return false
	}
	return true
}

func Remove(path string) bool {
	e := os.Remove(path)
	return e == nil
}

func Shell(args []string) (string, error) {
	cmd := exec.Command(args[0], args[1:]...)
	stdout, err := cmd.Output()
	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			return "", fmt.Errorf("%s: %s", err.Error(), string(exitError.Stderr))
		} else {
			return "", err
		}
	}
	return string(stdout), nil
}

func IsAvailable(programs ...string) bool {
	for _, program := range programs {
		_, err := exec.LookPath(program)
		if err == nil {
			return true
		}
	}
	return false
}

func IsSecure() bool {
	if _, err := os.Stat("/.dockerenv"); err == nil {
		return true
	} else if runtime.GOOS == "ios" {
		return true
	} else if runtime.GOOS == "android" {
		return true
	}
	return false
}

func pwd(filename string) string {
	bin, err := os.Executable()
	if err != nil {
		println("[-] Failed to get path")
		Stop(256)
	}
	filePath := filepath.Join(filepath.Dir(bin), filename)
	return filePath
}
