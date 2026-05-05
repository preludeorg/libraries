package agent

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

// --- parseInputVariables ---

func TestParseInputVariables(t *testing.T) {
	tests := []struct {
		name  string
		input []byte
		want  map[string]string
	}{
		{"empty", []byte(""), map[string]string{}},
		{"whitespace", []byte("  \n"), map[string]string{}},
		{"Variables wrapper", []byte(`{"Variables":{"token":"abc","host":"x"}}`), map[string]string{"token": "abc", "host": "x"}},
		{"flat map", []byte(`{"foo":"bar"}`), map[string]string{"foo": "bar"}},
		{"invalid JSON", []byte(`not json`), map[string]string{}},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got := parseInputVariables(tc.input)
			if len(got) != len(tc.want) {
				t.Fatalf("got %v, want %v", got, tc.want)
			}
			for k, v := range tc.want {
				if got[k] != v {
					t.Errorf("key %q: got %q, want %q", k, got[k], v)
				}
			}
		})
	}
}

// --- VstID ---

func TestVstID(t *testing.T) {
	id := VstID()
	if id == "" {
		t.Fatal("VstID returned empty string")
	}
	if strings.Contains(id, ".") {
		t.Errorf("VstID %q should not contain a file extension", id)
	}
	if strings.Contains(id, "_") {
		t.Errorf("VstID %q should not contain an underscore suffix", id)
	}
}

// --- PrivilegeLabel ---

func TestPrivilegeLabelNoMatch(t *testing.T) {
	if strings.HasPrefix(filepath.Base(cwd), "PreludeHelper_") {
		t.Skip("cwd matches PreludeHelper_ prefix, skipping no-match case")
	}
	if got := PrivilegeLabel(); got != "" {
		t.Errorf("expected empty label for non-PreludeHelper cwd, got %q", got)
	}
}

func TestPrivilegeLabelMatch(t *testing.T) {
	orig := cwd
	cwd = filepath.Join("/tmp", "PreludeHelper_Admin")
	defer func() { cwd = orig }()

	if got := PrivilegeLabel(); got != "admin" {
		t.Errorf("expected label %q, got %q", "admin", got)
	}
}

// --- ReadInputs ---

func TestReadInputsEmptyPipe(t *testing.T) {
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	w.Close()

	orig := os.Stdin
	os.Stdin = r
	defer func() { os.Stdin = orig; r.Close() }()

	if got := ReadInputs(); len(got) != 0 {
		t.Errorf("expected empty map from closed pipe, got %v", got)
	}
}

func TestReadInputsVariablesWrapper(t *testing.T) {
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	w.Write([]byte(`{"Variables":{"token":"abc123","env":"prod"}}`))
	w.Close()

	orig := os.Stdin
	os.Stdin = r
	defer func() { os.Stdin = orig; r.Close() }()

	got := ReadInputs()
	for k, want := range map[string]string{"token": "abc123", "env": "prod"} {
		if got[k] != want {
			t.Errorf("key %q: got %q, want %q", k, got[k], want)
		}
	}
}

func TestReadInputsFlatMap(t *testing.T) {
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	w.Write([]byte(`{"target":"host.local"}`))
	w.Close()

	orig := os.Stdin
	os.Stdin = r
	defer func() { os.Stdin = orig; r.Close() }()

	got := ReadInputs()
	if got["target"] != "host.local" {
		t.Errorf("expected target=host.local, got %v", got)
	}
}

// --- RequirePrivilege ---

func TestRequirePrivilegeUnprivileged(t *testing.T) {
	if os.Getuid() == 0 {
		t.Skip("running as root, cannot test unprivileged satisfied path")
	}
	// Should not exit — test process survives if satisfied
	RequirePrivilege("unprivileged")
}

func TestRequirePrivilegePrivileged(t *testing.T) {
	if os.Getuid() != 0 {
		t.Skip("not running as root, cannot test privileged satisfied path")
	}
	RequirePrivilege("privileged")
}

// TestRequirePrivilegeExits verifies that RequirePrivilege exits 109 when the
// privilege requirement is not met. Uses the subprocess pattern to avoid
// killing the test runner via os.Exit.
func TestRequirePrivilegeExits(t *testing.T) {
	if os.Getenv("_TEST_RUNAS_EXIT") == "1" {
		RequirePrivilege("privileged") // exits 109 when not root
		return
	}
	if os.Getuid() == 0 {
		t.Skip("running as root, privileged check would not exit")
	}

	cmd := exec.Command(os.Args[0], "-test.run=TestRequirePrivilegeExits", "-test.v")
	cmd.Env = append(os.Environ(), "_TEST_RUNAS_EXIT=1")
	err := cmd.Run()

	exit, ok := err.(*exec.ExitError)
	if !ok {
		t.Fatalf("expected exit error, got %v", err)
	}
	if exit.ExitCode() != 109 {
		t.Errorf("expected exit code 109, got %d", exit.ExitCode())
	}
}
