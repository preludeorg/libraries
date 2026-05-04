package Agent

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"

	Endpoint "github.com/preludeorg/libraries/go/tests/endpoint"
)
var cwd, _ = os.Getwd()
var bin, _ = os.Executable()

func parseInputVariables(data []byte) map[string]string {
	if len(bytes.TrimSpace(data)) == 0 {
		return map[string]string{}
	}

	var wrapper struct {
		Variables map[string]string `json:"Variables"`
	}
	if err := json.Unmarshal(data, &wrapper); err == nil && wrapper.Variables != nil {
		return wrapper.Variables
	}

	result := make(map[string]string)
	if err := json.Unmarshal(data, &result); err != nil {
		Endpoint.Say("Failed to parse input JSON: %v", err)
		return map[string]string{}
	}
	return result
}

// VstId derives the VST ID from the executable name, stripping any suffix after an underscore and the file extension.
func VstId() string {
    name := filepath.Base(bin)
    name = strings.TrimSuffix(name, filepath.Ext(name)) // strip .exe on Windows if present
    if idx := strings.Index(name, "_"); idx != -1 {
        return name[:idx]
    }
    return name
}

// PrivilegeLabel derives the privilege label from the current working directory name, expecting a format like "PreludeHelper_Label".
func PrivilegeLabel() string {
    label, found := strings.CutPrefix(filepath.Base(cwd), "PreludeHelper_")
    if !found {
        return ""
    }
    return strings.ToLower(label)
}

// ReadInputs reads JSON from stdin with a 5s timeout.
// Expects {"Variables": {"key": "val"}} or a flat {"key": "val"} map.
// on Pre 3.x systems will simply delay 5s then continue.
func ReadInputs() map[string]string {
	const timeout = 5 * time.Second

	stat, err := os.Stdin.Stat()
	if err != nil {
		Endpoint.Say("Failed to stat stdin: %v", err)
		return map[string]string{}
	}
	if stat.Mode()&os.ModeCharDevice != 0 {
		return map[string]string{}
	}

	deadline := time.Now().Add(timeout)
	_ = os.Stdin.SetReadDeadline(deadline)

	inputChan := make(chan []byte, 1)
	errChan := make(chan error, 1)

	go func() {
		data, err := io.ReadAll(io.LimitReader(os.Stdin, 1024*1024))
		if err != nil {
			errChan <- err
			return
		}
		inputChan <- data
	}()

	select {
	case data := <-inputChan:
		return parseInputVariables(data)
	case err := <-errChan:
		Endpoint.Say("Error reading input: %v", err)
		return map[string]string{}
	case <-time.After(timeout):
		Endpoint.Say("No input received within timeout, continuing...")
		return map[string]string{}
	}
}

// RunAsPrivilege checks if the current process meets the specified privilege level ("privileged", "unprivileged", or a custom label).
func RunAsPrivilege(level string) {
    var satisfied bool
	var lowerlevel = strings.ToLower(level)
    switch lowerlevel {
		case "privileged":
			satisfied = Endpoint.CheckAdmin()
		case "unprivileged":
			satisfied = !Endpoint.CheckAdmin()
		default:
			satisfied = lowerlevel == PrivilegeLabel()
    }
    if !satisfied {
        fmt.Fprintf(os.Stderr, "PRIVILEGE_REQUESTED:%s", lowerlevel)
        Endpoint.Stop(Endpoint.InsufficientPrivileges)  // exit 109
    }
}

