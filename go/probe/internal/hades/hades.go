package hades

import (
	"fmt"
	"github.com/preludeorg/libraries/go/probe/internal/util"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"
)

type Probe struct {
	signals       chan bool
	token         string
	hq            string
	dos           string
	sleep         time.Duration
	cwd           string
}

type Actions interface {
	Start()
	Stop()
	runTask([]byte)
	run(string) int
	save([]byte) (*os.File, error)
}

func CreateProbe(token, hq string) *Probe {
	wd, err := util.FindWorkingDirectory()
	if err != nil {
		return nil
	}
	return &Probe{
		signals:       make(chan bool),
		token:         token,
		hq:            strings.TrimSuffix(hq, "/"),
		dos:           strings.ToLower(fmt.Sprintf("%s-%s", runtime.GOOS, runtime.GOARCH)),
		sleep:         14400 * time.Second,
		cwd:           wd,
	}
}

func (p *Probe) Start() {
	for {
		p.runTask("")
		fmt.Println("INFO: Done running tests")
		select {
		case <-p.signals:
			return
		case <-time.After(p.sleep):
			continue
		}
	}
}

func (p *Probe) Stop() {
	p.signals <- true
}

func (p *Probe) runTask(data string) {
	if blob, uuid, err := util.Get(p.hq, map[string]string{"token": p.token, "dos": p.dos, "dat": data}); err == nil && uuid != "" {
		if exe, err := p.save(blob); err == nil {
            result := run(exe.Name())
            run(exe.Name(), "clean")
			_ = os.Remove(exe.Name())
			p.runTask(fmt.Sprintf("%s:%d", uuid, result))
		}
	}
}

func (p *Probe) save(data []byte) (*os.File, error) {
	f, err := os.CreateTemp(p.cwd, "detect")
	if err != nil {
		return nil, err
	}

	if _, err := f.Write(data); err != nil {
		return nil, err
	}

	if err := f.Close(); err != nil {
		return nil, err
	}

	err = os.Chmod(f.Name(), 0500)
	if err != nil {
		return nil, err
	}

	return f, nil
}

func run(executable string, args ...string) int {
	command := exec.Command(executable, args...)
	command.Stdout, command.Stderr = os.Stdout, os.Stderr
	command.Run()
	switch command.ProcessState.ExitCode() {
	case -1:  // the process hasn't exited or was terminated by a signal
        return 9
	default:
		return command.ProcessState.ExitCode()
	}
}
