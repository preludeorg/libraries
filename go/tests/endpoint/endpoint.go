package Endpoint

import (
	"archive/zip"
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"fmt"
	"io"
	"io/fs"
	"math/rand"
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
	case <-time.After(30 * time.Second):
		os.Exit(102)
	}
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

func Say(print string) {
	filename := filepath.Base(os.Args[0])
	name := strings.TrimSuffix(filename, filepath.Ext(filename))
	timeStamp := time.Now().Format("2006-01-02T15:04:05")
	fmt.Printf("[%s][%s] %v\n", timeStamp, name, print)
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
	bit, err := os.ReadFile(Pwd(path))
	if err != nil {
		Say(fmt.Sprintf("Error: %s", err))
	}
	return bit
}

func Write(filename string, contents []byte) {
	err := os.WriteFile(Pwd(filename), contents, 0644)
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

func GetOS() string {
	os := runtime.GOOS

	if os != "windows" && os != "linux" && os != "darwin" {
		return "unsupported"
	}

	return os
}

func Quarantined(filename string, contents []byte) bool {
	Write(filename, contents)
	path := Pwd(filename)
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
	bin, err := os.Executable()
	if err != nil {
		Say("Failed to get path")
		Stop(256)
	}
	filePath := filepath.Join(filepath.Dir(bin), filename)
	return filePath
}

func XorEncrypt(data []byte) ([]byte, []byte, error) {
	keyData, err := generateKey()
	if err != nil {
		return nil, nil, err
	}

	encrypted := make([]byte, len(data))
	for i, v := range data {
		encrypted[i] = v ^ (keyData[i%len(keyData)] + byte(i))
	}
	return encrypted, keyData, nil
}

func XorDecrypt(data []byte, key []byte) []byte {
	decrypted := make([]byte, len(data))
	for i, v := range data {
		decrypted[i] = v ^ (key[i%len(key)] + byte(i))
	}
	return decrypted
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

func generateKey() ([]byte, error) {
	key := make([]byte, 32)
	for i := range key {
		key[i] = byte(rand.Intn(256))
	}
	return key, nil
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
