package hades

import (
	"context"
	"fmt"
	"github.com/preludeorg/detect-clients/go/probe/internal/util"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"
)

type Probe struct {
	signals chan bool
	token   string
	hq      string
	dos     string
	sleep   time.Duration
	cwd     string
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
		signals: make(chan bool),
		token:   token,
		hq:      strings.TrimSuffix(hq, "/"),
		dos:     strings.ToLower(fmt.Sprintf("%s-%s", runtime.GOOS, runtime.GOARCH)),
		sleep:   43200 * time.Second,
		cwd:     wd,
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
	if blob, uuid, err := util.Request(fmt.Sprintf("%s?link=%s", p.hq, data), map[string]string{"token": p.token}); err == nil && uuid != "" {
		if exe, err := p.save(blob); err == nil {
			result := p.run(exe)
			_ = os.Remove(exe.Name())
			p.runTask(fmt.Sprintf("%s:%s:%d", p.dos, uuid, result))
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
	test := runWithTimeout(exe.Name(), "test")
	cleanup := runWithTimeout(exe.Name(), "cleanup")
	return util.Max(test, cleanup)
}

func runWithTimeout(executable, arg string) int {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
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
