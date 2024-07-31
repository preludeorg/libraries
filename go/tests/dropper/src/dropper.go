package main

import (
	"encoding/gob"
	"net"
	"os"
	"path/filepath"
)

type DropperPayload struct {
	Filename string
	Contents []byte
}

func main() {
	execPath, err := os.Executable()
	if err != nil {
		os.Exit(1)
	}

	socketPath := filepath.Join(filepath.Dir(execPath), "prelude_socket")

	if err := os.RemoveAll(socketPath); err != nil {
		os.Exit(1)
	}

	listener, err := net.Listen("unix", socketPath)
	if err != nil {
		os.Exit(1)
	}
	defer listener.Close()

	err = os.Chmod(socketPath, 0700)
	if err != nil {
		os.Exit(1)
	}

	conn, err := listener.Accept()
	if err != nil {
		os.Exit(1)
	}
	defer conn.Close()

	var payload DropperPayload
	if err = gob.NewDecoder(conn).Decode(&payload); err != nil {
		os.Exit(1)
	}

	if err = os.WriteFile(payload.Filename, payload.Contents, 0644); err != nil {
		os.Exit(1)
	}

	os.Exit(0)
}
