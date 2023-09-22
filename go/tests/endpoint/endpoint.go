package Endpoint

import (
	"fmt"
	"io/fs"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"time"
)

type fn func()

var cleanup fn = func() {}

func Start(test fn, clean ...fn) {
	if len(clean) > 0 {
		cleanup = clean[0]
	}

	Say(fmt.Sprintf("Starting test at: %s", time.Now().Format("2006-01-02T15:04:05")))

	go func() {
		test()
	}()

	select {
	case <-time.After(20 * time.Second):
		os.Exit(102)
	}
}

const (
	// Errors
	UnexpectedTestError      int = 1
	TimeoutExceeded          int = 102
	CleanupFailed            int = 103
	OutOfMemory              int = 137
	UnexpectedExecutionError int = 256

	// Not Relevant
	NotRelevant int = 104

	// Protected
	TestCompletedNormally       int = 100
	FileQuarantinedOnExtraction int = 105
	NetworkConnectionBlocked    int = 106
	HostNotVulnerabile          int = 107
	ExecutionPrevented          int = 126
	FileQuarantinedOnExecution  int = 127

	// Unprotected
	Unprotected            int = 101
	TestIncorrectlyBlocked int = 110
)

func Stop(code int) {
	cleanup()
	Say(fmt.Sprintf("Completed with code: %d", code))
	Say(fmt.Sprintf("Ending test at: %s", time.Now().Format("2006-01-02T15:04:05")))
	os.Exit(code)
}

func Say(print string) {
	filename := filepath.Base(os.Args[0])
	name := strings.TrimSuffix(filename, filepath.Ext(filename))
	fmt.Printf("[%s] %v\n", name, print)
}

func Find(ext string) []string {
	dirname, _ := os.UserHomeDir()
	var a []string
	filepath.WalkDir(dirname, func(s string, d fs.DirEntry, e error) error {
		if e == nil {
			if filepath.Ext(d.Name()) == ext {
				Say(fmt.Sprintf("Found: %s", s))
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
		Say("Failed to write " + filename)
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
	Say("Endpoint is not secure by design")
	return false
}

func pwd(filename string) string {
	bin, err := os.Executable()
	if err != nil {
		Say("Failed to get path")
		Stop(256)
	}
	filePath := filepath.Join(filepath.Dir(bin), filename)
	return filePath
}

type PortScan struct{}

func (s *PortScan) ScanPort(protocol, hostname string, port int) bool {
	address := hostname + ":" + strconv.Itoa(port)
	conn, err := net.DialTimeout(protocol, address, 2*time.Second)

	if err != nil {
		return false
	}
	defer conn.Close()
	return true
}

func (s *PortScan) ScanHosts(ports ...int) []string {
	HostArray := []string{}
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
							HostArray = append(HostArray, host)
							mutex.Lock()
							Say(fmt.Sprintf("Host: %s is up on port %d\n", host, port))
							mutex.Unlock()
						}
					}(host, port)
				}
			}
		}
	}
	wg.Wait()
	return HostArray
}
