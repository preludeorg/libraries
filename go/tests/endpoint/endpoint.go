package Endpoint

import (
	"archive/zip"
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"encoding/gob"
	"fmt"
	"io"
	"io/fs"
	"math/rand"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"
)

const (
	// Errors
	UnexpectedTestError      int = 1
	TimeoutExceeded          int = 102
	CleanupFailed            int = 103
	OutOfMemory              int = 137
	UnexpectedExecutionError int = 256

	// Not Relevant
	NotRelevant       	int = 104
	InsufficientPrivileges 	int = 109

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

var socketPath string

type DropperPayload struct {
	Filename string
	Contents []byte
}

type fn func()

var cleanup fn = func() {}

var cwd, cwdErr = os.Getwd()
var bin, binErr = os.Executable()

func init() {
	if cwdErr == nil && binErr == nil {
		bindir := filepath.Dir(bin)
		if bindir != cwd {
			Say("Current directory is \"%s\", changing to executable directory \"%s\" for test execution", cwd, bindir)
			os.Chdir(bindir)
			cwd = bindir
			Say("Directory successfully changed to \"%s\"", cwd)
		}
	}
}

func AES256GCMDecrypt(data, key []byte) ([]byte, error) {
	blockCipher, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	gcm, err := cipher.NewGCM(blockCipher)
	if err != nil {
		return nil, err
	}

	nonceSize := gcm.NonceSize()
	if len(data) < nonceSize {
		return nil, fmt.Errorf("ciphertext too short")
	}

	nonce, ciphertext := data[:nonceSize], data[nonceSize:]
	plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return nil, err
	}
	return plaintext, nil
}

func AES256GCMEncrypt(data []byte) ([]byte, []byte, error) {
	key, err := generateKey()
	if err != nil {
		return nil, nil, err
	}

	blockCipher, err := aes.NewCipher(key)
	if err != nil {
		return nil, nil, err
	}

	gcm, err := cipher.NewGCM(blockCipher)
	if err != nil {
		return nil, nil, err
	}

	nonce := make([]byte, gcm.NonceSize())
	for i := range nonce {
		nonce[i] = byte(rand.Intn(256))
	}

	ciphertext := gcm.Seal(nonce, nonce, data, nil)
	return ciphertext, key, nil
}

func CheckAdmin() bool {
	switch platform := runtime.GOOS; platform {
	case "windows":
		_, err := os.Open("\\\\.\\PHYSICALDRIVE0")
		if err != nil {
			return false
		}
		return true
	case "linux", "darwin":
		return os.Getuid() == 0
	default:
		Say("Platform not supported")
		return false
	}
}

func clearSocketPath() {
	Say("Clearing socket path")
	socketPath = ""
}

func Dropper(dropper []byte) error {
	Say("Writing dropper executable to disk")
	switch platform := GetOS(); platform {
	case "windows":
		if err := Write(fmt.Sprintf("%s_prelude_dropper.exe", GetTestIdFromExecutableName()), dropper); err != nil {
			return fmt.Errorf("got error \"%v\" when writing dropper to host", err)
		}
	default:
		if err := os.WriteFile(fmt.Sprintf("%s_prelude_dropper", GetTestIdFromExecutableName()), dropper, 0744); err != nil {
			return fmt.Errorf("got error \"%v\" when writing dropper to host", err)
		}
	}
	Say("Wrote dropper successfully")
	setSocketPath()
	return nil
}

func ExecuteRandomCommand(commands [][]string) (string, error) {
	var command []string
	if len(commands) == 0 {
		return "", fmt.Errorf("command slice is empty")
	} else if len(commands) == 1 {
		command = commands[0]
	} else {
		index := rand.Intn(len(commands))
		command = commands[index]
	}

	return Shell(command)
}

