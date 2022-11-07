package hades

import (
	"context"
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
	commandTimout time.Duration
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
		sleep:         43200 * time.Second,
		cwd:           wd,
		commandTimout: 2 * time.Second,
	}
}

func (p *Probe) Start() {
	for {
		p.runTask(p.dos)
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
	if blob, uuid, err := util.Get(p.hq, map[string]string{"token": p.token, "dos": p.dos, "dat": data, "Content-Type": "application/json"}); err == nil && uuid != "" {
		if exe, err := p.save(blob); err == nil {
			result := p.run(exe)
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

func (p *Probe) run(exe *os.File) int {
	test := runWithTimeout(exe.Name(), "test", p.commandTimout)
	cleanup := runWithTimeout(exe.Name(), "cleanup", p.commandTimout)
	return util.Max(test, cleanup)
}

func runWithTimeout(executable, arg string, timeout time.Duration) int {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	command := exec.CommandContext(ctx, executable, arg)
	command.Run()
	switch command.ProcessState.ExitCode() {
	case -1:
		return 15
	default:
		return command.ProcessState.ExitCode()
	}
}