func Exists(path string) bool {
	if _, err := os.Stat(path); err == nil {
		return true
	} else {
		return false
	}
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

func generateKey() ([]byte, error) {
	key := make([]byte, 32)
	for i := range key {
		key[i] = byte(rand.Intn(256))
	}
	return key, nil
}

func GetTestIdFromExecutableName() string {
	switch platform := GetOS(); platform {
	case "windows":
		return strings.Split(filepath.Base(os.Args[0]), ".")[0]
	default:
		return filepath.Base(os.Args[0])
	}
}

func GetOS() string {
	os := runtime.GOOS

	if os != "windows" && os != "linux" && os != "darwin" {
		return "unsupported"
	}

	return os
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

func Pwd(filename string) string {
	if cwdErr != nil {
		Say("Failed to get path. %v", cwdErr)
		Stop(256)
	}
	filePath := filepath.Join(cwd, filename)
	return filePath
}

func Quarantined(filename string, contents []byte) bool {
	if err := Write(filename, contents); err != nil {
		Say(fmt.Sprintf("Got error \"%v\" when writing file", err))
	}
	Wait(-1)
	if exists := Exists(Pwd(filename)); exists {
		return false // file exists so return not-quarantined
	}
	return true // file does not exist so return yes quarantined
}

func Read(path string) []byte {
	bit, err := os.ReadFile(Pwd(path))
	if err != nil {
		Say(fmt.Sprintf("Error: %s", err))
	}
	return bit
}

func Remove(path string) bool {
	e := os.Remove(path)
	return e == nil
}

func Say(print string, ifc ...interface{}) {
	filename := filepath.Base(os.Args[0])
	name := strings.TrimSuffix(filename, filepath.Ext(filename))
	timeStamp := time.Now().Format("2006-01-02T15:04:05")
	fmt.Printf("[%s][%s] %v\n", timeStamp, name, fmt.Sprintf(print, ifc...))
}

func setSocketPath() {
	Say("Setting socket path")
	execPath, _ := os.Executable()
	socketPath = filepath.Join(filepath.Dir(execPath), "prelude_socket")
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

func Start(test fn, clean ...fn) {
	if len(clean) > 0 {
		cleanup = clean[0]
	}

	Say(fmt.Sprintf("Starting test at: %s", time.Now().Format("2006-01-02T15:04:05")))

	go func() {
		test()
	}()

	select {
	case <-time.After(30 * time.Second):
		os.Exit(102)
	}
}

func startDropperChildProcess() (*os.Process, error) {
	execDir := filepath.Dir(socketPath)

	var listenerPath string

	switch platform := GetOS(); platform {
	case "windows":
		listenerPath = filepath.Join(execDir, fmt.Sprintf("%s_prelude_dropper.exe", GetTestIdFromExecutableName()))
	default:
		listenerPath = filepath.Join(execDir, fmt.Sprintf("%s_prelude_dropper", GetTestIdFromExecutableName()))
	}
	Say("Launching " + listenerPath)

	cmd := exec.Command(listenerPath)

	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("failed to start dropper child process: \"%v\"", err)
	}

	return cmd.Process, nil
}

func Stop(code int) {
	cleanup()
	// Get the caller's line number
	_, _, line, _ := runtime.Caller(1)

	Say(fmt.Sprintf("Completed with code: %d", code))
	Say(fmt.Sprintf("Exit called from line: %d", line))
	Say(fmt.Sprintf("Ending test at: %s", time.Now().Format("2006-01-02T15:04:05")))

	os.Exit(code)
}

func Unzip(zipData []byte) error {
	zipReader, err := zip.NewReader(bytes.NewReader(zipData), int64(len(zipData)))
	if err != nil {
		return err
	}

	for _, file := range zipReader.File {
		filePath := filepath.Join(".", file.Name)

		if file.FileInfo().IsDir() {
			os.MkdirAll(filePath, os.ModePerm)
			continue
		}

		fileData, err := file.Open()
		if err != nil {
			return err
		}
		defer fileData.Close()

		outFile, err := os.Create(filePath)
		if err != nil {
			return err
		}
		defer outFile.Close()

		_, err = io.Copy(outFile, fileData)
		if err != nil {
			return err
		}
	}

	return nil
}

// NB: time.Duration is an int64 cast
func Wait(dur time.Duration) {
	if dur <= 0 { // default
		Say("Waiting for 3 seconds")
		time.Sleep(3 * time.Second)
	} else {
		Say(fmt.Sprintf("Waiting for %d seconds", dur))
		time.Sleep(dur * time.Second)
	}
}

func Write(filename string, contents []byte) error {
	var err error
	path := Pwd(filename)
	if socketPath != "" {
		Say("Performing IPC-style file write")
		err = writeIPC(path, contents)
	} else {
		Say("Performing normal file write")
		err = os.WriteFile(path, contents, 0644)
	}
	if err != nil {
		return err
	}
	return nil
}

func writeIPC(filename string, contents []byte) error {
	dropProc, err := startDropperChildProcess()
	if err != nil {
		return fmt.Errorf("got error \"%v\" when starting dropper child process", err)
	}
	Say(fmt.Sprintf("Started dropper child process with PID %d", dropProc.Pid))

	Wait(-1)

	Say(fmt.Sprintf("Connecting to socket: %s", socketPath))
	conn, err := net.Dial("unix", socketPath)
	if err != nil {
		return fmt.Errorf("got error \"%v\" when connecting to socket", err)
	}
	Say("Connected to socket!")
	defer conn.Close()

	payload := DropperPayload{
		Filename: filename,
		Contents: contents,
	}

	if err = gob.NewEncoder(conn).Encode(payload); err != nil {
		return fmt.Errorf("got error \"%v\" when writing to socket", err)
	}

	Wait(1)
	Say("Killing dropper child process")
	dropProc.Kill()
	clearSocketPath()

	return nil
}

func XorDecrypt(data []byte, key byte) []byte {
	decrypted := make([]byte, len(data))
	for i, v := range data {
		decrypted[i] = v ^ key
	}
	return decrypted
}

func XorEncrypt(data []byte) ([]byte, byte, error) {
	keyData, err := generateKey()
	if err != nil {
		return nil, 0, err
	}
	key := keyData[0] // Use the first byte of the generated key

	encrypted := make([]byte, len(data))
	for i, v := range data {
		encrypted[i] = v ^ key
	}
	return encrypted, key, nil
}
